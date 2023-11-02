# 100DoC Clicker

***100DoC Clicker*** provides a script that will click its way through
all 100 lessons in [Replit's 100 Days of Code][1] Python course should you
so choose. Currently, it only supports Chrome and Firefox.

This package is not intended to be imported. Regardless, it is fully
typed and documented. Import it at your own risk.


## Installation and usage

This package is not published on PyPI.
To install, run the following command in your shell:

```shell
$ pip install git+https://github.com/InSyncWithFoo/100doc-clicker
```

Make sure that you are logged into your Replit account and have Python 3.10
or later installed. The main script can then be run with either:

```shell
$ start-100doc-clicker chrome [-d USER_DATA_DIRECTORY] [-p PROFILE_DIRECTORY]
```

```shell
$ start-100doc-clicker firefox [-p PROFILE_DIRECTORY]
```

For more information, use the `-h` flag:

```shell
$ start-100doc-clicker -h
$ start-100doc-clicker chrome -h
$ start-100doc-clicker firefox -h
```


  [1]: https://replit.com/learn/100-days-of-code
