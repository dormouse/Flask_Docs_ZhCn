Gunicorn
========

`Gunicorn`_ 是一个纯 Python WSGI 服务器，配置简单，多工作者实现，方便
性能调优。

*   它倾向于与主机平台轻松集成。
*   它不支持 Windows （但可以在 WSL 上运行）。
*   它很容易安装，因为不需要额外的依赖或编译。
*   它有内置的异步工作者，支持使用 gevent 或 eventlet。

本文概述运行 Gunicorn 基础。详细内容请参阅其 `文档`_ 并使用
``gunicorn --help`` 帮助理解。

.. _Gunicorn: https://gunicorn.org/
.. _文档: https://docs.gunicorn.org/


安装
----------

Gunicorn 很容易安装，因为不需要额外的依赖或编译。在 Windows 系统中，
它只能运行在 WSL 中。

创建一个虚拟环境，安装你的应用，然后安装 ``gunicorn`` 。

.. code-block:: text

    $ cd hello-app
    $ python -m venv venv
    $ . venv/bin/activate
    $ pip install .  # install your application
    $ pip install gunicorn


运行
-------

Gunicorn 唯一需要的参数是告诉它如何加载你的 Flask 应用。语法是
``{module_import}:{app_variable}`` 。 ``module_import`` 是带点的应用
模块导入名。 ``app_variable`` 是应用的变量。如果你使用的是工厂模式，
那么也可以是一个函数调用（可带任何参数）。

.. code-block:: text

    # equivalent to 'from hello import app'
    $ gunicorn -w 4 'hello:app'

    # equivalent to 'from hello import create_app; create_app()'
    $ gunicorn -w 4 'hello:create_app()'

    Starting gunicorn 20.1.0
    Listening at: http://127.0.0.1:8000 (x)
    Using worker: sync
    Booting worker with pid: x
    Booting worker with pid: x
    Booting worker with pid: x
    Booting worker with pid: x

``-w`` 选项指定要运行的进程数，一个起始值可以是 ``CPU * 2`` 。默认情
况下，只有一个工作者，这可能不是你想要。

默认情况下不显示每个请求的日志，只显示工作者信息和错误信息。要在
stdout 上显示访问日志，请使用 ``--access-logfile=-`` 选项。


外部绑定
------------------

Gunicorn 不应该以 root 身份运行，因为这将导致你的应用以 root 身份运行，
这是不安全的。然而，不以 root 身份运行意味着不可能绑定到 80 或 443 端
口。解决之道是在 Gunicorn 前面使用一个反向代理，如 :doc:`nginx` 或者
:doc:`apache-httpd` 。

使用 ``-b 0.0.0.0`` 选项，可以在一个非特权端口上绑定所有外部 IP 。但
是当使用反向代理时，不要这样做，否则就有可能绕过代理。

.. code-block:: text

    $ gunicorn -w 4 -b 0.0.0.0 'hello:create_app()'
    Listening at: http://0.0.0.0:8000 (x)

``0.0.0.0`` 不是一个有效的导航地址，你应该在浏览器中使用一个特定的 IP
地址。


用 gevent 或 eventlet 进行异步操作
----------------------------------------------------------

默认的同步工作者适合于许多使用情况。如果你需要异步支持， Gunicorn 提
供了使用 `gevent_` 或 `eventlet_` 的工作者。这与 Python 的
``async/await`` 不同，也不同于 ASGI 服务器规范。你必须在自己的代码中
实际使用 gevent/eventlet 才能看到使用工作者的好处。

当使用 gevent 或 eventlet 时， greenlet>=1.0 是必须的，否则，诸如
``request`` 之类的情境本地变量将不能如期工作。当使用 PyPy 时，需要
PyPy>=7.3.7 。

使用 gevent：

.. code-block:: text

    $ gunicorn -k gevent 'hello:create_app()'
    Starting gunicorn 20.1.0
    Listening at: http://127.0.0.1:8000 (x)
    Using worker: gevent
    Booting worker with pid: x

使用 eventlet：

.. code-block:: text

    $ gunicorn -k eventlet 'hello:create_app()'
    Starting gunicorn 20.1.0
    Listening at: http://127.0.0.1:8000 (x)
    Using worker: eventlet
    Booting worker with pid: x

.. _gevent: https://www.gevent.org/
.. _eventlet: https://eventlet.net/
