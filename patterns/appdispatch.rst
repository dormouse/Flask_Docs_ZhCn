.. _app-dispatch:

应用调度
=======================

应用调度是在 WSGI 层面组合多个 WSGI 应用的过程。可以组合多个 Flask 应用，也可以
组合 Flask 应用和其他 WSGI 应用。通过这种组合，如果有必要的话，甚至可以在同一个
解释器中一边运行 Django ，一边运行 Flask 。这种组合的好处取决于应用内部是如何
工作的。

应用调度与 :ref:`模块化 <larger-applications>` 的最大不同在于应用调度中的每个
应用是完全独立的，它们以各自的配置运行，并在 WSGI 层面被调度。


说明
--------------------------

下面所有的技术说明和举例都归结于一个可以运行于任何 WSGI 服务器的
``application`` 对象。对于生产环境，参见 :ref:`deployment` 。对于开发环境，
Werkzeug 提供了一个内建开发服务器，它使用 :func:`werkzeug.serving.run_simple`
来运行::

    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, application, use_reloader=True)

注意 :func:`run_simple <werkzeug.serving.run_simple>` 不能用于生产环境，生产
环境服务器参见 :ref:`成熟的 WSGI 服务器 <deployment>` 。

为了使用交互调试器，应用和简单服务器都应当处于调试模式。下面是一个简单的
“ hello world ”示例，使用了调试模式和
:func:`run_simple <werkzeug.serving.run_simple>`::

    from flask import Flask
    from werkzeug.serving import run_simple

    app = Flask(__name__)
    app.debug = True

    @app.route('/')
    def hello_world():
        return 'Hello World!'

    if __name__ == '__main__':
        run_simple('localhost', 5000, app,
                   use_reloader=True, use_debugger=True, use_evalex=True)


组合应用
----------------------

如果你想在同一个 Python 解释器中运行多个独立的应用，那么你可以使用
:class:`werkzeug.wsgi.DispatcherMiddleware` 。其原理是：每个独立的 Flask 应用都
是一个合法的 WSGI 应用，它们通过调度中间件组合为一个基于前缀调度的大应用。

假设你的主应用运行于 `/` ，后台接口位于 `/backend`::

    from werkzeug.wsgi import DispatcherMiddleware
    from frontend_app import application as frontend
    from backend_app import application as backend

    application = DispatcherMiddleware(frontend, {
        '/backend':     backend
    })


根据子域调度
---------------------

有时候你可能需要使用不同的配置来运行同一个应用的多个实例。可以把应用创建过程
放在一个函数中，这样调用这个函数就可以创建一个应用的实例，具体实现参见
:ref:`app-factories` 方案。

最常见的做法是每个子域创建一个应用，配置服务器来调度所有子域的应用请求，使用
子域来创建用户自定义的实例。一旦你的服务器可以监听所有子域，那么就可以使用一个
很简单的 WSGI 应用来动态创建应用了。

WSGI 层是完美的抽象层，因此可以写一个你自己的 WSGI 应用来监视请求，并把请求分配
给你的 Flask 应用。如果被分配的应用还没有创建，那么就会动态创建应用并被登记
下来::

    from threading import Lock

    class SubdomainDispatcher(object):

        def __init__(self, domain, create_app):
            self.domain = domain
            self.create_app = create_app
            self.lock = Lock()
            self.instances = {}

        def get_application(self, host):
            host = host.split(':')[0]
            assert host.endswith(self.domain), 'Configuration error'
            subdomain = host[:-len(self.domain)].rstrip('.')
            with self.lock:
                app = self.instances.get(subdomain)
                if app is None:
                    app = self.create_app(subdomain)
                    self.instances[subdomain] = app
                return app

        def __call__(self, environ, start_response):
            app = self.get_application(environ['HTTP_HOST'])
            return app(environ, start_response)


调度器示例::

    from myapplication import create_app, get_user_for_subdomain
    from werkzeug.exceptions import NotFound

    def make_app(subdomain):
        user = get_user_for_subdomain(subdomain)
        if user is None:
            # 如果子域没有对应的用户，那么还是得返回一个 WSGI 应用
            # 用于处理请求。这里我们把 NotFound() 异常作为应用返回，
            # 它会被渲染为一个缺省的 404 页面。然后，可能还需要把
            # 用户重定向到主页。
            return NotFound()

        # 否则为特定用户创建应用
        return create_app(user)

    application = SubdomainDispatcher('example.com', make_app)


根据路径调度
----------------

根据 URL 的路径调度非常简单。上面，我们通过查找 `Host` 头来判断子域，现在 
只要查找请求路径的第一个斜杠之前的路径就可以了::

    from threading import Lock
    from werkzeug.wsgi import pop_path_info, peek_path_info

    class PathDispatcher(object):

        def __init__(self, default_app, create_app):
            self.default_app = default_app
            self.create_app = create_app
            self.lock = Lock()
            self.instances = {}

        def get_application(self, prefix):
            with self.lock:
                app = self.instances.get(prefix)
                if app is None:
                    app = self.create_app(prefix)
                    if app is not None:
                        self.instances[prefix] = app
                return app

        def __call__(self, environ, start_response):
            app = self.get_application(peek_path_info(environ))
            if app is not None:
                pop_path_info(environ)
            else:
                app = self.default_app
            return app(environ, start_response)

与根据子域调度相比最大的不同是：根据路径调度时，如果创建函数返回 `None` ，那么
就会回落到另一个应用::

    from myapplication import create_app, default_app, get_user_for_prefix

    def make_app(prefix):
        user = get_user_for_prefix(prefix)
        if user is not None:
            return create_app(user)

    application = PathDispatcher(default_app, make_app)
