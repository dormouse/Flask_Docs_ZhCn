.. _sqlalchemy-pattern:

在 Flask 中使用 SQLAlchemy
==========================

许多人喜欢使用 `SQLAlchemy`_ 来访问数据库。建议在你的 Flask 应用中使用包来代替
模块，并把模型放入一个独立的模块中（参见 :ref:`larger-applications` ）。虽然这
不是必须的，但是很有用。

有四种 SQLAlchemy 的常用方法，下面一一道来：

Flask-SQLAlchemy 扩展
--------------------------

因为 SQLAlchemy 是一个常用的数据库抽象层，并且需要一定的配置才能使用，因此我们
为你做了一个处理 SQLAlchemy 的扩展。如果你需要快速的开始使用 SQLAlchemy ，那么
推荐你使用这个扩展。

你可以从 `PyPI <http://pypi.python.org/pypi/Flask-SQLAlchemy>`_ 下载
`Flask-SQLAlchemy`_ 。

.. _Flask-SQLAlchemy: http://packages.python.org/Flask-SQLAlchemy/


声明
-----------

SQLAlchemy 中的声明扩展是使用 SQLAlchemy 的最新方法，它允许你像 Django 一样，
在一个地方定义表和模型然后到处使用。除了以下内容，我建议你阅读 `声明`_ 的官方
文档。

以下是示例 `database.py` 模块::

    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.ext.declarative import declarative_base

    engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine)) 
    Base = declarative_base()
    Base.query = db_session.query_property()

    def init_db():
        # 在这里导入定义模型所需要的所有模块，这样它们就会正确的注册在
        # 元数据上。否则你就必须在调用 init_db() 之前导入它们。
        import yourapplication.models
        Base.metadata.create_all(bind=engine)

要定义模型的话，只要继承上面创建的 `Base` 类就可以了。你可能会奇怪这里为什么
不用理会线程（就像我们在 SQLite3 的例子中一样使用 :data:`~flask.g` 对象）。
原因是 SQLAlchemy 已经用 :class:`~sqlalchemy.orm.scoped_session` 为我们做好了此
类工作。

如果要在应用中以声明方式使用 SQLAlchemy ，那么只要把下列代码加入应用模块就可以
了。 Flask 会自动在请求结束时或者应用关闭时删除数据库会话::

    from yourapplication.database import db_session

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

以下是一个示例模型（放入 `models.py` 中）::

    from sqlalchemy import Column, Integer, String
    from yourapplication.database import Base

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)
        email = Column(String(120), unique=True)

        def __init__(self, name=None, email=None):
            self.name = name
            self.email = email

        def __repr__(self):
            return '<User %r>' % (self.name)

可以使用 `init_db` 函数来创建数据库：

>>> from yourapplication.database import init_db
>>> init_db()

在数据库中插入条目示例：

>>> from yourapplication.database import db_session
>>> from yourapplication.models import User
>>> u = User('admin', 'admin@localhost')
>>> db_session.add(u)
>>> db_session.commit()

查询很简单：

>>> User.query.all()
[<User u'admin'>]
>>> User.query.filter(User.name == 'admin').first()
<User u'admin'>

.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _declarative:
   http://www.sqlalchemy.org/docs/orm/extensions/declarative.html

人工对象关系映射
--------------------------------

人工对象关系映射相较于上面的声明方式有优点也有缺点。主要区别是人工对象关系映射
分别定义表和类并映射它们。这种方式更灵活，但是要多些代码。通常，这种方式与声明
方式一样运行，因此请确保把你的应用在包中分为多个模块。

示例 `database.py` 模块::

    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.orm import scoped_session, sessionmaker

    engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
    metadata = MetaData()
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine)) 
    def init_db():
        metadata.create_all(bind=engine)

就像声明方法一样，你需要在请求后或者应用环境解散后关闭会话。把以下代码放入你的
应用模块::

    from yourapplication.database import db_session

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

以下是一个示例表和模型（放入 `models.py` 中）::

    from sqlalchemy import Table, Column, Integer, String
    from sqlalchemy.orm import mapper
    from yourapplication.database import metadata, db_session

    class User(object):
        query = db_session.query_property()

        def __init__(self, name=None, email=None):
            self.name = name
            self.email = email

        def __repr__(self):
            return '<User %r>' % (self.name)

    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50), unique=True),
        Column('email', String(120), unique=True)
    )
    mapper(User, users)

查询和插入与声明方式的一样。


SQL 抽象层 
---------------------

如果你只需要使用数据库系统（和 SQL ）抽象层，那么基本上只要使用引擎::

    from sqlalchemy import create_engine, MetaData

    engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
    metadata = MetaData(bind=engine)

然后你要么像前文中一样在代码中声明表，要么自动载入它们::

    users = Table('users', metadata, autoload=True)

可以使用 `insert` 方法插入数据。为了使用事务，我们必须先得到一个连接：

>>> con = engine.connect()
>>> con.execute(users.insert(), name='admin', email='admin@localhost')

SQLAlchemy 会自动提交。

可以直接使用引擎或连接来查询数据库：

>>> users.select(users.c.id == 1).execute().first()
(1, u'admin', u'admin@localhost')

查询结果也是类字典元组：

>>> r = users.select(users.c.id == 1).execute().first()
>>> r['name']
u'admin'

你也可以把 SQL 语句作为字符串传递给
:meth:`~sqlalchemy.engine.base.Connection.execute` 方法：

>>> engine.execute('select * from users where id = :1', [1]).first()
(1, u'admin', u'admin@localhost')

关于 SQLAlchemy 的更多信息请移步其 `官方网站 <http://sqlalchemy.org/>`_ 。
