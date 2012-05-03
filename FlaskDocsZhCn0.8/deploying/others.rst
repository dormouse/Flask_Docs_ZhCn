.. _deploying-other-servers:

其他服务器
=============

还有一些流行的用 Python 写的服务器也可以用于运行 WSGI 应用。这些服务器是独立
运行的，你可以把网络服务器作为它们的代理。

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

Gunicorn
--------

`Gunicorn`_ 'Green Unicorn' 是一个 UNIX 下的 WSGI HTTP 服务器，它移植自 Ruby 的
Unicorn 项目，是一个 pre-fork worker 模型。它既支持 `eventlet`_ ，也支持
`greenlet`_ 。在 Gunicorn 上运行 Flask 应用非常方便::

    gunicorn myproject:app

`Gunicorn`_ 提供许多命令行参数，可以使用 ``gunicorn -h`` 来获得帮助。下面的例子
使用 4 worker 进程（ ``-w 4`` ）来运行 Flask 应用，绑定到 localhost 的 4000
端口（ ``-b 127.0.0.1:4000`` ）::

    gunicorn -w 4 -b 127.0.0.1:4000 myproject:app

.. _Gunicorn: http://gunicorn.org/
.. _eventlet: http://eventlet.net/
.. _greenlet: http://codespeak.net/py/0.9.2/greenlet.html

代理设置
------------

如果你要在一个 HTTP 代理后面在上述服务器上运行应用，那么必须重写一些头部才行。
通常，在 WSGI 环境中经常会出现问题的有两个变量：
`REMOTE_ADDR` 和 `HTTP_HOST` 。 Werkzeug 带有一个修复工具可以用于常用的设置，
但是你可能需要为特定的设置编写你自己的 WSGI 中间件。

最常用的设置是调用 `X-Forwarded-Host` 定义的主机和 `X-Forwarded-For` 定义的远程
地址::

    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

请注意，在非代理情况下使用这个中间件是有安全问题的，因为它会盲目信任恶意客户端
发来的头部。

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
