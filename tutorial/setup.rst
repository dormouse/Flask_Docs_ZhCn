.. _tutorial-setup:

步骤 2 ：应用设置代码
==============================

现在我们已经准备好了数据库模式了，下面来创建应用模块： :file:`flaskr.py`。这个文件
应当放在 :file:`flaskr/flaskr` 文件夹中。应用开头的几行代码的功能是导入必要的包。
随后的几行代码的功能是进行应用的设置。对于像 ``flaskr`` 这样的小型应用来说，可以把配置
直接放在模块中。但是更加清晰的方案是把配置放在一个独立的 `.ini` 或 `.py` 文件中，并在
模块中导入配置的值。

下列是导入包的代码（位于 :file:`flaskr.py` 的开头）::

    # all the imports
    import os
    import sqlite3
    from flask import Flask, request, session, g, redirect, url_for, abort, \
         render_template, flash

随后的代码会创建真正的应用实例并且根据配置来进行初始化，配置同样存放在
:file:`flaskr.py` 文件中：

.. sourcecode:: python

    app = Flask(__name__) # create the application instance :)
    app.config.from_object(__name__) # load config from this file , flaskr.py

    # Load default config and override config from an environment variable
    app.config.update(dict(
        DATABASE=os.path.join(app.root_path, 'flaskr.db'),
        SECRET_KEY='development key',
        USERNAME='admin',
        PASSWORD='default'
    ))
    app.config.from_envvar('FLASKR_SETTINGS', silent=True)

:class:`~flask.Config` 对象与字典差不多，因此可以使用新的值来更新。

.. admonition:: 数据库的路径

    操作系统会掌握每个进程的当前工作路径，但是网络应用就难说了，因为可能有多个应用使用同一个
    进程。

    因此，使用 ``app.root_path`` 属性可以获得应用的当前工作路径。然后结合
    ``os.root_path`` 模块就可以轻松定位文件了。在本教程中，我们会把数据库文件存放在当前
    工作路径中。

    在实际开发中，推荐使用 :ref:`instance-folders` 来代替 ``app.root_path`` 。

通常比较好的做法是载入一个独立的、相应环境的配置文件。 Flask 允许导入多个配置，并且会使用
最后一个导入的配置。使用 :meth:`~flask.Config.from_envvar` 可以增强导入配置的健壮性。

.. sourcecode:: python

   app.config.from_envvar('FLASKR_SETTINGS', silent=True)

只要简单地定义环境变量 :envvar:`FLASKR_SETTINGS` 就可以了，这个变量指向一个已经载入的
配置文件。 ``silent`` 是一个开关参数，这个参数为 ``True`` 时表示让 Flask 在没有设置该
环境变更的键时不要报怨。

除此之外也可以使用配置对象上的 :meth:`~flask.Config.from_object` 方法，并传递一个模块
的导入名作为参数。Flask 会从这个模块初始化变量。注意，变量名必须全部使用大写字母。

为保证客户端会话的安全，``secret_key`` 是必须的。请明智地设置这个参数，使其尽可能的复杂
一点，难猜一点。

最后，将添加一个方法以便于连接指定的数据库。这个方法可以在请求时打开一个数据库连接，
并且在交互式 Python shell 或者脚本中也能使用。 这为以后的操作提供了相当的便利。
我们创建了一个简单的 SQLite 数据库的连接，并让它用 :class:`sqlite3.Row` 对象来表现
数据库中的行。这样就可以通过字典而不是元组的形式访问行。

.. sourcecode:: python

    def connect_db():
        """Connects to the specific database."""
        rv = sqlite3.connect(app.config['DATABASE'])
        rv.row_factory = sqlite3.Row
        return rv

下一节将会学习如何运行应用。

下面请阅读 :ref:`tutorial-packaging` 。
