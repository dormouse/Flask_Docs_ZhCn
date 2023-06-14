.. currentmodule:: flask

请求情境
===================

请求情境在请求期间跟踪请求级数据。不是将请求对象传递给请求期间运行的
每个函数，而是访问 :data:`request` 和 :data:`session` 代理。

这类似于 :doc:`/appcontext` ，它跟踪独立于请求的应用级数据。推送请求
情境时会推送相应的应用情境。

情境的用途
----------------------

当 :class:`Flask` 应用处理请求时，它会根据从 WSGI 服务器收到的环境创
建一个 :class:`Request` 对象。因为 *工作者* （取决于服务器的线程，进
程或协程）一次只能处理一个请求，所以在该请求期间请求数据可被认为是该
工作者的全局数据。 Flask 对此使用术语 *本地情境* 。

处理请求时， Flask 自动 *推送* 请求情境。在请求期间运行的视图函数，错
误处理器和其他函数将有权访问 :data:`request` 代理，该请求代理指向当前
请求的请求对象。


情境的生命周期
-----------------------

当 Flask 应用开始处理请求时，它会推送请求情境，这也会推送
:doc:`app context </appcontext>` 。当请求结束时，它会弹出请求情境，然
后弹出应用程序情境。

情境对于每个线程（或其他工作者类型）是唯一的。 :data:`request` 不能传
递给另一个线程，另一个线程将拥有不同的情境堆栈，并且不会知道父线程指
向的请求。

本地情境使用 Python 的 :mod:`contextvars` 和 Werkzeug 的
:class:`~werkzeug.local.LocalProxy` 实现。 Python 自动管理情境变量的
生命周期，并且本地代理包装了低级接口，以便于数据使用。


手动推送情境
-----------------------

如果尝试在请求情境之外访问 :data:`request` 或任何使用它的东西，那么会
收到这个错误消息：

.. code-block:: pytb

    RuntimeError: Working outside of request context.

    这通常表示您试图使用功能需要一个活动的 HTTP 请求。
    有关如何避免此问题的信息，请参阅测试文档

通常只有在测试代码期望活动请求时才会发生这种情况。一种选择是使用
:meth:`测试客户端 <Flask.test_client>` 来模拟完整的请求。或者，可以在
``with`` 块中使用 :meth:`~Flask.test_request_context` ，块中运行的所
有内容都可以访问请求，并填充测试数据。::

    def generate_report(year):
        format = request.args.get("format")
        ...

    with app.test_request_context(
        "/make_report/2017", query_string={"format": "short"}
    ):
        generate_report()

如果在你的代码中的其他地方看到与测试无关的错误，则说明可能应该将该代
码移到视图函数中。

有关如何从交互式 Python shell 使用请求情境的信息，请参阅
:doc:`/shell` 。


情境如何工作
---------------------

处理每个请求时都会调用 :meth:`Flask.wsgi_app` 方法。它在请求期间管理
情境。在内部，请求和应用情境的工作方式类似于堆栈。当情境被压入堆栈时，
依赖它们的代理是可用的，并指向堆栈顶部项目的信息。

当请求开始时，将创建并推送 :class:`~ctx.RequestContext` ，如果该应用
程序的情境尚不是顶级情境，则该请求会首先创建并推送
:class:`~ctx.AppContext` 。在推送这些情境时， :data:`current_app` 、
:data:`g` 、 :data:`request` 和 :data:`session` 代理可用于处理请求的
原始线程。

在请求期间其它情境可能会被压入堆栈，导致代理变更。虽然这不是一种常见
模式，但它可以用于高级应用。比如，执行内部重定向或将不同应用程序链接
在一起。

在分派请求并生成和发送响应之后，会弹出请求情境，然后弹出应用情境。在
紧临弹出之前，会执行 :meth:`~Flask.teardown_request` 和
:meth:`~Flask.teardown_appcontext` 函数。即使在调度期间发生未处理的异
常，也会执行这些函数。


.. _callbacks-and-errors:

回调和错误
--------------------

Flask 会在多个阶段调度请求，这会影响请求，响应以及如何处理错误。情境
在所有这些阶段都处于活动状态。

:class:`Blueprint` 可以为该蓝图的事件添加处理器，处理器会在蓝图与请求
路由匹配的情况下运行。

#.  在每次请求之前， :meth:`~Flask.before_request` 函数都会被调用。如
    果其中一个函数返回了一个值，则其他函数将被跳过。返回值被视为响应，
    并且视图函数不会被调用。

#.  如果 :meth:`~Flask.before_request` 函数没有返回响应，则调用匹配路
    由的视图函数并返回响应。

#.  视图的返回值被转换为实际的响应对象并传递给
    :meth:`~Flask.after_request` 函数。每个函数都返回一个修改过的或新
    的响应对象。

#.  返回响应后，将弹出情境，该情境调用 :meth:`~Flask.teardown_request`
    和 :meth:`~Flask.teardown_appcontext` 函数。即使在上面任何一处引
    发了未处理的异常，也会调用这些函数。

如果在拆卸函数之前引发了异常， Flask 会尝试将它与
:meth:`~Flask.errorhandler` 函数进行匹配，以处理异常并返回响应。如果
找不到错误处理器，或者处理器本身引发异常， Flask 将返回一个通用的
``500 Internal Server Error`` 响应。拆卸函数仍然被调用，并传递异常对
象。

如果开启了调试模式，则未处理的异常不会转换为 ``500`` 响应，而是会传播
到 WSGI 服务器。这允许开发服务器向交互式调试器提供回溯。


拆解回调
~~~~~~~~~~~~~~~~~~

拆除回调与请求派发无关，而在情境弹出时由情境调用。即使在调度过程中出
现未处理的异常，以及手动推送的情境，也会调用这些函数。这意味着不能保
证请求调度的任何其他部分都先运行。 一定要以不依赖其他回调的方式编写这
些函数，并且不会失败。

在测试期间，推迟请求结束后弹出情境会很有用，这样可以在测试函数中访问
它们的数据。在 ``with`` 块中使用 :meth:`~Flask.test_client` 来保存情
境，直到 with 块结束。

.. code-block:: python

    from flask import Flask, request

    app = Flask(__name__)

    @app.route('/')
    def hello():
        print('during view')
        return 'Hello, World!'

    @app.teardown_request
    def show_teardown(exception):
        print('after with block')

    with app.test_request_context():
        print('during with block')

    # teardown functions are called after the context with block exits

    with app.test_client() as client:
        client.get('/')
        # the contexts are not popped even though the request ended
        print(request.path)

    # the contexts are popped and teardown functions are called after
    # the client with block exits

信号
~~~~~~~

如果 :data:`~signals.signals_available` 为真，那么会发送以下信号：

#.  :data:`request_started` 发送于
    :meth:`~Flask.before_request` 函数被调用之前。

#.  :data:`request_finished` 发送于
    :meth:`~Flask.after_request` 函数被调用之后。

#.  :data:`got_request_exception` 发送于异常开始处理的时候
    但早于 an :meth:`~Flask.errorhandler` 被找到或者调用的时候。

#.  :data:`request_tearing_down` 发送于
    :meth:`~Flask.teardown_request` 函数被调用之后。


.. _notes-on-proxies:

关于代理的说明
----------------

Flask 提供的一些对象是其他对象的代理。每个工作线程都能以相同的方式访
问代理，但是在后台每个工作线程绑定了唯一对象。

多数情况下，你不必关心这个问题。但是也有例外，在下列情况下，知道对象
是一个代理对象是有好处的：

-   代理对象不能将它们的类型伪装为实际的对象类型。如果要执行实例检查，
    则必须检查被代理的原始对象。
-   代理对象引用在某些情况下是必需的，例如发送 :doc:`signals` 或将数
    据传递给后台线程。

如果您需要访问被代理的源对象，请使用
:meth:`~werkzeug.local.LocalProxy._get_current_object` 方法::

    app = current_app._get_current_object()
    my_signal.send(app)
