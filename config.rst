.. _config:

配置管理
========

.. versionadded:: 0.3

应用总是需要一定的配置的。根据应用环境不同，会需要不同的配置。比如开关调试
模式、设置密钥以及其他依赖于环境的东西。

Flask 的设计思路是在应用开始时载入配置。你可以在代码中直接硬编码写入配置，对于
许多小应用来说这不一定是一件坏事，但是还有更好的方法。

不管你使用何种方式载入配置，都可以使用 :class:`~flask.Flask` 的
:attr:`~flask.Flask.config` 属性来操作配置的值。 Flask 本身就使用这个对象来保存
一些配置，扩展也可以使用这个对象保存配置。同时这也是你保存配置的地方。

配置入门
--------------------

:attr:`~flask.Flask.config` 实质上是一个字典的子类，可以像字典一样操作::

    app = Flask(__name__)
    app.config['DEBUG'] = True

某些配置值还转移到了 :attr:`~flask.Flask` 对象中，可以直接通过
:attr:`~flask.Flask` 来操作::

    app.debug = True

一次更新多个配置值可以使用 :meth:`dict.update` 方法::

    app.config.update(
        DEBUG=True,
        SECRET_KEY='...'
    )

内置配置变量
----------------------------

以下配置变量由 Flask 内部使用：

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

================================= =========================================
``DEBUG``                         开关调试模式
``TESTING``                       开关测试模式
``PROPAGATE_EXCEPTIONS``          显式开关异常的传播。当 `TESTING` 或
                                  `DEBUG` 为真时，总是开启的。
``PRESERVE_CONTEXT_ON_EXCEPTION`` 缺省情况下，如果应用在调试模式下运行，
                                  那么请求环境在发生异常时不会被弹出，以
                                  方便调试器内省数据。可以通过这个配置来
                                  禁止这样做。还可以使用这个配置强制不执行
                                  调试，这样可能有助于调试生产应用（风险
                                  大）。
``SECRET_KEY``                    密钥
``SESSION_COOKIE_NAME``           会话 cookie 的名称
``SESSION_COOKIE_DOMAIN``         会话 cookie 的域。如果没有配置，那么
                                  ``SERVER_NAME`` 的所有子域都可以使用
                                  这个 cookie 。
``SESSION_COOKIE_PATH``           会话 cookie 的路径。如果没有配置，那么
                                  所有 ``APPLICATION_ROOT`` 都可以使用
                                  cookie 。如果没有设置
                                  ``APPLICATION_ROOT`` ，那么 ``'/'`` 可以
                                  使用 cookie 。
``SESSION_COOKIE_HTTPONLY``       设置 cookie 的 httponly 标志，缺省为
                                  `True` 。
``SESSION_COOKIE_SECURE``         设置 cookie 的安全标志，缺省为
                                  `False` 。
``PERMANENT_SESSION_LIFETIME``    常驻会话的存活期，其值是一个
                                  :class:`datetime.timedelta` 对象。
                                  自 Flask 0.8 开始，其值可以是一个整数，
                                  表示秒数。
``USE_X_SENDFILE``                开关 x-sendfile
``LOGGER_NAME``                   日志记录器的名称
``SERVER_NAME``                   服务器的名称和端口号，用于支持子域（如：
                                  ``'myapp.dev:5000'`` ）。注意设置为
                                  “ localhost ”没有用，因为 localhost 不
                                  支持子域。设置了 ``SERVER_NAME`` 后，在
                                  缺省情况下会启用使用应用环境而不使用请求
                                  环境的 URL 生成。
``APPLICATION_ROOT``              如果应用不占用整个域或子域，那么可以用
                                  这个配置来设定应用的路径。这个配置还用作
                                  会话 cookie 的路径。如果使用了整个域，
                                  那么这个配置的值应当为 ``None`` 。
``MAX_CONTENT_LENGTH``            这个配置的值单位为字节，如果设置了，那么
                                  Flask 会拒绝超过设定长度的请求，返回一个
                                  413 状态码。
``SEND_FILE_MAX_AGE_DEFAULT``     :meth:`~flask.Flask.send_static_file` （
                                  缺省静态文件处理器）和
                                  :func:`~flask.send_file` 使用的缺省缓存
                                  最大存活期控制，以秒为单位。把
                                  :meth:`~flask.Flask.get_send_file_max_age`
                                  分别挂勾到 :class:`~flask.Flask` 或
                                  :class:`~flask.Blueprint` 上，可以重载每个
                                  文件的值。缺省值为 43200 （ 12 小时）。
``TRAP_HTTP_EXCEPTIONS``          如果设置为 ``True`` ，那么 Flask 将不
                                  执行 HTTP 异常的错误处理，而是把它像其它
                                  异常同样对待并把它压入异常堆栈。当你在
                                  必须查找出一个 HTTP 异常来自哪里的情况下
                                  这个 配置比较有用。
``TRAP_BAD_REQUEST_ERRORS``       Werkzeug 用于处理请求特殊数据的内部数据
                                  结构会引发坏请求异常。同样，许多操作为了
                                  一致性会使用一个坏请求隐藏操作失败。在
                                  这种情况下，这个配置可以在调试时辨别到底
                                  为什么会失败。如果这个配置设为
                                  ``True`` ，那么就只能得到一个普通的反馈。
``PREFERRED_URL_SCHEME``          在没有可用的模式的情况下， URL 生成所
                                  使用的 URL 模式。缺省值为 ``http`` 。
``JSON_AS_ASCII``                 缺省情况下 Flask 把对象序列化为
                                  ascii-encoded JSON 。如果这个参数值为
                                  ``False`` ，那么 Flask 就不会把对象编码
                                  为 ASCII ，只会原样输出返回 unicode 字符
                                  串。 ``jsonfiy`` 会自动把对象编码
                                  ``utf-8`` 字符用于传输。
``JSON_SORT_KEYS``                缺省情况下 Flask 会按键值排序 JSON 对象，
                                  这是为了确保字典的哈希种子的唯一性，返回
                                  值会保持一致，不会破坏外部 HTTP 缓存。
                                  改变这个参数的值就可以重载缺省的行为，
                                  重载后可能会提高缓存的性能，但是不推荐
                                  这样做。
``JSONIFY_PRETTYPRINT_REGULAR``   如果这个参数设置为 ``True`` （缺省值），
                                  并且如果 jsonify 响应不是被一个
                                  XMLHttpRequest 对象请求的（由
                                  ``X-Requested-With`` 头部控制），那么
                                  就会被完美打印。
================================= =========================================

.. admonition:: 关于 ``SERVER_NAME`` 的更多说明 

   ``SERVER_NAME`` 配置用于支持子域。如果要使用子域，那么就需要这个配置。因为
   Flask 在不知道真正服务器名称的情况下无法得知子域。这个配置也用于会话
   cookie 。

   请记住，不仅 Flask 是在使用子域时有这样的问题，你的浏览器同样如此。大多数
   现代浏览器不会允许在没有点的服务器名称上设置跨子域 cookie 。因此，如果你的
   服务器名称是 ``'localhost'`` ，那么你将不能为 ``'localhost'`` 和所有子域设置
   cookie 。在这种情况下请选择一个其他服务器名称，如
   ``'myapplication.local'`` 。并且把名称加上要使用的子域写入主机配置中或者设置
   一个本地 `bind`_ 。

.. _bind: https://www.isc.org/software/bind

.. versionadded:: 0.4
   ``LOGGER_NAME``

.. versionadded:: 0.5
   ``SERVER_NAME``

.. versionadded:: 0.6
   ``MAX_CONTENT_LENGTH``

.. versionadded:: 0.7
   ``PROPAGATE_EXCEPTIONS``, ``PRESERVE_CONTEXT_ON_EXCEPTION``

.. versionadded:: 0.8
   ``TRAP_BAD_REQUEST_ERRORS``, ``TRAP_HTTP_EXCEPTIONS``,
   ``APPLICATION_ROOT``, ``SESSION_COOKIE_DOMAIN``,
   ``SESSION_COOKIE_PATH``, ``SESSION_COOKIE_HTTPONLY``,
   ``SESSION_COOKIE_SECURE``

.. versionadded:: 0.9
   ``PREFERRED_URL_SCHEME``

.. versionadded:: 0.10
   ``JSON_AS_ASCII``, ``JSON_SORT_KEYS``, ``JSONIFY_PRETTYPRINT_REGULAR``

使用配置文件
----------------------

如果把配置放在一个单独的文件中会更有用。理想情况下配置文件应当放在应用包的
外面。这样可以在修改配置文件时不影响应用的打包与分发（
:ref:`distribute-deployment` ）。

因此，常见用法如下::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

首先从 `yourapplication.default_settings` 模块载入配置，然后根据
:envvar:`YOURAPPLICATION_SETTINGS` 环境变量所指向的文件的内容重载配置的值。在
启动服务器前，在 Linux 或 OS X 操作系统中，这个环境变量可以在终端中使用
export 命令来设置::

    $ export YOURAPPLICATION_SETTINGS=/path/to/settings.cfg
    $ python run-app.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader...

在 Windows 系统中使用内置的 `set` 来代替::

    >set YOURAPPLICATION_SETTINGS=\path\to\settings.cfg

配置文件本身实质是 Python 文件。只有全部是大写字母的变量才会被配置对象所使用。
因此请确保使用大写字母。

一个配置文件的例子::

    # 配置示例
    DEBUG = False
    SECRET_KEY = '?\xbf,\xb4\x8d\xa3"<\x9c\xb0@\x0f5\xab,w\xee\x8d$0\x13\x8b83'

请确保尽早载入配置，以便于扩展在启动时可以访问相关配置。除了从文件载入配置外，
配置对象还有其他方法可以载入配置，详见 :class:`~flask.Config` 对象的文档。


配置的最佳实践
----------------------------

前述的方法的缺点是测试有一点点麻烦。通常解决这个问题没有标准答案，但有些好的
好的建议：

1.  在一个函数中创建你的应用并注册“蓝图”。这样就可以使用不同配置创建多个
    实例，极大方便单元测试。你可以按需载入配置。

2.  不要编写在导入时就访问配置的代码。如果你限制自己只能通过请求访问代码，那么
    你可以以后按需配置对象。


开发/生产
------------------------

大多数应用需要一个以上的配置。最起码需要一个配置用于生产服务器，另一个配置用于
开发。应对这种情况的最简单的方法总是载入一个缺省配置，并把这个缺省配置作为版本
控制的一部分。然后，把需要重载的配置，如前文所述，放在一个独立的文件中::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

然后你只要增加一个独立的 `config.py` 文件并导出
``YOURAPPLICATION_SETTINGS=/path/to/config.py`` 就可了。当然还有其他方法可选，
例如可以使用导入或子类。

在 Django 应用中，通常的做法是在文件的开关增加
``from yourapplication.default_settings import *`` 进行显式地导入，然后手工重载
配置。你还可以通过检查一个 ``YOURAPPLICATION_MODE`` 之类的环境变量（变量值设置
为 `production` 或 `development` 等等）来导入不同的配置文件。

一个有趣的方案是使用类和类的继承来配置::

    class Config(object):
        DEBUG = False
        TESTING = False
        DATABASE_URI = 'sqlite://:memory:'

    class ProductionConfig(Config):
        DATABASE_URI = 'mysql://user@localhost/foo'

    class DevelopmentConfig(Config):
        DEBUG = True

    class TestingConfig(Config):
        TESTING = True

如果要使用这样的方案，那么必须使用
:meth:`~flask.Config.from_object`::

    app.config.from_object('configmodule.ProductionConfig')

配置的方法多种多样，由你定度。以下是一些建议：

-   在版本控制中保存一个缺省配置。要么在应用中使用这些缺省配置，要么先导入缺省
    配置然后用你自己的配置文件来重载缺省配置。
-   使用一个环境变量来切换不同的配置。这样就可以在 Python 解释器外进行切换，而
    根本不用改动代码，使开发和部署更方便，更快捷。如果你经常在不同的项目间
    切换，那么你甚至可以创建代码来激活 virtualenv 并导出开发配置。
-   在生产应用中使用 `fabric`_ 之类的工具，向服务器分别传送代码和配置。更多细节
    参见 :ref:`fabric-deployment` 方案。

.. _fabric: http://fabfile.org/


.. _instance-folders:

实例文件夹
----------------

.. versionadded:: 0.8

Flask 0.8 引入了实例文件夹。 Flask 花了很长时间才能够直接使用应用文件夹的路径（
通过 :attr:`Flask.root_path` ）。这也是许多开发者载入应用文件夹外的配置的方法。
不幸的是这种方法只能用于应用不是一个包的情况下，即根路径指向包的内容的情况。

Flask 0.8 引入了一个新的属性： :attr:`Flask.instance_path` 。它指向一个新名词：
“实例文件夹”。实例文件夹应当处于版本控制中并进行特殊部署。这个文件夹特别适合
存放需要在应用运行中改变的东西或者配置文件。

可以要么在创建 Flask 应用时显式地提供实例文件夹的路径，要么让 Flask 自动探测
实例文件夹。显式定义使用 `instance_path` 参数::

    app = Flask(__name__, instance_path='/path/to/instance/folder')

请记住，这里提供的路径 *必须* 是绝对路径。

如果 `instance_path` 参数没有提供，那么会使用以下缺省位置：

-   未安装的模块::

        /myapp.py
        /instance

-   未安装的包::

        /myapp
            /__init__.py
        /instance

-   已安装的模块或包::

        $PREFIX/lib/python2.X/site-packages/myapp
        $PREFIX/var/myapp-instance

    ``$PREFIX`` 是你的 Python 安装的前缀。可能是 ``/usr`` 或你的 virtualenv 的
    路径。可以通过打印 ``sys.prefix`` 的值来查看当前的前缀的值。

既然可以通过使用配置对象来根据关联文件名从文件中载入配置，那么就可以通过改变与
实例路径相关联的文件名来按需要载入不同配置。在配置文件中的关联路径的行为可以在
“关联到应用的根路径”（缺省的）和 “关联到实例文件夹”之间变换，具体通过应用
构建函数中的 `instance_relative_config` 来实现::

    app = Flask(__name__, instance_relative_config=True)

以下是一个完整的配置 Flask 的例子，从一个模块预先载入配置，然后从配置文件夹中的
一个配置文件（如果这个文件存在的话）载入要重载的配置::

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_pyfile('application.cfg', silent=True)

通过 :attr:`Flask.instance_path` 可以找到实例文件夹的路径。
Flask 还提供一个打开实例文件夹中的文件的快捷方法：
:meth:`Flask.open_instance_resource` 。

举例说明::

    filename = os.path.join(app.instance_path, 'application.cfg')
    with open(filename) as f:
        config = f.read()

    # 或者通过使用 open_instance_resource:
    with app.open_instance_resource('application.cfg') as f:
        config = f.read()
