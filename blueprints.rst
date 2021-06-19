.. _blueprints:

使用蓝图进行应用模块化
====================================

.. currentmodule:: flask

.. versionadded:: 0.7

为了在一个或多个应用中，使应用模块化并且支持常用方案， Flask 引入了 *蓝图*
概念。蓝图可以极大地简化大型应用并为扩展提供集中的注册入口。
:class:`Blueprint` 对象与 :class:`Flask` 应用对象的工作方式类似，但不是一
个真正的应用。它更像一个用于构建和扩展应用的 *蓝图* 。

为什么使用蓝图？
----------------

Flask 中蓝图有以下用途：

* 把一个应用分解为一套蓝图。这是针对大型应用的理想方案：一个项目可以实例化
  一个应用，初始化多个扩展，并注册许多蓝图。
* 在一个应用的 URL 前缀和（或）子域上注册一个蓝图。 URL 前缀和（或）子域的
  参数成为蓝图中所有视图的通用视图参数（缺省情况下）。
* 使用不同的 URL 规则在应用中多次注册蓝图。
* 通过蓝图提供模板过滤器、静态文件、模板和其他工具。蓝图不必执行应用或视图
  函数。
* 当初始化一个 Flask 扩展时，为以上任意一种用途注册一个蓝图。

Flask 中的蓝图不是一个可插拨的应用，因为它不是一个真正的应用，而是一套可以
注册在应用中的操作，并且可以注册多次。那么为什么不使用多个应用对象呢？可以
使用多个应用对象（参见 :doc:`/patterns/appdispatch` ），但是这样会导致每个
应用都使用自己独立的配置，且只能在 WSGI 层中管理应用。

而如果使用蓝图，那么应用会在 Flask 层中进行管理，共享配置，通过注册按需改
变应用对象。蓝图的缺点是一旦应用被创建后，只有销毁整个应用对象才能注销蓝图。

蓝图的概念
-------------------------

蓝图的基本概念是：在蓝图被注册到应用之后，所要执行的操作的集合。当分配请求
时， Flask 会把蓝图和视图函数关联起来，并生成两个端点之前的 URL 。

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
            return render_template(f'pages/{page}.html')
        except TemplateNotFound:
            abort(404)

当你使用 ``@simple_page.route`` 装饰器绑定一个函数时，蓝图会记录下所登记的
``show`` 函数。当以后在应用中注册蓝图时，这个函数会被注册到应用中。另外，它
会把构建 :class:`Blueprint` 时所使用的名称（在本例为 ``simple_page`` ）作
为函数端点的前缀。蓝图的名称不修改 URL ，只修改端点。

注册蓝图
----------------------

可以这样注册蓝图::

    from flask import Flask
    from yourapplication.simple_page import simple_page

    app = Flask(__name__)
    app.register_blueprint(simple_page)

以下是注册蓝图后形成的规则::

    >>> app.url_map
    Map([<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>,
     <Rule '/<page>' (HEAD, OPTIONS, GET) -> simple_page.show>,
     <Rule '/' (HEAD, OPTIONS, GET) -> simple_page.show>])

第一条很明显，是来自于应用本身的用于静态文件的。后面两条是用于蓝图
``simple_page`` 的 `show` 函数的。你可以看到，它们的前缀都是蓝图的名称，并
且使用一个点（ ``.`` ）来分隔。

蓝图还可以挂接到不同的位置::

    app.register_blueprint(simple_page, url_prefix='/pages')

这样就会形成如下规则::

    >>> app.url_map
    Map([<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>,
     <Rule '/pages/<page>' (HEAD, OPTIONS, GET) -> simple_page.show>,
     <Rule '/pages/' (HEAD, OPTIONS, GET) -> simple_page.show>])

总之，你可以多次注册蓝图，但是不一定每个蓝图都能正确响应。是否能够多次注册
实际上取决于你的蓝图是如何编写的，是否能根据不同的位置做出正确的响应。


嵌套蓝图
------------------

把一个蓝图注册在另一个蓝图上是可行的。

.. code-block:: python

    parent = Blueprint('parent', __name__, url_prefix='/parent')
    child = Blueprint('child', __name__, url_prefix='/child')
    parent.register_blueprint(child)
    app.register_blueprint(parent)

子蓝图会把父蓝图的名称作为其前缀，子 URL 也会把父 URL 作为前缀。

.. code-block:: python

    url_for('parent.child.create')
    /parent/child/create

父蓝图指定的请求前函数等会为子蓝图触发。如果子蓝图没有可以处理异常的出错
处理器，那么会尝试父蓝图的出错处理。


蓝图资源
-------------------

蓝图还可以用于提供资源。有时候，我们仅仅是为了使用一些资源而使用蓝图。

蓝图资源文件夹
`````````````````````````

和普通应用一样，蓝图一般都放在一个文件夹中。虽然多个蓝图可以共存于同一个文
件夹中，但是最好不要这样做。

文件夹由 :class:`Blueprint` 的第二个参数指定，通常为 `__name__` 。这个参数
指定与蓝图相关的逻辑 Python 模块或包。如果这个参数指向的是实际的 Python 包
（文件系统中的一个文件夹），那么它就是资源文件夹。如果是一个模块，那么这个
模块包含的包就是资源文件夹。可以通过  :attr:`Blueprint.root_path` 属性来查
看蓝图的资源文件夹::

    >>> simple_page.root_path
    '/Users/username/TestProject/yourapplication'

可以使用 :meth:`~Blueprint.open_resource` 函数快速打开这个文件夹中的资源::

    with simple_page.open_resource('static/style.css') as f:
        code = f.read()

静态文件
````````````

蓝图的第三个参数是 ``static_folder`` 。这个参数用以指定蓝图的静态文件所在的
文件夹，它可以是一个绝对路径也可以是相对路径。::

    admin = Blueprint('admin', __name__, static_folder='static')

缺省情况下，路径最右端的部分是在 URL 中暴露的部分。这可以通过
``static_url_path`` 来改变。因为上例中的文件夹为名称是 ``static`` ，那么
URL 应该是蓝图的 ``url_prefix`` 加上 ``/static`` 。
如果蓝图注册前缀为 ``/admin`` ，那么静态文件 URL 就是 ``/admin/static`` 。

端点的名称是 ``blueprint_name.static`` 。你可以像对待应用中的文件夹一样
使用 :func:`url_for` 来生成其 URL::

    url_for('admin.static', filename='style.css')

但是，如果蓝图没有 ``url_prefix`` ，那么不可能访问蓝图的静态文件夹。
这是因为在这种情况下，URL应该是 ``/ static`` ，而应用程序的 ``/ static``
路线优先。与模板文件夹不同，如果文件不存在于应用静态文件夹中，那么不会
搜索蓝图静态文件夹。


模板
`````````

如果你想使用蓝图来暴露模板，那么可以使用 :class:`Blueprint` 的
`template_folder` 参数::

    admin = Blueprint('admin', __name__, template_folder='templates')

对于静态文件，路径可以是绝对的或相对于蓝图的资源文件夹。

模板文件夹被添加到模板的搜索路径，但优先级低于实际应用的模板文件夹。这样就
可以轻松地重载在实际应用中蓝图提供的模板。这也意味着如果你不希望蓝图模板出
现意外重写，那么就要确保没有其他蓝图或实际的应用模板具有相同的相对路径。
多个蓝图提供相同的相对路径时，第一个注册的优先。

假设你的蓝图便于 ``yourapplication/admin`` 中，要渲染的模板是
``'admin/index.html'`` ， `template_folder` 参数值为 ``templates`` ，那么
真正的模板文件为：
:file:`yourapplication/admin/templates/admin/index.html` 。多出一个
``admin`` 文件夹是为了避免模板被实际应用模板文件夹中的 ``index.html`` 重载。

更详细一点说：如果你有一个名为 ``admin`` 的蓝图，该蓝图指定的模版文件是
:file:`index.html` ，那么最好按照如下结构存放模版文件::

    yourpackage/
        blueprints/
            admin/
                templates/
                    admin/
                        index.html
                __init__.py

这样，当你需要渲染模板的时候就可以使用 :file:`admin/index.html` 来找到模板。
如果没有载入正确的模板，那么应该启用 ``EXPLAIN_TEMPLATE_LOADING`` 配置变量。
启用这个变量以后，每次调用 ``render_template`` 时， Flask 会打印出定位模板的
步骤，方便调试。

创建 URL
-------------

如果要创建页面链接，可以和通常一样使用 :func:`url_for` 函数，只是要把蓝图
名称作为端点的前缀，并且用一个点（ ``.`` ）来分隔::

    url_for('admin.index')

另外，如果在一个蓝图的视图函数或者被渲染的模板中需要链接同一个蓝图中的其他
端点，那么使用相对重定向，只使用一个点使用为前缀::

    url_for('.index')

如果当前请求被分配到 admin 蓝图端点时，上例会链接到 ``admin.index`` 。


蓝图出错处理器
--------------

蓝图像 :class:`Flask` 应用对象一样支持 ``errorhandler`` 装饰器，所以很容易
使用蓝图特定的自定义错误页面。

下面是 "404 Page Not Found" 异常的例子::

    @simple_page.errorhandler(404)
    def page_not_found(e):
        return render_template('pages/404.html')

大多数错误处理器会按预期工作。然而，有一个涉及 404 和 405 例外处理器的警示。
这些错误处理器只会由一个适当的 ``raise`` 语句引发或者调用在另一个蓝图视图
中调用 ``abort`` 引发。它们不会引发于无效的 URL 访问。这是因为蓝图不“拥有”
特定的 URL 空间，在发生无效 URL 访问时，应用实例无法知道应该运行哪个蓝图错
误处理器。 如果你想基于 URL 前缀执行不同的错误处理策略，那么可以
在应用层使用 ``request`` 代理对象定义它们::

    @app.errorhandler(404)
    @app.errorhandler(405)
    def _handle_api_error(ex):
        if request.path.startswith('/api/'):
            return jsonify(error=str(ex)), ex.code
        else:
            return ex

参见 :doc:`/errorhandling` 。 

