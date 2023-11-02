# 100DoC Clicker

![Tests][B1]
[![License: Unlicense][B2]](http://unlicense.org/)

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

Make sure that you are logged into your Replit account, started the course
using the button on [the introduction page][1] and have Python 3.10
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


  [B1]: https://github.com/InSyncWithFoo/100doc-clicker/actions/workflows/tox.yaml/badge.svg
  [B2]: https://img.shields.io/badge/license-Unlicense-blue.svg

  [1]: https://replit.com/learn/100-days-of-code
