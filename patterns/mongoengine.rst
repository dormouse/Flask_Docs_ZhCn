通过 MongoEngine 使用 MongoDB
=============================

使用一个 MongoDB 之类的文档型数据库来代替关系 SQL 数据是很常见的。本方
案演示如何使用文档映射库 `MongoEngine`_ 来集成 MongoDB 。

先准备好一个运行中的 MongoDB 服务和 `Flask-MongoEngine`_ ::

    pip install flask-mongoengine

.. _MongoEngine: http://mongoengine.org
.. _Flask-MongoEngine: https://flask-mongoengine.readthedocs.io


配置
-------------

基本的配置是在 ``app.config`` 中定义 ``MONGODB_SETTINGS`` 并创建一个 
``MongoEngine`` 实例::

    from flask import Flask
    from flask_mongoengine import MongoEngine

    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {
        "db": "myapp",
    }
    db = MongoEngine(app)


映射文档
-----------------

声明用于一个 Mongo 文档的模型的方法是创建一个 ``Document`` 的子类，然后
声明每个字段::

    import mongoengine as me

    class Movie(me.Document):
        title = me.StringField(required=True)
        year = me.IntField()
        rated = me.StringField()
        director = me.StringField()
        actors = me.ListField()

如果文档包含嵌套的字段，那么使用 ``EmbeddedDocument`` 来定义嵌套的文
档，并在父文档中使用 ``EmbeddedDocumentField`` 声明相应的字段::

    class Imdb(me.EmbeddedDocument):
        imdb_id = me.StringField()
        rating = me.DecimalField()
        votes = me.IntField()

    class Movie(me.Document):
        ...
        imdb = me.EmbeddedDocumentField(Imdb)


创建数据
-------------

使用字段的关键字参数实例化文档类。还可以在实例化后为字段属性指定值。
然后调用 ``doc.save（）`` ::

    bttf = Movie(title="Back To The Future", year=1985)
    bttf.actors = [
        "Michael J. Fox",
        "Christopher Lloyd"
    ]
    bttf.imdb = Imdb(imdb_id="tt0088763", rating=8.5)
    bttf.save()


查询
-------

使用类的 ``objects`` 属性来执行查询。关键字参数用于字段的等值查询::

    bttf = Movies.objects(title="Back To The Future").get_or_404()

字段名称后加双下划线可以连接查询操作符。
``objects`` 及其返回的查询是可迭代的::

    some_theron_movie = Movie.objects(actors__in=["Charlize Theron"]).first()

    for recents in Movie.objects(year__gte=2017):
        print(recents.title)


相关文档
-------------

有许多关于使用 MongoEngine 定义和查询文档数据的方法，更多信息请参阅其
`官方文档 <MongoEngine_>`_ 。

Flask-MongoEngine 为 MongoEngine 添加了有用的工具，请参阅其
`文档说明 <Flask-MongoEngine_>`_ 。
