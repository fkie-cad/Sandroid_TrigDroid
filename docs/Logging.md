# Logging

TL;DR: Use `-h` option and see logging-section for shorter explanations.

- [Logging](#logging)
  - [General logging](#general-logging)
  - [Changelog](#changelog)

TrigDroid implements extensive logging. Here you can get an idea how to use it best for your needs.

## General logging

At first: TrigDroid avoids showing you a raw exception, it always catches it and displays an appropriate log message. This might be a bit annoying if you're a developer and want to debug the program (hint: use a debugger), but it helps people who are just using TrigDroid to easily understand what happens and how to fix it without digging deeper into the source code.

Now to logging and its configuration options. TrigDroid offers two output channels for the logs: First, the logs can be written to stdout. Here the logs are printed pretty with coloring and special formatting. This output is enabled by default, but can be disabled with the `suppress-console-logs` config option. Second, the logs can be written to a file. If you want to have your logs in a file, you should use this option instead of redirecting stdout to a file, because that way all the meta characters for coloring won't be included. By default the logs aren't written to a file, to enable it you have to specify the path to a log file with the `log-file` option. You can use either one, both or none of the output channels.

With the option `extended-log-format`, all logs include more specific information about the place the log is created at. This can be useful while debugging.

For the two channels introduced above, you can specify a log level. The `log-level` option sets the level for both channels. If you want to have different levels, you also need the `log-level-file` option. It overwrites the log level on the file channel, and the level specified with `log-level` is only applied to the stdout channel. The higher the level, the fewer logs you get, and it should be self-explanatory what kind of logs you get from which log level. The order of the log levels is: `DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`

If the log levels are not advanced enough, you can use log filters. These filters allow you to explicitly include, exclude, or set log levels in specific modules, functions, and even rows. But as you might expect, these filter configurations are a bit more complex. So let us start with the channels once again: You can start a log filter with `F` for the file channel, `S` for the stdout channel, or `B` for both channels. If you don't specify one of these characters, the filter will apply to both channels. Next, you can specify a module, if you specified a channel explicitly, you need to separate it with a `#`. Here you just have to specify a filename. For example, to filter the file testing.py, write 'testing'. The module is the only required part of a filter. It is followed by a `:` and a stronger specification. This specification can be either the name of a function in this file or a reference to specific lines. You can filter just one line by specifying the line number, or filter a range of lines by specifying them as `<first_line>-<last_line>`. Finally, you can add a `#` followed by one of the log levels mentioned in the previous paragraph. Then the filter will only apply to logs with that or a higher log level. Now you can pass a space-separated list of these filters to the `log-filter-incl` and `log-filter-excl` options. The first option explicitly shows the filtered logs, the second explicitly hides them. If the include option is used, regardless of the exclude option, all logs not explicitly included will be hidden. If you use both options together, the more specific filter will be used. Here, line specifications are always considered more specific than function specifications, and exclude filters are preferred over include filters. One last note: Please keep in mind that the log level options are sometimes stronger than the filters: If the log level is set to INFO, there's no way to show DEBUG logs - a filter using DEBUG would have no effect on this example.

Imagine two modules:

**module1.py**:

```python
def func1:                # 1
  logging.debug('a')      # 2
  logging.error('b')      # 3
                          # 4
def func2:                # 5
  logging.info('c')       # 6
  logging.warning('d')    # 7
```

**module2.py**:

```python
def func1:                # 1
  logging.debug('e')      # 2
  logging.warning('f')    # 3
                          # 4
def func2:                # 5
  logging.info('g')       # 6
  logging.critical('h')   # 7
```

… with …

**main.py**:

```python
import module1
import module2

module1.func1()
module1.func2()
module2.func1()
module2.func2()
```

Now we would have several options to log only the logs from the first module, here are a few:

```bash
$ python main.py --log-level DEBUG --log-filter-incl module1
abcd

$ python main.py --log-level DEBUG --log-filter-excl module2
abcd

$ python main.py --log-level DEBUG --log-filter-incl module1:func1 module1:6-7
abcd

$ python main.py --log-level DEBUG --log-filter-excl module1 --log-filter-incl module1:2-7
abcd

```

Here are some tricks for you:

```bash
$ python main.py --log-level WARNING --log-filter-incl "module2:func1#DEBUG"
d

$ python main.py --log-level INFO --log-filter-incl F#module1
$ cat file.log
cat: file.log: No such file or directory
$ python main.py --log-level INFO --log-filter-incl F#module1 --log-file file.log
$ cat file.log
abcd

$ python main.py --log-level INFO --log-filter-excl "module2:6-7#ERROR"
h

```

## Changelog

The changelog is easier to use and is intended to be used for post-processing and analyzing the results of this program - if you need a human-friendly changelog, it's recommended to use [general logging](#general-logging) with `log-level=DEBUG`. If you don't do anything, it's just there: On every start of the program the content of [changelog.json](/changelog.json) will be deleted or if the file doesn't exist it will be created. Then every change TrigDroid makes is logged in this file. If you take a look at a changelog file, you will find an array containing several entry objects. Each object contains several attributes. The keys of the attributes should be self-explanatory, but note that not all attributes are mandatory.

Now you can do some configuration on the changelog. First, you can change the filename and path of the output file using the `changelog-file` option. If you need the logs to be printed pretty for some reason - maybe you want to read them manually for debugging purposes - you can get it by using the `pretty-changelog` option. Next, you may notice that the changelog slows down some test steps extremely - these are steps that generate lots of changelog entries. Besides the problem that you have to wait for a long time, this can lead to different test results, because the frequency of successive changes on the Android device gets lower. To avoid this, you have two options: First, you can reduce the time it takes to generate changelog entries to a minimum by enabling some caching with the option `changelog-cache`. Normally this option shouldn't have any effect on the generated changelog entries, but if you use this option and notice some inconsistencies or deviations from your expectation, check if the attribute key of the anomaly is part of the caching list in the documentation of the `Changelog`-class in [changelog.py](/src/TrigDroid/logger/changelog.py). If it turns out that this was indeed the problem, please open an issue. The second option is to disable changelog creation altogether by using the option `disable-changelog`. If you use this option, all other named options will be ignored and no changelog file will be created or purged.
