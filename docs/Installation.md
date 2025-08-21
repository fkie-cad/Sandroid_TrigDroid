# Installation

> **Note `📝`** If you're developer and want to change something in code, read [developers section in readme](/README.md#for-developers) first.

- [Installation](#installation)
  - [Android Studio](#android-studio)
  - [Setup an Emulator](#setup-an-emulator)
  - [Add apksigner and adb to path](#add-apksigner-and-adb-to-path)
  - [apktool v2.7.0](#apktool-v270)
  - [Python Package Requirements](#python-package-requirements)

Here are some hints for dependency installations:

## Android Studio

You can either follow this [installation guide for Android Studio][android_studio_install_linux] or simply use [snap][android_studio_snap].

## Setup an Emulator

After installing and starting Android Studio, you can use it to create an Android Virtual Device (avd or emulator). Therefor, first check the [requirements][android_studio_run_emulator_requirements] for your system and then [create an emulator][android_studio_run_emulator_avd].

## Add apksigner and adb to path

With Android Studio you've installed the programs [apksigner][apksigner] and [adb][android_debug_bridge]. Now you need to add the directories of the programs to your `PATH` environment variable For the directory of the apksigner, you need to know the sdk version of the sdk you've installed on the android emulator while [setting it up](#setup-an-emulator). [Here is a tutorial][add_to_path] for adding a directory to this variable. You need to add following directories:

- apksigner: `~/Android/Sdk/build-tools/<sdk-version>`
- adb: `/Android/Sdk/platform-tools`

If you don't use the `install` option, you don't need to add the apksigner directory to the `PATH`.

## apktool v2.7.0

The `install` option uses the apktool v2.7.0. If you want to use this option, you have to install it. Inspired by the [installation guide of the apktool][apktool_install], I provide you an installation script, that installs the tool in `/usr/local/bin`. Please consider, that the script needs root privileges. You can run the script like this:

```bash
chmod +x installation/install_apktool.sh
sudo installation/install_apktool.sh
```

After executing the script, you should see the version of the tool (v2.7.0) and some more information. First you see the instruction to install Java, followed by the output of the command `java --version`. If the Java version is less then 1.8, you need to install a newer version of Java, you can to it with the command `sudo apt install default-jre`. At last, you're asked to add the apktool to the `PATH`, normally the directory given above should be already be part of it. You can print the PATH with `echo $PATH`. If this isn't the case, you can find a [tutorial about adding something to `PATH` here][add_to_path].

## Python Package Requirements

This program needs several external python libraries. To install them all together, you can use this command:

```bash
pip install -r installation/requirements.txt
```

<!-- external links -->

[add_to_path]: https://linuxize.com/post/how-to-add-directory-to-path-in-linux/ "Tutorial for adding something to PATH"
[android_debug_bridge]: https://developer.android.com/studio/command-line/adb "Android developers page of ADB"
[android_studio_install_linux]: https://developer.android.com/studio/install#linux "Androids own linux installation guide for Android Studio"
[android_studio_run_emulator_avd]: https://developer.android.com/studio/run/emulator#avd "Android Studio guide for running apps on an emulator. This link leads to the first Step: Create an Android Virtual Device"
[android_studio_run_emulator_requirements]: https://developer.android.com/studio/run/emulator#requirements "Android Studio guide for running apps on an emulator. This link leads to the first Step: Emulator system requirements"
[android_studio_snap]: https://snapcraft.io/android-studio "Snap page of Android Studio"
[apksigner]: https://developer.android.com/studio/command-line/
[apktool_install]: https://ibotpeaches.github.io/Apktool/install/ "apktool installation instructions"
