添加 HTTP 方法重载
============================

一些 HTTP 代理不支持所有 HTTP 方法或者不支持一些较新的 HTTP 方法（例如 PACTH
）。在这种情况下，可以通过使用完全相反的协议，用一种 HTTP 方法来“代理”另一种
HTTP 方法。

实现的思路是让客户端发送一个 HTTP POST 请求，并设置 ``X-HTTP-Method-Override``
头部为需要的 HTTP 方法（例如 ``PATCH`` ）。

通过 HTTP 中间件可以方便的实现::

    class HTTPMethodOverrideMiddleware(object):
        allowed_methods = frozenset([
            'GET',
            'HEAD',
            'POST',
            'DELETE',
            'PUT',
            'PATCH',
            'OPTIONS'
        ])
        bodyless_methods = frozenset(['GET', 'HEAD', 'OPTIONS', 'DELETE'])

        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()
            if method in self.allowed_methods:
                method = method.encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
            if method in self.bodyless_methods:
                environ['CONTENT_LENGTH'] = '0'
            return self.app(environ, start_response)

通过以下代码就可以与 Flask 一同工作了::

    from flask import Flask

    app = Flask(__name__)
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
