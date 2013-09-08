.. _app-factories:

应用工厂
=====================

如果你已经在应用中使用了包和蓝图（ :ref:`blueprints` ），那么还有许多方法可以更
进一步地改进你的应用。常用的方案是导入蓝图后创建应用对象，但是如果在一个函数中
创建对象，那么就可以创建多个实例。

那么这样做有什么用呢？

1.  用于测试。可以针对不同的情况使用不同的配置来测试应用。
2.  用于多实例，如果你需要运行同一个应用的不同版本的话。当然你可以在服务器上
    使用不同配置运行多个相同应用，但是如果使用应用工厂，那么你可以只使用一个
    应用进程而得到多个应用实例，这样更容易操控。

那么如何做呢？

基础工厂
---------------

方法是在一个函数中设置应用，具体如下::

    def create_app(config_filename):
        app = Flask(__name__)
        app.config.from_pyfile(config_filename)

        from yourapplication.model import db
        db.init_app(app)

        from yourapplication.views.admin import admin
        from yourapplication.views.frontend import frontend
        app.register_blueprint(admin)
        app.register_blueprint(frontend)

        return app

这个方法的缺点是在导入时无法在蓝图中使用应用对象。但是你可以在一个请求中使用它。
如何通过配置来访问应用？使用 :data:`~flask.current_app`::

    from flask import current_app, Blueprint, render_template
    admin = Blueprint('admin', __name__, url_prefix='/admin')

    @admin.route('/')
    def index():
        return render_template(current_app.config['INDEX_TEMPLATE'])

这里我们在配置中查找模板的名称。

扩展对象初始化时不会绑定到一个应用，应用可以使用 ``db.init_app`` 来设置扩展。
扩展对象中不会储存特定应用的状态，因此一个扩展可以被多个应用使用。关于扩展设计
的更多信息请参阅 :doc:`/extensiondev` 。

当使用 `Flask-SQLAlchemy <http://pythonhosted.org/Flask-SQLAlchemy/>`_ 时，你的
`model.py` 可能是这样的::

    from flask.ext.sqlalchemy import SQLAlchemy
    # no app object passed! Instead we use use db.init_app in the factory.
    db = SQLAlchemy()

    # create some models

使用应用
------------------

因此，要使用这样的应用就必须先创建它。下面是一个运行应用的示例 `run.py` 文件::

    from yourapplication import create_app
    app = create_app('/path/to/config.cfg')
    app.run()

改进工厂
--------------------

上面的工厂函数还不是足够好，可以改进的地方主要有以下几点：

1.  为了单元测试，要想办法传入配置，这样就不必在文件系统中创建配置文件。
2.  当设置应用时从蓝图调用一个函数，这样就可以有机会修改属性（如挂接请求前/后
    处理器等）。
3.  如果有必要的话，当创建一个应用时增加一个 WSGI 中间件。
