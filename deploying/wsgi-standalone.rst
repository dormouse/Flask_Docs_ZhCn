.. _deploying-wsgi-standalone:

独立 WSGI 容器
==========================

有一些用 Python 写的流行服务器可以容纳 WSGI 应用，提供 HTTP 服务。这些服务
器是独立运行的，你可以把代理从你的网络服务器指向它们。如果遇到问题，请阅读
:ref:`deploying-proxy-setups` 一节。

Gunicorn
--------

`Gunicorn`_ 'Green Unicorn' 是一个 UNIX 下的 WSGI HTTP 服务器，它是一个
移植自 Ruby 的 Unicorn 项目的 pre-fork worker 模型。它既支持 `eventlet`_ ，
也支持 `greenlet`_ 。在 Gunicorn 上运行 Flask 应用非常简单::

    gunicorn myproject:app

`Gunicorn`_ 提供许多命令行参数，可以使用 ``gunicorn -h`` 来获得帮助。下面
的例子使用 4 worker 进程（ ``-w 4`` ）来运行 Flask 应用，绑定到 localhost
的 4000 端口（ ``-b 127.0.0.1:4000`` ）::

    gunicorn -w 4 -b 127.0.0.1:4000 myproject:app

.. _Gunicorn: http://gunicorn.org/
.. _eventlet: http://eventlet.net/
.. _greenlet: https://greenlet.readthedocs.io/en/latest/


uWSGI
--------


`uWSGI`_ 一个用 C 写的快速应用服务器。它配置丰富，从而配置复杂度也大于
gunicorn 。

运行 `uWSGI HTTP Router`_::

    uwsgi --http 127.0.0.1:5000 --module myproject:app

更有组织的的配置，参见 `配置 uWSGI 和 NGINX`_.

.. _uWSGI: http://uwsgi-docs.readthedocs.io/en/latest/
.. _uWSGI HTTP Router: http://uwsgi-docs.readthedocs.io/en/latest/HTTP.html#the-uwsgi-http-https-router
.. _配置 uWSGI 和 NGINX: uwsgi.html#starting-your-app-with-uwsgi


Gevent
-------

`Gevent`_ 是一个 Python 并发网络库，它使用了基于 `libev`_ 事件循环的
`greenlet`_ 来提供一个高级同步 API::

    from gevent.wsgi import WSGIServer
    from yourapplication import app

    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()

.. _Gevent: http://www.gevent.org/
.. _greenlet: https://greenlet.readthedocs.io/en/latest/
.. _libev: http://software.schmorp.de/pkg/libev.html


Twisted Web
-----------

`Twisted Web`_ 是一个 `Twisted`_ 自带的网络服务器，是一个成熟的、异步的、
事件驱动的网络库。 Twisted Web 带有一个标准的 WSGI 容器，该容器可以使用
``twistd`` 工具运行命令行来控制::

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

如果你要在一个 HTTP 代理后面在上述服务器上运行应用，那么必须重写一些头部才
行。通常在 WSGI 环境中经常会出现问题的有两个变量： ``REMOTE_ADDR`` 和
``HTTP_HOST`` 。你可以通过设置你的 httpd 来传递这些头部，或者在中间件中修
正这些问题。 Werkzeug 带有一个修复工具可以用于常用的设置，但是你可能需要为
特定的设置编写你自己的 WSGI 中间件。

下面是一个简单的 nginx 配置，代理目标是 localhost 8000 端口提供的服务，设
置了适当的头部：

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

    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

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

