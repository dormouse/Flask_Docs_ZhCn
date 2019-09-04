.. _application-errors:

应用错误处理
============

.. versionadded:: 0.3

应用出错，服务器出错。或早或晚，你会遇到产品出错。即使你的代码是百分百正确，
还是会时常看见出错。为什么？因为其他相关东西会出错。以下是一些在代码完全正确的
条件下服务器出错的情况：

-   客户端已经中断了请求，但应用还在读取数据。
-   数据库已经过载，无法处理查询。
-   文件系统没有空间。
-   硬盘完蛋了。
-   后台服务过载。
-   使用的库出现程序错误。
-   服务器与另一个系统的网络连接出错。

以上只是你会遇到的问题的一小部分。那么如何处理这些问题呢？如果你的应用运行
在生产环境下，那么缺省情况下 Flask 会显示一个简单的出错页面，并把出错情况
记录到 :attr:`~flask.Flask.logger` 。

但可做的还不只这些，下面介绍一些更好的出错处理方法。


错误日志工具
-------------------

当足够多的用户触发了错误时，发送关于出错信息的邮件，即使仅包含严重错误的邮
件也会是一场空难。更不用提从来不会去看的日志文件了。
因此，推荐使用 `Sentry <https://sentry.io/>`_ 来处理应用错误。它可
以在一个开源项目 `on GitHub <https://github.com/getsentry/sentry>`_ 中获得，
也可以在 `hosted version <https://sentry.io/signup/>`_ 中免费试用。
Sentry 统计重复错误，捕获堆栈数据和本地变量用于排错，并在发生新的或者指定
频度的错误时发送电子邮件。

要使用 Sentry 需要安装带有 `flask` 依赖的 `sentry-sdk` 客户端::

    $ pip install sentry-sdk[flask]

把下面内容加入 Flask 应用::

    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init('YOUR_DSN_HERE',integrations=[FlaskIntegration()])


`YOUR_DSN_HERE` 需要被替换为在 Sentry 安装时获得的 DSN 值。

安装好以后，内部服务出错信息会自动向 Sentry 报告，你会接收到出错通知。

后续阅读：

* Sentry 也支持从队列（ RQ 、 Celery ）中捕获错误。详见
  `Python SDK 文档
  <https://docs.sentry.io/platforms/python/>`_ 。
* `Sentry 入门 <https://docs.sentry.io/quickstart/?platform=python>`_
* `Flask-相关文档 <https://docs.sentry.io/platforms/python/flask/>`_

.. _error-handlers:

错误处理
--------------

当错误发生时，你可能想要向用户显示自定义的出错页面。注册出错处理器或以做到
这点。

一个出错处理器是一个返回响应的普通视图函数。但是不同之在于它不是用于路由的
，而是用于一个异常或者当尝试处理请求时抛出 HTTP 状态码。

注册
```````````

通过使用 :meth:`~flask.Flask.errorhandler` 装饰函数来注册或者稍后使用
:meth:`~flask.Flask.register_error_handler` 来注册。
记得当返回响应的时候设置出错代码::

    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return 'bad request!', 400

    # or, without the decorator
    app.register_error_handler(400, handle_bad_request)

当注册时， :exc:`werkzeug.exceptions.HTTPException` 的子类，如
:exc:`~werkzeug.exceptions.BadRequest` ，和它们的 HTTP 代码是可替换的。
（ ``BadRequest.code == 400`` ）

因为 Werkzeug 无法识别非标准 HTTP 代码，因此它们不能被注册。替代地，使用适
当的代码定义一个 :class:`~werkzeug.exceptions.HTTPException` 子类，注册并
抛出异常类::

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

在处理请求时，当 Flask 捕捉到一个异常时，它首先根据代码检索。如果该代码没
有注册处理器，它会根据类的继承来查找，确定最合适的注册处理器。如果找不到已
注册的处理器，那么 :class:`~werkzeug.exceptions.HTTPException` 子类会显示
一个关于代码的通用消息。没有代码的异常会被转化为一个通用的 500 内部服务器
错误。

例如，如果一个 :exc:`ConnectionRefusedError` 的实例被抛出，并且一个出错处
理器注册到 :exc:`ConnectionError` 和 :exc:`ConnectionRefusedError` ，那么
会使用更合适的 :exc:`ConnectionRefusedError` 来处理异常实例，生成响应。

当一个蓝图在处理抛出异常的请求时，在蓝图中注册的出错处理器优先于在应用中全
局注册的出错处理器。但是，蓝图无法处理 404 路由错误，因为 404 发生的路由级
别还不能检测到蓝图。


通用异常处理器
``````````````````````````

可以为非常通用的基类注册异常处理器，例如 ``HTTPException`` 基类或者甚至
``Exception`` 基类。但是，请注意，这样会捕捉到超出你预期的异常。

基于 ``HTTPException`` 的异常处理器对于把缺省的 HTML 出错页面转换为 JSON
非常有用，但是这个处理器会触发不由你直接产生的东西，如路由过程中产生的
404 和 405 错误。请仔细制作你的处理器，确保不会丢失关于 HTTP 错误的信息。

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


基于 ``Exception`` 的异常处理器有助于改变所有异常处理的表现形式，甚至包含
未处理的异常。但是，与在 Python 使用 ``except Exception:`` 类似，这样会捕
获 *所有* 未处理的异常，包括所有 HTTP 状态码。因此，在大多数情况下，设定
只针对特定异常的处理器比较安全。
因为 ``HTTPException`` 实例是一个合法的 WSGI 响应，你可以直接传递该实例。

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

如果针为 ``InternalServerError`` 注册了异常处理器，那么出现内部服务错误时就
会调用这个处理器。自 Flask 1.1.0 开始，总是会传递一个
``InternalServerError`` 实例给这个异常处理器，而不是以前的未处理异常。原始
的异常可以通过 ``e.original_error`` 访问。在 Werkzeug 1.0.0 以前，这个属性
只有未处理异常有。建议使用 ``getattr`` 访问这个属性，以保证兼容性。

.. code-block:: python

    @app.errorhandler(InternalServerError)
    def handle_500(e):
        original = getattr(e, "original_exception", None)

        if original is None:
            # direct 500 error, such as abort(500)
            return render_template("500.html"), 500

        # wrapped unhandled error
        return render_template("500_unhandled.html", e=original), 500

日志
-------

如何记录异常，比如向管理者发送邮件，参见 :ref:`logging` 。

排除应用错误
============================

:ref:`application-errors` 一文所讲的是如何为生产应用设置日志和出错通知。本文要
讲的是部署中配置调试的要点和如何使用全功能的 Python 调试器深挖错误。


有疑问时，请手动运行
---------------------------

在生产环境中，配置应用时出错？如果你可以通过 shell 来访问主机，那么首先请
在部署环境中验证是否可以通过 shell 手动运行你的应用。请确保验证时使用的帐
户与配置的相同，这样可以排除用户权限引发的错误。可以在你的生产服务器上，
使用 Flask 内建的开发服务器，并且设置 `debug=True` ，这样有助于找到配置问
题。但是，请 **只能在可控的情况下临时这样做** ，绝不能在生产时使用
`debug=True` 。


.. _working-with-debuggers:

使用调试器
----------------------

为了更深入的挖掘错误，追踪代码的执行， Flask 提供一个开箱即用的调试器（参
见 :ref:`debug-mode` ）。如果你需要使用其他 Python 调试器，请注意调试器之
间的干扰问题。在使用你自己的调试器前要做一些参数调整：

* ``debug``        - 是否开启调试模式并捕捉异常
* ``use_debugger`` - 是否使用 Flask 内建的调试器
* ``use_reloader`` - 模块变化后是否重载并派生进程

``debug`` 必须设置为 True （即必须捕获异常），另两个随便。

如果你正在使用 Aptana 或 Eclipse 排错，那么 ``use_debugger`` 和
``use_reloader`` 都必须设置为 False 。

一个有用的配置模式如下（当然要根据你的应用调整缩进）::

   FLASK:
       DEBUG: True
       DEBUG_WITH_APTANA: True

然后，在应用入口（ main.py ），修改如下::

   if __name__ == "__main__":
       # To allow aptana to receive errors, set use_debugger=False
       app = create_app(config="config.yaml")

       use_debugger = app.debug and not(app.config.get('DEBUG_WITH_APTANA'))
       app.run(use_debugger=use_debugger, debug=app.debug,
               use_reloader=use_debugger, host='0.0.0.0')
