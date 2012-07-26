.. mongokit-pattern:

在 Flask 中使用 MongoKit
========================

现在使用文档型数据库来取代关系型数据库已越来越常见。本方案展示如何使用
MongoKit ,它是一个用于操作 MongoDB 的文档映射库。

本方案需要一个运行中的 MongoDB 服务器和已安装好的 MongoKit 库。

使用 MongoKit 有两种常用的方法，下面逐一说明：


声明
-----------

声明是 MongoKit 的缺省行为。这个思路来自于 Django 或 SQLAlchemy 的声明。

下面是一个示例 `app.py` 模块::

    from flask import Flask
    from mongokit import Connection, Document

    # configuration
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017

    # create the little application object
    app = Flask(__name__)
    app.config.from_object(__name__)

    # connect to the database
    connection = Connection(app.config['MONGODB_HOST'],
                            app.config['MONGODB_PORT'])


如果要定义模型，那么只要继承 MongoKit 的 `Document` 类就行了。如果你已经读过
SQLAlchemy 方案，那么可以会奇怪这里为什么没有使用会话，甚至没有定义一个
`init_db` 函数。一方面是因为 MongoKit 没有类似会话在东西。有时候这样会多写一点
代码，但会使它的速度更快。另一方面是因为 MongoDB 是无模式的。这就意味着可以在
插入数据的时候修改数据结构。 MongoKit 也是无模式的，但会执行一些验证，以确保
数据的完整性。

以下是一个示例文档（把示例内容也放入 `app.py` ）::

    def max_length(length):
        def validate(value):
            if len(value) <= length:
                return True
            raise Exception('%s must be at most %s characters long' % length)
        return validate

    class User(Document):
        structure = {
            'name': unicode,
            'email': unicode,
        }
        validators = {
            'name': max_length(50),
            'email': max_length(120)
        }
        use_dot_notation = True
        def __repr__(self):
            return '<User %r>' % (self.name)

    # 在当前连接中注册用户文档
    connection.register([User])


上例展示如何定义模式（命名结构）和字符串最大长度验证器。上例中还使用了一个
MongoKit 中特殊的 `use_dot_notation` 功能。缺省情况下， MongoKit 的运作方式和
Python 的字典类似。但是如果 `use_dot_notation` 设置为 `True` ，那么就可几乎像
其他 ORM 一样使用点符号来分隔属性。

可以像下面这样把条目插入数据库中：

>>> from yourapplication.database import connection
>>> from yourapplication.models import User
>>> collection = connection['test'].users
>>> user = collection.User()
>>> user['name'] = u'admin'
>>> user['email'] = u'admin@localhost'
>>> user.save()

注意， MongoKit 对于列类型的使用是比较严格的。对于 `name` 和 `email` 列，你都
不能使用 `str` 类型，应当使用 unicode 。

查询非常简单：

>>> list(collection.User.find())
[<User u'admin'>]
>>> collection.User.find_one({'name': u'admin'})
<User u'admin'>

.. _MongoKit: http://bytebucket.org/namlook/mongokit/


PyMongo 兼容层
---------------------------

如果你只需要使用 PyMongo ，也可以使用 MongoKit 。在这种方式下可以获得最佳的
性能。注意，以下示例中，没有 MongoKit 与 Flask 整合的内容，整合的方式参见上文::

    from MongoKit import Connection

    connection = Connection()

使用 `insert` 方法可以插入数据。但首先必须先得到一个连接。这个连接类似于 SQL 界
的表。

>>> collection = connection['test'].users
>>> user = {'name': u'admin', 'email': u'admin@localhost'}
>>> collection.insert(user)

MongoKit 会自动提交。

直接使用集合查询数据库：

>>> list(collection.find())
[{u'_id': ObjectId('4c271729e13823182f000000'), u'name': u'admin', u'email': u'admin@localhost'}]
>>> collection.find_one({'name': u'admin'})
{u'_id': ObjectId('4c271729e13823182f000000'), u'name': u'admin', u'email': u'admin@localhost'}

查询结果为类字典对象：

>>> r = collection.find_one({'name': u'admin'})
>>> r['email']
u'admin@localhost'

关于 MongoKit 的更多信息，请移步其
`官方网站 <https://github.com/namlook/mongokit>`_ 。
