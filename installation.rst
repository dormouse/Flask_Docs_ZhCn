安装
============


Python 版本
--------------

我们推荐使用最新版本的 Python 。 Flask 支持 Python 3.7 以上版本。

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

* `Blinker`_ 为 :doc:`signals` 提供支持。
* `python-dotenv`_ 当运行 ``flask`` 命令时为 :ref:`dotenv` 提供支持。
* `Watchdog`_ 为开发服务器提供快速高效的重载。

.. _Blinker: https://pythonhosted.org/blinker/
.. _python-dotenv: https://github.com/theskumar/python-dotenv#readme
.. _watchdog: https://pythonhosted.org/watchdog/

greenlet
~~~~~~~~

您可以选择使用 gevent 或者 eventlet 来服务您的应用。在这种情况下，
greenlet>=1.0 是必须的。当使用 PyPy 时，  PyPy>=7.3.7 是必须的。

上述版本是指支持的最小版本，应当尽量使用最新的版本。


虚拟环境
--------------------

建议在开发环境和生产环境下都使用虚拟环境来管理项目的依赖。

为什么要使用虚拟环境？随着你的 Python 项目越来越多，你会发现不同的项目
会需要不同的版本的 Python 库。同一个 Python 库的不同版本可能不兼容。

虚拟环境可以为每一个项目安装独立的 Python 库，这样就可以隔离不同项目之
间的 Python 库，也可以隔离项目与操作系统之间的 Python 库。

Python 内置了用于创建虚拟环境的 :mod:`venv` 模块。


.. _install-create-env:

创建一个虚拟环境
~~~~~~~~~~~~~~~~~~~~~

创建一个项目文件夹，然后创建一个虚拟环境。创建完成后项目文件夹中会有一个
:file:`venv` 文件夹：

.. tabs::

   .. group-tab:: macOS/Linux

      .. code-block:: text

         $ mkdir myproject
         $ cd myproject
         $ python3 -m venv venv

   .. group-tab:: Windows

      .. code-block:: text

         > mkdir myproject
         > cd myproject
         > py -3 -m venv venv


.. _install-activate-env:

激活虚拟环境
~~~~~~~~~~~~~~~~~~~~~~~~

在开始工作前，先要激活相应的虚拟环境：

.. tabs::

   .. group-tab:: macOS/Linux

      .. code-block:: text

         $ . venv/bin/activate

   .. group-tab:: Windows

      .. code-block:: text

         > venv\Scripts\activate

激活后，你的终端提示符会显示虚拟环境的名称。


安装 Flask
-------------

在已激活的虚拟环境中可以使用如下命令安装 Flask：

.. code-block:: sh

    $ pip install Flask

Flask 现在已经安装完毕。请阅读 :doc:`/quickstart` 或者
:doc:`文档目录 </index>` 。
