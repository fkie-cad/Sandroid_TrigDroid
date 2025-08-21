# Background Information

- [Background Information](#background-information)
  - [Command implementation and possible alternatives](#command-implementation-and-possible-alternatives)
    - [min-runtime](#min-runtime)
    - [background-time](#background-time)
    - [grant-/revoke-permissions](#grant-revoke-permissions)
    - [install](#install)
    - [uninstall](#uninstall)
    - [hide-apps](#hide-apps)
    - [wifi](#wifi)
    - [data](#data)
    - [bluetooth](#bluetooth)
    - [bluetooth-mac](#bluetooth-mac)
    - [nfc-available](#nfc-available)
    - [sensor-count](#sensor-count)
    - [geolocation](#geolocation)
    - [language](#language)
    - [acceleration / gyroscope](#acceleration--gyroscope)
    - [battery](#battery)
    - [interaction](#interaction)
    - [init-qemu-props](#init-qemu-props)
    - [qemu-fake-camera](#qemu-fake-camera)
    - [qemu-gles](#qemu-gles)
    - [qemu-lcd-density](#qemu-lcd-density)
    - [qemu-logcat](#qemu-logcat)
    - [qemu-timezone](#qemu-timezone)
    - [android-accessability-service](#android-accessability-service)
    - [uptime](#uptime)
    - [constants](#constants)
    - [remove-enabled-input-methods](#remove-enabled-input-methods)
    - [adb-enabled](#adb-enabled)
    - [ip-4](#ip-4)
    - [ip-6](#ip-6)
    - [time](#time)
    - [sleep](#sleep)
    - [sleep-update-date](#sleep-update-date)
    - [post-delayed](#post-delayed)
  - [Test Apps](#test-apps)
    - [accelH-app](#accelh-app)
    - [AccessService-app](#accessservice-app)
    - [adbEnable-app](#adbenable-app)
    - [adbPortDetector-app](#adbportdetector-app)
    - [atNight-app](#atnight-app)
    - [Background-app](#background-app)
    - [batteryCharging-app](#batterycharging-app)
    - [batteryFull-app](#batteryfull-app)
    - [batteryStatus-app](#batterystatus-app)
    - [constantCalls1-app](#constantcalls1-app)
    - [constantCalls2-app](#constantcalls2-app)
    - [constants1-app](#constants1-app)
    - [constants2-app](#constants2-app)
    - [constantsDLC-app](#constantsdlc-app)
    - [divById-app](#divbyid-app)
    - [Geolocation-app](#geolocation-app)
    - [getIpAddress-app](#getipaddress-app)
    - [HashComp-app](#hashcomp-app)
    - [installedApps-app](#installedapps-app)
    - [Language-app](#language-app)
    - [LogCredent-app](#logcredent-app)
    - [longAction-app](#longaction-app)
    - [Navigate-app](#navigate-app)
    - [Permission-app](#permission-app)
    - [postDelayed-app](#postdelayed-app)
    - [procNetTcp-app](#procnettcp-app)
    - [signatureVerification-app](#signatureverification-app)
    - [sleep-app](#sleep-app)
    - [uptime-app](#uptime-app)

Here you can get an overview about the features of TrigDroid an how to use them.

## Command implementation and possible alternatives

In this section, I give some information about how the testing options work in the background and what alternative methods are possible for the strategy used.

### min-runtime

After all other tests and before closing the app, the program will simply sleep for the given duration. This option should only be used if all other options like [`sleep`](#sleep) or [`postDelayed`](#post-delayed) aren't suitable. For example, it can be used to detect a payload that is triggered after 5000 primes have been calculated.

See [longAction](#longaction-app) for a usage example.

### background-time

Uses the buttons [HOME][button_home] and [APP_SWITCH][button_app_switch] to bring the focused app into the background and bringing it back after the program slept for the given duration.

See [Background](#background-app) for a usage example.

### grant-/revoke-permissions

Calls `adb pm (grant|revoke) <package> android.permission.<permission>`. See function `change_permission` of [testing.py](src/TrigDroid/testing.py) for details.

Have look at the introduction of the section [Test Apps](#test-apps) for a usage example.

### install

This repo contains a [dummy app](src/TrigDroid/dummy/dummy.apk), which is just a standard Android Studio app. If you use this option, this dummy app will be unpacked, some files will be edited, and this app will be repacked and signed. Finally, the app is installed on the device. The following tools are used for these steps:

- [align resource file script][alignResource]
- [apksigner][apksigner]
- [apktool][apktool]
- [keytool][keytool]
- [sed][sed]

For more details of the implementation see [dummy.py](/src/TrigDroid/test_runners/dummy.py).

Alternatively, the [`packageManager`][packageManager] could be hooked with frida. I didn't do that because I want to use a maximally realistic strategy. By installing a real app, I make sure that the app will be detected even if other ways of looking for installed apps are used or the API changes. Also, this approach doesn't require root privileges or a running frida server.

See [installedApps](#installedapps-app) for a usage example.

### uninstall

Calls `adb uninstall <package>`.

Alternatively, the package could be hidden by frida. This can be done by using [`--hide-apps`](#hide-apps). The advantage of `--uninstall` is, that it uses the maximally realistic strategy.  By actually uninstalling an app, we make sure that the app will be detected even if other ways of looking for installed apps are used or the API changes. Also, this approach doesn't require root privileges or a running frida server.

Be aware of the fact, that system apps can't be uninstalled. If you try to uninstall a system app, you'll get an error message in the logs. In this case you may use [--hide-apps](#hide-apps).

See [installedApps](#installedapps-app) for a usage example.

### hide-apps

Hooks [`android.os.Parcel.readString()`][parcel.readString] with frida and replaces every given packageName-String with the provided fake packageName.

Using this option is only recommended if [--uninstall](#uninstall) does not work.

See [installedApps](#installedapps-app) for a usage example.

### wifi

Uses `adb shell svc wifi`.

Alternatively you could use the [appium settings app][appium_settings]. I used the svc way because it's simpler and it's kind of a native and probably long-lasting way.

Usage example:

```bash
./TrigDroid -p com.example.package -w False
```

### data

Uses `adb shell svc data`.

Alternatively you could use the [appium settings app][appium_settings]. I used the svc way because it's simpler and it's kind of a native and probably long-lasting way.

Usage example:

```bash
./TrigDroid -p com.example.package -da True
```

### bluetooth

Uses `adb shell service call bluetooth_manager`.

In a [StackOverflow post][stack_overflow_post_bluetooth_patrik], [Patrik][stack_overflow_account_patrik] gives several options to en-/disable bluetooth. The used option is the only way, that worked for me on different android versions.

Note, that this option roots the android device.

Usage example:

```bash
./TrigDroid -p com.example.package -b True
```

### bluetooth-mac

Hooks some methods and the constructor [android.bluetooth.BluetoothAdapter][bluetoothAdapter] and [android.bluetooth.BluetoothManager.getAdapter][bluetoothManager.getAdapter].

If the adapter should be `null`, the program just hooks into [`getDefaultAdapter`][bluetoothAdapter.getDefaultAdapter] of [`BluetoothAdapter`][bluetoothAdapter] and [`getAdapter`][bluetoothManager.getAdapter] of [`BluetoothManager`][bluetoothManager] and returns `null`. If a mac address to simulate is specified, the program hooks the same get methods. Now in them the original get method gets called. If it returns a valid BluetoothAdapter, it just will be used and returned by the frida-implementation. Otherwise, meaning if the original get methods returns `null`, the [constructor of BluetoothAdapter][bluetoothAdapter.constructor] gets hooked and returns does nothing (a null object is created). Then the constructor of is called. Now it returns an empty real Java BluetoothAdapter. Additionally, still if a mac address is specified, the [`getAddress`][bluetoothAdapter.getAddress] of the [`BluetoothAdapter`] gets hooked to return the faked address. If a random mac address should be generated, the random library is used with the first byte of the sha3 hash of the [package name](../README.md#usage) has seed.

*Note 1*: In the past the constructor of the BluetoothAdapter took just one instead of two arguments. To avoid a function-not-found-error, the frida script first checks how many arguments the real constructor expects and then hooks the constructor according to the check.

*Note 2*: If the device / emulator doesn't support bluetooth, this option may create a [`BluetoothAdapter`][bluetoothAdapter] that is just a null Object (e.g. `android.bluetooth.BluetoothAdapter@9bfcc8e`, where `9bfcc8e` points to an address that point to `null`). This means, that this faked object doesn't have any methods or variables - even no static ones. But it's possible to simulate all of them with frida. The current implementation just provides [`getAddress`][bluetoothAdapter.getAddress] and [`finalize`][java.lang.object.finalize]. The last one to suppress an error log.

Usage examples

```bash
./TrigDroid -p com.example.package -bm null # hides any bluetooth adapter

./TrigDroid -p com.example.package -bm 01:23:45:56:89:ab # guarantees the existence of a (simulated) bluetooth adapter with the address "01:23:45:56:89:ab"

./TrigDroid -p com.example.package -bm random # like above but with the address "f5:8d:92:64:25:21" (seed 27)
```

### nfc-available

Hooks [android.nfc.NfcAdapter.getNfcAdapter(Context)][nfcAdapter.getNfcAdapter]. Every method that gets an NFC adapter calls this method. If an adapter should be hidden, the frida implementation throws an [`UnsupportedOperationException`][unsupportedOperationException], like the method would normally do if the device doesn't have an NFC Adapter. If an adapter should be simulated, the frida implementation calls the [NfcAdapter constructor][nfcAdapter.constructor] with the given context even if there isn't any physical NFC adapter.

Usage example:

```bash
./TrigDroid -p com.example.package -na True
```

### sensor-count

Hooks [`android.hardware.SensorManager.getSensorList`][sensorManager.getSensorList] to remove sensors or return existing sensors more than once to simulate a fake sensor count. The method `getSensorList` returns all sensors of a specified type (all types is also possible). The frida hook then gets the full sensor list, enumerates the sensors the faked full list should have and finally adopts the removals and duplications to the return value of `getSensorList`. With this approach I make sure, that even if the full list is build by manually requesting all sensor types the length is equivalent to getting all sensors at once.

Usage example:

```bash
./TrigDroid -p com.example.package -sc 5
```

### geolocation

Uses the [appium_settings app][appium_settings] to mock gps data. For implementation details see set_geolocation of [preparation.py](/src/TrigDroid/test_runners/testing/preparation.py). The implementation is inspired by the [appium settings doc to location mocking][appium_settings_mock_location] and a [StackExchange post][stack_exchange_post_gps_jmp] of [jmp][stack_exchange_account_jmp].

Alternatively, the corresponding parts of the [LocationManager][location_manager] could be hooked using frida. I decided to use appium setting instead, because it mocks out the geolocation in general and not only about specific JVM methods. Also, the appium is updated regularly, so it should be usable for newer API levels. Another alternative would be to change the behavior of TrigDroid so that it launches the emulator itself, while the geolocation could be set explicitly. I didn't use this approach because I don't want to start the emulator in this program to avoid long runtimes.

A limitation of this option is, that you can set speed and bearing of the device, but if an app regularly asks for gps data it may notice that the device actually doesn't move.

See [Geolocation](#geolocation-app) for a usage example.

### language

Uses the [appium settings app][appium_settings] to fake locale data. For implementation details see set_language of [preparation.py](/src/TrigDroid/test_runners/testing/preparation.py).

Alternatively, the corresponding parts of [Locale][locale] could be hooked using frida. I decided to use appium settings instead, because it mocks the locale in general and not just through specific JVM methods. Also, the appium app is updated regularly, so it should be usable for newer API levels.

This option roots the device to change the locale, it's not rooted while the test app is running.

See [Language](#language-app) for a usage example.

### acceleration / gyroscope

Uses the command `adb emu set sensor (acceleration|gyroscope) <x>:<y>:<z>`. Depending on how often the option is used, different times with different values for x, y and z will be executed. For more implementation details, have a look at the function `acceleration_or_gyroscope_rotation` of [active.py](/src//TrigDroid/test_runners/testing/active.py).

Alternatively, the [`sensorEvent`][sensorEvent] could be hooked with frida. I didn't do that because I want to use a maximally realistic strategy. By changing the actual sensor data, I make sure that the data will be detected even if other ways of looking for sensor data are used or the API changes. Also, this approach doesn't require root privileges or a running frida server.

This option covers a wide range of possible triggering data, but doesn't reflect a real user behavior.

See [accessservice](#accessservice-app) for a usage example.

### battery

Uses the command `adb emu power (ac|capacity|health|present|status) <…>`. Depending on how often the option is used, different times with different values will be executed. For more implementation details, have look at the function `battery_rotation` of [active.py](/src/TrigDroid/test_runners/testing/active.py).

Alternatively, the [`Intent`][intent] could be hooked with frida. I didn't do that because I want to use a maximally realistic strategy. By changing the actual battery data, I make sure that the data will be detected even if other ways of looking for battery data are used or the API changes. Also, this approach doesn't require root privileges or a running frida server.

This option covers a wide range of possible triggering data, but doesn't reflect a real device behavior.

See [batteryCharging](#batterycharging-app), [batteryFull](#batteryfull-app), or [batteryStatus](#batterystatus-app) for a usage example.

### interaction

This option starts taking a snapshot of the screen with `adb shell uiautomator dump`. On this snapshot TrigDroid looks for text inputs and buttons. Then each text input is filled with a random word. Now TrigDroid tries to press all buttons. After each press it checks if the screen has changed by comparing the hash of a snapshot of the current screen with the hashes of known screens. If it has changed, the process starts again. The algorithm stops when every button found has been pressed once.

> **Info `ℹ`** If your test app requires a login, it is recommended to login manually before starting TrigDroid, especially for this option.

Alternatively, a monkey test framework could be used. I didn't do that because it is much more inefficient, time consuming and not reproducible. An advantage of monkey testing would be a potentially wider coverage of events.

One obvious limitation is that this is very low-level interaction mocking: Pressing on non-button elements, scrolling down, text input that requires special input, or changing the state of radio buttons, checkboxes, and switches are not captured by this type of interaction mocking. Moreover, this option and way of testing can be very time consuming.

If you want to replace the interaction strategy with your own, e.g. a monkey tester, just replace the submodule `Interaction`. The submodule needs a file named [executer](src/TrigDroid/Interaction/executer.py) which contains a function `run()`. This function is called by TrigDroid to perform the interaction mocking. If your code raises an exception, this exception should inherit from the `InteractionException' which can be found in [interaction_exception.py](/src/TrigDroid/utils/exceptions/interaction_exception.py).

See [LogCredent](#logcredent-app) or [Navigation](#navigate-app) for a usage example.

### init-qemu-props

Uses `adb shell setprop` command to overwrite `inti.sv.qemu-props`. Before setting the value the `getprop`-command is used to get the old value and restore it after closing the app using `setprop` again.

The following command sets the property to the value "test":

```bash
./TrigDroid -p com.example.app -iqp test
```

To set it to an empty value, you can use this command:

```bash
./TrigDroid -p com.example.app -iqp ""
```

### qemu-fake-camera

Uses `adb shell setprop` command to overwrite `qemu.sf.fake_camera`. Before setting the value the `getprop`-command is used to get the old value and restore it after closing the app using `setprop` again.

The following command sets the property to the value "test":

```bash
./TrigDroid -p com.example.app -qfc test
```

To set it to an empty value, you can use this command:

```bash
./TrigDroid -p com.example.app -qfc ""
```

### qemu-gles

Uses `adb shell setprop` command to overwrite `qemu.gles`. Before setting the value the `getprop`-command is used to get the old value and restore it after closing the app using `setprop` again.

The following command sets the property to the value "test":

```bash
./TrigDroid -p com.example.app -qg test
```

To set it to an empty value, you can use this command:

```bash
./TrigDroid -p com.example.app -qg ""
```

### qemu-lcd-density

Uses `adb shell setprop` command to overwrite `qemu.sf.lcd_density`. Before setting the value the `getprop`-command is used to get the old value and restore it after closing the app using `setprop` again.

The following command sets the property to the value "test":

```bash
./TrigDroid -p com.example.app -qld test
```

To set it to an empty value, you can use this command:

```bash
./TrigDroid -p com.example.app -qld ""
```

### qemu-logcat

Uses `adb shell setprop` command to overwrite `qemu.logcat`. Before setting the value the `getprop`-command is used to get the old value and restore it after closing the app using `setprop` again.

The following command sets the property to the value "test":

```bash
./TrigDroid -p com.example.app -ql test
```

To set it to an empty value, you can use this command:

```bash
./TrigDroid -p com.example.app -ql ""
```

### qemu-timezone

Uses `adb shell setprop` command to overwrite `qemu.timezone`. Before setting the value the `getprop`-command is used to get the old value and restore it after closing the app using `setprop` again.

The following command sets the property to the value "test":

```bash
./TrigDroid -p com.example.app -qt test
```

To set it to an empty value, you can use this command:

```bash
./TrigDroid -p com.example.app -qt ""
```

### android-accessability-service

En-/Disables the settings *enabled_accessibility* and *enabled_accessibility_services* of namespace secure. For implementation details see `set_aas()` in [preparation.py](/src/TrigDroid/test_runners/testing/preparation.py).

See [AccessService](#accessservice-app) for a usage example.

### uptime

Hooks the methods [`uptimeMillis`][systemClock.uptimeMillis] of [`SystemClock`][systemClock]. First the hook gets the real value by calling the original method, then it adds/subtracts the given duration and returns it.

Alternatively, the device could be run until the specified uptime is reached. This way it would not be possible to subtract some time. I didn't use this strategy because it would take too much time. To avoid this, it would be possible to store several snapshots of emulators with different uptimes. This would have the advantage of being as realistic as possible, but I didn't do that because I don't want to include emulator creation and launching in the program to admit long runtimes.

This option only hooks methods of the Java Runtime. An app could bypass it by accessing `/proc/uptime` directly or using the command line program `uptime`.

See [uptime](#uptime-app) for a usage example.

### constants

Hooks several fields of different classes like [`Build`][build] or [`TelephonyManager`][telephony_manager].

Alternatively, a manipulated image could be created and used for an emulator. This would have the advantage of being as realistic as possible, but I didn't do that because I don't want to include emulator creation and launching in the program to admit long runtimes. An example would be manipulating the image like this ([example for IMEI manipulation][imei_manipulation_image]). It could be created and used for an emulator. This would have the advantage of being as realistic as possible, but I didn't do that because I don't want to include emulator creation and launching in the program to admit long runtimes. Additionally, there may be other ways to manipulate values ([manipulate IMEI using an external app][imei_manipulation_app], [outdated manipulate IMEI using adb][imei_manipulation_adb]), but we would need a different way for each value, and they wouldn't be very persistent across Android versions. To avoid problems with frequently changing behaviors, we use the all-in-one solution with frida, even if other ways would be more realistic.

See [constantCalls1](#constantcalls1-app), [constantCalls2](#constantcalls1-app), [divById](#divbyid-app), [constants1](#constants1-app) or [constantsDLC](#constantsdlc-app) and [constants2](#constants2-app) for usage examples.

### remove-enabled-input-methods

Hooks the methods `getEnabledInputMethodList()` and `getEnabledInputMethodList(int)` of the [`InputMethodManager`][input_method_manager].

The following usage removes all input methods with an id, that starts with a capital letter followed by minimum one non-capital letter, from the result:

```bash
./TrigDroid -p com.example.app -reim ^[A-Z][a-z]+
```

### adb-enabled

Hooks into the [`getStringForUser`][settings.nameValueCache.getStringForUser] method of the [`NameValueCache`][settings.nameValueCache] subclass of [`Settings`][Settings]. This method is called to get any setting property with a corresponding string constant. If the name of the string to get is *adb_enabled*, it returns the given value, otherwise it returns the original value.

This is the stack of the adb_enabled query:

- [`Settings.Secure.getInt`][settings.secure.getInt]
- [`Settings.Secure.getIntForUser`][settings.secure.getIntForUser]
- [`Settings.Secure.getStringForUser`][settings.secure.getStringForUser]
- [`Settings.Global.getStringForUser`][settings.global.getStringForUser]
- [`Settings.NameValueCache.getStringForUser`][settings.nameValueCache.getStringForUser]

See [adbEnabled](#adbenable-app) for a usage example.

### ip-4

Hooks the method [`getAddress`][java.net.InetAddress.InetAddressHolder.getAddress] of [`InetAddressHolder`][java.net.InetAddress.InetAddressHolder] - a subclass of [`InetAddress`][java.net.InetAddress]. The implementation calls the original method, checks if it's in a given range and returns a faked address if necessary.

Usage examples:

```bash
./TrigDroid -p com.example.app -i4 1.2.3.4+4.3.2.1 # replaces the ip address 1.2.3.4, e.g. from the gateway or a DNS server with 4.3.2.1

./TrigDroid -p com.example.app -i4 1.1.1.1+2.2.2.1 1.1.1.2+2.2.2.2 # replaces the ip address 1.1.1.1 with 2.2.2.2 and the ip address 1.1.1.2 with 2.2.2.2

./TrigDroid -p com.example.app -i4 1.1.1.1-2+2.2.2.x # does the same as the example above
```

Also used by the [getIpAddress-app](#getipaddress-app).

### ip-6

Hooks the [`getAddress`][java.net.Inet6Address.getAddress] of [`Inet6Address`][java.net.Inet6Address]. The implementation calls the original method, checks if it's in a given range and returns a faked address if necessary.

The usage is similar to the [--ip-4 option](#ip-4). Nevertheless, here is an usage example:

```bash
./TrigDroid -p de.hbrs.inf.shuesc2s.knowntechniques -i6 "fe(10-ff)::15:b2ff:fe00:(0-f)(0-aa)+0x::xx" # interesting for the "LinkProperties"-Technique
```

### time

Hooks the [constructor with a long parameter][java.util.date.init_long] of [`Date`][java.util.date]. If the given timestamp is plus/minus one second off the current time, a `Date` instance initialized with a timestamp changed according to the given value will be returned. Otherwise, a `Date` instance with the original timestamp is returned. For implementation details have a look at _FridaConfig._get_time in [frida_utils.py](src/TrigDroid/frida_utils.py) and with corresponding part in [hooks.js](/src/TrigDroid/frida/hooks.js).

Large parts of `Date` are deprecated and [`Calendar`][java.util.calendar] should be used instead, but internally `Calendar` also uses `Date`. Therefore, hooking into `Date` guarantees interception in both senses.

Limitation: This option captures every timestamp gotten through the Java API, but there are other ways of getting the current time for example a command line call or a website.

See [atNight](#atnight-app) for a usage example.

### sleep

Hooks the method [`sleep` with a long and an int parameter][java.lang.thread.init_long_int] of [`Thread`][java.lang.thread]. If the given duration is higher than this option allows, the new implementation calls `sleep` for 100 ms, otherwise it calls `sleep` with the original parameters.

There are two other overloads of the method `sleep`, but internally they both use the above named version, so it's enough to only hook into this one.

Alternatively, it would be possible to wait until the sleep time is over, but I want to avoid unnecessarily long runtimes for this program.

See also [sleep-update-data](#sleep-update-date).

See [sleep](#sleep-app) for a usage example.

### sleep-update-date

Behaves similar to [time](#time) if [sleep](#sleep) is used.

Limitations:

- Works only with [sleep](#sleep), not with post-delayed
- Updates [datetime](#time) only, not [uptime](#uptime)

Usage:

```bash
./TrigDroid -p com.example.app -s 10000 -t 01.01.2000T22:22 -sud
```

### post-delayed

Hooks the method [`postDelayed` with a Runnable and a long parameter][handler.postDelayed_runnable_long] of [`Handler`][handler]. If the given delay is higher than this option allows, the new implementation calls `postDelayed` with the same runnable for a delay of 100 ms, otherwise it calls `postDelayed` with the original parameters.

There is another overload of the method `postDelayed`, but internally is use the above named version, so it's enough to only hook into this one.

Alternatively, it would be possible to wait until the delay is over, but I want to avoid unnecessarily long runtimes for this program.

See [postDelayed](#postdelayed-app) for a usage example.

## Test Apps

The development of the framework was based on the [evadroid suit][evadroid] and some [additional apps][jflier2s_apps], developed by [jflier2s][jflier2s]. You can find all the used apps also in the folder [APKs](/APKs/). Here are some execution instructions for triggering and not triggering the payloads of the apps. The Apps are tested with TrigDroid for the Android API levels 24 to 33.

Since the payload can only be triggered if the SEND_SMS permission is granted, it should always be granted with `-gp SEND_SMS`. To shorten the following statements, this option isn't explicitly set.

Since nothing else is given, the command `./TrigDroid -p com.ibm.appName` leads to harmless behavior.

If you've cloned the repository and you're using [VS-Code][vscode], you can run all the given examples by using the debug configuration in the [launch.json](.vscode/launch.json). You can also run all apps with the [run_all_debug_configs script](run_all_debug_configs.py).

To run the commands the apps need to be installed. You can install all the apps at once with

```bash
chmod +x installation/installAPKs
./installation/installAPKs
```

. If you're attached to more than one device (`adb devices`), you can give the ID of the device you want to install the apps on as parameter:

```bash
chmod +x installation/installAPKs
./installation/installAPKs emulator-5554
```

Due to some outdated stuff I reproduced some of the apps so that they actually work. You can find the source codes in [CustomApps](./CustomApps/). If you want to build an use them, you need to sign them. [Here][sign_app] you can find a guide to sign apps. To create a simple keystore, you can use my [script](/installation/createCustomAppsKey):

```bash
chmod +x installation/createCustomAppsKey
./installation/createCustomAppsKey
```

All passwords you need, are `password` and the alias ist `customApps`.

### accelH-app

Emulators with the API levels 24 to 26 (both included) emulate constant small movements. Therefore, the payload always gets triggered on this versions.

```bash
./TrigDroid -p com.ibm.accelH -a
```

### AccessService-app

Harmless behavior:

```bash
./TrigDroid -p com.example.AccessService -aas False
```

Payload trigger:

```bash
./TrigDroid -p com.example.AccessService -aas True
```

### adbEnable-app

```bash
./TrigDroid -p com.ibm.adbEnable -ae false
```

### adbPortDetector-app

This app doesn't behave as it should because in current Android versions the `/proc/net/tcp` file does not contain the adb ports. The payload is always triggered.

### atNight-app

Harmless behavior:

```bash
./TrigDroid -p com.ibm.atNight -t T12
```

Payload trigger:

```bash
./TrigDroid -p com.ibm.atNight -t T02
```

### Background-app

Running the program with this app without triggering the payload at all is not possible, because TrigDroid always closes the app at the end, which triggers the payload.

```bash
./TrigDroid -p com.example.Background -bt 1
```

### batteryCharging-app

TrigDroid does not provide an option to not trigger the payload of this app, because charging is the default status on the most emulators and all battery options are designed to hit most possibly different statuses.

```bash
./TrigDroid -p com.ibm.batteryCharging -b
```

### batteryFull-app

TrigDroid does not provide an option to not trigger the payload of this app, because 100% is the default status on the most emulators and all battery options are designed to hit most possibly different statuses.

```bash
./TrigDroid -p com.ibm.batteryFull -b
```

### batteryStatus-app

```bash
./TrigDroid -p com.ibm.batteryStatus -b
```

### constantCalls1-app

Due to changes in the Android API and its permission handling, this application normally only runs for API level 22 or lower. Unfortunately, these versions are too old for current versions of frida. However, by hooking into the methods used by constantCalls1, which are the reason for the problems on higher API levels, the permission checks are not performed and the tests can be executed. Of course, this is more of a workaround as it doesn't reflect real world behavior.

Harmless behavior:

```bash
./TrigDroid -p com.ibm.constantCalls1 -tm .vscode/launch-configs/constantCalls1_Harmless.yml
```

Payload trigger:

```bash
./TrigDroid -p com.ibm.constantCalls1 -tm .vscode/launch-configs/constantCalls1_Trigger.yml
```

Now, I can provide an alternative app , that also works on newer devices:

This app needs API level 26 or higher.

Harmless behavior:

```bash
./TrigDroid -p de.fraunhofer.fkie.constantcalls1 -tm .vscode/launch-configs/constantCalls1_Harmless.yml
```

Payload trigger:

```bash
./TrigDroid -p de.fraunhofer.fkie.constantcalls1 -tm .vscode/launch-configs/constantCalls1_Trigger.yml
```

### constantCalls2-app

Due to changes in the Android API and its permission handling, this application normally only runs for API level 22 or lower. Unfortunately, these versions are too old for current versions of frida. However, by hooking into the methods used by constantCalls2, which are the reason for the problems on higher API levels, the permission checks are not performed and the tests can be executed. Of course, this is more of a workaround as it doesn't reflect real world behavior.

Harmless behavior:

```bash
./TrigDroid -p com.ibm.constantCalls2 -tm .vscode/launch-configs/constantCalls2_Harmless.yml
```

Payload trigger:

```bash
./TrigDroid -p com.ibm.constantCalls2 -tm .vscode/launch-configs/constantCalls2_Trigger.yml
```

Now, I can provide an alternative app, that also works on newer devices. Be aware, that you have to manually make the app to the default SMS handler.

This app needs API level 26 or higher.

Harmless behavior:

```bash
./TrigDroid -p de.fraunhofer.fkie.constantcalls2 -tm .vscode/launch-configs/constantCalls2_Harmless.yml
```

Payload trigger:

```bash
./TrigDroid -p de.fraunhofer.fkie.constantcalls2 -tm .vscode/launch-configs/constantCalls2_Trigger.yml
```

### constants1-app

Harmless behavior:

```bash
./TrigDroid -p com.ibm.constants1 -bc .vscode/launch-configs/constants1_Harmless.yml
```

Payload trigger:

```bash
./TrigDroid -p com.ibm.constants1 -bc .vscode/launch-configs/constants1_Trigger.yml
```

### constants2-app

In the source code of this app, the if-statement for testing if the device is an emulator contains a bug. Therefore, the payload is only triggered if the app is really sure that it is running on an emulator.

Harmless behavior (normally this should trigger the payload):

```bash
./TrigDroid -p com.ibm.constants2 -bc .vscode/launch-configs/constants2_Harmless.yml
```

Payload trigger (normally this should granite a harmless behavior):

```bash
./TrigDroid -p com.ibm.constants2 -bc .vscode/launch-configs/constants2_Trigger.yml
```

### constantsDLC-app

```bash
./TrigDroid -p com.ibm.constantsCLC -bc .vscode/launch-configs/constantsDLC_Trigger.yml
```

### divById-app

Due to changes in the Android API and its permission handling, this application normally only runs for API level 22 or lower. Unfortunately, these versions are too old for current versions of frida. However, by hooking into the methods used by divById, which are the reason for the problems on higher API levels, the permission checks are not performed and the tests can be executed. Of course, this is more of a workaround as it doesn't reflect real world behavior.

Harmless behavior:

```bash
./TrigDroid -p com.ibm.divById -tm .vscode/launch-configs/divById_Harmless.yml
```

Payload trigger:

```bash
./TrigDroid -p com.ibm.divById -tm .vscode/launch-configs/divById_Trigger.yml
```

Now, I can provide an alternative app, that also works on newer devices:

This app needs API level 26 or higher.

Harmless behavior:

```bash
./TrigDroid -p de.fraunhofer.fkie.divbyid -tm .vscode/launch-configs/divById_Harmless.yml
```

Payload trigger:

```bash
./TrigDroid -p de.fraunhofer.fkie.divbyid -tm .vscode/launch-configs/divById_Trigger.yml
```

### Geolocation-app

Harmless behavior:

```bash
./TrigDroid -p com.example.Geolocation -gp SEND_SMS ACCESS_FINE_LOCATION -g 0:0
```

Payload trigger:

```bash
./TrigDroid -p com.example.Geolocation -gp SEND_SMS ACCESS_FINE_LOCATION -g 40:-3
```

### getIpAddress-app

Harmless behavior:

```bash
./TrigDroid -p com.ibm.getByIpAddress -i4 0-255.0-255.0-255.0-255+0.0.0.0
```

Payload trigger:

```bash
./TrigDroid -p com.ibm.getByIpAddress -i4 0-255.0-255.0-255.0-255+1.2.3.4
```

### HashComp-app

TrigDroid never changes the behavior of this app, because it never unpacks APKs. Normally the payload should always be triggered. If you want to see the harmless behavior, un- and repack the APK, before you install it.

### installedApps-app

Harmless behavior:

```bash
./TrigDroid -p com.ibm.installedApps -i com.android.development
```

Payload trigger:

```bash
./TrigDroid -p com.ibm.installedApps -u com.android.development
```

This does not work for Android Versions with an API level less than 28, because here com.android.development is a system app. See [uninstall explanations](#uninstall) for more details. On those API levels you can use the following command:

```bash
./TrigDroid -p com.ibm.installedApps -ha com.android.development%com.android.tnempoleved
```

### Language-app

Harmless behavior:

```bash
./TrigDroid -p com.example.Language -l en-US
```

Payload trigger:

```bash
./TrigDroid -p com.example.Language -l es-US
```

### LogCredent-app

```bash
./TrigDroid -p com.example.LogCredent -in
```

### longAction-app

This app reads all files from `/vendor/lib` and copies them to `/dev/null`. Especially on newer devices this wouldn't be a longAction because this folder doesn't exist on those devices (only `/vendor/lib64` exists). Therefore, the payload may always be triggered.

```bash
./TrigDroid -p com.ibm.longAction -mr 15
```

There is no way to cover all long-running action triggers other than waiting. Fast machines can help in this case. On my development notebook, this app took only 7 minutes. Alternatively, `File` could be hooked, but this would only apply to this app, rather than long actions in general. Also, more advanced strategies like detecting and removing long running loops would not apply to many long actions.

### Navigate-app

```bash
./TrigDroid -p com.example.Navigate -in
```

### Permission-app

The app doesn't trigger its payload the first time it launches after granting all permissions. To trigger the payload, we put the app in the background for a short time.

For any reason the payload gets only triggered on phones with API Version 28 or higher.

```bash
./TrigDroid -p com.example.Permissions -gp SEND_SMS CAMERA READ_CONTACTS READ_EXTERNAL_STORAGE ACCESS_FINE_LOCATION RECORD_AUDIO READ_PHONE_STATE -bt 1
```

### postDelayed-app

```bash
./TrigDroid -p com.ibm.postDelayed -pd 60000
```

### procNetTcp-app

This app doesn't behave as it should because in current Android versions the `/proc/net/tcp` file does not contain the adb ports. The payload is always triggered.

### signatureVerification-app

This app doesn't behave the way it should. Even if the app wasn't unpacked and installed directly, the payload is not triggered. The app [HashComp](#hashcomp-app) is an alternative with the same functionality.

### sleep-app

```bash
./TrigDroid -p com.ibm.sleep -s 60000
```

### uptime-app

```bash
./TrigDroid -p com.ibm.uptime -up 240
```

<!-- external links -->

[alignResource]: https://stackoverflow.com/a/70647059 "Stackoverflow answer containing a script to align the resource file of an apk"
[apksigner]: https://developer.android.com/studio/command-line/
[apktool]: https://ibotpeaches.github.io/Apktool/ "apktool website"
[appium_settings_mock_location]: https://github.com/appium/io.appium.settings#setting-mock-locations "README section 'Setting Mock Locations' of GitHub page of appium settings app"
[appium_settings]: https://github.com/appium/io.appium.settings "GitHub page of appium settings app"
[bluetoothAdapter]: https://developer.android.com/reference/android/bluetooth/BluetoothAdapter "Android developers page of BluetoothAdapter"
[bluetoothAdapter.constructor]: https://cs.android.com/android/platform/superproject/main/+/main:packages/modules/Bluetooth/framework/java/android/bluetooth/BluetoothAdapter.java;l=1084;drc=cd273c5ab784874a76d40a49c6f2827dce70d737 "Android source code of the constructor of android.bluetooth.BluetoothAdapter"
[bluetoothAdapter.getAddress]: https://developer.android.com/reference/android/bluetooth/BluetoothAdapter#getAddress() "Android developers page of Bluetooth.getAddress()"
[bluetoothAdapter.getDefaultAdapter]: https://developer.android.com/reference/android/bluetooth/BluetoothAdapter#getDefaultAdapter() "Android developers page of BluetoothAdapter.getDefaultAdapter()"
[bluetoothManager]: https://developer.android.com/reference/android/bluetooth/BluetoothManager "Android developers page of BluetoothManager"
[bluetoothManager.getAdapter]: https://developer.android.com/reference/android/bluetooth/BluetoothManager#getAdapter() "Android developers page of BluetoothManager.getAdapter()"
[build]: https://developer.android.com/reference/android/os/Build "Android developers page of Build"
[button_app_switch]: https://developer.android.com/reference/android/view/KeyEvent#KEYCODE_APP_SWITCH "Section KEYCODE_APP_SWITCH of Android developers page of KeyEvent"
[button_home]: https://developer.android.com/reference/android/view/KeyEvent#KEYCODE_0 "Section KEYCODE_HOME of Android developers page of KeyEvent"
[evadroid]: https://ibmmobile.bitbucket.io/ "Evadroid Project"
[handler.postDelayed_runnable_long]: https://developer.android.com/reference/android/os/Handler#postDelayed(java.lang.Runnable,%20java.lang.Object,%20long) "Android Developers page of Handler.postDelayed(Runnable,long)"
[handler]: https://developer.android.com/reference/android/os/Handler "Android developers page of Handler"
[input_method_manager]: https://developer.android.com/reference/android/view/inputmethod/InputMethodManager "Android developers page of InputMethodManager"
[intent]: https://developer.android.com/reference/android/content/Intent "Android developers page of Intent"
[imei_manipulation_adb]: https://stackoverflow.com/questions/71790363/how-to-obtain-imei-via-adb: "StackOverflow post of how to obtain imei via adb"
[imei_manipulation_app]: https://github.com/viki3d/change-imei-android "Github: change-imei-android app"
[imei_manipulation_image]: http://blog.codepainters.com/2010/11/20/android-emulator-patch-for-configurable-imei-imsi-and-sim-card-serial-number/ "Blog post of how to change the imei by manipulating the emulator image"
[java.lang.object.finalize]: https://docs.oracle.com/javase/8/docs/api/java/lang/Object.html#finalize-- "Oracle docs of Object.finalize()"
[java.lang.thread.init_long_int]: https://docs.oracle.com/en/java/javase/19/docs/api/java.base/java/lang/Thread.html#sleep(long,int) "Oracle docs of Thread.sleep(long,int)"
[java.lang.thread]: https://docs.oracle.com/en/java/javase/19/docs/api/java.base/java/lang/Thread.html "Oracle docs of Thread"
[java.net.Inet6Address]: https://developer.android.com/reference/java/net/Inet6Address "Android developers page of the class Inet6Address"
[java.net.Inet6Address.getAddress]: https://developer.android.com/reference/java/net/Inet6Address#getAddress() "Android developers page of ths method Inet6Address.getAddress"
[java.net.InetAddress]: https://developer.android.com/reference/java/net/InetAddress "Android developers page of InetAddress"
[java.net.InetAddress.InetAddressHolder]: https://cs.android.com/android/platform/superproject/main/+/main:libcore/ojluni/src/main/java/java/net/InetAddress.java;l=201;bpv=0;bpt=1 "Android source code of the static class InetAddressHolder, that is part of java.net.InetAddress"
[java.net.InetAddress.InetAddressHolder.getAddress]: https://cs.android.com/android/platform/superproject/main/+/main:libcore/ojluni/src/main/java/java/net/InetAddress.java;l=250;bpv=0;bpt=1 "Android source code of the method getAddress of the class InetAddressHolder, that is part of java.net.InetAddress"
[java.util.calendar]: https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/Calendar.html "Oracle docs of Calendar"
[java.util.date]: https://docs.oracle.com/javase/8/docs/api/java/util/Date.html "Oracle docs of Date"
[java.util.date.init_long]: https://docs.oracle.com/javase/8/docs/api/java/util/Date.html#Date-long- "Oracle docs of Date(long)"
[jflier2s]: https://github.com/jflier2s "Github profile of jflier2s"
[jflier2s_apps]: https://github.com/jflier2s/TriggerEvaluator/tree/main/trigger "Repository links to the apps jflier2s used in his/her project"
[keytool]: https://docs.oracle.com/en/java/javase/18/docs/specs/man/keytool.html "Oracle docs for keytool"
[locale]: https://developer.android.com/reference/java/util/Locale "Android developers page of Locale"
[location_manager]: https://developer.android.com/reference/android/location/LocationManager "Android developers page of LocationManager"
[nfcAdapter.constructor]: https://cs.android.com/android/platform/superproject/main/+/main:frameworks/base/core/java/android/nfc/NfcAdapter.java;drc=cd273c5ab784874a76d40a49c6f2827dce70d737;l=758 "Android source code of the constructor of android.nfc.NfcAdapter"
[nfcAdapter.getNfcAdapter]: https://cs.android.com/android/platform/superproject/main/+/main:frameworks/base/core/java/android/nfc/NfcAdapter.java;drc=0b80090e02814093f2187c2ce7e64f87cb917edc;l=623 "Android source code of android.nfc.NfcAdapter.getNfcAdapter(Context)"
[packageManager]: https://developer.android.com/reference/android/content/pm/PackageManager "Android developers page of PackageManager"
[parcel.readString]: https://developer.android.com/reference/android/os/Parcel#readString() "Android developers page of Parcel.readString"
[sed]: https://wiki.ubuntuusers.de/sed/ "Ubuntu wiki entry of sed"
[sensorEvent]: https://developer.android.com/reference/android/hardware/SensorEvent "Android developers page of SensorEvent"
[sensorManager.getSensorList]: https://developer.android.com/reference/android/hardware/SensorManager#getSensorList(int) "Android developers page of SensorManager.getSensorList"
[settings.global.getStringForUser]: https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/provider/Settings.java;l=16027;drc=a512015bb5d4665141d3dcf6a02d0f577cbba4e8?hl=de "Android source code of Settings.Global.getStringForUser"
[settings.nameValueCache.getStringForUser]: https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/provider/Settings.java;l=3057;drc=5ca657189aac546af0aafaba11bbc9c5d889eab3;bpv=0;bpt=1?hl=de "Android source code of Settings.NameValueCache.getStringForUser"
[settings.nameValueCache]: https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/provider/Settings.java;l=2940;drc=5ca657189aac546af0aafaba11bbc9c5d889eab3;bpv=0;bpt=1?hl=de "Android source code of Settings.NameValueCache"
[settings.secure.getInt]: https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/provider/Settings.java;l=6380;drc=5ca657189aac546af0aafaba11bbc9c5d889eab3;bpv=0;bpt=1?hl=de "Android source code of Settings.Secure.getInt"
[settings.secure.getIntForUser]: https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/provider/Settings.java;drc=a512015bb5d4665141d3dcf6a02d0f577cbba4e8;bpv=0;bpt=1;l=6386?hl=de "Android source code of Settings.Secure.getIntForUser"
[settings.secure.getStringForUser]: https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/provider/Settings.java;drc=a512015bb5d4665141d3dcf6a02d0f577cbba4e8;bpv=0;bpt=1;l=6152?hl=de "Android source code of Settings.Secure.getStringForUser"
[settings]: https://developer.android.com/reference/android/provider/Settings "Android developers page of Settings"
[sign_app]: https://developer.android.com/studio/publish/app-signing "Android developers page tutorial for 'Sign your app'"
[stack_exchange_account_jmp]: https://android.stackexchange.com/users/281659/jmp "StackExchange account from jmp"
[stack_exchange_post_gps_jmp]: https://android.stackexchange.com/a/205034 "A post of jmp on StackExchange on the topic 'Is it possible to set device's Latitude and Longitude using ADB SHELL?'"
[stack_overflow_account_patrik]: https://stackoverflow.com/users/9887151/patrik "StackOverflow account from Patrik"
[stack_overflow_post_bluetooth_patrik]: https://stackoverflow.com/a/55064471 "A post of Patrik on StackOverflow on the topic 'android enable disable bluetooth via command line'"
[systemClock.uptimeMillis]: https://developer.android.com/reference/android/os/SystemClock#uptimeMillis() "Android developers page of SystemClock.uptimeMillis"
[systemClock]: https://developer.android.com/reference/android/os/SystemClock "Android developers page of SystemClock"
[telephony_manager]: https://developer.android.com/reference/android/telephony/TelephonyManager "Android Developers page of TelephonyManager"
[unsupportedOperationException]: https://docs.oracle.com/javase/8/docs/api/java/lang/UnsupportedOperationException.html "Oracle documentation of the UnsupportedOperationException"
[vscode]: https://code.visualstudio.com/ "Visual Studio Code Homepage"
