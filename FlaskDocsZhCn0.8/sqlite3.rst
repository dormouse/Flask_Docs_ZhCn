.. _sqlite3:

在 Flask 中使用 SQLite 3
=========================

在 Flask 中，通过使用特殊的 :class:`~flask.g` 对象可以使用
:meth:`~flask.Flask.before_request` 和 :meth:`~flask.Flask.teardown_request`
在请求开始前打开数据库连接，在请求结束后关闭连接。

以下是一个在 Flask 中使用 SQLite 3 的例子::

    import sqlite3
    from flask import g

    DATABASE = '/path/to/database.db'

    def connect_db():
        return sqlite3.connect(DATABASE)

    @app.before_request
    def before_request():
        g.db = connect_db()

    @app.teardown_request
    def teardown_request(exception):
        if hasattr(g, 'db'):
            g.db.close()

.. note::

   请记住，销毁函数是一定会被执行的。即使请求前处理器执行失败或根本没有执行，
   销毁函数也会被执行。因此，我们必须保证在关闭数据库连接之前数据库连接是存在
   的。

按需连接
-----------------

上述方式的缺点是只有在 Flask 执行了请求前处理器时才有效。如果你尝试在脚本或者
Python 解释器中使用数据库，那么你必须这样来执行数据库连接代码::

    with app.test_request_context():
        app.preprocess_request()
        # now you can use the g.db object

这样虽然不能排除对请求环境的依赖，但是可以按需连接数据库::

    def get_connection():
        db = getattr(g, '_db', None)
        if db is None:
            db = g._db = connect_db()
        return db

这样做的缺点是必须使用 ``db = get_connection()`` 来代替直接使用 ``g.db`` 。

.. _easy-querying:

简化查询
-------------

现在，在每个请求处理函数中可以通过访问 `g.db` 来得到当前打开的数据库连接。为了
简化 SQLite 的使用，这里有一个有用的辅助函数::

    def query_db(query, args=(), one=False):
        cur = g.db.execute(query, args)
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv

使用这个实用的小函数比直接使用原始指针和转接对象要舒服一点。

可以这样使用上述函数::

    for user in query_db('select * from users'):
        print user['username'], 'has the id', user['user_id']

只需要得到单一结果的用法::

    user = query_db('select * from users where username = ?',
                    [the_username], one=True)
    if user is None:
        print 'No such user'
    else:
        print the_username, 'has the id', user['user_id']

如果要给 SQL 语句传递参数，请在语句中使用问号来代替参数，并把参数放在一个列表中
一起传递。不要用字符串格式化的方式直接把参数加入 SQL 语句中，这样会给应用带来
`SQL 注入 <http://en.wikipedia.org/wiki/SQL_injection>`_ 的风险。

初始化模式
---------------

关系数据库是需要模式的，因此一个应用常常需要一个 `schema.sql` 文件来创建
数据库。因此我们需要使用一个函数来其于模式创建数据库。下面这个函数可以完成这个
任务::

    from contextlib import closing
    
    def init_db():
        with closing(connect_db()) as db:
            with app.open_resource('schema.sql') as f:
                db.cursor().executescript(f.read())
            db.commit()

可以使用上述函数在 Python 解释器中创建数据库：

>>> from yourapplication import init_db
>>> init_db()
