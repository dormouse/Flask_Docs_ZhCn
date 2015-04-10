.. _extension-dev:

Flask 扩展开发
==============

Flask 作为一个微框架，为了让第三方库可以运作，经常需要做一些重复工作。为了
避免重复劳动，我们创建了 `Flask 扩展注册表`_ ，把这些重复工作进行抽象，使
其可以支持不同项目。

如果你需要创建自己的扩展，那么本文可以帮助你让扩展立马上线运行。

.. _Flask 扩展注册表: http://flask.pocoo.org/extensions/

剖析一个扩展
-----------------------

扩展都放在一个名如 ``flask_something`` 的包中。其中的“ something ”就是
扩展所要连接的库的名称。例如假设你要为 Flask 添加 `simplexml` 库的支持，
那么扩展的包名称就应该是 ``flask_simplexml`` 。

但是，真正扩展的名称（可读名称）应当形如“ Flask-SimpleXML ”。请确保名称
中包含“ Flask ”，并且注意大小写。这样用户就可以在他们的 `setup.py` 文件
中注册依赖。

Flask 设置了一个名为 :data:`flask.ext` 重定向包，用户应当使用这个包来导入
扩展。假设你的扩展包名为 ``flask_something`` ，那么用户应当导入为
``flask.ext.something`` 。这样做是为了从老的命名空间过渡，详见
:ref:`ext-import-transition` 。

但是扩展具体是怎么样的呢？一个扩展必须保证可以同时在多个 Flask 应用中工作。
这是必要条件，因为许多人为了进行单元测试，会使用类似 :ref:`app-factories`
模式来创建应用并且需要支持多套配置。因此，你的应用支持这种行为非常重要。

最重要的是，扩展必须与一个 `setup.py` 文件一起分发，并且在 PyPI 上注册。
同时，用于开发的 checkout 链接也应该能工作，以便于在 virtualenv 中安装开发
版本，而不是手动下载库。

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

接下来 `setup.py` 是必需的，该文件用于安装你的 Flask 扩展。文件内容如下::

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
（ :ref:`sqlite3` ）正在连接到 SQLite 。那么，扩展如何获知应用对象的名称？

相当简单：你把名称传递给扩展。

推荐两种初始化扩展的方式:

初始化函数：

    如果你的扩展名为 `helloworld` ，那么你可能有一个名为
    ``init_helloworld(app[, extra_args])`` 的函数。该函数用来为应用初始化
    扩展，它可以在处理器之前或之后。

初始化类：

    初始化类与初始化函数的工作方式大致相同，区别是类在以后可以进一步改动。
    例如，查看一下 `OAuth 扩展`_ 的工作方式：有一个 `OAuth` 对象提供一些
    辅助函数（比如 `OAuth.remote_app` ）来创建使用 OAuth 的远程应用的引用。


使用哪种方式取决于你。对于 SQLite 3 扩展，我们会使用基于类的方式，因为这样
可以提供给用户一个用于打开和关闭数据库连接的对象。

当使用类初始化方式时，重要的一点是鼓励在模块层内共享。这种情况下，对象本身
在任何情况下不得存储任何应用的特定状态，而必须可以在不同的应用之间共享。


扩展的代码
----------

以下是 `flask_sqlite3.py` 的内容，可以复制/粘贴::

    import sqlite3
    from flask import current_app

    # Find the stack on which we want to store the database connection.
    # Starting with Flask 0.9, the _app_ctx_stack is the correct one,
    # before that we need to use the _request_ctx_stack.
    try:
        from flask import _app_ctx_stack as stack
    except ImportError:
        from flask import _request_ctx_stack as stack


    class SQLite3(object):

        def __init__(self, app=None):
            self.app = app
            if app is not None:
                self.init_app(app)

        def init_app(self, app):
            app.config.setdefault('SQLITE3_DATABASE', ':memory:')
            # Use the newstyle teardown_appcontext if it's available,
            # otherwise fall back to the request context
            if hasattr(app, 'teardown_appcontext'):
                app.teardown_appcontext(self.teardown)
            else:
                app.teardown_request(self.teardown)

        def connect(self):
            return sqlite3.connect(current_app.config['SQLITE3_DATABASE'])

        def teardown(self, exception):
            ctx = stack.top
            if hasattr(ctx, 'sqlite3_db'):
                ctx.sqlite3_db.close()

        @property
        def connection(self):
            ctx = stack.top
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
    处理器。它会试图使用新样式的应用环境处理器，并且如果它不存在，退回到
    请求环境处理器。
3.  接下来，我们定义了 ``connect`` 方法来打开一个数据库连接。
4.  最后，我们添加一个 ``connection`` 属性，首次访问时打开数据库连接，并把
    它存储在环境中。这也是处理资源的推荐方式：在资源第一次使用时获取资源，
    即惰性获取。

    注意这里，我们把数据库连接通过 ``_app_ctx_stack.top`` 附加到应用环境的
    栈顶。扩展应该使用上下文的栈顶来存储它们自己的信息，并使用足够复杂的
    名称。注意如果应用使用的是不支持它的老版本的 Flask 我们退回到
    ``_request_ctx_stack.top`` 。

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

同样地，如果在请求之外，并且使用支持应用环境的 Flask 0.9 或之后的版本，
可以用同样的方式使用数据库::

    with app.app_context():
        cur = db.connection.cursor()
        cur.execute(...)

在 `with` 块的末尾，销毁处理器会自动执行。

另外， ``init_app`` 方法用于在创建应用时支持工厂模式::

    db = Sqlite3()
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

如果 :data:`~flask._app_ctx_stack` 因为用户使用了老版本的 Flask 不存在，
建议退化到绑定在请求中的 :data:`~flask._request_ctx_stack` 。

解散形为
--------

*本段只有在想要支持 Flask 0.6 版本和更老版本时有用*

因为在 Flask 0.7 版本中修改了在请求的最后运行的相关函数，所以如果你的扩展
需要继续支持 Flask 的老版本，那么必须格外小心。下面的模式是一个新旧兼顾的
好方法::

    def close_connection(response):
        ctx = _request_ctx_stack.top
        ctx.sqlite3_db.close()
        return response

    if hasattr(app, 'teardown_request'):
        app.teardown_request(close_connection)
    else:
        app.after_request(close_connection)

严格地讲，上面的代码是错误的，因为解散函数接受异常且典型地不返回任何东西。
然而，因为返回值被丢弃，假设中间的代码不触碰传递的参数，这刚好有用。

学习借鉴
--------

本文只是谈了一些扩展开发的皮毛。如果想要深入，那么查看 `Flask 扩展注册表`_
上已有的扩展是明智的。如果你感到迷失，还可以通过 `邮件列表`_ 和
`IRC 频道`_ 学习到优秀的 APIs 。尤其当你要开发一个全新的扩展时，建议先多看
多问多听，这样不仅可以知道别人的需求，同时也避免多人重复开发。

谨记：设计优秀的 API 是艰难的。因此请先在邮件列表里介绍你的项目，让其他
开发者在 API 设计上助你一臂之力。

最好的 Flask 扩展是那些共享 API 智慧的扩展，因此越早共享越有效。

已审核的扩展
------------

Flask 有已审核的扩展的概念。已审核的扩展会被视作 Flask 的一部分来测试，以
保证扩展在新版本发布时不会出问题。这些已审核的扩展会在 `Flask 扩展注册表`_
中列出，并有相应的标记。如果你想要自己的扩展通过审核，请遵循以下的指导方针：

0.  一个已审核的 Flask 扩展需要一个维护者。如果一个扩展作者想要放弃项目，
    那么项目应该寻找一个新的维护者，包括移交完整的源码托管和 PyPI 访问。
    如果找不到新的维护者，请赋予 Flask 核心团队访问权限。
1.  一个已审核的 Flask 扩展必须提供一个名如 ``flask_extensionname`` 的包或
    模块。它们也可以存在于一个 ``flaskext`` 命名空间包内部，但是现在不推荐
    这么做。
2.  它必须带有测试套件，套件可以使用 ``make test`` 或者
    ``python setup.py test`` 来调用。如果是使用 ``make test`` 调用的测试
    套件，那么必须保证所有的依赖可以自动安装。如果是使用 ``python setup.py
    test`` 调用的测试套件，那么测试的依赖可以在 `setup.py` 文件中定义。
    测试套件分发的必要组成部分。
3.  已审核的扩展的 API 可以通过下面特性的检查:
    
    -   一个已审核的扩展必须支持在同一个 Python 进程中运行的多个应用。
    -   它必须支持使用工厂模式创建应用

4.  许可协议必须是 BSD/MIT/WTFPL 协议。
5.  官方扩展的命名模式是 *Flask-ExtensionName* 或 *ExtensionName-Flask* 。
6.  已审核的扩展必须在 `setup.py` 文件里定义所有的依赖关系，除非在 PyPI
    上不可用。
7.  扩展的文档必须使用两种 Flask 的 Sphinx 文档主题中的一个。
8.  setup.py 描述（即 PyPI 描述）必须链接到文档、网站（如果有的话），
    并且必须有自动安装开发版本的链接（ ``PackageName==dev`` ）。
9.  安装脚本中的 ``zip_safe`` 标志必须被设置为 ``False`` ，即使扩展对于
    压缩是安全的。
10. 现行扩展必须支持 Python 2.6 和 Python 2.7 。


.. _ext-import-transition:

扩展导入的迁移
--------------

一段时间，我们曾推荐对 Flask 扩展使用命名空间包。但这在实践中被证明是有
问题的，因为许多不同命名空间包系统存在竞争，并且 pip 会自动在不同的系统
中切换，这给用户带来了许多问题。

现在，我们推荐命名包为 ``flask_foo`` 替代过时的 ``flaskext.foo`` 。Flask
0.8 引入了重定向导入系统，允许从 ``flask.ext.foo`` 导入，并且如果
``flaskext.foo`` 失败时，会首先尝试 ``flask_foo`` 。

Flask 扩展应该鼓励用户从 ``flask.ext.foo`` 导入，而不是 ``flask_foo``
或 ``flaskext_foo`` ，这样扩展可以迁移到新的包名称而不烦扰用户。


.. _OAuth 扩展: http://packages.python.org/Flask-OAuth/
.. _邮件列表: http://flask.pocoo.org/mailinglist/
.. _IRC 频道: http://flask.pocoo.org/community/irc/

