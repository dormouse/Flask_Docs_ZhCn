.. _blueprints:

使用蓝图的模块化应用
====================================

.. versionadded:: 0.7

为了在一个或多个应用中，使应用模块化并且支持常用方案， Flask 引入了 *蓝图*
概念。蓝图可以极大地简化大型应用并为扩展提供集中的注册入口。
:class:`Blueprint` 对象与 :class:`Flask` 应用对象的工作方式类似，但不是一个真正
的应用。它更像一个用于构建和扩展应用的 *蓝图* 。

为什么使用蓝图？
----------------

Flask 中蓝图有以下用途：

* 把一个应用分解为一套蓝图。这是针对大型应用的理想方案：一个项目可以实例化一个
  应用，初始化多个扩展，并注册许多蓝图。
* 在一个应用的 URL 前缀和（或）子域上注册一个蓝图。 URL 前缀和（或）子域的参数
  成为蓝图中所有视图的通用视图参数（缺省情况下）。
* 使用不同的 URL 规则在应用中多次注册蓝图。
* 通过蓝图提供模板过滤器、静态文件、模板和其他工具。蓝图不必执行应用或视图
  函数。
* 当初始化一个 Flask 扩展时，为以上任意一种用途注册一个蓝图。

Flask 中的蓝图不是一个可插拨的应用，因为它不是一个真正的应用，而是一套可以注册
在应用中的操作，并且可以注册多次。那么为什么不使用多个应用对象呢？可以使用多个
应用对象（参见 :ref:`app-dispatch` ），但是这样会导致每个应用都使用自己独立的
配置，且只能在 WSGI 层中管理应用。

而如果使用蓝图，那么应用会在 Flask 层中进行管理，共享配置，通过注册按需改变应用
对象。蓝图的缺点是一旦应用被创建后，只有销毁整个应用对象才能注销蓝图。

蓝图的概念
-------------------------

蓝图的基本概念是：在蓝图被注册到应用之后，所要执行的操作的集合。当分配请求时，
Flask 会把蓝图和视图函数关联起来，并生成两个端点之前的 URL 。

第一个蓝图
------------------

以下是一个最基本的蓝图示例。在这里，我们将使用蓝图来简单地渲染静态模板::

    from flask import Blueprint, render_template, abort
    from jinja2 import TemplateNotFound

    simple_page = Blueprint('simple_page', __name__,
                            template_folder='templates')

    @simple_page.route('/', defaults={'page': 'index'})
    @simple_page.route('/<page>')
    def show(page):
        try:
            return render_template('pages/%s.html' % page)
        except TemplateNotFound:
            abort(404)

当你使用 ``@simple_page.route`` 装饰器绑定一个函数时，蓝图会记录下所登记的
`show` 函数。当以后在应用中注册蓝图时，这个函数会被注册到应用中。另外，它会把
构建 :class:`Blueprint` 时所使用的名称（在本例为 ``simple_page`` ）作为函数端点
的前缀。

注册蓝图
----------------------

可以这样注册蓝图::

    from flask import Flask
    from yourapplication.simple_page import simple_page

    app = Flask(__name__)
    app.register_blueprint(simple_page)

以下是注册蓝图后形成的规则::

    [<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>,
     <Rule '/<page>' (HEAD, OPTIONS, GET) -> simple_page.show>,
     <Rule '/' (HEAD, OPTIONS, GET) -> simple_page.show>]

第一条很明显，是来自于应用本身的用于静态文件的。后面两条是用于蓝图
``simple_page`` 的 `show` 函数的。你可以看到，它们的前缀都是蓝图的名称，并且
使用一个点（ ``.`` ）来分隔。

蓝图还可以挂接到不同的位置::

    app.register_blueprint(simple_page, url_prefix='/pages')

这样就会形成如下规则::

    [<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>,
     <Rule '/pages/<page>' (HEAD, OPTIONS, GET) -> simple_page.show>,
     <Rule '/pages/' (HEAD, OPTIONS, GET) -> simple_page.show>]

总之，你可以多次注册蓝图，但是不一定每个蓝图都能正确响应。是否能够多次注册实际
上取决于你的蓝图是如何编写的，是否能根据不同的位置做出正确的响应。

蓝图资源
-------------------

蓝图还可以用于提供资源。有时候，我们仅仅是为了使用一些资源而使用蓝图。

蓝图资源文件夹
`````````````````````````

和普通应用一样，蓝图一般都放在一个文件夹中。虽然多个蓝图可以共存于同一个文件夹
中，但是最好不要这样做。

文件夹由 :class:`Blueprint` 的第二个参数指定，通常为 `__name__` 。这个参数指定
与蓝图相关的逻辑 Python 模块或包。如果这个参数指向的是实际的 Python 包（文件
系统中的一个文件夹），那么它就是资源文件夹。如果是一个模块，那么这个模块包含的
包就是资源文件夹。可以通过  :attr:`Blueprint.root_path` 属性来查看蓝图的资源
文件夹::

    >>> simple_page.root_path
    '/Users/username/TestProject/yourapplication'

可以使用 :meth:`~Blueprint.open_resource` 函数快速打开这个文件夹中的资源::

    with simple_page.open_resource('static/style.css') as f:
        code = f.read()

静态文件
````````````

蓝图的第三个参数是 `static_folder` 。这个参数用以指定蓝图的静态文件所在的
文件夹，它可以是一个绝对路径也可以是相对路径。::

    admin = Blueprint('admin', __name__, static_folder='static')

缺省情况下，路径最右端的部分是在 URL 中暴露的部分。上例中的文件夹为
``static`` ，那么 URL 应该是蓝图加上 ``/static`` 。蓝图注册为 ``/admin`` ，那么
静态文件夹就是 ``/admin/static`` 。

端点的名称是 `blueprint_name.static` ，因此你可以使用和应用中的文件夹一样的方法
来生成其 URL::

    url_for('admin.static', filename='style.css')

模板
`````````

如果你想使用蓝图来暴露模板，那么可以使用 :class:`Blueprint` 的
`template_folder` 参数::

    admin = Blueprint('admin', __name__, template_folder='templates')

和静态文件一样，指向蓝图资源文件夹的路径可以是绝对的也可以是相对的。蓝图中的
模板文件夹会被添加到模板搜索路径中，但其优先级低于实际应用的模板文件夹。这样在
实际应用中可以方便地重载蓝图提供的模板。

假设你的蓝图便于 ``yourapplication/admin`` 中，要渲染的模板是
``'admin/index.html'`` ， `template_folder` 参数值为 ``templates`` ，那么真正的
模板文件为： ``yourapplication/admin/templates/admin/index.html`` 。

创建 URL
-------------

如果要创建页面链接，可以和通常一样使用
:func:`url_for` 函数，只是要把蓝图名称作为端点的前缀，并且用一个点（ ``.`` ）来
分隔::

    url_for('admin.index')

另外，如果在一个蓝图的视图函数或者被渲染的模板中需要链接同一个蓝图中的其他
端点，那么使用相对重定向，只使用一个点使用为前缀::

    url_for('.index')

如果当前请求被分配到 admin 蓝图端点时，上例会链接到 ``admin.index`` 。
