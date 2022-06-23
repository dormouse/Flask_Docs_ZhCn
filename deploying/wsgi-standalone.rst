独立 WSGI 服务器
==========================

大多数 WSGI 服务器也提供 HTTP 服务器，因此 WSGI 服务器可以独立运行
WSGI 应用并对外服务。当然在专门的 HTTP 服务器（例如 Apache 或者
Nginx ）后面运行 WSGI 服务器仍然不失为一个好主意。如果遇到问题，请阅读
:ref:`deploying-proxy-setups` 一节。

Gunicorn
--------

`Gunicorn`_ 是一个 UNIX 下的 WSGI 和 HTTP 服务器。
告诉 Gunicorn 如何导入你的 Flask 应用对象就可以运行 Flask 应用。

.. code-block:: text

    $ gunicorn -w 4 -b 0.0.0.0:5000 your_project:app

参数 ``-w 4`` 表示一次最多可以使用 4 个 worker 来处理 4 个请求。
``-b 0.0.0.0:5000`` 表示在所有接口的 5000 端口上提供服务。

Gunicorn 提供了非常的配置，可以使用配置文件，也可以使用命令行参数。
请使用 ``gunicorn --help`` 或者阅读其文档来获得更多信息。

``gunicorn`` 命令需要写明应用或者包的名称，其中必须包含应用实例。
如果你使用工厂模式，那么可以传递一个调用来实现。

.. code-block:: text

    $ gunicorn -w 4 -b 0.0.0.0:5000 "myproject:create_app()"


使用 Gevent 或者 Eventlet 同步
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

缺省的同步工作器在多数情况下已经够用了。如果你需要异步支持，那么
Gunicorn 提供使用 `gevent`_ 或者 `eventlet`_ 的工作器。这与 Python 的
``async/await`` 是不同的，与 ASGI 服务器规范也不同。

当使用 gevent 或者 eventlet 时， greenlet>=1.0 是必须的。否则情境局部
变量，例如 ``request`` ，将会无法工作。
当使用 PyPy 时， PyPy>=7.3.7 是必须的。

使用 gevent ：

.. code-block:: text

    $ gunicorn -k gevent -b 0.0.0.0:5000 your_project:app

使用 eventlet ：

.. code-block:: text

    $ gunicorn -k eventlet -b 0.0.0.0:5000 your_project:app

.. _gevent: http://www.gevent.org/
.. _eventlet: https://eventlet.net/
.. _greenlet: https://greenlet.readthedocs.io/en/latest/
 

uWSGI
--------


`uWSGI`_ 一个用 C 写的快速应用服务器。它配置丰富，从而配置复杂度也大于
gunicorn 。它也为撰写强大的网络应用提供了许多其他工具。
告诉 uWSGI 如何导入你的 Flask 应用对象就可以运行 Flask 应用。

.. code-block:: text

    $ uwsgi --master -p 4 --http 0.0.0.0:5000 -w your_project:app

参数 ``-p 4`` 表示一次最多可以使用 4 个 worker 来处理 4 个请求。
``-http 0.0.0.0:5000`` 表示在所有接口的 5000 端口上提供服务。

uWSGI 优化了与 Nginx 和 Apache 的集成，而不是使用一个标准的 HTTP 代理。
参见 :doc:`配置 uWSGI 和 Nginx <uwsgi>` 。

使用 Gevent 同步
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

缺省的同步工作器在多数情况下已经够用了。如果你需要异步支持，那么
uWSGI 提供使用 `gevent`_ 的工作器。这与 Python 的 ``async/await``
是不同的，与 ASGI 服务器规范也不同。

当使用 gevent 时， greenlet>=1.0 是必须的。否则情境局部变量，例如
``request`` ，将会无法工作。当使用 PyPy 时， PyPy>=7.3.7 是必须的。

.. code-block:: text

    $ uwsgi --master --gevent 100 --http 0.0.0.0:5000 -w your_project:app

.. _uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/


Gevent
-------

相较于直接使用 Gevent ，更推荐 `Gunicorn`_ 搭配 Gevent 一起使用。如前
文所述， Gunicorn 可以提供更丰富的配置，并且经过了生产测试。

`Gevent`_ 允许编写异步的、基于协程的代码，看起来像标准的同步 Python。
它使用 `greenlet`_ 来启用任务切换，而不用写 ``async/await`` 或使用
``asyncio`` 。

它提供了一个可以同时处理多个连接的 WSGI 服务器，而不是每个工作器处理一个。

`Eventlet`_ ，如下所述，是另一个做同样事情的库。您可以根据自身在情况选择
使用。

导入 ``WSGIServer`` 并用它来运行您的 ``app`` ，就可以使用 gevent 。

.. code-block:: python
 
    from gevent.pywsgi import WSGIServer
    from your_project import app
 
    http_server = WSGIServer(("", 5000), app)
    http_server.serve_forever()
 

Eventlet
--------

相较于直接使用 Eventlet ，更推荐 `Gunicorn`_ 搭配 Eventlet  一起使用。
如前文所述， Gunicorn 可以提供更丰富的配置，并且经过了生产测试。

`Eventlet`_ 允许编写异步的、基于协程的代码，看起来像标准的同步 Python。
它使用 `greenlet`_ 来启用任务切换，而不用写 ``async/await`` 或使用
``asyncio`` 。

它提供了一个可以同时处理多个连接的 WSGI 服务器，而不是每个工作器处理一个。

`Gevent`_ ，如前所述，是另一个做同样事情的库。您可以根据自身在情况选择
使用。

导入 ``wsgi.server`` 并用它来运行您的 ``app`` ，就可以使用 Eventlet 。

.. code-block:: python

    import eventlet
    from eventlet import wsgi
    from your_project import app

    wsgi.server(eventlet.listen(("", 5000), app)


Twisted Web
-----------

`Twisted Web`_ 是一个 `Twisted`_ 自带的网络服务器，是一个成熟的、异步的、
事件驱动的网络库。 Twisted Web 带有一个标准的 WSGI 容器，该容器可以使用
``twistd`` 工具运行命令行来控制：

.. code-block:: text

    $ twistd web --wsgi myproject.app

这个命令会运行一个名为 ``app`` 的 Flask 应用，其模块名为 ``myproject`` 。

与 ``twistd`` 工具一样， Twisted Web 支持许多标记和选项。更多信息参见
``twistd -h`` 和 ``twistd web -h`` 。例如下面命令在前台运行一个来自
``myproject`` 的应用， 端口为 8080 ：

.. code-block:: text

    $ twistd -n web --port tcp:8080 --wsgi myproject.app

.. _Twisted: https://twistedmatrix.com/trac/
.. _Twisted Web: https://twistedmatrix.com/trac/wiki/TwistedWeb


.. _deploying-proxy-setups:

代理设置
------------

如果你要在一个 HTTP 代理后面在上述服务器上运行应用，那么必须重写一些
头部才行。通常在 WSGI 环境中经常会出现问题的有两个变量：
``REMOTE_ADDR`` 和 ``HTTP_HOST`` 。你可以通过设置你的 httpd 来传递这
些头部，或者在中间件中修正这些问题。 Werkzeug 带有一个修复工具可以用
于常用的设置，但是你可能需要为特定的设置编写你自己的 WSGI 中间件。

下面是一个简单的 nginx 配置，代理目标是 localhost 8000 端口提供的服务，
设置了适当的头部：

.. sourcecode:: nginx

    server {
        listen 80;

        server_name _;

        access_log  /var/log/nginx/access.log;
        error_log  /var/log/nginx/error.log;

        location / {
            proxy_pass         http://127.0.0.1:8000/;
            proxy_redirect     off;

            proxy_set_header   Host                 $host;
            proxy_set_header   X-Real-IP            $remote_addr;
            proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto    $scheme;
        }
    }

如果你的 httpd 无法提供这些头部，那么最常用的设置是调用
``X-Forwarded-Host`` 定义的主机和 ``X-Forwarded-For`` 定义的远程地址::

    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

.. admonition:: 头部可信问题

   请注意，在非代理情况下使用这个中间件是有安全问题的，因为它会盲目信
   任恶意客户端发来的头部。

如果你要根据另一个头部来重写一个头部，那么可以像下例一样使用修复工具::


    class CustomProxyFix(object):

        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            host = environ.get('HTTP_X_FHOST', '')
            if host:
                environ['HTTP_HOST'] = host
            return self.app(environ, start_response)

    app.wsgi_app = CustomProxyFix(app.wsgi_app)

