.. _api:

API
===

.. module:: flask

本文涵盖了 Flask 的所有接口。对于 Flask 所依赖的外部库，本文阐述了最重要的部分，
同时提供了官方文档的链接。


应用对象
------------------

.. autoclass:: Flask
   :members:
   :inherited-members:


蓝图对象
-----------------

.. autoclass:: Blueprint
   :members:
   :inherited-members:

进来的请求数据
---------------------

.. autoclass:: Request
   :members:

   .. attribute:: form

      一个 :class:`~werkzeug.datastructures.MultiDict` 对象，包含 `POST` 或
      `PUT` 请求的被解析过的表单数据。请记住，有关文件上传的表单数据包含在
      :attr:`files` 属性中。

   .. attribute:: args

      一个 :class:`~werkzeug.datastructures.MultiDict` 对象，包含被解析过的查询
      字符串。（ URL 中问号后面的部分）

   .. attribute:: values

      一个 :class:`~werkzeug.datastructures.CombinedMultiDict` 对象，包含
      :attr:`form` 和 :attr:`args` 的内容。

   .. attribute:: cookies

      一个 :class:`dict` 对象，包含请求传送的所有 cookie 内容。

   .. attribute:: stream

      如果表单数据无法被已知的 MIME 类型编码，那么将以原始形态储存在这个数据流
      中。大多数时候，应当使用 :attr:`data` 来返回字符串形式的数据。流只能返回
      一次数据。

   .. attribute:: headers

      类似于字典对象的进来的请求头部。

   .. attribute:: data

      包含视作为字符串的 Flask 无法处理的 MINE 类型的数据。

   .. attribute:: files

      一个 :class:`~werkzeug.datastructures.MultiDict` 对象，包含 `POST` 或
      `PUT` 请求的上传的文件数据。每个文件被储存为一个 
      :class:`~werkzeug.datastructures.FileStorage` 对象。它基本上类似于一个
      标准的 Python 文件对象，只是多出了一个用于储存到文件系统的
      :meth:`~werkzeug.datastructures.FileStorage.save` 函数。

   .. attribute:: environ

      底层的 WSGI 环境。

   .. attribute:: method

      当前的请求方法（ ``POST`` 、 ``GET`` 等）。

   .. attribute:: path
   .. attribute:: script_root
   .. attribute:: url
   .. attribute:: base_url
   .. attribute:: url_root

      提供搜索当前 URL 的不同方法。假设你的应用侦听以下 URL::

          http://www.example.com/myapplication

      并且用户请求了如下 URL::

          http://www.example.com/myapplication/page.html?x=y

      在这种情况下，上述属性值如下：

      ============= ======================================================
      `path`        ``/page.html``
      `script_root` ``/myapplication``
      `base_url`    ``http://www.example.com/myapplication/page.html``
      `url`         ``http://www.example.com/myapplication/page.html?x=y``
      `url_root`    ``http://www.example.com/myapplication/``
      ============= ======================================================

   .. attribute:: is_xhr

      如果请求由一个 JavaScript `XMLHttpRequest` 触发，则值为 `True` 。只有与
      支持``X-Requested-With`` 头部并且设置为 `XMLHttpRequest` 同时使用时才
      有效。支持的库有 prototype 、 jQuery 和 Mochikit 等。

.. class:: request

   全局 `request` 对象可用于访问进来的请求数据。 Flask 为你解析进来的请求数据，
   然后你可以通过全局对象来访问请求数据。如果你的应用处于多线程环境， Flask 将
   在内部确保从活动线程获得正确的数据。

   请求对象是一个代理。更多信息参见 :ref:`notes-on-proxies` 。

   请求对象是 :class:`~werkzeug.wrappers.Request` 的子类的实例，拥有 Werkzeug
   所定义的所有属性。这里只是对最重要的内容进行概述。


响应对象
----------------

.. autoclass:: flask.Response
   :members: set_cookie, data, mimetype

   .. attribute:: headers

      表现响应对象头部的 :class:`Headers` 对象。

   .. attribute:: status_code

      整数类型的响应状态。


会话
--------

如果你设置了 :attr:`Flask.secret_key` ，那么就可以在 Flask 应用中使用会话。会话
的基本功能是在请求变更的过程中储存信息。 Flask 实现会话的方法是使用一个被标记的
cookie 。因此用户可以查看会话内容，但是不能修改，除非知道密钥。请确保密钥复杂性
和不可测性。

使用 :class:`session` 对象可以访问当前会话：

.. class:: session

   会话对象类似与普通的字典，不同之处在于会话还能追踪修改。

   会话对象是一个代理。更多信息参见 :ref:`notes-on-proxies` 。

   以下属性比较重要：

   .. attribute:: new

      如果会话为新，则值为 `True` ，否则值为 `False` 。

   .. attribute:: modified

      如果会话对象被修改过，则值为 `True` 。这里要注意的是可变结构的变动是不会
      自动修改这个属性的，必须自己手动把这个属性设置为 `True` 。示例::

          # 可变对象（下面的列表）的变动不会自动修改这个属性。
          session['objects'].append(42)
          # 因此需要手动设置这个属性
          session.modified = True

   .. attribute:: permanent

      这个属性如果设置为 `True` ，那么这个会话的存活期为
      :attr:`~flask.Flask.permanent_session_lifetime` 所设定的时间（缺省值为 31
      天。这个属性如果设置为 `False` （缺省情况），那么会话在关闭浏览器时会被
      删除。


会话接口
-----------------

.. versionadded:: 0.8

The session interface provides a simple way to replace the session
implementation that Flask is using.

.. currentmodule:: flask.sessions

.. autoclass:: SessionInterface
   :members:

.. autoclass:: SecureCookieSessionInterface
   :members:

.. autoclass:: NullSession
   :members:

.. autoclass:: SessionMixin
   :members:

.. admonition:: Notice

   The ``PERMANENT_SESSION_LIFETIME`` config key can also be an integer
   starting with Flask 0.8.  Either catch this down yourself or use
   the :attr:`~flask.Flask.permanent_session_lifetime` attribute on the
   app which converts the result to an integer automatically.


Test Client
-----------

.. currentmodule:: flask.testing

.. autoclass:: FlaskClient
   :members:


Application Globals
-------------------

.. currentmodule:: flask

To share data that is valid for one request only from one function to
another, a global variable is not good enough because it would break in
threaded environments.  Flask provides you with a special object that
ensures it is only valid for the active request and that will return
different values for each request.  In a nutshell: it does the right
thing, like it does for :class:`request` and :class:`session`.

.. data:: g

   Just store on this whatever you want.  For example a database
   connection or the user that is currently logged in.

   This is a proxy.  See :ref:`notes-on-proxies` for more information.


Useful Functions and Classes
----------------------------

.. data:: current_app

   Points to the application handling the request.  This is useful for
   extensions that want to support multiple applications running side
   by side.

   This is a proxy.  See :ref:`notes-on-proxies` for more information.

.. autofunction:: has_request_context

.. autofunction:: url_for

.. function:: abort(code)

   Raises an :exc:`~werkzeug.exceptions.HTTPException` for the given
   status code.  For example to abort request handling with a page not
   found exception, you would call ``abort(404)``.

   :param code: the HTTP error code.

.. autofunction:: redirect

.. autofunction:: make_response

.. autofunction:: send_file

.. autofunction:: send_from_directory

.. autofunction:: safe_join

.. autofunction:: escape

.. autoclass:: Markup
   :members: escape, unescape, striptags

Message Flashing
----------------

.. autofunction:: flash

.. autofunction:: get_flashed_messages

Returning JSON
--------------

.. autofunction:: jsonify

.. data:: json

    If JSON support is picked up, this will be the module that Flask is
    using to parse and serialize JSON.  So instead of doing this yourself::

        try:
            import simplejson as json
        except ImportError:
            import json

    You can instead just do this::

        from flask import json

    For usage examples, read the :mod:`json` documentation.

    The :func:`~json.dumps` function of this json module is also available
    as filter called ``|tojson`` in Jinja2.  Note that inside `script`
    tags no escaping must take place, so make sure to disable escaping
    with ``|safe`` if you intend to use it inside `script` tags:

    .. sourcecode:: html+jinja

        <script type=text/javascript>
            doSomethingWith({{ user.username|tojson|safe }});
        </script>

    Note that the ``|tojson`` filter escapes forward slashes properly.

Template Rendering
------------------

.. autofunction:: render_template

.. autofunction:: render_template_string

.. autofunction:: get_template_attribute

Configuration
-------------

.. autoclass:: Config
   :members:

Extensions
----------

.. data:: flask.ext

   This module acts as redirect import module to Flask extensions.  It was
   added in 0.8 as the canonical way to import Flask extensions and makes
   it possible for us to have more flexibility in how we distribute
   extensions.

   If you want to use an extension named “Flask-Foo” you would import it
   from :data:`~flask.ext` as follows::

        from flask.ext import foo

   .. versionadded:: 0.8

Useful Internals
----------------

.. autoclass:: flask.ctx.RequestContext
   :members:

.. data:: _request_ctx_stack

   The internal :class:`~werkzeug.local.LocalStack` that is used to implement
   all the context local objects used in Flask.  This is a documented
   instance and can be used by extensions and application code but the
   use is discouraged in general.

   The following attributes are always present on each layer of the
   stack:

   `app`
      the active Flask application.

   `url_adapter`
      the URL adapter that was used to match the request.

   `request`
      the current request object.

   `session`
      the active session object.

   `g`
      an object with all the attributes of the :data:`flask.g` object.

   `flashes`
      an internal cache for the flashed messages.

   Example usage::

      from flask import _request_ctx_stack

      def get_session():
          ctx = _request_ctx_stack.top
          if ctx is not None:
              return ctx.session

.. autoclass:: flask.blueprints.BlueprintSetupState
   :members:

信号
-------

.. when modifying this list, also update the one in signals.rst

.. versionadded:: 0.6

.. data:: signals_available

   信号系统可用时，其值为 `True` ，说明 `blinker`_ 已经安装好了。

.. data:: template_rendered

   这个信号发送于一个模板被渲染成功后。信号传递的 `template` 是模板的实例，
   `context` 是环境对象是一个字典。

.. data:: request_started

   这个信号发送于请求开始之前，且请求环境设置完成之后。因为请求环境已经绑定，
   所以订阅者可以用标准的全局代理，如 :class:`~flask.request` 来操作请求。

.. data:: request_finished

   这个信号发送于向客户端发送响应之前。信号传递的 `response` 为将要发送的响应。

.. data:: got_request_exception

   这个信号发送于请求进行中发生异常的时候。它的发送 *早于* 标准异常处理介于。
   在调试模式下，虽然没有异常处理，但发生异常时也发送这个信号。信号传递的
   `exception` 是异常对象。

.. data:: request_tearing_down

   这个信号发送于请求崩溃的时候，不管是否引发异常。目前，侦听此信号的函数在一般
   崩溃处理器后调用，但是没有什么东西可用。

.. currentmodule:: None

.. class:: flask.signals.Namespace

   如果 blinker 可用，那么这是一个 :class:`blinker.base.Namespace` 的别名。
   否则就是一个创建假信号的虚拟类。这个类用于需要提供像 Flask 一样的反馈系统的
   Flask 扩展。

   .. method:: signal(name, doc=None)

      如果 blinker 可用，那么创建一个这个命名空间的新信号。否则，返回一个假
      信号。这个假信号有一个发送方法，这个方法不能做任何事，除了在所有操作，
      包括连接时失败，引发一个 :exc:`RuntimeError` 。

.. _blinker: http://pypi.python.org/pypi/blinker

Class Based Views
-----------------

.. versionadded:: 0.7

.. currentmodule:: None

.. autoclass:: flask.views.View
   :members:

.. autoclass:: flask.views.MethodView
   :members:

.. _url-route-registrations:

URL 路由注册
-----------------------

定义路由系统规则一般有三种方法：

1.  使用 :meth:`flask.Flask.route` 装饰器。
2.  使用 :meth:`flask.Flask.add_url_rule` 函数。
3.  通过 :attr:`flask.Flask.url_map` 直接操作底层的 Werkzeug 路由系统。

可以使用尖括号来定义路由中的变量（ ``/user/<username>`` ）。缺省情况下， URL 中
的变量可以是任何不包含斜杠的字符串。可以使用 ``<converter:name>`` 来转换变量。

URL 中的变量会作为关键字参数传递给视图函数。

可以使用以下转换器：

=========== ===============================================
`unicode`   接受任何不包含斜杠的文本（缺省）
`int`       接受整数
`float`     接受浮点数
`path`      与缺省的类似，但是可以接受斜杠
=========== ===============================================

一些示例::

    @app.route('/')
    def index():
        pass

    @app.route('/<username>')
    def show_user(username):
        pass

    @app.route('/post/<int:post_id>')
    def show_post(post_id):
        pass

一个应当注意的细节是 Flask 如何处理尾部斜杠。为了使每个 URL 保持唯一，其处理的
规则如下：

1. 如果 URL 规则的尾部有斜杠，而用户请求没有斜杠，那么会自动加上一个发问斜杠。
2. 如果 URL 规则的尾部没有斜杠，而用户请求有斜杠，那么引发 404 页面未找到错误。

以上规则与网络服务器处理静态文件的规则一致。同时以上规则也保证相对连接可以安全
使用。

同一个函数可以使用多个规则，但是必须保证规则是唯一的。设置规则时还可以定义
缺省值。以下是可接受参数页面的规则定义示例::

    @app.route('/users/', defaults={'page': 1})
    @app.route('/users/page/<int:page>')
    def show_users(page):
        pass

以上规则定义了 ``/users/`` 为第一页的 URL ， ``/users/page/N`` 为第 N 页的 URL 。

以下是 :meth:`~flask.Flask.route` 和 :meth:`~flask.Flask.add_url_rule` 能够接受
的参数。两者唯一不同之处在于前者使用装饰器定义路由参数，后者使用 `view_func`
参数定义视图函数。

=============== ==========================================================
`rule`          字符串格式的 URL 规则。
`endpoint`      已注册的 URL 规则的底端。如果没有显式定义这个参数，那么
                Flask 会假定底端为视图函数的名称。
`view_func`     the function to call when serving a request to the
                provided endpoint.  If this is not provided one can
                specify the function later by storing it in the
                :attr:`~flask.Flask.view_functions` dictionary with the
                endpoint as key.
`defaults`      A dictionary with defaults for this rule.  See the
                example above for how defaults work.
`subdomain`     specifies the rule for the subdomain in case subdomain
                matching is in use.  If not specified the default
                subdomain is assumed.
`**options`     the options to be forwarded to the underlying
                :class:`~werkzeug.routing.Rule` object.  A change to
                Werkzeug is handling of method options.  methods is a list
                of methods this rule should be limited to (`GET`, `POST`
                etc.).  By default a rule just listens for `GET` (and
                implicitly `HEAD`).  Starting with Flask 0.6, `OPTIONS` is
                implicitly added and handled by the standard request
                handling.  They have to be specified as keyword arguments.
=============== ==========================================================

.. _view-func-options:

视图函数选项
---------------------

For internal usage the view functions can have some attributes attached to
customize behavior the view function would normally not have control over.
The following attributes can be provided optionally to either override
some defaults to :meth:`~flask.Flask.add_url_rule` or general behavior:

-   `__name__`: The name of a function is by default used as endpoint.  If
    endpoint is provided explicitly this value is used.  Additionally this
    will be prefixed with the name of the blueprint by default which
    cannot be customized from the function itself.

-   `methods`: If methods are not provided when the URL rule is added,
    Flask will look on the view function object itself is an `methods`
    attribute exists.  If it does, it will pull the information for the
    methods from there.

-   `provide_automatic_options`: if this attribute is set Flask will
    either force enable or disable the automatic implementation of the
    HTTP `OPTIONS` response.  This can be useful when working with
    decorators that want to customize the `OPTIONS` response on a per-view
    basis.

完整的例子::

    def index():
        if request.method == 'OPTIONS':
            # custom options handling here
            ...
        return 'Hello World!'
    index.provide_automatic_options = False
    index.methods = ['GET', 'OPTIONS']

    app.add_url_rule('/', index)

.. versionadded:: 0.8
   添加了 `provide_automatic_options` 功能。
