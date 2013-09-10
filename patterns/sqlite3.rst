.. _sqlite3:

在 Flask 中使用 SQLite 3
=========================

在 Flask 中，你可以方便的按需打开数据库连接，并且在环境解散时关闭这个连接（
通常是请求结束的时候）。

以下是一个在 Flask 中使用 SQLite 3 的例子::

    import sqlite3
    from flask import g

    DATABASE = '/path/to/database.db'

    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = connect_to_database()
        return db

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()


为了使用数据库，所有应用都必须准备好一个处于激活状态的环境。使用 ``get_db``
函数可以得到数据库连接。当环境解散时，数据库连接会被切断。

注意：如果你使用的是 Flask 0.9 或者以前的版本，那么你必须使用
``flask._app_ctx_stack.top`` ，而不是 ``g`` 。因为 :data:`flask.g` 对象是绑定到
请求的，而不是应用环境。

示例::

    @app.route('/')
    def index():
        cur = get_db().cursor()
        ...

.. note::

   请记住，解散请求和应用环境的函数是一定会被执行的。即使请求前处理器执行失败或
   根本没有执行，解散函数也会被执行。因此，我们必须保证在关闭数据库连接之前
   数据库连接是存在的。

按需连接
-----------------

上述方式（在第一次使用时连接数据库）的优点是只有在真正需要时才打开数据库连接。
如果你想要在一个请求环境之外使用数据库连接，那么你可以手动在 Python 解释器打开
应用环境::

    with app.app_context():
        # now you can use get_db()

.. _easy-querying:

简化查询
-------------

现在，在每个请求处理函数中可以通过访问 `g.db` 来得到当前打开的数据库连接。为了
简化 SQLite 的使用，这里有一个有用的行工厂函数。该函数会转换每次从数据库返回的
结果。例如，为了得到字典类型而不是元组类型的返回结果，可以这样::

    def make_dicts(cursor, row):
        return dict((cur.description[idx][0], value)
                    for idx, value in enumerate(row))

    db.row_factory = make_dicts

或者更简单的::

    db.row_factory = sqlite3.Row

此外，把得到游标，执行查询和获得结果组合成一个查询函数不失为一个好办法::
    
    def query_db(query, args=(), one=False):
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

上述的方便的小函数与行工厂联合使用与使用原始的数据库游标和连接相比要方便多了。

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

    def init_db():
        with app.app_context():
            db = get_db()
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()

可以使用上述函数在 Python 解释器中创建数据库：

>>> from yourapplication import init_db
>>> init_db()
