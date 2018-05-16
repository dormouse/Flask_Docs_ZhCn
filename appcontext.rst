.. currentmodule:: flask

.. _app-context:

应用情境
=======================

应用情境在请求， CLI 命令或其他活动期间跟踪应用级数据。不是将应用程序传递
给每个函数，而是代之以访问 :data:`current_app` 和 :data:`g` 代理。

这与 :doc:`/reqcontext` 类似，它在请求期间跟踪请求级数据。推送请求情境时会
推送相应的应用情境。

情境的目的
----------------------

:class:`Flask` 应用对象具有诸如 :attr:`~Flask.config` 之类的属性，这些属
性对于在视图和 :doc:`CLI commands </cli>` 中访问很有用。但是，在项目中的模
块内导入 ``app`` 实例容易导致循环导入问题。当使用
:doc:`应用程序工厂方案 </patterns/appfactories>` 或编写可重用的
:doc:`blueprints </blueprints>` 或 :doc:`extensions </extensions>` 时，根
本不会有应用程序实例导入。

Flask 通过 *应用情境* 解决了这个问题。不是直接引用一个 ``app`` ，而是使用
 :data:`current_app` 代理，该代理指向处理当前活动的应用。

处理请求时， Flask 自动 *推送* 应用情境。在请求期间运行的视图函数、错误处
理器和其他函数将有权访问 :data:`current_app` 。

运行使用 ``@app.cli.command()`` 注册到 :attr:`Flask.cli` 的 CLI 命令时，
Flask 还会自动推送应用情境。


情境的生命周期
-----------------------

应用情境根据需要创建和销毁。当 Flask 应用开始处理请求时，它会推送应用情境
和 :doc:`请求情境 </reqcontext>` 。当请求结束时，它会在请求情境中弹出，然
后在应用情境中弹出。通常，应用情境将具有与请求相同的生命周期。

请参阅 :doc:`/reqcontext` 以获取有关情境如何工作以及请求的完整生命周期的更
多信息。

手动推送情境
-----------------------

如果您尝试在应用情境之外访问 :data:`current_app` ，或其他任何使用它的东西，
则会看到以下错误消息：

.. code-block:: pytb

    RuntimeError: Working outside of application context.

    这通常意味着您试图使用功能需要以某种方式与当前的应用程序对象进行交互。
    要解决这个问题，请使用 app.app_context（）设置应用情境。

如果在配置应用时发现错误（例如初始化扩展时），那么可以手动推送上下文。因为
你可以直接访问 ``app`` 。在 ``with`` 块中使用 :meth:`~Flask.app_context` ，
块中运行的所有内容都可以访问 :data:`current_app` 。::

    def create_app():
        app = Flask(__name__)

        with app.app_context():
            init_db()

        return app

如果您在代码中的其他地方看到与配置应用无关的错误，则很可能表明应该将该代码
移到视图函数或 CLI 命令中。

存储数据
------------

应用情境是在请求或 CLI 命令期间存储公共数据的好地方。Flask 为此提供了
:data:`g 对象 <g>` 。它是一个简单的命名空间对象，与应用情境具有相同的生命
周期。

.. note::
    ``g`` 表示“全局”的意思，但是指的是数据在 *情境* 之中是全局的。 ``g``
    中的数据在情境结束后丢失，因此它不是在请求之间存储数据的恰当位置。使用
    :data:`session` 或数据库跨请求存储数据。

:data:`g` 的常见用法是在请求期间管理资源。

1.   ``get_X()`` 创建资源 ``X`` （如果它不存在），将其缓存为 ``g.X`` 。
2.   ``teardown_X()`` 关闭或以其他方式解除分配资源（如果存在）。它被注册为
     :meth:`~Flask.teardown_appcontext` 处理器。

例如，您可以使用以下方案管理数据库连接::

    from flask import g

    def get_db():
        if 'db' not in g:
            g.db = connect_to_database()

        return g.db

    @app.teardown_appcontext
    def teardown_db():
        db = g.pop('db', None)

        if db is not None:
            db.close()

在一个请求中，每次调用 ``get_db()`` 会返回同一个连接，并且会在请求结束时
自动关闭连接。

你可以使用 :class:`~werkzeug.local.LocalProxy` 基于 ``get_db()``
生成一个新的本地情境::

    from werkzeug.local import LocalProxy
    db = LocalProxy(get_db)

访问 ``db`` 就会内部调用 ``get_db`` ，与 :data:`current_app` 的工作方式相同。

----

如果你正在编写扩展， :data:`g` 应该保留给用户。你可以将内部数据存储在情境
本身中，但一定要使用足够唯一的名称。当前上下文使用
:data:`_app_ctx_stack.top <_app_ctx_stack>` 访问。 欲了解更多信息，请参阅
:doc:`extensiondev` 。

事件和信号
------------------

当应用情境被弹出时，应用将调用使用 :meth:`~Flask.teardown_appcontext`
注册的函数。

如果 :data:`~signals.signals_available` 为真，则发送以下信号：
:data:`appcontext_pushed` 、 :data:`appcontext_tearing_down` 和
:data:`appcontext_popped` 。
