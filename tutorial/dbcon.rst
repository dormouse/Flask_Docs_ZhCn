.. _tutorial-dbcon:

步骤 4 ：请求数据库连接
------------------------------------

现在我们已经学会如何打开并在代码中使用数据库连接，但是如何优雅地在请求时使用它
呢？我们会在每一个函数中用到数据库连接，因此有必要在请求之前初始化连接，并在
请求之后关闭连接。

Flask 中可以使用 :meth:`~flask.Flask.before_request` 、
:meth:`~flask.Flask.after_request` 和 :meth:`~flask.Flask.teardown_request`
装饰器达到这个目的::

    @app.before_request
    def before_request():
        g.db = connect_db()

    @app.teardown_request
    def teardown_request(exception):
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()
        g.db.close()

使用 :meth:`~flask.Flask.before_request` 装饰的函数会在请求之前调用，且不传递
参数。使用 :meth:`~flask.Flask.after_request` 装饰的函数会在请求之后调用，且
传递发送给客户端响应对象。它们必须传递响应对象，所以在出错的情况下就不会执行。
因此我们就要用到 :meth:`~flask.Flask.teardown_request` 装饰器了。这个装饰器下
的函数在响应对象构建后被调用。它们不允许修改请求，并且它们的返回值被忽略。如果
请求过程中出错，那么这个错误会传递给每个函数；否则传递 `None` 。

我们把数据库连接保存在 Flask 提供的特殊的 :data:`~flask.g` 对象中。这个对象与
每一个请求是一一对应的，并且只在函数内部有效。不要在其它对象中储存类似信息，
因为在多线程环境下无效。这个特殊的 :data:`~flask.g` 对象会在后台神奇的工作，保
证系统正常运行。

若想更好地处理这种资源，请参阅 :ref:`sqlite3` 。

下面请阅读 :ref:`tutorial-views`.

.. hint:: 我该把这些代码放在哪里？

   如果你按教程一步一步读下来，那么可能会疑惑应该把这个步骤和以后的代码放在哪
   里？比较有条理的做法是把这些模块级别的函数放在一起，并把新的
   ``before_request`` 和 ``teardown_request`` 函数放在前文的 ``init_db`` 函数
   下面（即按照教程的顺序放置）。

   如果你已经晕头转向了，那么你可以参考一下 `示例源代码`_ 。在 Flask 中，你可以
   把应用的所有代码都放在同一个 Python 模块中。但是你没有必要这样做，尤其是当你
   的应用 :ref:`变大了 <larger-applications>` 的时候，更不应当这样。

.. _示例源代码:
   http://github.com/mitsuhiko/flask/tree/master/examples/flaskr/
