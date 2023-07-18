基于类的视图
=================

.. currentmodule:: flask.views


本页介绍了使用 :class:`View` 和 :class:`MethodView` 这两个类来编写基
于类的视图。

基于类的视图是具有视图功能的类。因为它是一个类，所以可以用不同的参数
创建不同的实例，实现不同的功能。这样的视图就视为通用、可重用或可插拔
的视图。

实用的例子是，比如定义一个类，它可以根据被初始化的数据库模型创建一个
相应的 API 。

对于更复杂的 API 行为和定制，请研究 Flask 的各种 API 扩展。


基本可重用视图
-------------------

让我们通过一个例子，将一个视图函数转换为一个视图类。我们从一个查询用
户列表的视图函数开始，然后渲染一个模板来显示这个列表。

.. code-block:: python

    @app.route("/users/")
    def user_list():
        users = User.query.all()
        return render_template("users.html", users=users)

这对用户模型有效，但假设还有更多的模型需要列表页。你需要为每个模型编
写一个视图函数，尽管唯一会改变的是模型和模板名称。

相反，你可以写一个 :class:`View` 子类，它将查询一个模型并渲染一个模板。
作为第一步，我们将把视图转换为一个类，不做任何定制。

.. code-block:: python

    from flask.views import View

    class UserList(View):
        def dispatch_request(self):
            users = User.query.all()
            return render_template("users.html", objects=users)

    app.add_url_rule("/users/", view_func=UserList.as_view("user_list"))

:meth:`View.dispatch_request` 方法等同于视图函数。调用
:meth:`View.as_view` 方法将创建一个视图函数，
该函数可以在应用上使用 :meth:`~flask.Flask.add_url_rule` 方法来注册。


`as_view` 的第一个参数是用于 :func:`~flask.url_for` 的指向视图的名称。

.. note::

    你不能像装饰基本视图函数一样使用 ``@app.route()`` 来装饰这个类。


接下来，我们需要能够为不同的模型和模板注册同一个视图类，以使它比原来
的函数更有用。这个类将接受两个参数，模型和模板，并将它们存储在
``self`` 上。然后 ``dispatch_request`` 可以引用这些参数而不是而不是硬
编码的值。

.. code-block:: python

    class ListView(View):
        def __init__(self, model, template):
            self.model = model
            self.template = template

        def dispatch_request(self):
            items = self.model.query.all()
            return render_template(self.template, items=items)

记住，我们用 ``View.as_view()`` 创建视图函数，而不是直接创建类。任何
传递给``as_view``的额外参数都会在创建类时传递。现在我们可以注册同一个
视图来处理多个模型。

.. code-block:: python

    app.add_url_rule(
        "/users/",
        view_func=ListView.as_view("user_list", User, "users.html"),
    )
    app.add_url_rule(
        "/stories/",
        view_func=ListView.as_view("story_list", Story, "stories.html"),
    )


URL变量
-------------


任何由URL捕获的变量都会作为关键字参数传递给 ``dispatch_request`` 方法，
就像普通的视图函数一样。

.. code-block:: python

    class DetailView(View):
        def __init__(self, model):
            self.model = model
            self.template = f"{model.__name__.lower()}/detail.html"

        def dispatch_request(self, id)
            item = self.model.query.get_or_404(id)
            return render_template(self.template, item=item)

    app.add_url_rule(
        "/users/<int:id>",
        view_func=DetailView.as_view("user_detail", User)
    )


视图的生命周期和 ``self``
--------------------------

默认情况下，每次处理请求时都会创建一个新的视图类的实例。这意味着，在
请求期间向 ``self`` 写入数据是安全的，因为下一个请求不会看到它，不像
其他形式的全局状态。

然而，如果你的视图类需要做很多复杂的初始化，那么为每一个请求做初始化
是没有必要的，而且可能是低效的。为了避免这种情况，将
:attr:`View.init_every_request` 设置为 ``False`` ，将会只创建一个类的
实例，并将其用于每个请求。在这种情况下，写数据到 ``self`` 是不安全的。
如果你需要在请求期间存储数据，那么请使用 :data:`~flask.g` 代替。

在 ``ListView`` 的例子中，在请求过程中没有任何东西写到`self'，所以更
有效的做法是创建一个单一的实例。

.. code-block:: python

    class ListView(View):
        init_every_request = False

        def __init__(self, model, template):
            self.model = model
            self.template = template

        def dispatch_request(self):
            items = self.model.query.all()
            return render_template(self.template, items=items)

每一个 ``as_view`` 的调用仍然会创建不同的实例，但不会为这些视图的每个
请求而创建。


视图装饰器
---------------

视图类本身不是视图函数。视图装饰器需要应用到由 ``as_view`` 返回的视图
函数，而不是类本身。将 :attr:`View.decorators` 设置为一个要应用的装饰
器列表。

.. code-block:: python

    class UserList(View):
        decorators = [cache(minutes=2), login_required]

    app.add_url_rule('/users/', view_func=UserList.as_view())

如果你没有设置 ``decorators`` ，你可以手动应用它们来代替。

这相当于：

.. code-block:: python

    view = UserList.as_view("users_list")
    view = cache(minutes=2)(view)
    view = login_required(view)
    app.add_url_rule('/users/', view_func=view)

请记住，顺序很重要。如果你习惯于 ``@decorator`` 风格，这相当于：

.. code-block:: python

    @app.route("/users/")
    @login_required
    @cache(minutes=2)
    def user_list():
        ...


方法提示
------------

一个常见的模式是用 ``methods=["GET", "POST"]`` 注册一个视图，
然后检查 ``request.method == "POST"`` 来决定做什么。设置
:attr:`View.methods` 等同于将方法列表传递给 ``add_url_rule`` 或
``route`` 。
.. code-block:: python

    class MyView(View):
        methods = ["GET", "POST"]

        def dispatch_request(self):
            if request.method == "POST":
                ...
            ...

    app.add_url_rule('/my-view', view_func=MyView.as_view('my-view'))

这等同于下面的内容，只是进一步的子类可以继承或改变这些方法。

.. code-block:: python

    app.add_url_rule(
        "/my-view",
        view_func=MyView.as_view("my-view"),
        methods=["GET", "POST"],
    )


方法调度和 API
---------------------------


对于 API 来说，为每个 HTTP 方法使用不同的函数可能会有帮助。
:class:`MethodView` 扩展了基本的 :class:`View` ，以根据请求方法调度
类的不同方法。每个 HTTP 方法都会映射到类中具有相同（小写）名称的方法。

:class:`MethodView` 基于该类定义的方法自动设置 :attr:`View.methods` 。
它甚至知道如何处理子类覆盖或定义其他方法。

我们可以制作一个通用的 ``ItemAPI`` 类，提供 get （详细）、
patch （编辑）和删除的方法给一个给定的模型。一个 ``GroupAPI`` 可以
提供 get（列表）和 post（创建）方法。

.. code-block:: python

    from flask.views import MethodView

    class ItemAPI(MethodView):
        init_every_request = False

        def __init__(self, model):
            self.model = model
            self.validator = generate_validator(model)

        def _get_item(self, id):
            return self.model.query.get_or_404(id)

        def get(self, id):
            item = self._get_item(id)
            return jsonify(item.to_json())

        def patch(self, id):
            item = self._get_item(id)
            errors = self.validator.validate(item, request.json)

            if errors:
                return jsonify(errors), 400

            item.update_from_json(request.json)
            db.session.commit()
            return jsonify(item.to_json())

        def delete(self, id):
            item = self._get_item(id)
            db.session.delete(item)
            db.session.commit()
            return "", 204

    class GroupAPI(MethodView):
        init_every_request = False

        def __init__(self, model):
            self.model = model
            self.validator = generate_validator(model, create=True)

        def get(self):
            items = self.model.query.all()
            return jsonify([item.to_json() for item in items])

        def post(self):
            errors = self.validator.validate(request.json)

            if errors:
                return jsonify(errors), 400

            db.session.add(self.model.from_json(request.json))
            db.session.commit()
            return jsonify(item.to_json())

    def register_api(app, model, name):
        item = ItemAPI.as_view(f"{name}-item", model)
        group = GroupAPI.as_view(f"{name}-group", model)
        app.add_url_rule(f"/{name}/<int:id>", view_func=item)
        app.add_url_rule(f"/{name}/", view_func=group)

    register_api(app, User, "users")
    register_api(app, Story, "stories")

这样产生了以下视图，一个标准的 REST API ！

================= ========== ===================
URL               方法       说明
----------------- ---------- -------------------
``/users/``       ``GET``    所有用户列表
``/users/``       ``POST``   创建一个新用户
``/users/<id>``   ``GET``    显示一个单独用户
``/users/<id>``   ``PATCH``  更新一个用户
``/users/<id>``   ``DELETE`` 删除一个用户
``/stories/``     ``GET``    显示所有故事
``/stories/``     ``POST``   创建一个新故事
``/stories/<id>`` ``GET``    显示一个单独的故事
``/stories/<id>`` ``PATCH``  更新一个故事
``/stories/<id>`` ``DELETE`` 删除一个故事
================= ========== ===================

