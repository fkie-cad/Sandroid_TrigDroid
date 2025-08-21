# Development

> **Disclaimer `📝`** Currently there's a problem with running frida in an VS Code internal terminal. The development still works, but you've to run the program from an external terminal if you need an option that uses frida.

- [Development](#development)
  - [Create / Read the documentation](#create--read-the-documentation)
  - [How to extend the program](#how-to-extend-the-program)
    - [1. Add the option itself](#1-add-the-option-itself)
    - [2a. Executing frida-based options](#2a-executing-frida-based-options)
    - [2b. Executing non-frida-based options](#2b-executing-non-frida-based-options)
    - [3. Logging and readability](#3-logging-and-readability)
      - [Logging-Module](#logging-module)
      - [Changelog-Module](#changelog-module)
    - [4. Documentation](#4-documentation)

I recommend [vs code][vscode] as development environment. Here you can use my configurations for several add-ons. I also recommend installing the following add-ons:

- [Better Comments][better_comments]
- [Code Spell Checker][code_spell_checker]
- [Python Extension Pack][python_extension_pack]
- [Even Better TOML][even_better_toml] (not as important as the others)

Before installing `requirements.txt`, you could [create a virtual environment][vscode_create_venv].

## Create / Read the documentation

The source code is well documented, but it doesn't exist an documentation website. If you want to have an documentation website anyway, you can run it yourself with nearly no effort:

```bash
cd src/TrigDroid
pdoc --http : interaction logger test_runners utils
```

Of course, you can run any other pdoc command to, for example to generate a PDF documentation file.

## How to extend the program

If you want to extend the program you probably want to add some methods to change the app environment. In other words, add options. Here is a simple guide of what you need to do. So you do not need to understand the whole source code to add options without missing up some important steps, reinventing the wheel or breaking the structure of the program.

### 1. Add the option itself

To add an option to the global config and make it available to users, go to [config.py](src/TrigDroid/config.py). At the top of the `Config` class you'll find a quick guide on what you need to add an option. The constructor of `_OPTION` has many parameters. See which ones you might need. Also take a look at other existing options to see how you can configure your new option wisely. Last but not least, you should be aware of the key of your option in dict. It will determine the key in the config file and the command line arguments - if possible, it should never be changed.

### 2a. Executing frida-based options

If you want to hook some Java runtime functionality with frida, there's an easy way to include it in this program.

Once you've written the hooking script, you can paste it into [hooks.js](/src/TrigDroid/frida/hooks.js). Then add the instructions on when to use which part and what values to set. At the top of the file you will find a guide on how to add these instructions.

After inserting the hooking script, you need to provide a frida configuration to tell the program under which conditions your script should be used and with which values the variables should be replaced. Go to the class `_FridaConfig` of [frida_config.py](/src/TrigDroid/test_runners/frida_utils/frida_config.py) and add a method with the exact name `_get_<option_name>`. The *option_name* is the string you used as key in the options dict (see [above](#1-add-the-option-itself)). The method takes the appropriate input from the command line or config file as a parameter and is only executed if the option is not equal to its default value. In the method, you can calculate whatever you need. Then return a dict with the calculated instructions for using your hook. For details see the documentation of the class `_FridaConfig` in [frida_config.py](/src/TrigDroid/test_runners/frida_utils/frida_config.py).

If you're frida hook just replaces one variable, you can also use the already existing config option `--constants` and skip the mapping with `_get_<option_name>`. You just need to add your variable to the `templates` in `register_default_templates` in the [constants init file](../src/TrigDroid/utils/config/constants/__init__.py). For information about how to do this are provided at the top of the file.

<!-- markdownlint-disable MD052 -->
Since you cannot use logging and changelog directly, you must use the `send` method. For normal logs, you can simply pass the log message as a parameter. If you want to add a changelog, write your message in this format `#changelog <property>[ 0<old_value>][ 1<new_value>][ description]`. To add a changelog, you can also use the changelog snippet.
<!-- markdownlint-enable MD052 -->

If you're not sure about what to do, have a look at the already existing options using frida and its implementations.

### 2b. Executing non-frida-based options

Non-frida based options should be executed from the [main file](src/TrigDroid/__main__.py), but the actual executing code should be placed in [testing.py](src/TrigDroid/testing.py).To do this, write a function with the testing code in the appropriate part of the [testing files](/src/TrigDroid/test_runners/testing/). Then call it from one of the functions `_setup` or `_on_app_active` in [src/TrigDroid/\_\_main\_\_.py](src/TrigDroid/__main__.py) at an appropriate place. If you call your function in `_setup`, it will be executed before the app is launched. If you call it in `_on_app_active`, it will run after the app is launched. If you need to perform some teardown action, the `_tear_down` function in the same file is the place you're looking for.

You'll probably need some additional information for your functionality, which may already be provided by the program environment. To access the configuration from the command line or the config file, just create a new config instance (`Config().<option_name>`) and if you want to access the information you gave when adding your configuration, you can get it through the `OPTIONS` dictionary (`Config.OPTIONS['<option_name>']`). The *option_name* is the string you used as key in the options dict (see [above](#1-add-the-option-itself)).

You may also need some helper utils. The [`ADB`](/src/TrigDroid/utils/android_debug_bridge.py) class provides many convenient methods for the adb command line. In [helpers.py](/src/TrigDroid/utils/helpers.py) you can find some other useful tools. If one of these files does not contain what you need, it might be a good idea to add it there instead of typing it directly into your testing function. It may also be nice to report if a command line execution failed. In such a case you can use the function `handle_sh_res` form [output_helpers.py](/src/TrigDroid/logger/logging_utils/output_helpers.py) to avoid repeating yourself.

If you're not sure about what to do, have a look at the already existing options and its implementations.

### 3. Logging and readability

After each small step you take, you should ask yourself some questions and perhaps make some refactoring changes. Even these refactoring changes are steps that should be followed by a validation if further refactoring steps are advisable. Also look at other parts of the program and how they look. These are the questions for you:

- Does my implementation **work**?
- Did I follow the [**KISS**][kiss] principle?
- Did I use a single function per functionally?
- Are there any reports from **python, pylint, codeSpell** etc.?
- Is the code **readable** (no infinite mapping-in-mappings, speaking names for variables and methods, here and there blank lines between "code sections", ...)?
- Have I used **explanatory comments** over every part of the code that is not self-explanatory in two seconds?
- **Very important**: Did I use **logging** in a way that (a) logs everything the code does and changes on the emulator, and (b) reports every error that happens to the user in understandable language?
- Also **important**: Have I reported **every** change I made at the Android device to the **changelog**?
- All in all, if I looked at this code a year from now, would I understand it right away?

Last but not least, some general information about logging:

#### Logging-Module

In general, it's easy to use the logging module. For everything the program "does", you call `logging.<method>(<text>)` once. For `text` you can write any message that explains in clear language what happened. For `method` you can choose between `debug`, `info`, `warning`, `error` and `critical`. You should use `critical` for information about something that will cause the program to crash, `error` when something definitely can't be done as intended and `warning` when something doesn't work correctly but all in all the program still does what it should. The other two methods are used for information only. The `info` method is used when a whole programmatic functionality or a bundle of coherent actions is the subject of the information, while `debug` gets every single step of a functionality or action. However, you shouldn't log thousands of steps or every execution statement, for example a loop that is executed 100 times doesn't need 100 logs, you can just make one log that says "Did xyz 100 times".

#### Changelog-Module

The changelog module is a bit more complex. It should be used for every change you make to the Android device. And *every* means really every change - if you change a sensor mock 100 times, you should log it 100 times. It's recommended to initialize a `Changelog` once at a proper place, like a constructor, with the appropriate file entry point. Then you can use it anywhere in the file. If you need to add a single entry, you can use the `add_and_write`-method, if your process needs to add multiple entries, use `add()` to create a single entry and then write them all together with `write()` - this can save a huge amount of time. Note that the `Changelog`-instance may cache some values between `write`-calls. You can find a list of cached attributes in the [`Changelog`] documentation (/src/TrigDroid/changelog.py). If you change something relating to the list, you should also update the list.

When you add a changelog entry, you must first specify a `property`. This is the value you want to change, e.g. "theRealSenor" or "special_constant". This value can be chosen freely, but it should be consistent throughout the program. Then you can give the `old_value` and the `new_value`. It's not always possible or useful to give both values, but if you can, you should. Next you can add a `description`. The `description` is a free text field and, unlike the first three parameters, is not intended to be machine-readable, but for human beings as additional information. The `description` is optional, but should be given if it can provide supplementary information to the first three parameters. All the mentioned parameters should match a regular expression, you can find it in [changelog.py](/src/TrigDroid/changelog.py). The last two parameters are some kind of meta information. With `overwrite_entrypoint` you can change the entrypoint given in the constructor. This overwrite only applies to this entry, all other entries will still use the initialization entrypoint. Each changelog entry contains information about the origin of the item. By default it uses the location where the `add` method is called from. You can change this, for example if you are writing a utility function for easier access, by specifying a `proxy_count`. By default, this value is set to `1`, which means that the last but one entry of the trace stack is used. This means that in the utility method example you should use `proxy_count=2`:

```python
[
  'changelog.add',        # 0
  'your.utility',         # 1
  'call_of_your_utility'  # 2
]
```

Note that you should never use `0` for `proxy_count`, as this would relegate it to a line in the `add` method of the `changelog` class.

### 4. Documentation

It would be advisable to write detailed documentation for each method and function - this is also useful for [readability](#3-logging-and-readability).

When you are done writing your code, you should document it in this [README](/README.md) file:

- If you need an external program, document it in the [Installation section](/README.md#installation).
- If you are adding an option, document it in the [Command implementation and possible alternatives](/docs/Background.md#command-implementation-and-possible-alternatives) section. As the name implies, you should also list possible alternatives to your way of implementing this functionality, and explain why you chose your solution. A usage example would also be nice.
- If there's an app you've tested your payload triggerer against, document it in [Test Apps](/docs/Background.md#test-apps).
- If you add something that might be important for other developers to set up their environments, document it in this file.
- If you've found a potential source of user confusion, document it in [Troubleshooting](/README.md#troubleshooting).

If you've installed or updated some libraries, please update the [requirements.txt](/installation/requirements.txt) with `pip freeze > installation/requirements.txt`.

Moreover, if you've installed a new library that is not only for development reasons used, add it to the dependencies of [pyproject.toml](../pyproject.toml).

<!-- external links -->

[better_comments]: https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments "Better Comments Homepage"
[code_spell_checker]: https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker "Code Spell Checker Homepage"
[even_better_toml]: https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml "Event Better TOML Homepage"
[kiss]: https://en.wikipedia.org/wiki/KISS_principle "Keep it simple stupid (Wikipedia)"
[python_extension_pack]: https://marketplace.visualstudio.com/items?itemName=donjayamanne.python-extension-pack "Python Extension Pack Homepage"
[vscode]: https://code.visualstudio.com/ "Visual Studio Code Homepage"
[vscode_create_venv]: https://code.visualstudio.com/docs/python/environments#_creating-environments "VS Code Tutorial for creating a virtual environment"
