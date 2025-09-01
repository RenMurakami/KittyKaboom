# KittyKaboom

**Kitty Kaboom** is a Kivy-based Android game project.

This repository contains all files needed to build the game, including Python source, Docker environment, and Android build configuration.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Building the Android App](#building-the-android-app)
4. [Project Structure](#project-structure)
5. [Managing Dependencies](#managing-dependencies)
6. [Notes](#notes)

---

## Prerequisites

- **Docker** (recommended for consistent environment)
- **Git**

> Python or Android SDK setup is fully handled inside Docker, so no local Python installation is required.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your_repo_url>
cd KittyKaboom
```

### 2. Build Docker Image
```bash
docker build -t kivy-dev-full .
```

### 3. Run Docker Container
```bash
docker run --rm -it -v $(pwd):/app kivy-dev-full
```
Inside the container:

```bash
# Activate Python virtual environment
source .venv/bin/activate

# Install missing dependencies if needed
uv pip install -r requirements.txt
```

## Building the Android App
Inside the Docker container with ```.venv``` activated:

```bash
buildozer android debug
```

The APK will be generated in:

```text
bin/kittykaboom-debug.apk
```
To clean build artifacts:

```bash
buildozer android clean
```
## Project Structure
```bash
KittyKaboom/
├── source/             # Python source code
├── p4a/                # python-for-android local recipes
├── Dockerfile          # Docker environment definition
├── buildozer.spec      # Buildozer configuration
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Project metadata (UV)
├── uv.lock             # Locked Python dependencies
└── README.md
```
```.venv/``` and ```.buildozer/``` are generated locally and not included in Git.

## Managing Dependencies 
Add new Python packages:

```bash
uv pip install <package_name>
```
Synchronize installed packages with requirements.txt and lock file:

```bash
uv pip sync
uv lock
```
This ensures that any contributor using the repository gets the exact same Python environment.

## Notes
* Always use Docker for building to ensure consistent environment across machines.

* The project uses uv for Python dependency and virtual environment management.

* Android SDK, NDK, and Build Tools are installed automatically inside Docker.
