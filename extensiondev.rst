Flask 扩展开发
==============

Flask 作为一个微框架，不可避免地会使用第三方库。使用第三方库时，经常需要做
一些重复工作。为了避免重复劳动， `PyPI`_ 提供了许多扩展。

如果你需要创建自己的扩展，那么本文可以帮助你让扩展立马上线运行。

剖析一个扩展
-----------------------

扩展都放在一个名如 ``flask_something`` 的包中。其中的“ something ”就是扩
展所要连接的库的名称。例如假设你要为 Flask 添加 `simplexml` 库的支持，那么
扩展的包名称就应该是 ``flask_simplexml`` 。

但是，真正扩展的名称（可读名称）应当形如“ Flask-SimpleXML ”。请确保名称
中包含“ Flask ”，并且注意大小写。这样用户就可以在他们的 :file:`setup.py`
文件中注册依赖。

但是扩展具体是怎么样的呢？一个扩展必须保证可以同时在多个 Flask 应用中工
作。这是必要条件，因为许多人为了进行单元测试，会使用类似
:doc:`/patterns/appfactories` 模式来创建应用并且需要支持多套配置。因此，
你的应用支持这种行为非常重要。

最重要的是，扩展必须与一个 :file:`setup.py` 文件一起分发，并且在 PyPI 上注
册。同时，用于开发的检出链接也应该能工作，以便于在 virtualenv 中安装开发版
本，而不是手动下载库。

Flask 扩展必须使用 BSD 或 MIT 或更自由的许可证来许可，这样才能被添加进
Flask 扩展注册表。请记住， Flask 扩展注册表是比较稳健的，并且扩展在发布前
会进行预审是否符合要求。

“ Hello Flaskext! ”
---------------------

好吧，让我们开展创建一个 Flask 扩展。这个扩展的用途是提供最基本的 SQLite3
支持。

首先创建如下结构的文件夹和文件::

    flask-sqlite3/
        flask_sqlite3.py
        LICENSE
        README

以下是最重要的文件及其内容：

setup.py
````````

接下来 :file:`setup.py` 是必需的，该文件用于安装你的 Flask 扩展。文件内容
如下::

    """
    Flask-SQLite3
    -------------

    This is the description for that library
    """
    from setuptools import setup


    setup(
        name='Flask-SQLite3',
        version='1.0',
        url='http://example.com/flask-sqlite3/',
        license='BSD',
        author='Your Name',
        author_email='your-email@example.com',
        description='Very short description',
        long_description=__doc__,
        py_modules=['flask_sqlite3'],
        # if you would be using a package instead use packages instead
        # of py_modules:
        # packages=['flask_sqlite3'],
        zip_safe=False,
        include_package_data=True,
        platforms='any',
        install_requires=[
            'Flask'
        ],
        classifiers=[
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ]
    )

代码相当多，但是你可以从现有的扩展中直接复制/粘贴，并修改相应的内容。

flask_sqlite3.py
````````````````

这个文件是你的扩展的具体实现。但是一个扩展到底是怎么样的？最佳实践是什么？
继续阅读吧。

初始化扩展
----------

许多扩展会需要某种类型的初始化步骤。例如，假设一个应用像文档中建议的一样
（ :doc:`/patterns/sqlite3` ）正在连接到 SQLite 。那么，扩展如何获知应用
对象的名称？

相当简单：你把名称传递给扩展。

推荐两种初始化扩展的方式:

初始化函数：

    如果你的扩展名为 `helloworld` ，那么你可能有一个名为
    ``init_helloworld(app[, extra_args])`` 的函数。该函数用来为应用初始化
    扩展，它可以在处理器之前或之后。

初始化类：

    初始化类与初始化函数的工作方式大致相同，区别是类在以后可以进一步改动。


使用哪种方式取决于你。对于 SQLite 3 扩展，我们会使用基于类的方式，因为这样
可以提供给用户一个用于打开和关闭数据库连接的对象。

当设计类时，重要的一点是使用它们在模块层易于复用。也就是说，对象本身在任何
情况下不应存储任何应用的特定状态，而必须可以在不同的应用之间共享。


扩展的代码
----------

以下是 `flask_sqlite3.py` 的内容，可以复制/粘贴::

    import sqlite3
    from flask import current_app, _app_ctx_stack


    class SQLite3(object):
        def __init__(self, app=None):
            self.app = app
            if app is not None:
                self.init_app(app)

        def init_app(self, app):
            app.config.setdefault('SQLITE3_DATABASE', ':memory:')
            app.teardown_appcontext(self.teardown)

        def connect(self):
            return sqlite3.connect(current_app.config['SQLITE3_DATABASE'])

        def teardown(self, exception):
            ctx = _app_ctx_stack.top
            if hasattr(ctx, 'sqlite3_db'):
                ctx.sqlite3_db.close()

        @property
        def connection(self):
            ctx = _app_ctx_stack.top
            if ctx is not None:
                if not hasattr(ctx, 'sqlite3_db'):
                    ctx.sqlite3_db = self.connect()
                return ctx.sqlite3_db


那么这是这些代码的含义是什么:

1.  ``__init__`` 方法接收应用对象，该对象是可选的。如果提供了该对象，那么
    就调用 ``init_app`` 。
2.  ``init_app`` 方法使得 ``SQLite3`` 对象不需要应用对象就可以实例化。这个
    方法支持工厂模式来创建应用。 ``init_app`` 会配置数据库。如果不提供
    配置，默认配置为内存数据库。此外， ``init_app`` 方法附加了 ``teardown``
    处理器。
3.  接下来，我们定义了 ``connect`` 方法来打开一个数据库连接。
4.  最后，我们添加一个 ``connection`` 属性，首次访问时打开数据库连接，并把
    它存储在环境中。这也是处理资源的推荐方式：在资源第一次使用时获取资源，
    即惰性获取。

    注意这里，我们把数据库连接通过 ``_app_ctx_stack.top`` 附加到应用环境的
    栈顶。扩展应该使用上下文的栈顶来存储它们自己的信息，并使用足够复杂的
    名称。

那么为什么我们决定在此使用基于类的方法？因为我们的扩展是这样使用的::

    from flask import Flask
    from flask_sqlite3 import SQLite3

    app = Flask(__name__)
    app.config.from_pyfile('the-config.cfg')
    db = SQLite3(app)

你可以在视图中这样使用数据库::

    @app.route('/')
    def show_all():
        cur = db.connection.cursor()
        cur.execute(...)

同样，如果在请求之外，可以通过压入应用情境的方法使用数据库::

    with app.app_context():
        cur = db.connection.cursor()
        cur.execute(...)

在 ``with`` 块的末尾，拆卸处理器会自动执行。

另外， ``init_app`` 方法用于在创建应用时支持工厂模式::

    db = SQLite3()
    # Then later on.
    app = create_app('the-config.cfg')
    db.init_app(app)

记住已审核的 Flask 扩展必须支持用工厂模式来创建应用（下面会解释）。

.. admonition:: ``init_app`` 的注意事项

   如你所见， ``init_app`` 不分配 ``app`` 到 ``self`` 。这是故意的！基于
   类的 Flask 扩展必须只在应用传递到构造函数时才在对象上存储应用。这告诉
   扩展：我对使用多个应用没有兴趣。

   当扩展需要找到当前应用，且没有一个指向当前应用的引用时，必须使用
   :data:`~flask.current_app` 环境局部变量或用一种你可以显式传递应用的方法
   更改 API 。
    

使用 _app_ctx_stack
--------------------

在上面的例子中，在每个请求之前，一个 ``sqlite3_db`` 变量被分配到
``_app_ctx_stack.top`` 。在一个视图函数中，这个变量可以使用 ``SQLite3``
的属性 ``connection`` 来访问。在请求解散时， ``sqlite3_db`` 连接被关闭。
通过使用这个模式，在请求持续的期间，可以访问 *相同* 的 sqlite3 数据库连接。


学习借鉴
--------

本文只涉及了一些扩展开发的皮毛。如果想要深入，那么明智的选择是查看 `PyPI`_
上现存的扩展。如果你感到迷失，还可以通过 `邮件列表`_ 和 `Discord 服务`_
学习到优秀的 APIs 。尤其当你要开发一个全新的扩展时，建议先多看多问多听，
这样不仅可以知道别人的需求，同时也避免闭门造车。

谨记：设计优秀的 API 是艰难的。因此请先在邮件列表里介绍你的项目，让其他
开发者在 API 设计上助你一臂之力。

最好的 Flask 扩展是那些共享 API 智慧的扩展，因此越早共享越有效。

已审核的扩展
------------

以前， Flask 有已审核的扩展的概念，主要是审核扩展的支持度和兼容性。但是随着
时间的推移，已审核扩展的清单地维护变得越来越困难了。但是以下对于扩展的指南
仍然有着重要的意义，可以帮助 Flask 生态系统保持一致和兼容。 

0.  一个已审核的 Flask 扩展需要一个维护者。如果一个扩展作者想要放弃项目，
    那么项目应该寻找一个新的维护者，包括移交完整的源码托管和 PyPI 访问。
    如果找不到新的维护者，请赋予 Pallets 核心团队访问权限。
1.  命名模式是 *Flask-ExtensionName* 或者 *ExtensionName-Flask* 。必须
    提供一个名如 ``flask_extension_name`` 的包或者模块。
2.  扩展必须使用 BSD 或者 MIT 许可协议，必须是开源的，属于公共领域的。
3.  扩展的 API 必须具备以下特性:
    
    -   必须支持在同一个 Python 进程中运行的多个应用。每个应用实例的配置和
        状态应当使用 ``current_app`` 储存，而不是 ``self.app`` 。
    -   它必须支持使用工厂模式创建应用。使用 ``ext.init_app()`` 方案。

4.  如果是以克隆方式获得扩展的话，那么扩展的依赖必须可以使用
    ``pip install -e .`` 安装。
5.  必须带有一个可以通过 ``tox -e py`` 或者 ``pytest`` 调用的测试套件。如果
    使用 ``tox`` ，那么测试依赖应当在一个 ``requirements.txt`` 文件中定义。
    测试必须是 sdist 分发的一部分。
6.  扩展的文档必须使用来自 `官方 Pallets 主题`_ 的 ``flask`` 主题。
    PyPI 的元数据或者自述文件中必须包含文档或者项目的链接。
7.  为了获得最大的兼容性，扩展应当支持与 Flask 支持的同样版本的 Python 。
    2020年推荐支持 3.6+ 版本的 Python 。请在 ``setup.py`` 中使用
    ``python_requires=">= 3.6"`` 明确支持的 Python 版本。

.. _PyPI: https://pypi.org/search/?c=Framework+%3A%3A+Flask
.. _邮件列表: https://mail.python.org/mailman/listinfo/flask
.. _Discord 服务: https://discord.gg/pallets
.. _官方 Pallets 主题: https://pypi.org/project/Pallets-Sphinx-Themes/

