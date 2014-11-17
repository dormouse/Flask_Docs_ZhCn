.. _tutorial-dbinit:

步骤 3 ：创建数据库
=============================

如前所述 Flaskr 是一个数据库驱动的应用，更准确地说是一个关系型数据库驱动的
应用。关系型数据库需要一个数据库模式来定义如何储存信息，因此必须在第一次运行
服务器前创建数据库模式。

使用 `sqlite3` 命令通过管道导入 `schema.sql` 创建模式::

    sqlite3 /tmp/flaskr.db < schema.sql

上述方法的不足之处是需要额外的 sqlite3 命令，但这个命令不是每个系统都有的。而且还必须提供数据库的路径，容易出错。因此更好的方法是在应用中添加一个数据库初始化
函数。

添加的方法是：首先从 contextlib 库中导入 :func:`contextlib.closing` 函数，即在
`flaskr.py` 文件的导入部分添加如下内容::

    from contextlib import closing

接下来，可以创建一个用来初始化数据库的 `init_db` 函数，其中我们使用了先前创建的
`connect_db` 函数。把这个初始化函数放在 `flaskr.py` 文件中的`connect_db` 函数
下面::

    def init_db():
        with closing(connect_db()) as db:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()

:func:`~contextlib.closing` 帮助函数允许我们在 `with` 代码块保持数据库连接
打开。应用对象的 :func:`~flask.Flask.open_resource` 方法支持也支持这个功能，
可以在 `with` 代码块中直接使用。这个函数打开一个位于来源位置（你的
`flaskr` 文件夹）的文件并允许你读取文件的内容。这里我们用于在数据库连接上执行
代码。

当我们连接到数据库时，我们得到一个提供指针的连接对象（本例中的 `db` ）。这个
指针有一个方法可以执行完整的代码。最后我们提供要做的修改。 SQLite 3 和其他
事务型数据库只有在显式提交时才会真正提交。

现在可以创建数据库了。打开 Python shell ，导入，调用函数::

>>> from flaskr import init_db
>>> init_db()

.. admonition:: 故障处理

   如果出现表无法找到的问题，请检查是否写错了函数名称（应该是 `init_db` ），
   是否写错了表名（例如单数复数错误）。

下面请阅读 :ref:`tutorial-dbcon` 。
