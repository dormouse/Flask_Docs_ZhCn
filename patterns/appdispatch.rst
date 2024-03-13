应用调度
=======================

应用调度是在 WSGI 层面组合多个 Flask 应用的过程。可以组合多个 Flask 应
用，也可以组合 Flask 应用和其他 WSGI 应用。通过这种组合，如果有必要的
话，甚至可以在同一个解释器中一边运行 Django ，一边运行 Flask 。这种组合
的好处取决于应用内部是如何工作的。

应用调度与 :doc:`packages` 的最大不同在于应用调度中的每个应用是完全独立
的，它们以各自的配置运行，并在 WSGI 层面被调度。


说明
--------------------------

下面所有的技术说明和举例都归结于一个可以运行于任何 WSGI 服务器的
``application`` 对象。对于开发环境，使用 ``flask run`` 启动开发服务
器。对于生产环境，参见 :doc:`/deploying/index` 。

.. code-block:: python

    from flask import Flask

    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello World!'


组合应用
----------------------

如果你想在同一个 Python 解释器中运行多个独立的应用，那么你可以使用
:class:`werkzeug.wsgi.DispatcherMiddleware` 。其原理是：每个独立的 Flask
应用都是一个合法的 WSGI 应用，它们通过调度中间件组合为一个基于前缀调度
的大应用。

假设你的主应用运行于 ``/`` ，后台接口位于 ``/backend`` 。

.. code-block:: python

    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from frontend_app import application as frontend
    from backend_app import application as backend

    application = DispatcherMiddleware(frontend, {
        '/backend': backend
    })


根据子域调度
---------------------

有时候你可能需要使用不同的配置来运行同一个应用的多个实例。可以把应用创
建过程放在一个函数中，这样调用这个函数就可以创建一个应用的实例，具体实现
参见 :doc:`appfactories` 方案。

最常见的做法是每个子域创建一个应用，配置服务器来调度所有子域的应用请
求，使用子域来创建用户自定义的实例。一旦你的服务器可以监听所有子域，那
么就可以使用一个很简单的 WSGI 应用来动态创建应用了。

WSGI 层是完美的抽象层，因此可以写一个你自己的 WSGI 应用来监视请求，并把
请求分配给你的 Flask 应用。如果被分配的应用还没有创建，那么就会动态创建
应用并被登记下来。

.. code-block:: python

    from threading import Lock

    class SubdomainDispatcher:

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


调度器示例:

.. code-block:: python

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

根据 URL 的路径调度非常简单。上面，我们通过查找 ``Host`` 头来判断子域，
现在只要查找请求路径的第一个斜杠之前的路径就可以了。

.. code-block:: python

    from threading import Lock
    from wsgiref.util import shift_path_info

    class PathDispatcher:

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
            app = self.get_application(_peek_path_info(environ))
            if app is not None:
                shift_path_info(environ)
            else:
                app = self.default_app
            return app(environ, start_response)

    def _peek_path_info(environ):
        segments = environ.get("PATH_INFO", "").lstrip("/").split("/", 1)
        if segments:
            return segments[0]

        return None

与根据子域调度相比最大的不同是：根据路径调度时，如果创建函数返回
``None`` ，那么就会回落到另一个应用。

.. code-block:: python

    from myapplication import create_app, default_app, get_user_for_prefix

    def make_app(prefix):
        user = get_user_for_prefix(prefix)
        if user is not None:
            return create_app(user)

    application = PathDispatcher(default_app, make_app)

