.. currentmodule:: flask

定义和操作数据库
==============================

应用使用一个 `SQLite`_ 数据库来储存用户和博客内容。
Python 内置了 SQLite 数据库支持，相应的模块为 :mod:`sqlite3` 。

使用 SQLite 的便利性在于不需要单独配置一个数据库服务器，并且 Python 提供了
内置支持。但是当并发请求同时要写入时，会比较慢一点，因为每个写操作是按顺序
进行的。小应用没有问题，但是大应用可能就需要考虑换成别的数据库了。

本教程不会详细讨论 SQL 。如果你不是很熟悉 SQL ，请先阅读 SQLite 文档中的
`相关内容`_ 。

.. _SQLite: https://sqlite.org/about.html
.. _相关内容: https://sqlite.org/lang.html


连接数据库
-----------------------

当使用 SQLite 数据库（包括其他多数数据库的 Python 库）时，第一件事就是创建
一个数据库的连接。所有查询和操作都要通过该连接来执行，完事后该连接关闭。

在网络应用中连接往往与请求绑定。在处理请求的某个时刻，连接被创建。在发送响应
之前连接被关闭。

.. code-block:: python
    :caption: ``flaskr/db.py``

    import sqlite3

    import click
    from flask import current_app, g
    from flask.cli import with_appcontext


    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row

        return g.db


    def close_db(e=None):
        db = g.pop('db', None)

        if db is not None:
            db.close()

:data:`g` 是一个特殊对象，独立于每一个请求。在处理请求过程中，它可以用于储存
可能多个函数都会用到的数据。把连接储存于其中，可以多次使用，而不用在同一个
请求中每次调用 ``get_db`` 时都创建一个新的连接。

:data:`current_app` 是另一个特殊对象，该对象指向处理请求的 Flask 应用。这里
使用了应用工厂，那么在其余的代码中就不会出现应用对象。当应用创建后，在处理
一个请求时， ``get_db`` 会被调用。这样就需要使用 :data:`current_app` 。

:func:`sqlite3.connect` 建立一个数据库连接，该连接指向配置中的 ``DATABASE``
指定的文件。这个文件现在还没有建立，后面会在初始化数据库的时候建立该文件。

:class:`sqlite3.Row` 告诉连接返回类似于字典的行，这样可以通过列名称来操作
数据。

``close_db`` 通过检查 ``g.db`` 来确定连接是否已经建立。如果连接已建立，那么
就关闭连接。以后会在应用工厂中告诉应用 ``close_db`` 函数，这样每次请求后就会
调用它。


创建表
-----------------

在 SQLite 中，数据储存在 *表* 和 *列* 中。在储存和调取数据之前需要先创建它们。
Flaskr 会把用户数据储存在 ``user`` 表中，把博客内容储存在 ``post`` 表中。下面
创建一个文件储存用于创建空表的 SQL 命令：

.. code-block:: sql
    :caption: ``flaskr/schema.sql``

    DROP TABLE IF EXISTS user;
    DROP TABLE IF EXISTS post;

    CREATE TABLE user (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL
    );

    CREATE TABLE post (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      author_id INTEGER NOT NULL,
      created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      title TEXT NOT NULL,
      body TEXT NOT NULL,
      FOREIGN KEY (author_id) REFERENCES user (id)
    );

在 ``db.py`` 文件中添加 Python 函数，用于运行这个 SQL 命令：

.. code-block:: python
    :caption: ``flaskr/db.py``

    def init_db():
        db = get_db()

        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))


    @click.command('init-db')
    @with_appcontext
    def init_db_command():
        """Clear the existing data and create new tables."""
        init_db()
        click.echo('Initialized the database.')

:meth:`open_resource() <Flask.open_resource>` 打开一个文件，该文件名是相对于
``flaskr`` 包的。这样就不需要考虑以后应用具体部署在哪个位置。 ``get_db``
返回一个数据库连接，用于执行文件中的命令。

:func:`click.command` 定义一个名为 ``init-db`` 命令行，它调用
``init_db`` 函数，并为用户显示一个成功的消息。
更多关于如何写命令行的内容请参阅 ref:`cli` 。


在应用中注册
-----------------------------

``close_db`` 和 ``init_db_command`` 函数需要在应用实例中注册，否则无法使用。
然而，既然我们使用了工厂函数，那么在写函数的时候应用实例还无法使用。代替地，
我们写一个函数，把应用作为参数，在函数中进行注册。

.. code-block:: python
    :caption: ``flaskr/db.py``

    def init_app(app):
        app.teardown_appcontext(close_db)
        app.cli.add_command(init_db_command)

:meth:`app.teardown_appcontext() <Flask.teardown_appcontext>` 告诉
Flask 在返回响应后进行清理的时候调用此函数。

:meth:`app.cli.add_command() <click.Group.add_command>` 添加一个新的
可以与 ``flask`` 一起工作的命令。

在工厂中导入并调用这个函数。在工厂函数中把新的代码放到
函数的尾部，返回应用代码的前面。

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    def create_app():
        app = ...
        # existing code omitted

        from . import db
        db.init_app(app)

        return app


初始化数据库文件
----------------------------

现在 ``init-db`` 已经在应用中注册好了，可以与 ``flask`` 命令一起使用了。
使用的方式与前一页的 ``run`` 命令类似。

.. note::

    如果你还在运行着前一页的服务器，那么现在要么停止该服务器，要么在新的
    终端中运行这个命令。如果是新的终端请记住在进行项目文件夹并激活环境，
    参见 :ref:`install-activate-env` 。同时还要像前一页所述设置
    ``FLASK_APP`` 和 ``FLASK_ENV`` 。

运行 ``init-db`` 命令：

.. code-block:: none

    $ flask init-db
    Initialized the database.

现在会有一个 ``flaskr.sqlite`` 文件出现在项目所在文件夹的 ``instance`` 文件夹
中。

下面请阅读 :doc:`views` 。
