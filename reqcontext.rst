.. currentmodule:: flask

.. _request-context:

请求情境
===================

请求情境在请求期间跟踪请求级数据。不是将请求对象传递给请求期间运行的每个函
数，而是访问 :data:`request` 和 :data:`session` 代理。

这类似于 :doc:`/appcontext` ，它跟踪独立于请求的应用级数据。推送请求情境时
会推送相应的应用情境。

情境的用途
----------------------

当 :class:`Flask` 应用处理请求时，它会根据从 WSGI 服务器收到的环境创建一个
:class:`Request` 对象。因为 *工作者* （取决于服务器的线程，进程或协程）一
次只能处理一个请求，所以在该请求期间请求数据可被认为是该工作者的全局数据。
Flask 对此使用术语 *本地情境* 。

处理请求时， Flask 自动 *推送* 请求情境。在请求期间运行的视图函数，错误处
理器和其他函数将有权访问 :data:`request` 代理，该请求代理指向当前请求的请
求对象。


情境的生命周期
-----------------------

当 Flask 应用开始处理请求时，它会推送请求情境，这也会推送
:doc:`/appcontext` 。当请求结束时，它会弹出请求情境，然后弹出应用程序情境。

情境对于每个线程（或其他工作者类型）是唯一的。 :data:`request` 不能传递给
另一个线程，另一个线程将拥有不同的情境堆栈，并且不会知道父线程指向的请求。

本地情境在 Werkzeug 中实现。有关内部如何工作的更多信息，请参阅
:doc:`werkzeug:local` 。


手动推送情境
-----------------------

如果尝试在请求情境之外访问 :data:`request` 或任何使用它的东西，那么会收到
这个错误消息：

.. code-block:: pytb

    RuntimeError: Working outside of request context.

    这通常表示您试图使用功能需要一个活动的 HTTP 请求。
    有关如何避免此问题的信息，请参阅测试文档

通常只有在测试代码期望活动请求时才会发生这种情况。一种选择是使用
:meth:`测试客户端 <Flask.test_client>` 来模拟完整的请求。或者，可以在
``with`` 块中使用 :meth:`~Flask.test_request_context` ，块中运行的所有内容
都可以访问请求，并填充测试数据。::

    def generate_report(year):
        format = request.args.get('format')
        ...

    with app.test_request_context(
            '/make_report/2017', data={'format': 'short'}):
        generate_report()

如果在你的代码中的其他地方看到与测试无关的错误，则说明可能应该将该代码移到
视图函数中。

有关如何从交互式 Python shell 使用请求情境的信息，请参阅 :doc:`/shell` 。


情境如何工作
---------------------

处理每个请求时都会调用 :meth:`Flask.wsgi_app` 方法。它在请求期间管理情境。
在内部，请求和应用程序情境实质是 :data:`_request_ctx_stack` 和
:data:`_app_ctx_stack` 堆栈。当情境被压入堆栈时，依赖它们的代理可用并指向
堆栈顶部情境中的信息。

当请求开始时，将创建并推送 :class:`~ctx.RequestContext` ，如果该应用程序的
情境尚不是顶级情境，则该请求会首先创建并推送 :class:`~ctx.AppContext` 。在
推送这些情境时， :data:`current_app` 、 :data:`g` 、 :data:`request` 和
:data:`session` 代理可用于处理请求的原始线程。

由于情境是堆栈，因此在请求期间可能会压入其他情境导致代理变更。虽然这不是一
种常见模式，但它可以在高级应用使用。比如，执行内部重定向或将不同应用程序链
接在一起。

在分派请求并生成和发送响应之后，会弹出请求情境，然后弹出应用情境。在紧临弹
出之前，会执行 :meth:`~Flask.teardown_request` 和
:meth:`~Flask.teardown_appcontext` 函数。即使在调度期间发生未处理的异常，
也会执行这些函数。


.. _callbacks-and-errors:

回调和错误
--------------------

Flask 会在多个阶段调度请求，这会影响请求，响应以及如何处理错误。情境在所有
这些阶段都处于活动状态。

:class:`Blueprint` 可以为该蓝图的事件添加处理器，处理器会在蓝图与请求路由
匹配的情况下运行。

#.  在每次请求之前， :meth:`~Flask.before_request` 函数都会被调用。如果其
    中一个函数返回了一个值，则其他函数将被跳过。返回值被视为响应，并且视图
    函数不会被调用。

#.  如果 :meth:`~Flask.before_request` 函数没有返回响应，则调用匹配路由的
    视图函数并返回响应。

#.  视图的返回值被转换为实际的响应对象并传递给 :meth:`~Flask.after_request`
    函数。每个函数都返回一个修改过的或新的响应对象。

#.  返回响应后，将弹出情境，该情境调用 :meth:`~Flask.teardown_request` 和
    :meth:`~Flask.teardown_appcontext` 函数。即使在上面任何一处引发了未处
    理的异常，也会调用这些函数。

如果在拆卸函数之前引发了异常， Flask 会尝试将它与
:meth:`~Flask.errorhandler` 函数进行匹配，以处理异常并返回响应。如果找不到
错误处理器，或者处理器本身引发异常， Flask 将返回一个通用的
``500 Internal Server Error`` 响应。拆卸函数仍然被调用，并传递异常对象。

如果开启了调试模式，则未处理的异常不会转换为 ``500`` 响应，而是会传播到
WSGI 服务器。这允许开发服务器向交互式调试器提供回溯。


拆解回调
~~~~~~~~~~~~~~~~~~

拆除回调与请求派发无关，而在情境弹出时由情境调用。即使在调度过程中出现未处
理的异常，以及手动推送的情境，也会调用这些函数。这意味着不能保证请求调度的
任何其他部分都先运行。 一定要以不依赖其他回调的方式编写这些函数，并且不会
失败。

在测试期间，推迟请求结束后弹出情境会很有用，这样可以在测试函数中访问它们的
数据。在 ``with`` 块中使用 :meth:`~Flask.test_client` 来保存情境，直到
with 块结束。

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

    with app.test_client():
        client.get('/')
        # the contexts are not popped even though the request ended
        print(request.path)

    # the contexts are popped and teardown functions are called after
    # the client with block exists


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


出错情境保存
-----------------------------

在请求结束时，会弹出请求情境，并且与其关联的所有数据都将被销毁。如果在开发
过程中发生错误，延迟销毁数据以进行调试是有用的。

当开发服务器以开发模式运行时（ ``FLASK_ENV`` 环境变量设置为
``'development'`` ），错误和数据将被保留并显示在交互式调试器中。

该行为可以通过 :data:`PRESERVE_CONTEXT_ON_EXCEPTION` 配置进行控制。如前文
所述，它在开发环境中默认为 ``True`` 。

不要在生产环境中启用 :data:`PRESERVE_CONTEXT_ON_EXCEPTION` ，因为它会导致
应用在发生异常时泄漏内存。


.. _notes-on-proxies:

关于代理的说明
----------------

Flask 提供的一些对象是其他对象的代理。每个工作线程都能以相同的方式
访问代理，但是在后台每个工作线程绑定了唯一对象。

多数情况下，你不必关心这个问题。但是也有例外，在下列情况有下，知道对象是一
个代理 对象是有好处的：

-   代理对象不能将它们的类型伪装为实际的对象类型。如果要执行实例检查，则必
    须检查被代理的原始对象。
-   对象引用非常重要的情况，例如发送 :ref:`signals` 或将数据传递给后台线程。

如果您需要访问被代理的源对象，请使用
:meth:`~werkzeug.local.LocalProxy._get_current_object` 方法::

    app = current_app._get_current_object()
    my_signal.send(app)
