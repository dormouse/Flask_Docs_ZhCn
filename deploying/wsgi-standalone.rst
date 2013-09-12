.. _deploying-wsgi-standalone:

独立 WSGI 容器
==========================

有一些用 Python 写的流行服务器可以容纳 WSGI 应用，提供 HTTP 服务。这些服务器是
独立运行的，你可以把代理从你的网络服务器指向它们。如果遇到问题，请阅读
:ref:`deploying-proxy-setups` 一节。

Gunicorn
--------

`Gunicorn`_ 'Green Unicorn' 是一个 UNIX 下的 WSGI HTTP 服务器，它是一个
移植自 Ruby 的 Unicorn 项目的 pre-fork worker 模型。它既支持 `eventlet`_ ，
也支持 `greenlet`_ 。在 Gunicorn 上运行 Flask 应用非常简单::

    gunicorn myproject:app

`Gunicorn`_ 提供许多命令行参数，可以使用 ``gunicorn -h`` 来获得帮助。下面的例子
使用 4 worker 进程（ ``-w 4`` ）来运行 Flask 应用，绑定到 localhost 的 4000
端口（ ``-b 127.0.0.1:4000`` ）::

    gunicorn -w 4 -b 127.0.0.1:4000 myproject:app

.. _Gunicorn: http://gunicorn.org/
.. _eventlet: http://eventlet.net/
.. _greenlet: http://codespeak.net/py/0.9.2/greenlet.html


Tornado
--------

`Tornado`_ 是构建 `FriendFeed`_ 的服务器和工具的开源版本，具有良好的伸缩性，非
阻塞性。得益于其非阻塞的方式和对 epoll 的运用，它可以同步处理数以千计的独立
连接，因此 Tornado 是实时 Web 服务的一个理想框架。用它来服务 Flask 是小事一桩::

    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from toranado.ioloop import IOLoop
    from yourapplication import app

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()


.. _Tornado: http://www.tornadoweb.org/
.. _FriendFeed: http://friendfeed.com/

Gevent
-------

`Gevent`_ 是一个 Python 并发网络库，它使用了基于 `libevent`_ 事件循环的
`greenlet`_ 来提供一个高级同步 API::

    from gevent.wsgi import WSGIServer
    from yourapplication import app

    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()

.. _Gevent: http://www.gevent.org/
.. _greenlet: http://codespeak.net/py/0.9.2/greenlet.html
.. _libevent: http://monkey.org/~provos/libevent/

Twisted Web
-----------

`Twisted Web`_ 是一个 `Twisted`_ 自带的网络服务器，是一个成熟的、异步的、事件
驱动的网络库。 Twisted Web 带有一个标准的 WSGI 容器，该容器可以使用 ``twistd``
工具运行命令行来控制::

    twistd web --wsgi myproject.app

这个命令会运行一个名为 ``app`` 的 Flask 应用，其模块名为 ``myproject`` 。

与 ``twistd`` 工具一样， Twisted Web 支持许多标记和选项。更多信息参见
``twistd -h`` 和 ``twistd web -h`` 。例如下面命令在前台运行一个来自
``myproject`` 的应用， 端口为 8080::

    twistd -n web --port 8080 --wsgi myproject.app

.. _Twisted: https://twistedmatrix.com/
.. _Twisted Web: https://twistedmatrix.com/trac/wiki/TwistedWeb

.. _deploying-proxy-setups:

代理设置
------------

如果你要在一个 HTTP 代理后面在上述服务器上运行应用，那么必须重写一些头部才行。
通常在 WSGI 环境中经常会出现问题的有两个变量： `REMOTE_ADDR` 和 `HTTP_HOST` 。
你可以通过设置你的 httpd 来传递这些头部，或者在中间件中修正这些问题。
Werkzeug 带有一个修复工具可以用于常用的设置，但是你可能需要为特定的设置编写你
自己的 WSGI 中间件。

下面是一个简单的 nginx 配置，代理目标是 localhost 8000 端口提供的服务，设置了
适当的头部：

.. sourcecode:: nginx

    server {
        listen 80;

        server_name _;

        access_log  /var/log/nginx/access.log;
        error_log  /var/log/nginx/error.log;

        location / {
            proxy_pass         http://127.0.0.1:8000/;
            proxy_redirect     off;

            proxy_set_header   Host             $host;
            proxy_set_header   X-Real-IP        $remote_addr;
            proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        }
    }

如果你的 httpd 无法提供这些头部，那么最常用的设置是调用 `X-Forwarded-Host` 定义
的主机和 `X-Forwarded-For` 定义的远程地址::

    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

.. admonition:: 头部可信问题

   请注意，在非代理情况下使用这个中间件是有安全问题的，因为它会盲目信任恶意
   客户端发来的头部。

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
