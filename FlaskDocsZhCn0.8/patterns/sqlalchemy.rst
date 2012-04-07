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


Declarative
-----------

SQLAlchemy 中的 declarative 扩展是使用 SQLAlchemy 的最新方法，它允许你像
Django 一样，在一个地方定义表和模型然后到处使用。除了以下内容，我建议你阅读
`declarative`_ 的官方文档。

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
        # import all modules here that might define models so that
        # they will be registered properly on the metadata.  Otherwise
        # you will have to import them first before calling init_db()
        import yourapplication.models
        Base.metadata.create_all(bind=engine)

To define your models, just subclass the `Base` class that was created by
the code above.  If you are wondering why we don't have to care about
threads here (like we did in the SQLite3 example above with the
:data:`~flask.g` object): that's because SQLAlchemy does that for us
already with the :class:`~sqlalchemy.orm.scoped_session`.

To use SQLAlchemy in a declarative way with your application, you just
have to put the following code into your application module.  Flask will
automatically remove database sessions at the end of the request for you::

    from yourapplication.database import db_session

    @app.teardown_request
    def shutdown_session(exception=None):
        db_session.remove()

Here is an example model (put this into `models.py`, e.g.)::

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

To create the database you can use the `init_db` function:

>>> from yourapplication.database import init_db
>>> init_db()

You can insert entries into the database like this:

>>> from yourapplication.database import db_session
>>> from yourapplication.models import User
>>> u = User('admin', 'admin@localhost')
>>> db_session.add(u)
>>> db_session.commit()

Querying is simple as well:

>>> User.query.all()
[<User u'admin'>]
>>> User.query.filter(User.name == 'admin').first()
<User u'admin'>

.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _declarative:
   http://www.sqlalchemy.org/docs/orm/extensions/declarative.html

Manual Object Relational Mapping
--------------------------------

Manual object relational mapping has a few upsides and a few downsides
versus the declarative approach from above.  The main difference is that
you define tables and classes separately and map them together.  It's more
flexible but a little more to type.  In general it works like the
declarative approach, so make sure to also split up your application into
multiple modules in a package.

Here is an example `database.py` module for your application::

    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.orm import scoped_session, sessionmaker

    engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
    metadata = MetaData()
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine)) 
    def init_db():
        metadata.create_all(bind=engine)

As for the declarative approach you need to close the session after
each request.  Put this into your application module::

    from yourapplication.database import db_session

    @app.teardown_request
    def shutdown_session(exception=None):
        db_session.remove()

Here is an example table and model (put this into `models.py`)::

    from sqlalchemy import Table, Column, Integer, String
    from sqlalchemy.orm import mapper
    from yourapplication.database import metadata, db_session

    class User(object):
        query = db_session.query_property()

        def __init__(self, name=None, email=None):
            self.name = name
            self.email = email

        def __repr__(self):
            return '<User %r>' % (self.name, self.email)

    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50), unique=True),
        Column('email', String(120), unique=True)
    )
    mapper(User, users)

Querying and inserting works exactly the same as in the example above.


SQL Abstraction Layer
---------------------

If you just want to use the database system (and SQL) abstraction layer
you basically only need the engine::

    from sqlalchemy import create_engine, MetaData

    engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
    metadata = MetaData(bind=engine)

Then you can either declare the tables in your code like in the examples
above, or automatically load them::

    users = Table('users', metadata, autoload=True)

To insert data you can use the `insert` method.  We have to get a
connection first so that we can use a transaction:

>>> con = engine.connect()
>>> con.execute(users.insert(name='admin', email='admin@localhost'))

SQLAlchemy will automatically commit for us.

To query your database, you use the engine directly or use a connection:

>>> users.select(users.c.id == 1).execute().first()
(1, u'admin', u'admin@localhost')

These results are also dict-like tuples:

>>> r = users.select(users.c.id == 1).execute().first()
>>> r['name']
u'admin'

You can also pass strings of SQL statements to the
:meth:`~sqlalchemy.engine.base.Connection.execute` method:

>>> engine.execute('select * from users where id = :1', [1]).first()
(1, u'admin', u'admin@localhost')

For more information about SQLAlchemy, head over to the
`website <http://sqlalchemy.org/>`_.
