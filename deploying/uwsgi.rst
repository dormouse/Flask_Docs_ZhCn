uWSGI
=====

`uWSGI`_ 是一个快速、编译的服务器套件，相较于基本的服务器具有更广泛的
配置和功能。

*   由于是编译过的程序，它具有很好的性能。
*   相较于基本的应用，它的配置很复杂，有很多的选项。因此，对于新手来
    来说，上手是有难度的。
*   它不支持 Windows （但可以在 WSL 上运行）。
*   在某些情况下，它需要一个编译器来安装。

本文概述了运行 uWSGI 的基础知识。请务必阅读它的文档，以解其详。

.. _uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/


安装
----------

uWSGI 有多种安装方式。最直接的方法是安装 ``pyuwsgi`` 包，它为常见的平
台提供了预编译的 wheel 。然而，它不提供SSL支持，这可以通过反向代理来
实现。

创建一个虚拟环境，安装你的应用，然后安装 ``pyuwsgi`` 。

.. code-block:: text

    $ cd hello-app
    $ python -m venv .venv
    $ . .venv/bin/activate
    $ pip install .  # install your application
    $ pip install pyuwsgi

如果你有一个可用的编译器，你可以安装``uwsgi``包来代替。或者从 sdist
安装 ``pyuwsgi`` 包，而不是 wheel 。无论哪种方法都会包括 SSL 支持。

.. code-block:: text

    $ pip install uwsgi

    # or
    $ pip install --no-binary pyuwsgi pyuwsgi


运行
-------

运行 uWSGI 的最基本方法是告诉它启动一个 HTTP 服务器，并导入你的应用。

.. code-block:: text

    $ uwsgi --http 127.0.0.1:8000 --master -p 4 -w hello:app

    *** Starting uWSGI 2.0.20 (64bit) on [x] ***
    *** Operational MODE: preforking ***
    mounting hello:app on /
    spawned uWSGI master process (pid: x)
    spawned uWSGI worker 1 (pid: x, cores: 1)
    spawned uWSGI worker 2 (pid: x, cores: 1)
    spawned uWSGI worker 3 (pid: x, cores: 1)
    spawned uWSGI worker 4 (pid: x, cores: 1)
    spawned uWSGI http 1 (pid: x)

如果你使用应用工厂模式，那么需要创建一个小的 Python 文件来创建应用，
然后将 uWSGI 指向它。

.. code-block:: python
    :caption: ``wsgi.py``

    from hello import create_app

    app = create_app()

.. code-block:: text

    $ uwsgi --http 127.0.0.1:8000 --master -p 4 -w wsgi:app

通过 ``--http`` 选项在 127.0.0.1 的 8000 端口启动一个 HTTP 服务器。
选项中的 ``--master`` 选项指定了标准的工作管理员。 ``-p`` 选项选项启
动4个工作进程；起始值可以是 ``CPU * 2`` 。 ``-w`` 选项告诉 uWSGI 如何
导入你的应用。

外部绑定
------------------

uWSGI 不应该像本文的配置一样以 root 身份运行，因为它将导致你的应用以
root 身份运行，这是不安全的。 然而，这样意味着它将无法绑定到端口 80
或 443。解决之道是在 uWSGI 前使用一个反向代理，如 :doc:`nginx` 或
:doc:`apache-httpd` 。 uWSGI 可以以root身份安全地运行，但这已经超出了
本文的范围。

uWSGI 没有使用一个标准的 HTTP 代理，而是经针对 `Nginx uWSGI`_ 和
`Apache mod_proxy_uwsgi`_ 进行了优化，也可以针对其他服务器进行了优化。
这样的配置已经超出本文的范围，更多信息详见：

.. _Nginx uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html
.. _Apache mod_proxy_uwsgi: https://uwsgi-docs.readthedocs.io/en/latest/Apache.html#mod-proxy-uwsgi

使用 ``--http 0.0.0.0:8000`` 选项，可以在一个非特权端口上绑定所有外部
IP 。但是当使用反向代理时，不要这样做，否则就有可能绕过代理。

.. code-block:: text

    $ uwsgi --http 0.0.0.0:8000 --master -p 4 -w wsgi:app

``0.0.0.0`` 不是一个有效的导航地址，你应该在浏览器中使用一个特定的 IP
地址。


用 gevent 进行异步操作
----------------------------------------------------------

默认的同步工作者适合于许多使用情况。如果你需要异步支持， uWSGI 提供了
使用 `gevent_` 的工作者。这与 Python 的 ``async/await`` 不同，也不同
于 ASGI 服务器规范。你必须在自己的代码中实际使用 gevent/eventlet 才能
看到使用工作者的好处。

当使用 gevent 时， greenlet>=1.0 是必须的，否则，诸如 ``request`` 之
类的情境本地变量将不能如期工作。当使用 PyPy 时，需要 PyPy>=7.3.7 。

.. code-block:: text

    $ uwsgi --http 127.0.0.1:8000 --master --gevent 100 -w wsgi:app

    *** Starting uWSGI 2.0.20 (64bit) on [x] ***
    *** Operational MODE: async ***
    mounting hello:app on /
    spawned uWSGI master process (pid: x)
    spawned uWSGI worker 1 (pid: x, cores: 100)
    spawned uWSGI http 1 (pid: x)
    *** running gevent loop engine [addr:x] ***


.. _gevent: https://www.gevent.org/
