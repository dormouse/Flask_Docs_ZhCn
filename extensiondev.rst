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
    例如，查看一下 `OAuth extension`_ 的工作方式：有一个 `OAuth` 对象提供
    一些辅助函数（比如 `OAuth.remote_app` ）来创建使用 OAuth 的远程应用的
    引用。


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

In the example above, before every request, a ``sqlite3_db`` variable is
assigned to ``_app_ctx_stack.top``.  In a view function, this variable is
accessible using the ``connection`` property of ``SQLite3``.  During the
teardown of a request, the ``sqlite3_db`` connection is closed.  By using
this pattern, the *same* connection to the sqlite3 database is accessible
to anything that needs it for the duration of the request.

If the :data:`~flask._app_ctx_stack` does not exist because the user uses
an old version of Flask, it is recommended to fall back to
:data:`~flask._request_ctx_stack` which is bound to a request.

Teardown Behavior
-----------------

*This is only relevant if you want to support Flask 0.6 and older*

Due to the change in Flask 0.7 regarding functions that are run at the end
of the request your extension will have to be extra careful there if it
wants to continue to support older versions of Flask.  The following
pattern is a good way to support both::

    def close_connection(response):
        ctx = _request_ctx_stack.top
        ctx.sqlite3_db.close()
        return response

    if hasattr(app, 'teardown_request'):
        app.teardown_request(close_connection)
    else:
        app.after_request(close_connection)

Strictly speaking the above code is wrong, because teardown functions are
passed the exception and typically don't return anything.  However because
the return value is discarded this will just work assuming that the code
in between does not touch the passed parameter.

Learn from Others
-----------------

This documentation only touches the bare minimum for extension
development.  If you want to learn more, it's a very good idea to check
out existing extensions on the `Flask 扩展注册表`_.  If you feel
lost there is still the `mailinglist`_ and the `IRC channel`_ to get some
ideas for nice looking APIs.  Especially if you do something nobody before
you did, it might be a very good idea to get some more input.  This not
only to get an idea about what people might want to have from an
extension, but also to avoid having multiple developers working on pretty
much the same side by side.

Remember: good API design is hard, so introduce your project on the
mailinglist, and let other developers give you a helping hand with
designing the API.

The best Flask extensions are extensions that share common idioms for the
API.  And this can only work if collaboration happens early.

Approved Extensions
-------------------

Flask also has the concept of approved extensions.  Approved extensions
are tested as part of Flask itself to ensure extensions do not break on
new releases.  These approved extensions are listed on the `Flask 扩展注册表`_ and marked appropriately.  If you want your own
extension to be approved you have to follow these guidelines:

0.  An approved Flask extension requires a maintainer. In the event an
    extension author would like to move beyond the project, the project should
    find a new maintainer including full source hosting transition and PyPI
    access.  If no maintainer is available, give access to the Flask core team.
1.  An approved Flask extension must provide exactly one package or module
    named ``flask_extensionname``.  They might also reside inside a
    ``flaskext`` namespace packages though this is discouraged now.
2.  It must ship a testing suite that can either be invoked with ``make test``
    or ``python setup.py test``.  For test suites invoked with ``make
    test`` the extension has to ensure that all dependencies for the test
    are installed automatically.  If tests are invoked with ``python setup.py
    test``, test dependencies can be specified in the `setup.py` file.  The
    test suite also has to be part of the distribution.
3.  APIs of approved extensions will be checked for the following
    characteristics:

    -   an approved extension has to support multiple applications
        running in the same Python process.
    -   it must be possible to use the factory pattern for creating
        applications.

4.  The license must be BSD/MIT/WTFPL licensed.
5.  The naming scheme for official extensions is *Flask-ExtensionName* or
    *ExtensionName-Flask*.
6.  Approved extensions must define all their dependencies in the
    `setup.py` file unless a dependency cannot be met because it is not
    available on PyPI.
7.  The extension must have documentation that uses one of the two Flask
    themes for Sphinx documentation.
8.  The setup.py description (and thus the PyPI description) has to
    link to the documentation, website (if there is one) and there
    must be a link to automatically install the development version
    (``PackageName==dev``).
9.  The ``zip_safe`` flag in the setup script must be set to ``False``,
    even if the extension would be safe for zipping.
10. An extension currently has to support Python 2.6 as well as
    Python 2.7


.. _ext-import-transition:

Extension Import Transition
---------------------------

For a while we recommended using namespace packages for Flask extensions.
This turned out to be problematic in practice because many different
competing namespace package systems exist and pip would automatically
switch between different systems and this caused a lot of problems for
users.

Instead we now recommend naming packages ``flask_foo`` instead of the now
deprecated ``flaskext.foo``.  Flask 0.8 introduces a redirect import
system that lets uses import from ``flask.ext.foo`` and it will try
``flask_foo`` first and if that fails ``flaskext.foo``.

Flask extensions should urge users to import from ``flask.ext.foo``
instead of ``flask_foo`` or ``flaskext_foo`` so that extensions can
transition to the new package name without affecting users.


.. _OAuth extension: http://packages.python.org/Flask-OAuth/
.. _mailinglist: http://flask.pocoo.org/mailinglist/
.. _IRC channel: http://flask.pocoo.org/community/irc/
