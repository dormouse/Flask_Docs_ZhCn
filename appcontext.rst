.. _app-context:

应用环境
=======================

.. versionadded:: 0.9

Flask 的设计思路之一是代码有两种不同的运行“状态”。一种是“安装”状态，从
:class:`Flask` 对象被实例化后开始，到第一个请求到来之前。在这种状态下，以下规则
成立：

-   可以安全地修改应用对象。
-   还没有请求需要处理。
-   没有应用对象的引用，因此无法修改应用对象。

相反，在请求处理时，以下规则成立：

-   当请求活动时，本地环境对象 （ :data:`flask.request` 或其他对象）指向当前
    请求。
-   这些本地环境对象可以任意修改。

除了上述两种状态之外，还有位于两者之间的第三种状态。这种状态下，你正在处理应用，
但是没有活动的请求。就类似于，你座在 Python 交互终端前，与应用或一个命令行程序
互动。

应用环境是 :data:`~flask.current_app` 本地环境的源动力。

应用环境的作用
----------------------------------

应用环境存在的主要原因是，以前过多的功能依赖于请求环境，缺乏更好的处理方案。
Flask 的一个重要设计原则是可以在同一个 Pyhton 进程中运行多个应用。

那么，代码如何找到“正确”的应用呢？以前我们推荐显式地传递应用，但是有可能会
引发库与库之间的干扰。

问题的解决方法是使用 :data:`~flask.current_app` 代理。
:data:`~flask.current_app` 是绑定到当前请求的应用的引用。但是没有请求的情况下
使用请求环境是一件奢侈在事情，于是就引入了应用环境。

创建一个应用环境
-------------------------------

创建应用环境有两种方法。一种是隐式的：当一个请求环境被创建时，如果有需要就会
相应创建一个应用环境。因此，你可以忽略应用环境的存在，除非你要使用它。

另一种是显式的，使用 :meth:`~flask.Flask.app_context` 方法::

    from flask import Flask, current_app

    app = Flask(__name__)
    with app.app_context():
        # 在本代码块中， current_app 指向应用。
        print current_app.name

在 ``SERVER_NAME`` 被设置的情况下，应用环境还被 :func:`~flask.url_for` 函数
使用。这样可以让你在没有请求的情况下生成 URL 。

环境的作用域
-----------------------

应用环境按需创建和消灭，它从来不在线程之间移动，也不被不同请求共享。因此，它是
一个存放数据库连接信息和其他信息的好地方。内部的栈对象被称为
:data:`flask._app_ctx_stack` 。扩展可以在栈的最顶端自由储存信息，前提是使用唯一
的名称，而 :data:`flask.g` 对象是留给用户使用的。 

更多信息参见 :ref:`extension-dev` 。

环境的用法
-------------

环境的典型用途是缓存一个请求需要预备或使用的资源，例如一个数据库连接。因为环境
是一个 Flask 的应用和扩展共享的地方，所以储存的资源必须使用独一无二的名称。

最常见的用法是把资源管理分为以下两个部分：

1.  在环境中缓存一个隐式的资源。
2.  资源释放后的环境解散。

通常会有一个形如 ``get_X()`` 函数，这个函数的用途是当资源 ``X`` 存在时就返回
这个资源，否则就创建这个资源。还会有一个 ``teardown_X()`` 函数用作解散句柄。

这是一个连接数据库的例子::

    import sqlite3
    from flask import g

    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = connect_to_database()
        return db

    @app.teardown_appcontext
    def teardown_db(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

第一次调用 ``get_db()`` 时，连接将会被建立。建立的过程中隐式地使用了一个
:class:`~werkzeug.local.LocalProxy` 类::

    from werkzeug.local import LocalProxy
    db = LocalProxy(get_db)

这样，用户就可以通过 ``get_db()`` 来直接访问 ``db`` 了。
