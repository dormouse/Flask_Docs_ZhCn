.. _views:

可插拨视图
===============

.. versionadded:: 0.7

Flask 0.7 版本引入了可插拨视图。可插拨视图基于使用类来代替函数，其灵感来自于
Django 的通用视图。可插拨视图的主要用途是用可定制的、可插拨的视图来替代部分
实现。

基本原理
---------------

假设有一个函数用于从数据库中载入一个对象列表并在模板中渲染::

    @app.route('/users/')
    def show_users(page):
        users = User.query.all()
        return render_template('users.html', users=users)

上例简单而灵活。但是如果要把这个视图变成一个可以用于其他模型和模板的通用视图，
那么这个视图还是不够灵活。因此，我们就需要引入可插拨的、基于类的视图。第一步，
可以把它转换为一个基础视图::


    from flask.views import View

    class ShowUsers(View):

        def dispatch_request(self):
            users = User.query.all()
            return render_template('users.html', objects=users)

    app.add_url_rule('/users/', view_func=ShowUsers.as_view('show_users'))

就如你所看到的，必须做的是创建一个 :class:`flask.views.View` 的子类，并且执行
:meth:`~flask.views.View.dispatch_request` 。然后必须通过使用
:meth:`~flask.views.View.as_view` 方法把类转换为实际视图函数。传递给函数的
字符串是最终视图的名称。但是这本身没有什么帮助，所以让我们来小小地重构一下::

    
    from flask.views import View

    class ListView(View):

        def get_template_name(self):
            raise NotImplementedError()

        def render_template(self, context):
            return render_template(self.get_template_name(), **context)

        def dispatch_request(self):
            context = {'objects': self.get_objects()}
            return self.render_template(context)

    class UserView(ListView):

        def get_template_name(self):
            return 'users.html'

        def get_objects(self):
            return User.query.all()

这样做对于示例中的小应用没有什么用途，但是可以足够清楚的解释基本原理。当你有
一个基础视图类时，问题就来了：类的 `self` 指向什么？解决之道是：每当请求发出时
就创建一个类的新实例，并且根据来自 URL 规则的参数调用
:meth:`~flask.views.View.dispatch_request` 方法。类本身根据参数实例化后传递给
:meth:`~flask.views.View.as_view` 函数。例如可以这样写一个类::

    class RenderTemplateView(View):
        def __init__(self, template_name):
            self.template_name = template_name
        def dispatch_request(self):
            return render_template(self.template_name)

然后可以这样注册::

    app.add_url_rule('/about', view_func=RenderTemplateView.as_view(
        'about_page', template_name='about.html'))

方法提示
------------

可插拨视图可以像普通函数一样加入应用。加入的方式有两种，一种是使用
:func:`~flask.Flask.route` ，另一种是使用更好的
:meth:`~flask.Flask.add_url_rule` 。在加入的视图中应该提供所使用的 HTTP 方法的
名称。提供名称的方法是使用 :attr:`~flask.views.View.methods` 属性::

    class MyView(View):
        methods = ['GET', 'POST']

        def dispatch_request(self):
            if request.method == 'POST':
                ...
            ...

    app.add_url_rule('/myview', view_func=MyView.as_view('myview'))


基于方法调度
------------------------

对于 REST 式的 API 来说，为每种 HTTP 方法提供相对应的不同函数显得尤为有用。使用
:class:`flask.views.MethodView` 可以轻易做到这点。在这个类中，每个 HTTP 方法
都映射到一个同名函数（函数名称为小写字母）::

    from flask.views import MethodView

    class UserAPI(MethodView):

        def get(self):
            users = User.query.all()
            ...

        def post(self):
            user = User.from_form_data(request.form)
            ...

    app.add_url_rule('/users/', view_func=UserAPI.as_view('users'))

使用这种方式，不必提供 :attr:`~flask.views.View.methods` 属性，它会自动使用相应
的类方法。

装饰视图
----------------

视图函数会被添加到路由系统中，而视图类则不会。因此视图类不需要装饰，只能以手工
使用 :meth:`~flask.views.View.as_view` 来装饰返回值::

    def user_required(f):
        """Checks whether user is logged in or raises error 401."""
        def decorator(*args, **kwargs):
            if not g.user:
                abort(401)
            return f(*args, **kwargs)
        return decorator

    view = user_required(UserAPI.as_view('users'))
    app.add_url_rule('/users/', view_func=view)

自 Flask 0.8 版本开始，新加了一种选择：在视图类中定义装饰的列表::

    class UserAPI(MethodView):
        decorators = [user_required]

请牢记：因为从调用者的角度来看，类的 self 被隐藏了，所以不能在类的方法上单独
使用装饰器。

用于 API 的方法视图
---------------------

网络 API 经常直接对应 HTTP 变量，因此很有必要实现基于
:class:`~flask.views.MethodView` 的 API 。即多数时候， API 需要把不同的 URL
规则应用到同一个方法视图。例如，假设你需要这样使用一个 user 对象：

=============== =============== ======================================
URL             方法            说明
--------------- --------------- --------------------------------------
``/users/``     ``GET``         给出一个包含所有用户的列表
``/users/``     ``POST``        创建一个新用户
``/users/<id>`` ``GET``         显示一个用户
``/users/<id>`` ``PUT``         更新一个用户
``/users/<id>`` ``DELETE``      删除一个用户
=============== =============== ======================================

那么如何使用 :class:`~flask.views.MethodView` 来实现呢？方法是使用多个规则对应
到同一个视图。

假设视图是这样的::

    class UserAPI(MethodView):

        def get(self, user_id):
            if user_id is None:
                # 返回一个包含所有用户的列表
                pass
            else:
                # 显示一个用户
                pass

        def post(self):
            # 创建一个新用户
            pass

        def delete(self, user_id):
            # 删除一个用户
            pass

        def put(self, user_id):
            # update a single user
            pass

那么如何把这个视图挂接到路由系统呢？方法是增加两个规则并为每个规则显式声明
方法::

    user_view = UserAPI.as_view('user_api')
    app.add_url_rule('/users/', defaults={'user_id': None},
                     view_func=user_view, methods=['GET',])
    app.add_url_rule('/users/', view_func=user_view, methods=['POST',])
    app.add_url_rule('/users/<int:user_id>', view_func=user_view,
                     methods=['GET', 'PUT', 'DELETE'])

如果你有许多类似的 API ，那么可以代码如下::

    def register_api(view, endpoint, url, pk='id', pk_type='int'):
        view_func = view.as_view(endpoint)
        app.add_url_rule(url, defaults={pk: None},
                         view_func=view_func, methods=['GET',])
        app.add_url_rule(url, view_func=view_func, methods=['POST',])
        app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                         methods=['GET', 'PUT', 'DELETE'])

    register_api(UserAPI, 'user_api', '/users/', pk='user_id')
