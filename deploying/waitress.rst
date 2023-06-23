Waitress
========

`Waitress`_ 是一个纯 Python 的 WSGI 服务器。


*   它很容易配置。
*   它直接支持 Windows 。
*   它很容易安装，因为它不需要额外的依赖或编译。
*   它不支持流式请求，完整的请求数据总是被缓冲。 
*   它使用一个具有多个线程工作者的单一进程。

本文概述了运行 Waitress 的基础知识。请务必阅读它的文档，并使用
``waitress-serve --help`` 详细了解有哪些功能。

.. _Waitress: https://docs.pylonsproject.org/projects/waitress/


安装
----------

创建一个虚拟环境，安装你的应用，然后安装 ``waitress`` 。

.. code-block:: text

    $ cd hello-app
    $ python -m venv .venv
    $ . .venv/bin/activate
    $ pip install .  # install your application
    $ pip install waitress


运行
-------

``waitress-serve`` 唯一需要的参数是告诉它如何加载你的 Flask 应用。语
法是 ``{module}:{app}`` 。 ``module`` 是带点的应用模块导入名。
``app`` 是应用程序的变量。如果你使用应用工厂模式，那么使用
``--call {module}:{factory}`` 来代替。

.. code-block:: text

    # equivalent to 'from hello import app'
    $ waitress-serve --host 127.0.0.1 hello:app

    # equivalent to 'from hello import create_app; create_app()'
    $ waitress-serve --host 127.0.0.1 --call hello:create_app

    Serving on http://127.0.0.1:8080

``--host`` 选项仅将服务器绑定到本地 ``127.0.0.1`` 。

不显示每个请求的日志，只显示错误信息。日志记录可以可以通过 Python 接
口而不是命令行来配置。


外部绑定
------------------

Waitress  不应该以 root 身份运行，因为这将导致你的应用以 root 身份运
行，这样是不安全的。然而，不以 root 身份运行意味着不可能绑定到 80 或
443端口。解决之道是在 Waitress 前面使用一个反向代理，如 :doc:`nginx`
或者 :doc:`apache-httpd` 。

不使用 ``--host`` 选项，可以在一个非特权端口上绑定所有外部 IP 。但
是当使用反向代理时，不要这样做，否则就有可能绕过代理。

``0.0.0.0`` 不是一个有效的导航地址，你应该在浏览器中使用一个特定的 IP
地址。
