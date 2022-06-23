使用 SQLite 3
=========================

在 Flask 中可以方便地按需打开数据库连接，并在情境结束时（通常是请求结
束时）关闭。

下面是一个如何在 Flask 中使用 SQLite 3 的例子::

    import sqlite3
    from flask import g

    DATABASE = '/path/to/database.db'

    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
        return db

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

现在，要使用数据库，应用必须要么有一个活动的应用情境（在存在请求的情
况下，总会有一个），要么创建一个应用情境。在这种情况下， ``get_db``
函数可以用于获得当前数据库连接。一旦情境灭失，数据库连接就会中断。

注意：如果使用 Flask 0.9 版或者更早版本，需要使用
``flask._app_ctx_stack.top`` 代替 ``g`` ，因为 :data:`flask.g`
对象绑定到请求而不是应用情境。

示例::

    @app.route('/')
    def index():
        cur = get_db().cursor()
        ...


.. note::

   请牢记，拆卸请求（ teardown request ）和应用情境（ appcontext ）
   函数总是会执行，即使一个请求前处理器（ before-request handler ）
   失败或者没有执行也是如此。因此，我们在关闭数据库前应当确认数据库已
   经存在。

按需连接
-----------------

在第一次使用时连接的好处是只会在真正需要的时候打开连接。如果需要在一
个请求情境之外使用这个代码，可以在 Python shell 中手动打开应用情境后
使用::

    with app.app_context():
        # now you can use get_db()


简化查询
-------------

现在每个请求处理函数中可以通过 `get_db()` 来得到当前打开的数据库连接。
一个行工厂（ row factory  ）可以简化 SQLite 的使用，它会在每个结果返
回的时候对返回结果进行加工。例如，为了得到字典型而不是元组型的结果，
以下内容可以插入到前文的 ``get_db`` 函数中:: 

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                    for idx, value in enumerate(row))

    db.row_factory = make_dicts

这样， sqlite3 模块就会返回方便处理的字典类型的结果了。更进一步，我们
可以把以下内容放到 ``get_db`` 中::

    db.row_factory = sqlite3.Row

这样查询会返回 Row 对象，而不是字典。 Row 对象是 ``namedtuple`` ，因
此既可以通过索引访问也以通过键访问。例如，假设我们有一个
``sqlite3.Row`` 名为 ``r`` ，记录包含 ``id`` 、 ``FirstName`` 、
``LastName`` 和 ``MiddleInitial`` 字段::

    >>> # 基于键的名称取值
    >>> r['FirstName']
    John
    >>> # 或者基于索引取值
    >>> r[1]
    John
    # Row 对象是可迭代的：
    >>> for value in r:
    ...     print(value)
    1
    John
    Doe
    M

另外，提供一个函数，用于获得游标、执行查询和获取结果是一个好主意::

    def query_db(query, args=(), one=False):
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

这个方便称手的小函数与行工厂联合使用比使用原始的数据库游标和连接对象
要方便多了。

使用该函数示例::

    for user in query_db('select * from users'):
        print(user['username'], 'has the id', user['user_id'])

只需要得到单一结果的用法::

    user = query_db('select * from users where username = ?',
                    [the_username], one=True)
    if user is None:
        print('No such user')
     else:
        print(the_username, 'has the id', user['user_id'])

如果要给 SQL 语句传递参数，请在语句中使用问号来代替参数，并把参数放在
一个列表中一起传递。不要用字符串格式化的方式直接把参数加入 SQL 语句中，
这样会给应用带来
`SQL 注入 <https://en.wikipedia.org/wiki/SQL_injection>`_ 的风险。


初始化模式
---------------

关系数据库是需要模式的，因此一个应用常常需要一个 `schema.sql` 文件来
创建数据库。因此我们需要使用一个函数，用来基于模式创建数据库。下面这
个函数可以完成这个任务::

    def init_db():
        with app.app_context():
            db = get_db()
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()

接下来可以在 Python shell 中创建数据库：

>>> from yourapplication import init_db
>>> init_db()
