应用错误处理
============

应用出错，服务器出错。或早或晚，你会遇到产品出错。即使你的代码是百分百
正确，还是会时常看见出错。为什么？因为其他相关东西会出错。以下是一些在
代码完全正确的条件下服务器出错的情况：

-   客户端已经中断了请求，但应用还在读取数据。
-   数据库已经过载，无法处理查询。
-   文件系统没有空间。
-   硬盘完蛋了。
-   后台服务过载。
-   使用的库出现程序错误。
-   服务器与另一个系统的网络连接出错。

以上只是你会遇到的问题的一小部分。那么如何处理这些问题呢？如果你的应用
运行在生产环境下，那么缺省情况下 Flask 会显示一个简单的出错页面，并把出
错情况记录到 :attr:`~flask.Flask.logger` 。

但可做的还不只这些，下面介绍一些更好的出错处理方式，包括自定义异常和第
三方工具。


.. _error-logging-tools:

错误日志工具
-------------------

即使发送出错信息的邮件仅包含严重错误，当足够多的用户触发了错误时，也会
是一场灾难，更不用提从来不会去看的日志文件了。
因此，推荐使用 `Sentry <https://sentry.io/>`_ 来处理应用错误。它是一个
`GitHub 上 <https://github.com/getsentry/sentry>`_ 的可提供源代码项目，
也可以在 `托管版本 <https://sentry.io/signup/>`_ 中免费试用。 Sentry
可以统计重复错误，捕获堆栈数据和本地变量用于排错，并在发生新的错误时或
者按指定频度发送电子邮件。

要使用 Sentry 需要安装带有 `flask` 依赖的 `sentry-sdk` 客户端。

.. code-block:: text

    $ pip install sentry-sdk[flask]

并且把下面内容加入 Flask 应用：

.. code-block:: python

    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init('YOUR_DSN_HERE', integrations=[FlaskIntegration()])

``YOUR_DSN_HERE`` 需要被替换为在 Sentry 安装时获得的 DSN 值。

安装好以后，内部服务出错信息会自动向 Sentry 报告，你会接收到出错通知。

后续阅读：

-  Sentry 也支持从队列（ RQ 、 Celery ）中捕获错误。详见
   `Python SDK 文档 <https://docs.sentry.io/platforms/python/>`__ 。
-  `Flask-相关文档 <https://docs.sentry.io/platforms/python/flask/>`__

.. _error-handlers:

还可以看看：

-   Sentry 也支持以类似的方式从队列（ RQ 、 Celery ）中捕获错误。详见
    `Python SDK 文档 <https://docs.sentry.io/platforms/python/>`__ 。
-   `Sentry 入门 <https://docs.sentry.io/quickstart/?platform=python>`__
-   `Flask-相关文档 <https://docs.sentry.io/platforms/python/guides/flask/>`__


错误处理器
--------------

在 Flask 中发生错误时，会返回一个相应的 `HTTP 状态码
<https://developer.mozilla.org/en-US/docs/Web/HTTP/Status>`__ 。
状态码 400-499 表示客户端的请求数据或者与之相关的错误。状态码 500-599
表示服务器或者应用本身的错误。

当错误发生时，你可能想要向用户显示自定义的出错页面。注册出错处理器可以
做到这点。

一个出错处理器是一个函数，当发生某类错误时返回一个响应。类似于一个视图
函数，当请求 URL 匹配时返回一个响应。它传递了正在处理的错误的实例，基本
上是一个 :exc:`~werkzeug.exceptions.HTTPException` 。

响应的状态代码不会设置为处理器的代码。请确保从处理器返回一个响应时提供
适当的 HTTP 状态码。

注册
```````````

通过使用 :meth:`~flask.Flask.errorhandler` 装饰函数来注册或者稍后使用
:meth:`~flask.Flask.register_error_handler` 来注册。
记得当返回响应的时候设置出错代码。

.. code-block:: python

    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return 'bad request!', 400

    # or, without the decorator
    app.register_error_handler(400, handle_bad_request)

当注册时， :exc:`werkzeug.exceptions.HTTPException` 的子类，如
:exc:`~werkzeug.exceptions.BadRequest` ，和它们的 HTTP 代码是可替换的。
（ ``BadRequest.code == 400`` ）

因为 Werkzeug 无法识别非标准 HTTP 代码，所以它们不能被注册。相反，使用
适当的代码定义一个 :class:`~werkzeug.exceptions.HTTPException` 子类，
注册并抛出异常类。

.. code-block:: python

    class InsufficientStorage(werkzeug.exceptions.HTTPException):
        code = 507
        description = 'Not enough storage space.'

    app.register_error_handler(InsufficientStorage, handle_507)

    raise InsufficientStorage()

出错处理器可被用于任何异常类的注册，除了
:exc:`~werkzeug.exceptions.HTTPException` 子类或者 HTTP 状态码。
出错处理器可被用于特定类的注册，也可用于一个父类的所有子类的注册。


处理
````````

在构建 Flask 应用时，您 *会* 遇到异常。如果在处理请求时（且您没有注册
错误处理器），你的代码中断了，那么将默认返回“ 500 内部服务器错误”
（ :exc:`~werkzeug.exceptions.InternalServerError` ）。
同样，如果请求被发送到未注册的路由，则会产生 “ 404 未找到”
（ :exc:`~werkzeug.exceptions.NotFound` ）错误。
如果路由接收到被禁止的请求方法，则会产生“ 405 方法被禁止”
(:exc:`~werkzeug.exceptions.MethodNotAllowed`) 。
Flask 默认提供这些 :class:`~werkzeug.exceptions.HTTPException` 的子类。

Flask 使您能够注册 Werkzeug 提供的任意 HTTP 异常。但是，默认的 HTTP 异
常返回简单的异常页。您可能希望在发生错误时向用户显示自定义错误页面。可
以通过注册错误处理器来完成。

在处理请求时，当 Flask 捕捉到一个异常时，它首先根据代码检索。如果该代码
没有注册处理器，它会根据类的继承来查找，确定最合适的注册处理器。如果找
不到已注册的处理器，那么 :class:`~werkzeug.exceptions.HTTPException` 子
类会显示一个关于代码的通用消息。没有代码的异常会被转化为一个通用的
“ 500 内部服务器错误”。

例如，如果一个 :exc:`ConnectionRefusedError` 的实例被抛出，并且一个出错
处理器注册到 :exc:`ConnectionError` 和 :exc:`ConnectionRefusedError` ，
那么会使用更合适的 :exc:`ConnectionRefusedError` 来处理异常实例，生成响
应。

当一个蓝图在处理抛出异常的请求时，在蓝图中注册的出错处理器优先于在应用
中全局注册的出错处理器。但是，蓝图无法处理 404 路由错误，因为 404 发生
的路由级别还不能检测到蓝图。


通用异常处理器
``````````````````````````

可以为非常通用的基类注册异常处理器，例如 ``HTTPException`` 基类或者甚至
``Exception`` 基类。但是，请注意，这样会捕捉到超出你预期的异常。

例如，基于 ``HTTPException`` 的异常处理器对于把缺省的 HTML 出错页面转换
为 JSON 非常有用，但是这个处理器会触发不由你直接产生的东西，如路由过程
中产生的 404 和 405 错误。请仔细制作你的处理器，确保不会丢失关于 HTTP
错误的信息。

.. code-block:: python

    from flask import json
    from werkzeug.exceptions import HTTPException

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

用于 ``Exception`` 的异常处理器有助于改变所有异常处理的表现形式，甚至包含
未处理的异常。但是，与在 Python 使用 ``except Exception:`` 类似，这样会捕
获 *所有* 未处理的异常，包括所有 HTTP 状态码。

因此，在大多数情况下，设定只针对特定异常的处理器比较安全。因为
``HTTPException`` 实例是一个合法的 WSGI 响应，你可以直接传递该实例。

.. code-block:: python

    from werkzeug.exceptions import HTTPException

    @app.errorhandler(Exception)
    def handle_exception(e):
        # pass through HTTP errors
        if isinstance(e, HTTPException):
            return e

        # now you're handling non-HTTP exceptions only
        return render_template("500_generic.html", e=e), 500

异常处理器仍然遵循异常烦类的继承层次。如果同时基于 ``HTTPException`` 和
``Exception`` 注册了异常处理器， ``Exception`` 处理器不会处理
``HTTPException`` 子类，因为 ``HTTPException`` 更有针对性。


未处理的异常
````````````````````

当一个异常发生时，如果没有对应的异常处理器，那么就会返回一个 500
内部服务错误。关于此行为的更多内容参见
:meth:`flask.Flask.handle_exception` 。

如果针对 ``InternalServerError`` 注册了异常处理器，那么出现内部服务错误
时就会调用这个处理器。自 Flask 1.1.0 开始，总是会传递一个
``InternalServerError`` 实例给这个异常处理器，而不是以前的未处理异常。

原始的异常可以通过 ``e.original_exception`` 访问。

除了显式的 500 错误外，未捕获的异常也会被传递给用于处理
“ 500 内部服务器错误”的错误处理器。在调试模式下，用于处理
“ 500 内部服务器错误”的错误处理器不会被启用。相反，将显示交互调试器。


自定义错误页面
------------------

有时在构建 Flask 应用时，您可能希望产生一个
:exc:`~werkzeug.exceptions.HTTPException` ，向用户发出信号，提示请求有
问题。幸运的是，Flask 附带了一个方便的来自 werkzeug 的
:func:`~flask.abort` 函数，可以中止请求，产生 HTTP 错误。它还提供一个带
有基本描述的朴素的黑白页面。

依据错误代码，用户可以或多或少，知道一些错误。

考虑下面的代码，我们可能有一个用户配置文件路由，如果用户未能传递用户名，
我们可以引发“ 400 错误请求”。 如果用户传递了用户名，但是我们找不到它，
我们引发“ 404 页面未找到”。 

.. code-block:: python

    from flask import abort, render_template, request

    # a username needs to be supplied in the query args
    # a successful request would be like /profile?username=jack
    @app.route("/profile")
    def user_profile():
        username = request.arg.get("username")
        # if a username isn't supplied in the request, return a 400 bad request
        if username is None:
            abort(400)

        user = get_user(username=username)
        # if a user can't be found by their username, return 404 not found
        if user is None:
            abort(404)

        return render_template("profile.html", user=user)

这是“404 页面未找到”异常的另一个示例实现：

.. code-block:: python

    from flask import render_template

    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return render_template('404.html'), 404

当使用 :doc:`/patterns/appfactories` 时：

.. code-block:: python

    from flask import Flask, render_template

    def page_not_found(e):
      return render_template('404.html'), 404

    def create_app(config_filename):
        app = Flask(__name__)
        app.register_error_handler(404, page_not_found)
        return app

一个示例模板如下：

.. code-block:: html+jinja

    {% extends "layout.html" %}
    {% block title %}Page Not Found{% endblock %}
    {% block body %}
      <h1>Page Not Found</h1>
      <p>What you were looking for is just not there.
      <p><a href="{{ url_for('index') }}">go somewhere nice</a>
    {% endblock %}


进一步的例子
``````````````````

上面的例子实际上并未对默认异常页面进行改进。我们可以像这样创建一个自定
义的 500.html 模板： 

.. code-block:: html+jinja

    {% extends "layout.html" %}
    {% block title %}Internal Server Error{% endblock %}
    {% block body %}
      <h1>Internal Server Error</h1>
      <p>Oops... we seem to have made a mistake, sorry!</p>
      <p><a href="{{ url_for('index') }}">Go somewhere nice instead</a>
    {% endblock %}

发生“ 500 内部服务器错误”时，模板会用于渲染页面:

.. code-block:: python

    from flask import render_template

    @app.errorhandler(500)
    def internal_server_error(e):
        # note that we set the 500 status explicitly
        return render_template('500.html'), 500

当使用 :doc:`/patterns/appfactories` 时：

.. code-block:: python

    from flask import Flask, render_template

    def internal_server_error(e):
      return render_template('500.html'), 500

    def create_app():
        app = Flask(__name__)
        app.register_error_handler(500, internal_server_error)
        return app

当使用 :doc:`/blueprints` 时：

.. code-block:: python

    from flask import Blueprint

    blog = Blueprint('blog', __name__)

    # as a decorator
    @blog.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # or with register_error_handler
    blog.register_error_handler(500, internal_server_error)


蓝印错误处理器
------------------------

在 :doc:`/blueprints` 中，大多数错误处理器会按预期工作，但是处理 404 和
405 错误的处理器比较特殊，要小心。这些错误处理器只有从适当的 ``raise``
语句调用时或者在另一个蓝印在视图函数中调用 ``abort`` 时才会调用。相反，
例如非法 URL 访问时，则不会调用。

这是因为蓝印不“拥有”一定的 URL 空间，所以应用实例无法知道非法 URL 访
问应当调用哪个蓝印的错误处理器。如果需要基于 URL 前缀配置不同的处理策略，
那么可以使用 ``rquest`` 代理对象在应用层面进行配置。

.. code-block:: python

    from flask import jsonify, render_template

    # at the application level
    # not the blueprint level
    @app.errorhandler(404)
    def page_not_found(e):
        # if a request is in our blog URL space
        if request.path.startswith('/blog/'):
            # we return a custom blog 404 page
            return render_template("blog/404.html"), 404
        else:
            # otherwise we return our generic site-wide 404 page
            return render_template("404.html"), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        # if a request has the wrong method to our API
        if request.path.startswith('/api/'):
            # we return a json saying so
            return jsonify(message="Method Not Allowed"), 405
        else:
            # otherwise we return a generic site-wide 405 page
            return render_template("405.html"), 405


将 API 错误作为 JSON 返回
----------------------------

在 Flask 中构建 API 时，一些开发人员意识到内置的异常对于 API 来说表达能
力不够，而且发出的 :mimetype:`text/html` 内容类型对 API 使用者来说不是
很有用。

使用与上述相同的技术和 :func:`~flask.json.jsonify` 我们可以对 API 错误
返回 JSON 格式的响应。
调用 :func:`~flask.abort` 时，使用 ``description`` 参数，错误处理器会把
这个参数的内容作为 JSON 错误信息，并设置状态码为 404 。

.. code-block:: python

    from flask import abort, jsonify

    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error=str(e)), 404

    @app.route("/cheese")
    def get_one_cheese():
        resource = get_resource()

        if resource is None:
            abort(404, description="Resource not found")

        return jsonify(resource)

我们还可以创建自定义异常类。 例如，我们可以为 API 引入一个新的自定义异常，
该异常可以包含可读性良好的错误消息、状态码以及与错误相关的可选内容。

举个简单的例子：

.. code-block:: python

    from flask import jsonify, request

    class InvalidAPIUsage(Exception):
        status_code = 400

        def __init__(self, message, status_code=None, payload=None):
            super().__init__()
            self.message = message
            if status_code is not None:
                self.status_code = status_code
            self.payload = payload

        def to_dict(self):
            rv = dict(self.payload or ())
            rv['message'] = self.message
            return rv

    @app.errorhandler(InvalidAPIUsage)
    def invalid_api_usage(e):
        return jsonify(e.to_dict()), e.status_code

    # an API app route for getting user information
    # a correct request might be /api/user?user_id=420
    @app.route("/api/user")
    def user_api(user_id):
        user_id = request.arg.get("user_id")
        if not user_id:
            raise InvalidAPIUsage("No user id provided!")

        user = get_user(user_id=user_id)
        if not user:
            raise InvalidAPIUsage("No such user!", status_code=404)

        return jsonify(user.to_dict())

一个视图现在可以引发带有错误信息的异常。此外，一些额外的内容可以通过
`payload` 参数，以字典的方式提供。


日志
-------

关于如何记录异常，比如以向管理员发邮件的方式记录，请参阅
:doc:`/logging` 。


调试
---------

关于如何在开发模式和生产模式下调试的内容请参阅 :doc:`/debugging` 。
