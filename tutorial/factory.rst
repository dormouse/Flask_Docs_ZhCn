.. currentmodule:: flask

应用设置
=================

一个 Flask 应用是一个 :class:`Flask` 类的实例。应用的所有东西（例如配置
和 URL ）都会和这个实例一起注册。

创建一个 Flask 应用最粗暴直接的方法是在代码的最开始创建一个全局
:class:`Flask` 实例。前面的 "Hello, World!" 示例就是这样做的。有的情况
下这样做是简单和有效的，但是当项目越来越大的时候就会有些力不从心了。

可以在一个函数内部创建 :class:`Flask` 实例来代替创建全局实例。这个函数被
称为 *应用工厂* 。所有应用相关的配置、注册和其他设置都会在函数内部完成，
然后返回这个应用。


应用工厂
-----------------------

写代码的时候到了！创建 ``flaskr`` 文件夹并且文件夹内添加
``__init__.py`` 文件。 ``__init__.py`` 有两个作用：一是包含应用工厂；二
是告诉 Python  ``flaskr`` 文件夹应当视作为一个包。

.. code-block:: none

    $ mkdir flaskr

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    import os

    from flask import Flask


    def create_app(test_config=None):
        # create and configure the app
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        )

        if test_config is None:
            # load the instance config, if it exists, when not testing
            app.config.from_pyfile('config.py', silent=True)
        else:
            # load the test config if passed in
            app.config.from_mapping(test_config)

        # ensure the instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        # a simple page that says hello
        @app.route('/hello')
        def hello():
            return 'Hello, World!'

        return app

``create_app`` 是一个应用工厂函数，后面的教程中会用到。这个看似简单的函
数其实已经做了许多事情。

#.  ``app = Flask(__name__, instance_relative_config=True)`` 创建
    :class:`Flask` 实例。

    *   ``__name__`` 是当前 Python 模块的名称。应用需要知道在哪里设置路
        径，使用 ``__name__`` 是一个方便的方法。

    *   ``instance_relative_config=True`` 告诉应用配置文件是相对于
        :ref:`instance folder <instance-folders>` 的相对路径。实例文件
        夹在 ``flaskr`` 包的外面，用于存放本地数据（例如配置密钥和数据
        库），不应当提交到版本控制系统。

#.  :meth:`app.config.from_mapping() <Config.from_mapping>` 设置一个应
    用的缺省配置：

    *   :data:`SECRET_KEY` 是被 Flask 和扩展用于保证数据安全的。在开发
        过程中，为了方便可以设置为 ``'dev'`` ，但是在发布的时候应当使用
        一个随机值来重载它。

    *   ``DATABASE`` SQLite 数据库文件存放在路径。它位于 Flask 用于存放
        实例的 :attr:`app.instance_path <Flask.instance_path>` 之内。下
        一节会更详细地学习数据库的东西。

#.  :meth:`app.config.from_pyfile() <Config.from_pyfile>` 使用
    ``config.py`` 中的值来重载缺省配置，如果 ``config.py`` 存在的话。
    例如，当正式部署的时候，用于设置一个正式的 ``SECRET_KEY`` 。

    *   ``test_config`` 也会被传递给工厂，并且会替代实例配置。这样可以
        实现测试和开发的配置分离，相互独立。

#.  :func:`os.makedirs` 可以确保
    :attr:`app.instance_path <Flask.instance_path>` 存在。 Flask 不会自
    动创建实例文件夹，但是必须确保创建这个文件夹，因为 SQLite 数据库文
    件会被保存在里面。

#.  :meth:`@app.route() <Flask.route>` 创建一个简单的路由，这样在继续教
    程下面的内容前你可以先看看应用如何运行的。它创建了 URL ``/hello``
    和一个函数之间的关联。这个函数会返回一个响应，即一个
    ``'Hello, World!'`` 字符串。


运行应用
-------------------

现在可以通过使用 ``flask`` 命令来运行应用。在终端中告诉 Flask 你的应用
在哪里，然后在开发模式下运行应用。请记住，现在还是应当在最顶层的
``flask-tutorial`` 目录下，不是在 ``flaskr`` 包里面。

开发模式下，当页面出错的时候会显示一个交互调试器，并且当你修改代码保存
后会重启服务器。在学习本教程的过程中，你可以一直让它保持运行，只需要刷
新页面就可以了。

.. tabs::

   .. group-tab:: Bash

      .. code-block:: text

         $ export FLASK_APP=flaskr
         $ export FLASK_ENV=development
         $ flask run

   .. group-tab:: Fish

      .. code-block:: text

         $ set -x FLASK_APP flaskr
         $ set -x FLASK_ENV development
         $ flask run

   .. group-tab:: CMD

      .. code-block:: text

         > set FLASK_APP=flaskr
         > set FLASK_ENV=development
         > flask run

   .. group-tab:: Powershell

      .. code-block:: text

         > $env:FLASK_APP = "flaskr"
         > $env:FLASK_ENV = "development"
         > flask run

可以看到类似如下输出内容：

.. code-block:: none

     * Serving Flask app "flaskr"
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: 855-212-761

在浏览器中访问 http://127.0.0.1:5000/hello ，就可以看到 "Hello, World!"
信息。恭喜你， Flask 网络应用成功运行了！

如果其他应用程序已经占用了 5000 端口，那么在启动服务的时候会看到
``OSError: [Errno 98]`` 或者 ``OSError: [WinError 10013]`` 出错信息。
如何处理这个问题，请参阅 :ref:`address-already-in-use` 。

下面请阅读 :doc:`database` 。
