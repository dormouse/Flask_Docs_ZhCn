应用程序结构和生命周期
===================================

Flask 使编写 Web应用程序变得非常容易。但是应用程序的不同部分及其处理
每个请求会有许多不同。知道在应用程序设置、服务和处理请求期间会发生什
么将有助您了解在 Flask 中什么是可能的以及如何构建您的应用程序。


应用程序设置
-----------------

创建 Flask 应用程序的第一步是创建应用对象。每个 Flask 应用都是
:class:`.Flask` 类的一个实例，它收集所有的配置、扩展和视图。

.. code-block:: python

    from flask import Flask

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )
    app.config.from_prefixed_env()

    @app.route("/")
    def index():
        return "Hello, World!"

这被称为“应用设置阶段”，它是位于任何视图函数或其他处理程序外面的代
码。它可以在不同的模块和子包，但所有代码必须导入成为应用程序一部分，
以便注册。

在开始为应用程序和请求处理提供服务之前，必须完成所有应用设置。这是因
为 WSGI 服务器在多个工作线程之间划分工作，工作可以分布在多台计算机上。
如果一个工人的配置发生更改， Flask 无法确保其他工作线程之间的一致性。

如果在处理请求后调用与设置相关的方法，那么 Flask 会显示一个错误信息，
以帮助开发者获得设置问题。在这种情况下您将看到此错误：

    The setup method 'route' can no longer be called on the application. It has already
    handled its first request, any changes will not be applied consistently.
    Make sure all imports, decorators, functions, etc. needed to set up the application
    are done before running it.


但是，Flask 无法检测到所有无序设置的情况。通常，不要在请求期间从内部
视图函数执行任何操作来修改 ``Flask`` 应用对象和 ``Blueprint`` 对象。
这包括：

-    使用 ``@app.route`` 、 ``@app.errorhandler`` 、
     ``@app.before_request`` 等添加路由、视图函数和其他请求处理程序。
-    注册蓝图。
-    使用 ``app.config`` 加载配置。
-    使用 ``app.jinja_env`` 设置 Jinja 模板环境。
-    设置会话接口，而不是默认的 itsdangerous cookie 。
-    使用 ``app.json`` 作为 JSON 提供程序，而不是使用缺省的提供程序。
-    创建和初始化 Flask 扩展。


为应用程序提供服务
-----------------------

Flask 是一个 WSGI 应用框架。 WSGI 的另一半是 WSGI 服务器。在开发过程
中， Flask 使用 ``flask run`` CLI 命令，通过 Werkzeug 提供了一个开发
WSGI 服务器。完成开发后，请使用生产服务器为应用提供服务，请参阅
:doc:`deploying/index` 。

无论使用什么服务器，它都将遵循 :pep:`3333` WSGI 规范。
该 WSGI 服务器将被告知如何访问您的 Flask 应用对象，即 WSGI 应用。
然后它将开始侦听 HTTP 请求，翻译请求数据
进入 WSGI 环境，并使用该数据调用 WSGI 应用。WSGI应用
将返回转换为 HTTP 响应的数据。

#.  浏览器或其他客户端发出 HTTP 请求。
#.  WSGI 服务器接收请求。
#.  WSGI 服务器将 HTTP 数据转换为 WSGI ``environ`` 字典。
#.  WSGI服务器使用 ``environ`` 调用 WSGI 应用程序。
#.  Flask ,即 WSGI 应用程序，执行其所有内部处理来路由请求到视图函数，
    处理错误等。
#.  Flask 将视图函数返回转换为 WSGI 响应数据，并将其传递给 WSGI 服务
    器。
#.  WSGI 服务器创建并发送 HTTP 响应。
#.  客户端接收 HTTP 响应。


中间件
~~~~~~~~~~

上述 WSGI 应用是以某种方式运行的可调用对象。中间件是一个 WSGI 应用程
序，它包装了另一个 WSGI 应用程序，它类似于 Python 装饰器。最外层的中
间件将由服务器调用。它可以修改传递给它的数据，然后调用被它包装 WSGI
应用程序（或进一步的中间件），以此类推。它可以获取该调用的返回值并进
一步修改它。

从 WSGI 服务器的角度来看，只有一个直接调用的 WSGI 应用程序。通常，
Flask 是中间件链末端的“真正”应用程序。但即使是 Flask 也可以调用进一
步的 WSGI 应用程序，尽管这是一个高级、不常见的用例。

一个常见的与 Flask 一起使用中间件是 Werkzeug 的
:class:`~werkzeug.middleware.proxy_fix.ProxyFix` ，它会修改请求，就像
直接来自客户端一样，即使它在途中通过 HTTP 代理。还有其他中间件可以提
供静态文件、身份验证等。


如何处理请求
------------------------

对我们来说，上述步骤中有趣的部分是当 Flask 被 WSGI 服务器（或中间件）
调用时。
在这个点上，它将做很多事情来处理请求和
生成响应。最基本的，它将 URL 匹配并调用到一个视图函数，并将返回值传递
回服务器。但还有更多可用于自定义其行为的部份。

#.  WSGI 服务器调用 Flask 对象，该对象调用 :meth:`.Flask.wsgi_app` 。
#.  一个 :class:`.RequestContext` 对象被创建，将 WSGI ``environ`` 字
    典转换为一个 :class:`.Request` 对象。它还创建一个
    :class:`AppContext` 对象。
#.  :doc:`app context <appcontext>` 被推送，这使得
    :data:`.current_app` 和 :data:`.g` 可用。
#.  发送 :data:`.appcontext_pushed` 信号。
#.  :doc:`request context <reqcontext>` 被推送，这使得
    :attr:`.request` 和 :class:`.session` 可用。
#.  会话被打开，使用应用程序的 :attr:`~.Flask.session_interface` ，一
    个 :class:`.SessionInterface` 实例，载入所有现存的会话数据。
#.  将 URL 与在应用设置期间使用 :meth:`~.Flask.route` 装饰器注册的
    URL 规则进行匹配。如果没有匹配项，则错误（通常是 404 、405 或重
    定向）被存储以供以后处理。
#.  发送 :data:`.request_started` 信号。
#.  调用所有 :meth:`~.Flask.url_value_preprocessor` 装饰的函数。
#.  调用所有 :meth:`~.Flask.before_request` 装饰的函数。如果有任何返
    回值，那么就立即被视为响应。
#.  如果 URL 在几个步骤前与路由不匹配，则现在会引发该错误。
#.  与匹配的 URL 关联的 :meth:`~.Flask.route` 装饰器视图函数
    被调用并返回要用作响应的值。
#.  如果到目前为止的任何步骤引发了异常，并且有一个
    :meth:`~.Flask.errorhandler` 装饰器函数与异常类或 HTTP 错误代码匹
    配，那么调用它处理错误并返回响应。
#.  不管是请求前函数、视图或错误处理程序，都会返回一个响应值，并被转
    换为 :class:`.Response` 对象。
#.  任何 :func:`~.after_this_request` 装饰的函数都会被调用，然后被清
    除。
#.  任何 :meth:`~.Flask.after_request` 装饰的函数都会被调用，它们可以
    修改响应对象。
#.  会话被保存，使用应用程序的:attr:`~.Flask.session_interface` 装饰
    函数来持久化任何已修改的会话数据。
#.  :data:`.request_finished` 信号被发送。
#.  如果到目前为止的任何步骤引发了一个异常，并且没有被错误处理函数处
    理,那么现在会被处理。 HTTP 异常会使用对应的状态代码作为响应，其他
    的异常被转换为一个通用的 500 响应。
    :data:`.got_request_exception` 信号被发送。
#.  响应对象的状态、头部信息和正文被返回给 WSGI 服务器。
#.  任何 :meth:`~.Flask.teardown_request` 装饰的函数都被调用。
#.  :data:`.request_tearing_down` 信号被发送。
#.  请求情境被弹出， :attr:`.request` 和 :class:`.session` 不再可用。
#.  任何 :meth:`~.Flask.teardown_appcontext` 的装饰函数都被调用。
#.  :data:`.appcontext_tearing_down` 信号被发送。
#.  应用情境被弹出， :data:`.current_app` 和 :data:`.g` 不再可用。
#.  :data:`.appcontext_popped` 信号被发送。

甚至还有比这更多的装饰器和定制点，但它们并不是每个请求生命周期都有的
部分。它们更多的是针对在请求过程中可能使用的某些东西，如模板、构建URL
或处理 JSON 数据。请参阅本文档的其余部分，以及 :doc:`api` 来进一步研
究。

