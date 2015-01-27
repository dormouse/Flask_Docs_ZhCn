.. _tutorial-setup:

步骤 2 ：应用构建代码
==============================

现在我们已经准备好了数据库模式了，下面来创建应用模块。我们把模块命名为
`flaskr.py` ，并放在 `flaskr` 文件夹中。为了方便初学者学习，我们把库的导入与
相关配置放在了一起。对于小型应用来说，可以把配置直接放在模块中。但是更加清晰的
方案是把配置放在一个独立的 `.ini` 或 `.py` 文件中，并在模块中导入配置的值。

在 `flaskr.py` 文件中::

    # all the imports
    import sqlite3
    from flask import Flask, request, session, g, redirect, url_for, \
         abort, render_template, flash

    # configuration
    DATABASE = '/tmp/flaskr.db'
    DEBUG = True
    SECRET_KEY = 'development key'
    USERNAME = 'admin'
    PASSWORD = 'default'

接着创建真正的应用，并用同一文件中的配置来初始化，在 `flaskr.py` 文件中::

    # create our little application :)
    app = Flask(__name__)
    app.config.from_object(__name__)

:meth:`~flask.Config.from_object` 会查看给定的对象（如果该对象是一个字符串就会
直接导入它），搜索对象中所有变量名均为大字字母的变量。在我们的应用中，已经将配
置写在前面了。你可以把这些配置放到一个独立的文件中。

通常，从一个配置文件中导入配置是比较好的做法，我们使用
:meth:`~flask.Config.from_envvar` 来完成这个工作，把上面的
:meth:`~flask.Config.from_object` 一行替换为::

    app.config.from_envvar('FLASKR_SETTINGS', silent=True)

这样做就可以设置一个 :envvar:`FLASKR_SETTINGS` 的环境变量来指定一个配置文件，并
根据该文件来重载缺省的配置。 silent 开关的作用是告诉 Flask 如果没有这个环境变量
不要报错。

`secret_key` （密钥）用于保持客户端会话安全，请谨慎地选择密钥，并尽可能的使它
复杂而且不容易被猜到。 DEBUG 标志用于开关交互调试器。因为调试模式允许用户执行
服务器上的代码，所以 *永远不要在生产环境中打开调试模式* ！

我们还添加了一个方便连接指定数据库的方法。这个方法可以用于在请求时打开连接，也
可以用于 Python 交互终端或代码中。以后会派上用场。

::

    def connect_db():
        return sqlite3.connect(app.config['DATABASE'])

最后，在文件末尾添加以单机方式启动服务器的代码::

    if __name__ == '__main__':
        app.run()

到此为止，我们可以顺利运行应用了。输入以下命令开始运行::

   python flaskr.py

你会看到服务器已经运行的信息，其中包含应用访问地址。

因为我们还没创建视图，所以当你在浏览器中访问这个地址时，会得到一个 404 页面未
找到错误。很快我们就会谈到视图，但我们先要弄好数据库。

.. admonition:: 外部可见的服务器

   想让你的服务器被公开访问？详见 :ref:`外部可见的服务器 <public-server>` 。

下面请阅读 :ref:`tutorial-dbinit` 。
