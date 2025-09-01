# ===== 基本イメージ =====
FROM ubuntu:22.04

# ===== 環境変数 =====
ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV ANDROIDSDK=/root/.buildozer/android/platform/android-sdk
ENV ANDROIDNDK=/root/.buildozer/android/platform/android-ndk-r25c
ENV ANDROIDAPI=33
ENV ANDROIDMINAPI=21
ENV BUILDIZER_ALLOW_ROOT=1

# ===== 必須パッケージのインストール =====
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git wget curl unzip zip openjdk-17-jdk \
    build-essential libssl-dev libffi-dev \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libsqlite3-dev libreadline-dev libbz2-dev \
    liblzma-dev libgdbm-dev libnss3-dev \
    pkg-config xz-utils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ===== Python ツールのインストール =====
RUN pip install --no-cache-dir uv buildozer cython

# ===== 作業ディレクトリ =====
WORKDIR /app

# ===== UV 仮想環境作成 & パッケージインストール =====
RUN uv venv && \
    /bin/bash -c "source $VIRTUAL_ENV/bin/activate && uv pip install kivy plyer pyjnius"

# ===== Buildozer 初期化 =====
RUN /bin/bash -c "source $VIRTUAL_ENV/bin/activate && yes | buildozer init"

# ===== Android SDK / NDK 自動セットアップ =====
RUN mkdir -p $ANDROIDSDK && \
    cd /tmp && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-9123335_latest.zip -O cmdline-tools.zip && \
    unzip cmdline-tools.zip -d $ANDROIDSDK && \
    rm cmdline-tools.zip && \
    mv $ANDROIDSDK/cmdline-tools $ANDROIDSDK/cmdline-tools-temp && \
    mkdir -p $ANDROIDSDK/cmdline-tools && \
    mv $ANDROIDSDK/cmdline-tools-temp $ANDROIDSDK/cmdline-tools/latest

# ===== Android SDK の必要コンポーネントインストール =====
RUN yes | $ANDROIDSDK/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROIDSDK \
    "platform-tools" \
    "platforms;android-$ANDROIDAPI" \
    "build-tools;33.0.2" \
    "ndk;25.2.9519653" \
    "cmake;3.22.1"

# ===== PATH 調整 =====
ENV PATH="$ANDROIDSDK/cmdline-tools/latest/bin:$ANDROIDSDK/platform-tools:$PATH"

# ===== デフォルトコマンド =====
CMD ["/bin/bash"]
