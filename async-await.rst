.. _async_await:

使用 ``async`` 和 ``await``
============================

.. versionadded:: 2.0

如果在安装 Flask 时使用了额外的 ``async`` （ 即用
``pip install flask[async]`` 命令安装），那么路由、出错处理器、请求前、请
求后和拆卸函数都可以是协程函数。这样，视图可以使用 ``async def`` 定义，并
使用 ``await`` 。 ``pip install flask[async]`` 命令会用到
``contextvars.ContextVar`` ， 因此需要 Python 3.7 以上版本。

.. code-block:: python

    @app.route("/get-data")
    async def get_data():
        data = await async_db_query(...)
        return jsonify(data)

可插入基类视图也支持以协程方式运行的处理器。这同样适用于
:meth:`~flask.views.View.dispatch_request` 方法，该方法从
:class:`flask.views.View` 类继承而来。 所有视图中的 HTTP 方法处理器
从 :class:`flask.views.MethodView` 类继承而来一样。

.. admonition:: 在 Windows 的 Python 3.8 下使用 ``async`` 

    Python 3.8 的 Windows 版异步处理是有问题的。如果您遇到类似
    ``ValueError: set_wakeup_fd only works in main thread`` 的问题，请升级
    到 Python 3.9 。


性能
-----------

异步函数需要一个事件循环来运行。 Flask，作为 WSGI 应用，使用一个 worker 来
处理一个请求 / 响应周期。当请求进入异步视图时， Flask 会在一个线程中启动一
个事件循环，在其中运行视图函数，然后返回结果。

即使对于异步视图，每个请求仍然会绑定一个 worker 。好处是您可以在一个视图内
运行异步代码，例如多个并发数据库查询，对外部 API 的 HTTP 请求，等等。但是，
您的应用程序可以处理的请求并发数量将保持不变。

**异步本质上并不比同步快。** 在执行并发 IO 绑定任务时， 异步是有益的。但是
对于 CPU 密集型任务，则未必有用，因此传统的 Flask 视图仍然适用于大多数用例。
Flask 异步支持的引入，带来本地化编写和使用异步代码的可能性。


后台任务
----------------

异步函数将在事件循环中运行，当函数运行完成，事件循环就会停止。这意味着当
异步功能完成时，任何额外的，尚未完成的衍生任务将被取消。因此你不能衍生产生
后台任务，例如不能通过 ``asyncio.create_task`` 衍生后台任务。

如果您希望使用后台任务，那么最好使用任务队列触发后台工作，而不是在视图函数
中衍生任务。考虑到这一点，您可以通过 ASGI 服务器和 asgiref WsgiToAsgi 适配
器（详见 :ref:`asgi` ）来衍生异步任务。这样，任务就可以持续运行下去。 


何时使用 Quart 代替
-------------------------

因为 Flask 的实现方式的原因， Flask 的异步支持性能不如异步优先框架。如果您
的代码主要是基于异步的，那么可以考虑 `Quart`_ 。 Quart 是一个 Flask 的重新
实现，但是基于 `ASGI`_ 标准而不是WSGI。这允许它处理大量并发请求、长时间运行
的请求和 websocket ，而不需要多个工作进程或线程。

同时，早已可以使用 Gevent 或 Eventlet 运行 Flask ，以获得异步请求处理的诸多
好处。 这些库修补低级 Python 函数来实现这一点，而 ``async``/ ``await`` 和
ASGI 则使用标准的现代 Python 功能。决定应该使用 Flask 还是 Quart 或其他东西
最终还是取决于项目的具体需求。 

.. _Quart: https://gitlab.com/pgjones/quart
.. _ASGI: https://asgi.readthedocs.io/en/latest/


扩展
----------

在 Flask 的提供异步支持之前的 Flask 扩展不要指望异步视图支持。如果扩展提供
增加功能的装饰器，那么有可能是无法用于异步视图的，因为不会等待函数或者可等
待。提供的其他函数也不会可等待，并且如果在异步视图中调用，可能会阻塞。

扩展作者可以利用 :meth:`flask.Flask.ensure_sync` 方法支持异步功能。
例如，在调用装饰函数前提供一个视力函数增加 ``ensure_sync`` ，

.. code-block:: python

    def extension(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ...  # Extension logic
            return current_app.ensure_sync(func)(*args, **kwargs)

        return wrapper

在使用扩展前，请检查其修改记录，以确认是否支持异步或者向作者发出支持异步
功能需求。


其他事件循环
-----------------

此时， Flask 只支持 :mod:`asyncio` 。重载 :meth:`flask.Flask.ensure_sync`
可以改变异步函数的包裹方式，这样就可以使用其他不同的库了。
