配置管理
========

应用总是需要一定的配置的。根据应用环境不同，会需要不同的配置。比如开关
调试模式、设置密钥以及其他依赖于环境的东西。

Flask 的设计思路是在应用开始时载入配置。你可以在代码中直接硬编码写入配
置，对于许多小应用来说这不一定是一件坏事，但是还有更好的方法。

不管你使用何种方式载入配置，都可以使用 :class:`~flask.Flask` 对象的
:attr:`~flask.Flask.config` 属性来操作配置的值。 Flask 本身就使用这个对
象来保存一些配置，扩展也可以使用这个对象保存配置。同时这也是你保存配置
的地方。


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
        SECRET_KEY='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf
    )


调试模式
------------------------------

:data:`DEBUG` 是一个特殊的配置值，因为这个值如果在应用设置完成之后改变，
那么可能表现出不同的行为。为了获得可靠的调试模式，应当在 ``flask`` 命令
上使用 ``--debug`` 参数或者使用 ``flask run`` 命令。 ``flask run`` 命令
默认在调试模式下使用交互调试器和重载器。

.. code-block:: text
 
    $ flask --app hello run --debug

推荐使用参数。尽管可以在你的配置中或者代码中设置 :data:`DEBUG` ，但是强
烈不推荐这样做。因为它们不能被 ``flask run`` 命令提前使用，并且一些系统
或扩展可能会根据前面的值来配置自己。 


内置配置变量
----------------------------

以下配置变量由 Flask 内部使用：

.. py:data:: DEBUG

    是否开启调试模式。使用 ``flask run`` 启动开发服务器时，遇到未能处理
    的异常时会显示一个交互调试器，并且当代码变动后服务器会重启。
    :attr:`~flask.Flask.debug` 属性映射了这个配置键。这是由
    ``FLASK_DEBUG`` 环境变量设置的，如果只是在代码中设置，那么可能会出
    问题。

    缺省值： ``False``

.. py:data:: TESTING

    开启测试模式。异常会被广播而不是被应用的错误处理器处理。扩展可能也
    会为了测试方便而改变它们的行为。你应当在自己的调试中开启本变量。

    缺省值： ``False``

.. py:data:: PROPAGATE_EXCEPTIONS

    异常会重新引发而不是被应用的错误处理器处理。在没有设置本变量的情况
    下，当 ``TESTING`` 或 ``DEBUG`` 开启时，本变量隐式地为真。

    缺省值： ``None``

.. py:data:: TRAP_HTTP_EXCEPTIONS

    如果没有处理 ``HTTPException`` 类型异常的处理器，重新引发该异常用于
    被交互调试器处理，而不是作为一个简单的错误响应来返回。

    缺省值： ``False``

.. py:data:: TRAP_BAD_REQUEST_ERRORS

    尝试操作一个请求字典中不存在的键，如 ``args`` 和 ``form`` ，会返回
    一个 400 Bad Request error 页面。开启本变量，可以把这种错误作为一个
    未处理的异常处理，这样就可以使用交互调试器了。本变量是一个特殊版本
    的 ``TRAP_HTTP_EXCEPTIONS`` 。如果没有设置，本变量会在调试模式下开
    启。

    缺省值： ``None``

.. py:data:: SECRET_KEY

    密钥用于会话 cookie 的安全签名，并可用于应用或者扩展的其他安全需求。
    密钥应当是一个长的随机的 ``bytes`` 或者 ``str`` 。例如，复制下面的
    输出到你的配置中::

        $ python -c 'import secrets; print(secrets.token_hex())'
        '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
 
    **当发贴提问或者提交代码时，不要泄露密钥。**

    缺省值： ``None``

.. py:data:: SESSION_COOKIE_NAME

    会话 cookie 的名称。假如已存在同名 cookie ，本变量可改变。

    缺省值： ``'session'``

.. py:data:: SESSION_COOKIE_DOMAIN
    
    会话 cookie 上的 ``Domain`` 参数值。如果不设置，浏览器将只把
    cookie 发送到它所设定的确切域。否则，它们也会把它发送到给定值的任何
    子域。

    不设置这个值比设置它更有限制性和安全性。

    缺省值： ``None``

    .. versionchanged:: 2.3
        默认情况下不设置，不会回落到 ``SERVER_NAME`` 。

.. py:data:: SESSION_COOKIE_PATH

    认可会话 cookie 的路径。如果没有设置本变量，那么路径为
    ``APPLICATION_ROOT`` ，如果 ``APPLICATION_ROOT`` 也没有设置，那么会
    是 ``/`` 。

    缺省值： ``None``

.. py:data:: SESSION_COOKIE_HTTPONLY

    为了安全，浏览器不会允许 JavaScript 操作标记为“ HTTP only ”的
    cookie 。

    缺省值： ``True``

.. py:data:: SESSION_COOKIE_SECURE

    如果 cookie 标记为“ secure ”，那么浏览器只会使用基于 HTTPS 的请求
    发送 cookie 。应用必须使用 HTTPS 服务来启用本变量。

    缺省值： ``False``

.. py:data:: SESSION_COOKIE_SAMESITE

    限制来自外部站点的请求如何发送 cookie 。可以被设置为 ``'Lax'`` （推
    荐）或者 ``'Strict'`` 。参见 :ref:`security-cookie` 。

    缺省值： ``None``

    .. versionadded:: 1.0

.. py:data:: PERMANENT_SESSION_LIFETIME

    如果 ``session.permanent`` 为真， cookie 的有效期为本变量设置的数字，
    单位为秒。本变量可能是一个 :class:`datetime.timedelta` 或者一个
    ``int`` 。

    Flask 的缺省 cookie 机制会验证电子签章不老于这个变量的值。

    缺省值： ``timedelta(days=31)`` （ ``2678400`` 秒）

.. py:data:: SESSION_REFRESH_EACH_REQUEST

    当 ``session.permanent`` 为真时，控制是否每个响应都发送 cookie 。每
    次都发送 cookie （缺省情况）可以有效地防止会话过期，但是会使用更多
    的带宽。
    会持续会话不受影响。

    缺省值： ``True``

.. py:data:: USE_X_SENDFILE

    当使用 Flask 提供文件服务时，设置 ``X-Sendfile`` 头部。有些网络服务
    器，如 Apache ，识别这种头部，以利于更有效地提供数据服务。本变量只
    有使用这种服务器时才有效。

    缺省值： ``False``

.. py:data:: SEND_FILE_MAX_AGE_DEFAULT

    当提供文件服务时，设置缓存控制最长存活期，以秒为单位。可以是一个
    :class:`datetime.timedelta` 或者一个 ``int`` 。在一个应用或者蓝图上
    使用 :meth:`~flask.Flask.get_send_file_max_age` 可以基于单个文件重
    载本变量。

    如果设置为 ``None`` ，那么 ``send_file`` 会告诉浏览器使用条件请求代
    替一个计时缓存，这样做比较推荐。

    缺省值： ``None``

.. py:data:: SERVER_NAME

    通知应用其所绑定的主机和端口。子域路由匹配需要本变量。

    如果这样配置了， ``url_for`` 可以为应用生成一个单独的外部 URL ，而
    不是一个请求情境。

    缺省值： ``None``

    .. versionchanged:: 2.3
        不影响 ``SESSION_COOKIE_DOMAIN`` 。

.. py:data:: APPLICATION_ROOT

    通知应用应用的根路径是什么。这个变量用于生成请求环境之外的 URL （请
    求内的会根据 ``SCRIPT_NAME`` 生成；参见 :doc:`/patterns/appdispatch`
    ）。

    如果 ``SESSION_COOKIE_PATH`` 没有配置，那么本变量会用于会话 cookie
    路径。

    缺省值： ``'/'``

.. py:data:: PREFERRED_URL_SCHEME

    当不在请求情境内时使用些预案生成外部 URL 。

    缺省值： ``'http'``

.. py:data:: MAX_CONTENT_LENGTH

    在进来的请求数据中读取的最大字节数。如果本变量没有配置，并且请求没
    有指定 ``CONTENT_LENGTH`` ，那么为了安全原因，不会读任何数据。

    缺省值： ``None``

.. py:data:: TEMPLATES_AUTO_RELOAD

    当模板改变时重载它们。如果没有配置，在调试模式下会启用。

    缺省值： ``None``

.. py:data:: EXPLAIN_TEMPLATE_LOADING

    记录模板文件如何载入的调试信息。使用本变量有助于查找为什么模板没有
    载入或者载入了错误的模板的原因。

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
   ``JSON_AS_ASCII`` 、 ``JSON_SORT_KEYS`` 、
   ``JSONIFY_PRETTYPRINT_REGULAR``

.. versionadded:: 0.11
   ``SESSION_REFRESH_EACH_REQUEST``, ``TEMPLATES_AUTO_RELOAD``,
   ``LOGGER_HANDLER_POLICY``, ``EXPLAIN_TEMPLATE_LOADING``

.. versionchanged:: 1.0
    ``LOGGER_NAME`` 和 ``LOGGER_HANDLER_POLICY`` 被删除。关于配置的更多
    内容参见 :doc:`/logging` 。

    添加 :data:`ENV` 来映射 :envvar:`FLASK_ENV` 环境变量。

    添加 :data:`SESSION_COOKIE_SAMESITE` 来控制会话 cookie 的
    ``SameSite`` 选项。

    添加 :data:`MAX_COOKIE_SIZE` 来控制来自于 Werkzeug 警告。

.. versionchanged:: 2.2
    移除 ``PRESERVE_CONTEXT_ON_EXCEPTION``.

.. versionchanged:: 2.3
    ``JSON_AS_ASCII`` 、 ``JSON_SORT_KEYS`` 、 ``JSONIFY_MIMETYPE`` 和
    ``JSONIFY_PRETTYPRINT_REGULAR`` 被移除。默认的 ``app.json`` 提供了
    相等的属性可以替代。

.. versionchanged:: 2.3
    ``ENV`` 被移除。


使用 Python 配置文件
----------------------

如果把配置放在一个单独的文件中会更有用。理想情况下配置文件应当放在应用
包之外。你针对不同的部署使用特定的配置。

常见用法如下::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

首先从 `yourapplication.default_settings` 模块载入配置，然后根据
:envvar:`YOURAPPLICATION_SETTINGS` 环境变量所指向的文件的内容重载配置的
值。在启动服务器前，这个环境变量可以在终端中设置:

.. tabs::

   .. group-tab:: Bash

      .. code-block:: text

         $ export YOURAPPLICATION_SETTINGS=/path/to/settings.cfg
         $ flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: Fish

      .. code-block:: text

         $ set -x YOURAPPLICATION_SETTINGS /path/to/settings.cfg
         $ flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: CMD

      .. code-block:: text

         > set YOURAPPLICATION_SETTINGS=\path\to\settings.cfg
         > flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: Powershell

      .. code-block:: text

         > $env:YOURAPPLICATION_SETTINGS = "\path\to\settings.cfg"
         > flask run
          * Running on http://127.0.0.1:5000/

配置文件本身实质是 Python 文件。只有全部是大写字母的变量才会被配置对象
所使用。因此请确保使用大写字母。

一个配置文件的例子::

    # Example configuration
    SECRET_KEY = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf

请确保尽早载入配置，以便于扩展在启动时可以访问相关配置。除了从文件载入
配置外，配置对象还有其他方法可以载入配置，详见 :class:`~flask.Config`
对象的文档。


使用数据文件来配置
---------------------------

也可以使用 :meth:`~flask.Config.from_file` 从其他格式的文件来加载配置。
例如，从 TOML 文件加载：

.. code-block:: python

    import toml
    app.config.from_file("config.toml", load=toml.load)

或者从 JSON 文件加载：

.. code-block:: python

    import json
    app.config.from_file("config.json", load=json.load)



使用环境变量来配置
--------------------------------------

除了使用环境变量指向配置文件之外，你可能会发现直接从环境中控制配置值很
有用（或者很有必要）。 Flask 可以使用
:meth:`~flask.Config.from_prefixed_env` 来指定载入以特定前缀开头的所有
环境变量。

在启动服务器前，可以在终端中设置环境变量:

.. tabs::

   .. group-tab:: Bash

      .. code-block:: text

         $ export FLASK_SECRET_KEY="5f352379324c22463451387a0aec5d2f"
         $ export FLASK_MAIL_ENABLED=false
         $ flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: Fish

      .. code-block:: text

         $ set -x FLASK_SECRET_KEY "5f352379324c22463451387a0aec5d2f"
         $ set -x FLASK_MAIL_ENABLED false
         $ flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: CMD

      .. code-block:: text

         > set FLASK_SECRET_KEY="5f352379324c22463451387a0aec5d2f"
         > set FLASK_MAIL_ENABLED=false
         > flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: Powershell

      .. code-block:: text

         > $env:FLASK_SECRET_KEY = "5f352379324c22463451387a0aec5d2f"
         > $env:FLASK_MAIL_ENABLED = "false"
         > flask run
          * Running on http://127.0.0.1:5000

这样变量就可以被载入了，使用时键名要去掉前缀。

.. code-block:: python

    app.config.from_prefixed_env()
    app.config["SECRET_KEY"]  # Is "5f352379324c22463451387a0aec5d2f"

缺省的前缀是 ``FLASK_`` 。前缀可以通过
:meth:`~flask.Config.from_prefixed_env` 的 ``prefix`` 参数来变更。

变量在解析的时候会优先转换为更特殊的数据类型，如果无法转换为其他类型，
那么最后会转换为字符串类型。变量解析缺省使用 :func:`json.loads` ，因此
可以使用任何合法的 JSON 值，包括列表和字典。解析的行为是可以自定义的，
通过 :meth:`~flask.Config.from_prefixed_env` 的 ``loads`` 参数可以自定
义解析的行为。

当使用缺省的 JSON 解析时，只有小写的 ``true`` 和 ``false`` 是合法的布尔
值。请牢记，所有非空的字符在 Python 中都会被视为 ``True`` 。

使用双下划线（ ``__`` ）可以设置嵌套的字典，如果嵌套字典的中间键不存
在话会被初始化为空字典。

.. code-block:: text

    $ export FLASK_MYAPI__credentials__username=user123

.. code-block:: python

    app.config["MYAPI"]["credentials"]["username"]  # Is "user123"

在 Windows 系统下，环境变量总是大写的，因此上面的例子最终会变成
``MYAPI__CREDENTIALS__USERNAME`` 。

更多的配置载入功能，包括合并和 Windows 系统中小写变量名的支持等等功能，
请尝试使用其他更专门的库，比如 Dynaconf_ 库。

.. _Dynaconf: https://www.dynaconf.com


配置的最佳实践
----------------------------

前面提到的方法的缺点是它使测试更加困难。一般来说，这个问题没有一个
100％ 完美的解决方案，但你可以牢记几件事以改善这种体验：

1.  在一个函数中创建你的应用并注册“蓝图”。这样就可以使用不同配置创建
    多个实例，极大方便单元测试。你可以按需载入配置。

2.  不要编写在导入时就访问配置的代码。如果你限制自己只能通过请求访问代
    码，那么就可以在以后按需重设配置对象。

3.  确保尽早载入配置，这样扩展就可以在调用 ``init_app`` 时读取配置。


.. _config-dev-prod:

开发/生产
------------------------

大多数应用需要一个以上的配置。最起码需要一个配置用于生产服务器，另一个
配置用于开发。应对这种情况的最简单的方法总是载入一个缺省配置，并把这个
缺省配置作为版本控制的一部分。然后，把需要重载的配置，如前文所述，放在
一个独立的文件中::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

然后你只要增加一个独立的 `config.py` 文件并导出
``YOURAPPLICATION_SETTINGS=/path/to/config.py`` 即可。当然还有其他方法
可选，例如可以使用导入或子类。

在 Django 应用中，通常的做法是在文件的开关增加
``from yourapplication.default_settings import *`` 进行显式地导入，然后
手工重载配置。你还可以通过检查一个 ``YOURAPPLICATION_MODE`` 之类的环境
变量（变量值设置为 `production` 或 `development` 等等）来导入不同的配置
文件。

一个有趣的方案是使用类和类的继承来配置::

    class Config(object):
        TESTING = False

    class ProductionConfig(Config):
        DATABASE_URI = 'mysql://user@localhost/foo'

    class DevelopmentConfig(Config):
        DATABASE_URI = "sqlite:////tmp/foo.db"

    class TestingConfig(Config):
        DATABASE_URI = 'sqlite:///:memory:'
        TESTING = True

如果要使用这样的方案，那么必须使用 :meth:`~flask.Config.from_object`::

    app.config.from_object('configmodule.ProductionConfig')

注意 :meth:`~flask.Config.from_object` 不会实例化类对象。如果要操作已经
实例化的类，比如读取一个属性，那么在调用
:meth:`~flask.Config.from_object` 之前应当先实例化这个类::

    from configmodule import ProductionConfig
    app.config.from_object(ProductionConfig())

    # Alternatively, import via string:
    from werkzeug.utils import import_string
    cfg = import_string('configmodule.ProductionConfig')()
    app.config.from_object(cfg)

在你的配置类中，实例化配置对象时允许使用 ``@property`` ::

    class Config(object):
        """Base config, uses staging database server."""
        TESTING = False
        DB_SERVER = '192.168.1.56'

        @property
        def DATABASE_URI(self):  # Note: all caps
            return f"mysql://user@{self.DB_SERVER}/foo"

    class ProductionConfig(Config):
        """Uses production database server."""
        DB_SERVER = '192.168.19.32'

    class DevelopmentConfig(Config):
        DB_SERVER = 'localhost'

    class TestingConfig(Config):
        DB_SERVER = 'localhost'
        DATABASE_URI = 'sqlite:///:memory:'

配置的方法多种多样，由你定度。以下是一些好的建议：

-   在版本控制中保存一个缺省配置。要么在应用中使用这些缺省配置，要么先导入
    缺省配置然后用你自己的配置文件来重载缺省配置。
-   使用一个环境变量来切换不同的配置。这样就可以在 Python 解释器外进行切换，
    而根本不用改动代码，使开发和部署更方便，更快捷。如果你经常在不同的项目
    间切换，那么你甚至可以创建代码来激活 virtualenv 并导出开发配置。
-   在生产应用中使用 `fabric`_ 之类的工具，向服务器分别传送代码和配置。

.. _fabric: https://www.fabfile.org/


.. _instance-folders:

实例文件夹
----------------

.. versionadded:: 0.8

Flask 0.8 引入了实例文件夹。 Flask 花了很长时间才能够直接使用应用文件夹
的路径（通过 :attr:`Flask.root_path` ）。这也是许多开发者载入应用文件夹
外的配置的方法。不幸的是这种方法只能用于应用不是一个包的情况下，即根路
径指向包的内容的情况。

Flask 0.8 引入了一个新的属性： :attr:`Flask.instance_path` 。它指向一个
新名词：“实例文件夹”。实例文件夹应当处于版本控制中并进行特殊部署。这
个文件夹特别适合存放需要在应用运行中改变的东西或者配置文件。

可以要么在创建 Flask 应用时显式地提供实例文件夹的路径，要么让 Flask 自
动探测实例文件夹。显式定义使用 `instance_path` 参数::

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

        $PREFIX/lib/pythonX.Y/site-packages/myapp
        $PREFIX/var/myapp-instance

    ``$PREFIX`` 是你的 Python 安装的前缀。可能是 ``/usr`` 或你的
    virtualenv 的路径。可以通过打印 ``sys.prefix`` 的值来查看当前的前缀
    的值。

既然可以通过使用配置对象来根据关联文件名从文件中载入配置，那么就可以通
过改变与实例路径相关联的文件名来按需要载入不同配置。在配置文件中的关联
路径的行为可以在 “关联到应用的根路径”（缺省的）和 “关联到实例文件夹”
之间变换，具体通过应用构建函数中的 `instance_relative_config` 来实现::

    app = Flask(__name__, instance_relative_config=True)

以下是一个完整的配置 Flask 的例子，从一个模块预先载入配置，然后从实例文
件夹中的一个配置文件（如果这个文件存在的话）载入要重载的配置::

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_pyfile('application.cfg', silent=True)

通过 :attr:`Flask.instance_path` 可以找到实例文件夹的路径。Flask 还提供
一个打开实例文件夹中的文件的快捷方法：
:meth:`Flask.open_instance_resource` 。

举例说明::

    filename = os.path.join(app.instance_path, 'application.cfg')
    with open(filename) as f:
        config = f.read()

    # or via open_instance_resource:
    with app.open_instance_resource('application.cfg') as f:
        config = f.read()
