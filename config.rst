.. _config:

配置管理
========

应用总是需要一定的配置的。根据应用环境不同，会需要不同的配置。比如开关调试
模式、设置密钥以及其他依赖于环境的东西。

Flask 的设计思路是在应用开始时载入配置。你可以在代码中直接硬编码写入配置，
对于许多小应用来说这不一定是一件坏事，但是还有更好的方法。

不管你使用何种方式载入配置，都可以使用 :class:`~flask.Flask` 对象的
:attr:`~flask.Flask.config` 属性来操作配置的值。 Flask 本身就使用这个对象
来保存一些配置，扩展也可以使用这个对象保存配置。同时这也是你保存配置的地方。


配置入门
--------

:attr:`~flask.Flask.config` 实质上是一个字典的子类，可以像字典一样操作::

    app = Flask(__name__)
    app.config['TESTING'] = True

某些配置值还转移到了 :attr:`~flask.Flask` 对象中，可以直接通过
:attr:`~flask.Flask` 来操作::

    app.testing = True

一次更新多个配置值可以使用 :meth:`dict.update` 方法::

    app.config.update(
        TESTING=True,
        SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/'
    )


环境和调试特征
------------------------------

:data:`ENV` 和 :data:`DEBUG` 配置值是特殊的，因为它们如果在应用设置完成之
后改变，那么可以会有不同的行为表现。为了重可靠的设置环境和调试， Flask 使
用环境变量。

环境用于为 Flask 、扩展和其他程序（如 Sentry ）指明 Flask 运行的情境是什么。
环境由 :envvar:`FLASK_ENV` 环境变量控制，缺省值为 ``production`` 。

把 :envvar:`FLASK_ENV` 设置为 ``development`` 可以打开调试模式。
在调试模式下， ``flask run`` 会缺省使用交互调试器和重载器。如果需要脱离
环境，单独控制调试模式，请使用
:envvar:`FLASK_DEBUG` 标示。

.. versionchanged:: 1.0
    Added :envvar:`FLASK_ENV` to control the environment separately
    from debug mode. The development environment enables debug mode.

为把 Flask 转换到开发环境并开启调试模式，设置 :envvar:`FLASK_ENV`::

    $ export FLASK_ENV=development
    $ flask run

（在 Windows 下，使用 ``set`` 代替 ``export`` 。）

推荐使用如上文的方式设置环境变量。虽然可以在配置或者代码中设置
环境变量无法及时地被 ``flask`` 命令读取，一个系统或者扩展就可能会使用自己
已定义的环境变量。


内置配置变量
----------------------------

以下配置变量由 Flask 内部使用：

.. py:data:: ENV

    应用运行于什么环境。 Flask 和 扩展可以根据环境不同而行为不同，如打开或
    关闭调试模式。 :attr:`~flask.Flask.env` 属性映射了这个配置键。本变量由
    :envvar:`FLASK_ENV` 环境变量设置。如果本变量是在代码中设置的话，可能出
    现意外。

    **在生产环境中不要使用 development 。**

    缺省值： ``'production'``

    .. versionadded:: 1.0

.. py:data:: DEBUG

    是否开启调试模式。使用 ``flask run`` 启动开发服务器时，遇到未能处理的
    异常时会显示一个交互调试器，并且当代码变动后服务器会重启。
    :attr:`~flask.Flask.debug` 属性映射了这个配置键。当 :data:`ENV` 是
    ``'development'`` 时，本变量会启用，并且会被 ``FLASK_DEBUG`` 环境变量
    重载。如果本变量是在代码中设置的话，可能会出现意外。

    **在生产环境中不要开启调试模式。**

    缺省值：当 :data:`ENV` 是 ``'development'`` 时，为 ``True`` ；否则为
    ``False`` 。

.. py:data:: TESTING

    开启测试模式。异常会被广播而不是被应用的错误处理器处理。扩展可能也会为
    了测试方便而改变它们的行为。你应当在自己的调试中开启本变量。

    缺省值： ``False``

.. py:data:: PROPAGATE_EXCEPTIONS

    异常会重新引发而不是被应用的错误处理器处理。在没有设置本变量的情况下，
    当 ``TESTING`` 或 ``DEBUG`` 开启时，本变量隐式地为真。

    缺省值： ``None``

.. py:data:: PRESERVE_CONTEXT_ON_EXCEPTION

    当异常发生时，不要弹出请求情境。在没有设置该变量的情况下，如果
    ``DEBUG`` 为真，则本变量为真。这样允许调试器错误请求数据。本变量通常不
    需要直接设置。

    缺省值： ``None``

.. py:data:: TRAP_HTTP_EXCEPTIONS

    如果没有处理 ``HTTPException`` 类型异常的处理器，重新引发该异常用于被
    交互调试器处理，而不是作为一个简单的错误响应来返回。

    缺省值： ``False``

.. py:data:: TRAP_BAD_REQUEST_ERRORS

    尝试操作一个请求字典中不存在的键，如 ``args`` 和 ``form`` ，会返回一个
    400 Bad Request error 页面。开启本变量，可以把这种错误作为一个未处理的
    异常处理，这样就可以使用交互调试器了。本变量是一个特殊版本的
    ``TRAP_HTTP_EXCEPTIONS`` 。如果没有设置，本变量会在调试模式下开启。

    缺省值： ``None``

.. py:data:: SECRET_KEY

    密钥用于会话 cookie 的安全签名，并可用于应用或者扩展的其他安全需求。本
    变量应当是一个字节型长随机字符串，虽然 unicode 也是可以接受的。例如，
    复制如下输出到你的配置中::

        python -c 'import os; print(os.urandom(16))'
        b'_5#y2L"F4Q8z\n\xec]/'

    **当发贴提问或者提交代码时，不要泄露密钥。**

    缺省值： ``None``

.. py:data:: SESSION_COOKIE_NAME

    会话 cookie 的名称。假如已存在同名 cookie ，本变量可改变。

    缺省值： ``'session'``

.. py:data:: SESSION_COOKIE_DOMAIN

    认可会话 cookie 的域的匹配规则。如果本变量没有设置，那么 cookie 会被
    :data:`SERVER_NAME` 的所有子域认可。如果本变量设置为
    ``False`` ，那么 cookie 域不会被设置。

    缺省值： ``None``

.. py:data:: SESSION_COOKIE_PATH

    认可会话 cookie 的路径。如果没有设置本变量，那么路径为
    ``APPLICATION_ROOT`` ，如果 ``APPLICATION_ROOT`` 也没有设置，那么会是
    ``/`` 。

    缺省值： ``None``

.. py:data:: SESSION_COOKIE_HTTPONLY

    为了安全，浏览器不会允许 JavaScript 操作标记为“ HTTP only ”的 cookie 。

    缺省值： ``True``

.. py:data:: SESSION_COOKIE_SECURE

    如果 cookie 标记为“ secure ”，那么浏览器只会使用基于 HTTPS 的请求发
    送 cookie 。应用必须使用 HTTPS 服务来启用本变量。

    缺省值： ``False``

.. py:data:: SESSION_COOKIE_SAMESITE

    限制来自外部站点的请求如何发送 cookie 。可以被设置为 ``'Lax'`` （推荐）
    或者 ``'Strict'`` 。参见 :ref:`security-cookie`.

    缺省值： ``None``

    .. versionadded:: 1.0

.. py:data:: PERMANENT_SESSION_LIFETIME

    如果 ``session.permanent`` 为真， cookie 的有效期为本变量设置的数字，
    单位为秒。本变量可能是一个 :class:`datetime.timedelta` 或者一个
    ``int`` 。

    Flask 的缺省 cookie 机制会验证电子签章不老于这个变量的值。

    缺省值： ``timedelta(days=31)`` （ ``2678400`` 秒）

.. py:data:: SESSION_REFRESH_EACH_REQUEST

    当 ``session.permanent`` 为真时，控制是否每个响应都发送 cookie 。每次
    都发送 cookie （缺省情况）可以有效地防止会话过期，但是会使用更多的带宽。
    会持续会话不受影响。

    缺省值： ``True``

.. py:data:: USE_X_SENDFILE

    当使用 Flask 提供文件服务时，设置 ``X-Sendfile`` 头部。有些网络服务器，
    如 Apache ，识别这种头部，以利于更有效地提供数据服务。本变量只有使用这
    种服务器时才有效。

    缺省值： ``False``

.. py:data:: SEND_FILE_MAX_AGE_DEFAULT

    当提供文件服务时，设置缓存，控制最长存活期，以秒为单位。可以是一个
    :class:`datetime.timedelta` 或者一个 ``int`` 。在一个应用或者蓝图上使
    用 :meth:`~flask.Flask.get_send_file_max_age` 可以基于单个文件重载本变
    量。

    缺省值： ``timedelta(hours=12)`` （ ``43200`` 秒）

.. py:data:: SERVER_NAME

    通知应用其所绑定的主机和端口。子域路由匹配需要本变量。

    如果配置了本变量， :data:`SESSION_COOKIE_DOMAIN` 没有配置，那么本变量
    会被用于会话 cookie 的域。现代网络浏览器不会允许为没有点的域设置
    cookie 。为了使用一个本地域，可以在你的 ``host`` 文件中为应用路由添加
    任意名称。::

        127.0.0.1 localhost.dev

    如果这样配置了， ``url_for`` 可以为应用生成一个单独的外部 URL ，而不是
    一个请求情境。

    缺省值： ``None``

.. py:data:: APPLICATION_ROOT

    通知应用应用的根路径是什么。

    如果 ``SESSION_COOKIE_PATH`` 没有配置，那么本变量会用于会话 cookie 路
    径。

    缺省值： ``'/'``

.. py:data:: PREFERRED_URL_SCHEME

    当不在请求情境内时使用些预案生成外部 URL 。

    缺省值： ``'http'``

.. py:data:: MAX_CONTENT_LENGTH

    在进来的请求数据中读取的最大字节数。如果本变量没有配置，并且请求没有指
    定 ``CONTENT_LENGTH`` ，那么为了安全原因，不会读任何数据。

    缺省值： ``None``

.. py:data:: JSON_AS_ASCII

    把对象序列化为 ASCII-encoded JSON 。如果禁用，那么 JSON 会被返回为一个
    Unicode 字符串或者被 ``jsonify`` 编码为 ``UTF-8`` 格式。本变量应当保持
    启用，因为在模块内把 JSON 渲染到 JavaScript 时会安全一点。

    缺省值： ``True``

.. py:data:: JSON_SORT_KEYS

    按字母排序 JSON 对象的键。这对于缓存是有用的，因为不管 Python 的哈希种
    子是什么都能够保证数据以相同的方式序列化。为了以缓存为代价的性能提高可
    以禁用它，虽然不推荐这样做。

    缺省值： ``True``

.. py:data:: JSONIFY_PRETTYPRINT_REGULAR

    ``jsonify`` 响应会输出新行、空格和缩进以便于阅读。在调试模式下总是启用
    的。

    缺省值： ``False``

.. py:data:: JSONIFY_MIMETYPE

    ``jsonify`` 响应的媒体类型。

    缺省值： ``'application/json'``

.. py:data:: TEMPLATES_AUTO_RELOAD

    当模板改变时重载它们。如果没有配置，在调试模式下会启用。

    缺省值： ``None``

.. py:data:: EXPLAIN_TEMPLATE_LOADING

    记录模板文件如何载入的调试信息。使用本变量有助于查找为什么模板没有载入
    或者载入了错误的模板的原因。

    缺省值： ``False``

.. py:data:: MAX_COOKIE_SIZE

    当 cookie 头部大于本变量配置的字节数时发出警告。缺省值为 ``4093`` 。
    更大的 cookie 会被浏览器悄悄地忽略。本变量设置为 ``0`` 时关闭警告。

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

.. versionadded:: 0.11
   ``SESSION_REFRESH_EACH_REQUEST``, ``TEMPLATES_AUTO_RELOAD``,
   ``LOGGER_HANDLER_POLICY``, ``EXPLAIN_TEMPLATE_LOADING``

.. versionchanged:: 1.0
    ``LOGGER_NAME`` 和 ``LOGGER_HANDLER_POLICY`` 被删除。关于配置的更多内
    容参见 :ref:`logging` 。

    添加 :data:`ENV` 来映射 :envvar:`FLASK_ENV` 环境变量。

    添加 :data:`SESSION_COOKIE_SAMESITE` 来控制会话 cookie 的 ``SameSite``
    选项。

    添加 :data:`MAX_COOKIE_SIZE` 来控制来自于 Werkzeug 警告。


使用配置文件
----------------------

如果把配置放在一个单独的文件中会更有用。理想情况下配置文件应当放在应用包之
外。这样可以使用不同的工具进行打包与分发（ :ref:`distribute-deployment` ），
而后修改配置文件也没有影响。

因此，常见用法如下::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

首先从 `yourapplication.default_settings` 模块载入配置，然后根据
:envvar:`YOURAPPLICATION_SETTINGS` 环境变量所指向的文件的内容重载配置的值。
在启动服务器前，在 Linux 或 OS X 操作系统中，这个环境变量可以在终端中使用
export 命令来设置::

    $ export YOURAPPLICATION_SETTINGS=/path/to/settings.cfg
    $ python run-app.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader...

在 Windows 系统中使用内置的 `set` 来代替::

    >set YOURAPPLICATION_SETTINGS=\path\to\settings.cfg

配置文件本身实质是 Python 文件。只有全部是大写字母的变量才会被配置对象所使
用。因此请确保使用大写字母。

一个配置文件的例子::

    # Example configuration
    DEBUG = False
    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

请确保尽早载入配置，以便于扩展在启动时可以访问相关配置。除了从文件载入配置外，
配置对象还有其他方法可以载入配置，详见 :class:`~flask.Config` 对象的文档。


使用环境变量来配置
--------------------------------------

除了使用环境变量指向配置文件之外，你可能会发现直接从环境中控制配置值很有用
（或必要）。

启动服务器之前，可以在 Linux 或 OS X 上使用 shell 中的export命令设置环境变
量::

    $ export SECRET_KEY='5f352379324c22463451387a0aec5d2f'
    $ export DEBUG=False
    $ python run-app.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader...

在 Windows 系统中使用内置的 `set` 来代替::

    >set SECRET_KEY='5f352379324c22463451387a0aec5d2f'
    >set DEBUG=False

尽管这种方法很简单易用，但重要的是要记住环境变量是字符串，它们不会自动反序
列化为 Python 类型。

以下是使用环境变量的配置文件示例::

    # Example configuration
    import os

    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", default=False)
    if ENVIRONMENT_DEBUG.lower() in ("f", "false"):
        ENVIRONMENT_DEBUG = False

    DEBUG = ENVIRONMENT_DEBUG
    SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
    if not SECRET_KEY:
        raise ValueError("No secret key set for Flask application")

请注意，除了空字符串之外的任何值都将被解释为 Python 中的布尔值 ``True`` ，
如果环境显式设置值为 ``False`` ，则需要注意。

确保尽早加载配置，以便扩展能够在启动时访问配置。除了从文件加载，配置对象还
有其他方法可以加载。完整的参考参见 :class:`~flask.Config` 类文档。


配置的最佳实践
----------------------------

前面提到的方法的缺点是它使测试更加困难。一般来说，这个问题没有一个 100％
完美的解决方案，但你可以牢记几件事以改善这种体验：

1.  在一个函数中创建你的应用并注册“蓝图”。这样就可以使用不同配置创建多个
    实例，极大方便单元测试。你可以按需载入配置。

2.  不要编写在导入时就访问配置的代码。如果你限制自己只能通过请求访问代码，
    那么就可以在以后按需重设配置对象。


.. _config-dev-prod:

开发/生产
------------------------

大多数应用需要一个以上的配置。最起码需要一个配置用于生产服务器，另一个配置
用于开发。应对这种情况的最简单的方法总是载入一个缺省配置，并把这个缺省配置
作为版本控制的一部分。然后，把需要重载的配置，如前文所述，放在一个独立的文
件中::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

然后你只要增加一个独立的 `config.py` 文件并导出
``YOURAPPLICATION_SETTINGS=/path/to/config.py`` 即可。当然还有其他方法可选，
例如可以使用导入或子类。

在 Django 应用中，通常的做法是在文件的开关增加
``from yourapplication.default_settings import *`` 进行显式地导入，然后手
工重载配置。你还可以通过检查一个 ``YOURAPPLICATION_MODE`` 之类的环境变量（
变量值设置为 `production` 或 `development` 等等）来导入不同的配置文件。

一个有趣的方案是使用类和类的继承来配置::

    class Config(object):
        DEBUG = False
        TESTING = False
        DATABASE_URI = 'sqlite:///:memory:'

    class ProductionConfig(Config):
        DATABASE_URI = 'mysql://user@localhost/foo'

    class DevelopmentConfig(Config):
        DEBUG = True

    class TestingConfig(Config):
        TESTING = True

如果要使用这样的方案，那么必须使用 :meth:`~flask.Config.from_object`::

    app.config.from_object('configmodule.ProductionConfig')

配置的方法多种多样，由你定度。以下是一些好的建议：

-   在版本控制中保存一个缺省配置。要么在应用中使用这些缺省配置，要么先导入
    缺省配置然后用你自己的配置文件来重载缺省配置。
-   使用一个环境变量来切换不同的配置。这样就可以在 Python 解释器外进行切换，
    而根本不用改动代码，使开发和部署更方便，更快捷。如果你经常在不同的项目
    间切换，那么你甚至可以创建代码来激活 virtualenv 并导出开发配置。
-   在生产应用中使用 `fabric`_ 之类的工具，向服务器分别传送代码和配置。更
    多细节参见 :ref:`fabric-deployment` 方案。

.. _fabric: http://www.fabfile.org/


.. _instance-folders:


实例文件夹
----------------

.. versionadded:: 0.8

Flask 0.8 引入了实例文件夹。 Flask 花了很长时间才能够直接使用应用文件夹的
路径（通过 :attr:`Flask.root_path` ）。这也是许多开发者载入应用文件夹外的
配置的方法。不幸的是这种方法只能用于应用不是一个包的情况下，即根路径指向包
的内容的情况。

Flask 0.8 引入了一个新的属性： :attr:`Flask.instance_path` 。它指向一个新
名词：“实例文件夹”。实例文件夹应当处于版本控制中并进行特殊部署。这个文件
夹特别适合存放需要在应用运行中改变的东西或者配置文件。

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

    ``$PREFIX`` 是你的 Python 安装的前缀。可能是 ``/usr`` 或你的
    virtualenv 的路径。可以通过打印 ``sys.prefix`` 的值来查看当前的前缀的
    值。

既然可以通过使用配置对象来根据关联文件名从文件中载入配置，那么就可以通过改
变与实例路径相关联的文件名来按需要载入不同配置。在配置文件中的关联路径的行
为可以在 “关联到应用的根路径”（缺省的）和 “关联到实例文件夹”之间变换，
具体通过应用构建函数中的 `instance_relative_config` 来实现::

    app = Flask(__name__, instance_relative_config=True)

以下是一个完整的配置 Flask 的例子，从一个模块预先载入配置，然后从配置文件
夹中的一个配置文件（如果这个文件存在的话）载入要重载的配置::

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_pyfile('application.cfg', silent=True)

通过 :attr:`Flask.instance_path` 可以找到实例文件夹的路径。Flask 还提供一
个打开实例文件夹中的文件的快捷方法： :meth:`Flask.open_instance_resource` 。

举例说明::

    filename = os.path.join(app.instance_path, 'application.cfg')
    with open(filename) as f:
        config = f.read()

    # or via open_instance_resource:
    with app.open_instance_resource('application.cfg') as f:
        config = f.read()
