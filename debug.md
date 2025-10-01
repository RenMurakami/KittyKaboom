# 🚀 KittyKaboom Project

A mobile application developed using **Kivy** and packaged for Android using **Buildozer** and **Python-for-Android**.

## 💻 Development Environment

* **Framework:** Kivy / Python 3
* **Target Platform:** Android (arm64-v8a, armeabi-v7a)
* **Build Toolchain:** Buildozer / Python-for-Android (p4a)
* **Host OS:** Linux / WSL (Ubuntu 22.04)

## 📦 Requirements

To build this project for Android, ensure you have the necessary Buildozer dependencies, an active Python virtual environment (`.venv`), and the Android SDK/NDK configured.

### Build Dependencies (Host OS)

The following system packages are **essential** for a successful cross-compilation process:

```bash
sudo apt install build-essential python3-pip git zip unzip
```

### Summary of Errors and Solutions\

| Bug Encountered | Error Snippet | Detailed Cause and Solution | Command to Fix
| :--- | :--- | :--- | :---|
| **Missing `ctypes`** | `ModuleNotFoundError: No module named '_ctypes'` | **Cause:** The host Python interpreter (Hostpython) failed to compile and link its `_ctypes` module because the required **Foreign Function Interface** development headers were missing from the operating system. | **FIX:** Install the headers: `sudo apt install libffi-dev`. **Action:** Requires full Hostpython cache cleanup. |
| **Missing SSL** | `SSLError("Can't connect to HTTPS URL...")` | **Cause:** Hostpython failed to integrate the **SSL module**, meaning its internal `pip` could not establish secure (HTTPS) connections to download packages from PyPI. This is due to missing OpenSSL development headers. | **FIX:** Install the headers: `sudo apt install libssl-dev`. **Action:** Requires full Hostpython cache cleanup. |
| **Missing Utility** | `sh.CommandNotFound: zip` | **Cause:** The Python-for-Android toolchain explicitly calls the `zip` command-line utility to package the Python Standard Library into a deployable `.zip` file, but the utility was not installed on the system. | **FIX:** Install the utility: `sudo apt install zip`. **Action:** No cache cleanup needed; just rerun the build. |


### Summary of All Build Issues and Solutions

| Problem Type | Error/Symptom | Detailed Cause and Solution | Command to Fix
| :--- | :--- | :--- | :---
| **Git Submodules** | Build fails early; missing directories (`p4a`, `pyjnius`). | **Cause:** The `p4a` and `pyjnius` directories were empty because the repository's submodules were not initialized after cloning. | **FIX:** Update the submodules: `git submodule update --init --recursive`. |
| **Missing `ctypes`** | `ModuleNotFoundError: No module named '_ctypes'` | **Cause:** Hostpython lacked **Foreign Function Interface** support. | **FIX:** Install headers: `sudo apt install libffi-dev`. **Action:** Requires full Hostpython cache cleanup. |
| **Missing SSL** | `SSLError("Can't connect to HTTPS URL...")` | **Cause:** Hostpython lacked **OpenSSL** support, preventing secure `pip` connections. | **FIX:** Install headers: `sudo apt install libssl-dev`. **Action:** Requires full Hostpython cache cleanup. |
| **Missing Utility** | `sh.CommandNotFound: zip` | **Cause:** The build system was missing the basic **`zip`** utility required for final packaging of the standard library. | **FIX:** Install the utility: `sudo apt install zip`. **Action:** No cache cleanup needed; just rerun the build. |


