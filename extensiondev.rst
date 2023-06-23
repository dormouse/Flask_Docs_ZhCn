Flask 扩展开发
==============

.. currentmodule:: flask

扩展是为 Flask 应用添加功能的额外的包。虽然 `PyPI`_ 已经包含了许多
Flask 扩展，但是如果找不到合适的，那么可以创建自己的扩展，并发布以供
他人使用。

本文将展示如何创建 Flask 扩展，以及一些常见模式和要求。由于扩展可以做
任何事情，本文无法涵盖所有可能性。

了解扩展的最佳方法是查看其他扩展如何编写的，并与他人讨论。讨论地点为
`Discord Chat`_ 或者 `GitHub Discussions`_ 。

一个好的扩展应当共享共同的模式。只有在一开头就共享，才能有效地协作。


命名
------

Flask 扩展通常把 ``flask`` 作为前缀或后缀。如果它包裹了另一个库，那么
在其名称中应当体现出被包裹库的名称。这样便于搜索，也可以明确扩展的功
能。


一般来说， Python 包建议是包索引中的安装名称和 ``import`` 语句中使用
的名称应当是相关联的。导入名称为小写，单词之间用下划线（ ``_`` ）分
隔。安装名称为小写或标题大小写，单词用短划线（ ``_`` ）分隔。如果它包
裹了另一个库，首选使用与该库名称相同的大小写。

下面是一些安装和导入名称示例：

-   ``Flask-Name`` imported as ``flask_name``
-   ``flask-name-lower`` imported as ``flask_name_lower``
-   ``Flask-ComboName`` imported as ``flask_comboname``
-   ``Name-Flask`` imported as ``name_flask``


扩展类和初始化
--------------------------------------

任何扩展都需要为应用提供一个入口点来初始化扩展。最常见的模式是创建一
个类，用于扩展的配置和行为。该类具有一个 ``init_app`` 方法，用于向指
定的应用实例提供该扩展的实例。

.. code-block:: python

    class HelloExtension:
        def __init__(self, app=None):
            if app is not None:
                self.init_app(app)

        def init_app(self, app):
            app.before_request(...)

重要的是应用不要存储在扩展上，不要使用 ``self.app = app`` 。扩展直接
访问应用的唯一一次是在 ``init_app`` 中，其他时候应使用
:data: `current_app` 。

这样做，扩展可以支持应用工厂模式，避免导入扩展实例时出现循环导入问题，
并且便于使用不同配置进行测试。

.. code-block:: python

    hello = HelloExtension()

    def create_app():
        app = Flask(__name__)
        hello.init_app(app)
        return app

上例中， ``hello`` 扩展实例独立于应用。这意味着用户项目中的其他模块可
以执行 ``from project import hello`` ，并且可以在应用存在之前，在蓝图
中使用该扩展。

:attr:`Flask.extensions` 字典可用于存储应用扩展的引用或者其他状态。
请注意，这是一个单一的命名空间，因此请使用一个不同于扩展的独立的名称，
例如扩展的名称去掉” flask “前缀。


添加行为
---------------

扩展可以通过多种方式添加行为。任何可用于 :class:`Flask` 对象的都可以
在扩展的 ``init_app`` 方法中使用。

一种常见的模式是使用 :meth:`~Flask.before_request` 来初始化每个请求开
头的一些数据或连接，最后在 :meth:`~Flask.teardown_request` 中进行清理。
这可以存储在 :data:`g` 中，下面将详细讨论。

更懒惰的做法是提供一个方法，用于初始化和缓存数据或连接。
例如， ``ext.get_db`` 方法可以在首次调用时创建一个数据库连接。这样，
不使用数据库的视图就不会创建数据库的连接。

除了在每个视图之前和之后执行某些操作外，扩展程序可能还想添加一些特定
的视图。在这种情况下，您可以定义一个 :class:`Blueprint` ，然后在
``init_app`` 中调用 :meth:`~Flask.register_blueprint` ，将蓝图添加到
应用程序。


配置技术
------------------------

扩展的配置需要面对不同的层次和资源，所以需要仔细推敲。

-   ``app.config`` 的值对应每个应用实例的配置。这个配置可以在每次部署
    应用的时候初需变动。一个常见的例子是用于配置一个外部资源的 URL ，
    比如一个数据库的 URL 。配置键应当以扩展名开头，这样就不会被其他扩
    展干扰。
-   ``__init__`` 参数对应每个扩展实例的配置。
    此配置通常会影响扩展的使用方式，不会在每次部署时改变。
-   实例属性和装饰器方法对应每个扩展实例的配置。
    在扩展实例被创建之后，给 ``ext.value`` 赋值或使用
    ``@ext.register`` 装饰器来注册一个函数更加合理。
-   类属性对应全局配置。更改类似 ``Ext.connection_class`` 这样的类属
    性可以不创建子类而改变缺省行为。这可以结合每个扩展的配置来覆盖默
    认值。
-   子类化和重写方法和属性。
    使得扩展本身的 API 可以被重写，可以为高级定制提供一个非常强大的工
    具。

:class:`~flask.Flask` 对象本身使用所有这些技术。

你可以根据需求来决定什么配置适合你。

在应用程序设置阶段完成和服务器开始处理请求之后，不应改变配置。配置是
全局的，对它的任何改变都不能保证对其他工作者可见。


请求期间的数据
---------------------

在编写 Flask 应用程序时， :data:`~flask.g` 对象被用来存储请求期间的信
息。例如 :doc:`tutorial <tutorial/database>` 存储一个连接到 SQLite
数据库的连接为 ``g.db`` 。扩展也可以使用这个，但要注意。由于 ``g`` 是
一个单一的全局命名空间，扩展必须使用唯一的名称，以免与用户数据相冲突。
例如，将扩展的名称作为前缀，或者作为命名空间。

.. code-block:: python

    # an internal prefix with the extension name
    g._hello_user_id = 2

    # or an internal prefix as a namespace
    from types import SimpleNamespace
    g._hello = SimpleNamespace()
    g._hello.user_id = 2


``g`` 中的数据在一个应用情境中持续存在。当一个请求情境被激活，或者一
个 CLI 命令被执行时，一个应用情境被激活。如果你要关闭存储的东西，请使
用 :meth:`~flask.Flask.teardown_appcontext` 来确保它在应用情境结束时
被关闭。如果它只应当在一个请求期间有效，或者不会在请求之外的 CLI 中使
用，请使用 :meth:`~flask.Flask.teardown_request` 。


视图和模型
----------------

你的扩展视图可能想与数据库中的特定模型或与应用程序相连的其他扩展或数
据进行交互。

例如，让我们假设一个 ``Flask-SimpleBlog`` 扩展，它与 Flask-SQLAlchemy
一起工作，提供了一个 ``Post`` 模型和一个和视图来写入和读取帖子。

``Post`` 模型需要子类化 Flask-SQLAlchemy 的 ``db.Model`` 对象。但这只
有在你创建了该扩展的实例后才可用。而不是在你的扩展定义其视图的时候。
因此，如何编写视图才能在模型存在之前定义，访问模型？


一种方法是使用 :doc:`views` 。在 ``__init__`` 中，创建模型，然后通过
将模型传递给视图类的 :meth:`~views.View.as_view` 方法创建视图。

.. code-block:: python

    class PostAPI(MethodView):
        def __init__(self, model):
            self.model = model

        def get(self, id):
            post = self.model.query.get(id)
            return jsonify(post.to_json())

    class BlogExtension:
        def __init__(self, db):
            class Post(db.Model):
                id = db.Column(primary_key=True)
                title = db.Column(db.String, nullable=False)

            self.post_model = Post

        def init_app(self, app):
            api_view = PostAPI.as_view(model=self.post_model)

    db = SQLAlchemy()
    blog = BlogExtension(db)
    db.init_app(app)
    blog.init_app(app)


另一种技术是在扩展上使用一个属性，比如上面的 ``self.post_model`` 。将
扩展添加到 ``init_app`` 中的 ``app.extensions`` 中， 然后从视图访问
``current_app.extensions["simple_blog"].post_model`` 。

你可能还想提供基类，以便用户可以提供自己的 ``Post`` 模型，以符合你的
扩展所期望的 API 。这样他们可以实现 ``class Post(blog.BasePost)`` ，
然后设置为 ``blog.post_model`` 。

如你所见，这可能会变得有点复杂。不幸的是，没有完美的解决方案，只有不
同的策略和权衡，这取决于你的需求和定制化程度。幸运的是这种资源依赖性
对于大多数的扩展并不常见。请记住，如果你在设计方面需要帮助，请在我们
的 `Discord Chat`_ 或 `GitHub Discussions`_ 提问。


推荐的扩展指南
--------------------------------


Flask 以前有一个”认证的扩展“的概念，即
在列出扩展之前， Flask维护者会评估其质量、支持和兼容性。

虽然这个列表随着时间的推移变得太难
变得难以维护，但这些准则仍然适用于今天维护和开发的所有
的扩展，因为它们有助于Flask
生态系统保持一致和兼容。

1.  一个扩展需要一个维护者。如果一个扩展的作者想要放弃一个项目那么应
    该找到一个新的项目维护者，并移交仓库、文档、 PyPI 和所有其他服务
    操作权限。 GitHub 上的 `Pallets-Eco`_ 组织允许社区在 Pallets 维护
    者的监督下进行维护。
2.  命名方式为 *Flask-ExtensionName* 或 *ExtensionName-Flask* 。必须
    提供一个且仅一个名为 ``flask_extension_name`` 的软件包或模块。
3.  扩展必须使用开源许可协议。 Python 网络生态系统倾向于使用 BSD 或者
    MIT 协议。协议必须是开源的并且公开可用。
4.  扩展的 API 必须具有以下特点：

    - 它必须支持在同一个 Python 进程中运行的多个应用程序。
      使用 ``current_app`` 而不是 ``self.app`` ，为每个应用实例存储
      配置和状态。
    - 必须能够使用工厂模式来创建应用。使用 ``ext.init_app()`` 模式。

5.  从版本库的克隆中，一个扩展及其依赖关系必须可以在可编辑模式下用
    ``pip install -e .`` 安装。
6.  必须提供可以用普通工具调用的测试，如 ``tox -e py`` 、
    ``nox -s test`` 或 ``pytest`` 。如果不使用 ``tox`` ，那么应在需求
    文件中指定测试的依赖性。测试必须是 sdist 发布的一部分。
7.  文档或项目网站的链接必须出现在PyPI元数据或readme中。文档应该使用
    来自 `Official Pallets Themes`_ 的 Flask 主题。
8.  扩展的依赖不应该使用上界或假设任何特定的版本。应当使用下限来表示
    最小的兼容性支持。例如 ``sqlalchemy>=1.4`` 。
9.  使用 ``python_requires=">=version"`` 说明支持的 Python 版本。
    2023年4月时， Flask 本身支持 Python >=3.8 ，这将随着时间的推移而
    更新。

.. _PyPI: https://pypi.org/search/?c=Framework+%3A%3A+Flask
.. _Discord Chat: https://discord.gg/pallets
.. _GitHub Discussions: https://github.com/pallets/flask/discussions
.. _Official Pallets Themes: https://pypi.org/project/Pallets-Sphinx-Themes/
.. _Pallets-Eco: https://github.com/pallets-eco

