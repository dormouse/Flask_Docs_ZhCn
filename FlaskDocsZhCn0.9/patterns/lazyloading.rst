惰性载入视图
====================

Flask 通常使用装饰器。装饰器简单易用，只要把 URL 放在相应的函数的前面就可以了。
但是这种方式有一个缺点：使用装饰器的代码必须预先导入，否则 Flask 就无法真正找到
你的函数。

当你必须快速导入应用时，这就会成为一个问题。在 Google App Engine 或其他系统中，
必须快速导入应用。因此，如果你的应用存在这个问题，那么必须使用集中 URL 映射。

:meth:`~flask.Flask.add_url_rule` 函数用于集中 URL 映射，与使用装饰器不同的是你
需要一个设置应用所有 URL 的专门文件。

转换为集中 URL 映射
---------------------------------

假设有如下应用::

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def index():
        pass

    @app.route('/user/<username>')
    def user(username):
        pass

为了集中映射，我们创建一个不使用装饰器的文件（ `views.py` ）::

    def index():
        pass

    def user(username):
        pass

在另一个文件中集中映射函数与 URL::

    from flask import Flask
    from yourapplication import views
    app = Flask(__name__)
    app.add_url_rule('/', view_func=views.index)
    app.add_url_rule('/user/<username>', view_func=views.user)

延迟载入
------------

至此，我们只是把视图与路由分离，但是模块还是预先载入了。理想的方式是按需载入
视图。下面我们使用一个类似函数的辅助类来实现按需载入::

    from werkzeug import import_string, cached_property

    class LazyView(object):

        def __init__(self, import_name):
            self.__module__, self.__name__ = import_name.rsplit('.', 1)
            self.import_name = import_name

        @cached_property
        def view(self):
            return import_string(self.import_name)

        def __call__(self, *args, **kwargs):
            return self.view(*args, **kwargs)

上例中最重要的是正确设置 `__module__` 和 `__name__` ，它被用于在不提供 URL 规则
的情况下正确命名 URL 规则。

然后可以这样集中定义 URL 规则::

    from flask import Flask
    from yourapplication.helpers import LazyView
    app = Flask(__name__)
    app.add_url_rule('/',
                     view_func=LazyView('yourapplication.views.index'))
    app.add_url_rule('/user/<username>',
                     view_func=LazyView('yourapplication.views.user'))

还可以进一步优化代码：写一个函数调用 :meth:`~flask.Flask.add_url_rule` ，加上
应用前缀和点符号::

    def url(url_rule, import_name, **options):
        view = LazyView('yourapplication.' + import_name)
        app.add_url_rule(url_rule, view_func=view, **options)

    url('/', 'views.index')
    url('/user/<username>', 'views.user')

有一件事情要牢记：请求前和请求后处理器必须在第一个请求前导入。

其余的装饰器可以同样用上述方法改写。
