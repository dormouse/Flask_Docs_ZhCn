.. _installation:

安装
============

Python 版本
--------------

我们推荐使用最新版本的 Python 3 。 Flask 支持 Python 3.5 及更高版本的
Python 3 、 Python 2.7 和 PyPy 。

依赖
------------

当安装 Flask 时，以下配套软件会被自动安装。

* `Werkzeug`_ 用于实现 WSGI ，应用和服务之间的标准 Python 接口。
* `Jinja`_ 用于渲染页面的模板语言。
* `MarkupSafe`_ 与 Jinja 共用，在渲染页面时用于避免不可信的输入，防止注入攻击。
* `ItsDangerous`_ 保证数据完整性的安全标志数据，用于保护 Flask 的 session cookie.
* `Click`_ 是一个命令行应用的框架。用于提供 ``flask`` 命令，并允许添加自定义
  管理命令。

.. _Werkzeug: https://palletsprojects.com/p/werkzeug/
.. _Jinja: https://palletsprojects.com/p/jinja/
.. _MarkupSafe: https://palletsprojects.com/p/markupsafe/
.. _ItsDangerous: https://palletsprojects.com/p/itsdangerous/
.. _Click: https://palletsprojects.com/p/click/

可选依赖
~~~~~~~~~~~~~~~~~~~~~

以下配套软件不会被自动安装。如果安装了，那么 Flask 会检测到这些软件。

* `Blinker`_ 为 :ref:`signals` 提供支持。
* `SimpleJSON`_ 是一个快速的 JSON 实现，兼容 Python's ``json`` 模块。如果安装
  了这个软件，那么会优先使用这个软件来进行 JSON 操作。
* `python-dotenv`_ 当运行 ``flask`` 命令时为 :ref:`dotenv` 提供支持。
* `Watchdog`_ 为开发服务器提供快速高效的重载。

.. _Blinker: https://pythonhosted.org/blinker/
.. _SimpleJSON: https://simplejson.readthedocs.io/
.. _python-dotenv: https://github.com/theskumar/python-dotenv#readme
.. _watchdog: https://pythonhosted.org/watchdog/

虚拟环境
--------------------

建议在开发环境和生产环境下都使用虚拟环境来管理项目的依赖。

为什么要使用虚拟环境？随着你的 Python 项目越来越多，你会发现不同的项目会需要
不同的版本的 Python 库。同一个 Python 库的不同版本可能不兼容。

虚拟环境可以为每一个项目安装独立的 Python 库，这样就可以隔离不同项目之间的
Python 库，也可以隔离项目与操作系统之间的 Python 库。

Python 3 内置了用于创建虚拟环境的 :mod:`venv` 模块。如果你使用的是较新的
Python 版本，那么请接着阅读本文下面的内容。

如果你使用 Python 2 ，请首先参阅 :ref:`install-install-virtualenv` 。

.. _install-create-env:

创建一个虚拟环境
~~~~~~~~~~~~~~~~~~~~~

创建一个项目文件夹，然后创建一个虚拟环境。创建完成后项目文件夹中会有一个
:file:`venv` 文件夹：

.. code-block:: sh

    $ mkdir myproject
    $ cd myproject
    $ python3 -m venv venv

在 Windows 下：

.. code-block:: bat

    $ py -3 -m venv venv

在老版本的 Python 中要使用下面的命令创建虚拟环境：

.. code-block:: sh

    $ python2 -m virtualenv venv

在 Windows 下：

.. code-block:: bat

    > \Python27\Scripts\virtualenv.exe venv

.. _install-activate-env:

激活虚拟环境
~~~~~~~~~~~~~~~~~~~~~~~~

在开始工作前，先要激活相应的虚拟环境：

.. code-block:: sh

    $ . venv/bin/activate

在 Windows 下：

.. code-block:: bat

    > venv\Scripts\activate

激活后，你的终端提示符会显示虚拟环境的名称。

安装 Flask
-------------

在已激活的虚拟环境中可以使用如下命令安装 Flask：

.. code-block:: sh

    $ pip install Flask

Flask 现在已经安装完毕。请阅读 :doc:`/quickstart` 或者
:doc:`文档目录 </index>` 。

与时俱进
~~~~~~~~

如果想要在正式发行之前使用最新的 Flask 开发版本，可以使用如下命令从主分支
安装或者更新代码：

.. code-block:: sh

    $ pip install -U https://github.com/pallets/flask/archive/master.tar.gz

.. _install-install-virtualenv:

安装 virtualenv
------------------

如果你使用的是 Python 2 ，那么 venv 模块无法使用。相应的，必须安装
`virtualenv`_.

在 Linux 下， virtualenv 通过操作系统的包管理器安装：

.. code-block:: sh

    # Debian, Ubuntu
    $ sudo apt-get install python-virtualenv

    # CentOS, Fedora
    $ sudo yum install python-virtualenv

    # Arch
    $ sudo pacman -S python-virtualenv

如果是 Mac OS X 或者 Windows ，下载 `get-pip.py`_ ，然后：

.. code-block:: sh

    $ sudo python2 Downloads/get-pip.py
    $ sudo python2 -m pip install virtualenv

在 Windows 下，需要要 administrator 权限：

.. code-block:: bat

    > \Python27\python.exe Downloads\get-pip.py
    > \Python27\python.exe -m pip install virtualenv

现在可以返回上面， :ref:`install-create-env` 。

.. _virtualenv: https://virtualenv.pypa.io/
.. _get-pip.py: https://bootstrap.pypa.io/get-pip.py
