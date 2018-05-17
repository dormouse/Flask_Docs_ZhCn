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

工厂与扩展
----------------------

最好分别创建扩展和应用工厂，这样扩展对象就不会过早绑定到应用。

以使用 `Flask-SQLAlchemy <http://flask-sqlalchemy.pocoo.org/>`_ 为例，不应
当这样::

    def create_app(config_filename):
        app = Flask(__name__)
        app.config.from_pyfile(config_filename)

        db = SQLAlchemy(app)

而是在 model.py （或其他等价文件）中::

    db = SQLAlchemy()

在 application.py （或其他等价文件）中::

    def create_app(config_filename):
        app = Flask(__name__)
        app.config.from_pyfile(config_filename)

        from yourapplication.model import db
        db.init_app(app)

使用这个设计方案，不会有应用特定状态储存在扩展对象上，因此扩展对象就可以被
多个应用使用。更多关于扩展设计的信息参见 :doc:`/extensiondev` 。

使用应用
------------------

使用 :command:`flask` 命令运行工厂应用::

    export FLASK_APP=myapp
    flask run
    
Flask 会自动在 ``myapp`` 中探测工厂（ ``create_app`` 或者 ``make_app`` ）。
还可这样向工厂传递参数::

    export FLASK_APP="myapp:create_app('dev')"
    flask run
    
这样，  ``myapp`` 中的 ``create_app`` 工厂就会使用
``'dev'`` 作为参数。更多细节参见 :doc:`/cli` 。


改进工厂
--------------------

上面的工厂函数还不是足够好，可以改进的地方主要有以下几点：

1.  为了单元测试，要想办法传入配置，这样就不必在文件系统中创建配置文件。
2.  当设置应用时从蓝图调用一个函数，这样就可以有机会修改属性（如挂接请求
    前/后处理器等）。
3.  如果有必要的话，当创建一个应用时增加一个 WSGI 中间件。

