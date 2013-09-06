.. _signals:

信号
=======

.. versionadded:: 0.6

Flask 自 0.6 版本开始在内部支持信号。信号功能由优秀的 `blinker`_ 库提供支持，
如果没有安装该库就无法使用信号功能，但不影响其他功能。

什么是信号？当核心框架的其他地方或另一个 Flask 扩展中发生动作时，信号通过发送
通知来帮助你解耦应用。简言之，信号允许某个发送者通知接收者有事情发生了。

Flask 自身有许多信号，其他扩展可能还会带来更多信号。请记住，信号使用目的是通知
接收者，不应该鼓励接收者修改数据。你会注意到信号的功能与一些内建的装饰器类似（
如 :data:`~flask.request_started` 与 :meth:`~flask.Flask.before_request` 非常
相似），但是它们的工作原理不同。例如核心的 :meth:`~flask.Flask.before_request`
处理器以一定的顺序执行，并且可以提前退出请求，返回一个响应。相反，所有的信号
处理器是乱序执行的，并且不修改任何数据。

信号的最大优势是可以安全快速的订阅。比如，在单元测试中这些临时订阅十分有用。
假设你想知道请求需要渲染哪个模块，信号可以给你答案。

订阅信号
----------------------

使用信号的 :meth:`~blinker.base.Signal.connect` 方法可以订阅该信号。该方法的
第一个参数是当信号发出时所调用的函数。第二个参数是可选参数，定义一个发送者。
使用 :meth:`~blinker.base.Signal.disconnect` 方法可以退订信号。

所有核心 Flask 信号的发送者是应用本身。因此当订阅信号时请指定发送者，除非你真的
想要收听应用的所有信号。当你正在开发一个扩展时，尤其要注意这点。

下面是一个环境管理器的辅助工具，可用于在单元测试中辨别哪个模板被渲染了，哪些
变量被传递给了模板::

    from flask import template_rendered
    from contextlib import contextmanager

    @contextmanager
    def captured_templates(app):
        recorded = []
        def record(sender, template, context, **extra):
            recorded.append((template, context))
        template_rendered.connect(record, app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, app)

上例可以在测试客户端中轻松使用::

    with captured_templates(app) as templates:
        rv = app.test_client().get('/')
        assert rv.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'index.html'
        assert len(context['items']) == 10

为了使 Flask 在向信号中添加新的参数时不发生错误，请确保使用一个额外的
``**extra`` 参数。

在 with 代码块中，所有由 `app` 渲染的模板会被记录在 `templates` 变量中。每当有
模板被渲染，模板对象及环境就会追加到变量中。

另外还有一个方便的辅助方法（ :meth:`~blinker.base.Signal.connected_to` ）。它
允许临时把一个使用环境对象的函数订阅到一个信号。因为环境对象的返回值不能被
指定，所以必须把列表作为参数::

    from flask import template_rendered

    def captured_templates(app, recorded, **extra):
        def record(sender, template, context):
            recorded.append((template, context))
        return template_rendered.connected_to(record, app)

上例可以这样使用::

    templates = []
    with captured_templates(app, templates, **extra):
        ...
        template, context = templates[0]

.. admonition:: Blinker API 变化

   Blinker version 1.1 版本中增加了
   :meth:`~blinker.base.Signal.connected_to` 方法。


创建信号
----------------

如果相要在你自己的应用中使用信号，那么可以直接使用 blinker 库。最常见的,也是最
推荐的方法是在自定义的 :class:`~blinker.base.Namespace` 中命名信号::

    from blinker import Namespace
    my_signals = Namespace()

接着可以像这样创建新的信号::

    model_saved = my_signals.signal('model-saved')

信号的名称应当是唯一的，并且应当简明以便于调试。可以通过
:attr:`~blinker.base.NamedSignal.name` 属性获得信号的名称。

.. admonition:: 扩展开发者注意

   如果你正在编写一个 Flask 扩展，并且想要妥善处理 blinker 安装缺失的情况，那么
   可以使用 :class:`flask.signals.Namespace` 类。

.. _signals-sending:

发送信号
---------------

如果想要发送信号，可以使用 :meth:`~blinker.base.Signal.send` 方法。它的第一个
参数是一个发送者，其他参数要发送给订阅者的东西，其他参数是可选的::

    class Model(object):
        ...

        def save(self):
            model_saved.send(self)

请谨慎选择发送者。如果是一个发送信号的类，请把 `self` 作为发送者。如果发送信号
的是一个随机的函数，那么可以把 ``current_app._get_current_object()`` 作为
发送者。

.. admonition:: 传递代理作为发送者

   不要把 :data:`~flask.current_app` 作为发送者传递给信号。请使用
   ``current_app._get_current_object()`` 。因为 :data:`~flask.current_app` 是
   一个代理，不是实际的应用对象。

信号与 Flask 的请求环境
-----------------------------------

信号在接收时，完全支持 :ref:`request-context` 。在
:data:`~flask.request_started` 和 :data:`~flask.request_finished` 本地环境变量
始终可用。因此你可以依赖 :class:`flask.g` 及其他本地环境变量。
请注意在 :ref:`signals-sending` 中所述的限制和
:data:`~flask.request_tearing_down` 信号。

信号订阅装饰器
------------------------------------

Blinker 1.1 版本中你还可以通过使用新的
:meth:`~blinker.base.NamedSignal.connect_via` 装饰器轻松订阅信号::

    from flask import template_rendered

    @template_rendered.connect_via(app)
    def when_template_rendered(sender, template, context, **extra):
        print 'Template %s is rendered with %s' % (template.name, context)

核心信号
------------

.. when modifying this list, also update the one in api.rst

Flask 中有以下信号:

.. data:: flask.template_rendered
   :noindex:

   这个信号发送于一个模板被渲染成功后。信号传递的 `template` 是模板的实例，
   `context` 是环境对象是一个字典。

   订阅示例::

        def log_template_renders(sender, template, context, **extra):
            sender.logger.debug('Rendering template "%s" with context %s',
                                template.name or 'string template',
                                context)

        from flask import template_rendered
        template_rendered.connect(log_template_renders, app)

.. data:: flask.request_started
   :noindex:

   这个信号发送于请求开始之前，且请求环境设置完成之后。因为请求环境已经绑定，
   所以订阅者可以用标准的全局代理，如 :class:`~flask.request` 来操作请求。

   订阅示例::

        def log_request(sender, **extra):
            sender.logger.debug('Request context is set up')

        from flask import request_started
        request_started.connect(log_request, app)

.. data:: flask.request_finished
   :noindex:

   这个信号发送于向客户端发送响应之前。信号传递的 `response` 为将要发送的响应。

   订阅示例::

        def log_response(sender, response, **extra):
            sender.logger.debug('Request context is about to close down.  '
                                'Response: %s', response)

        from flask import request_finished
        request_finished.connect(log_response, app)

.. data:: flask.got_request_exception
   :noindex:

   这个信号发送于请求进行中发生异常的时候。它的发送 *早于* 标准异常处理介于。
   在调试模式下，虽然没有异常处理，但发生异常时也发送这个信号。信号传递的
   `exception` 是异常对象。

   订阅示例::

        def log_exception(sender, exception, **extra):
            sender.logger.debug('Got exception during processing: %s', exception)

        from flask import got_request_exception
        got_request_exception.connect(log_exception, app)

.. data:: flask.request_tearing_down
   :noindex:

   这个信号发送于请求崩溃的时候，不管是否引发异常。目前，侦听此信号的函数在一般
   崩溃处理器后调用，但是没有什么东西可用。

   订阅示例::

        def close_db_connection(sender, **extra):
            session.close()

        from flask import appcontext_tearing_down
        request_tearing_down.connect(close_db_connection, app)

   在 Flask 版本 0.9 中，这还会传递一个 `exc` 关键字参数，如果这个参数存在的话。
   这个参数是引发崩溃的异常的引用。

.. data:: flask.appcontext_tearing_down
   :noindex:

   当应用环境崩溃时发送这个信号。这个信号总是会发送，甚至是因为一个异常引发的
   崩溃。侦听这个信号的函数会在常规崩溃处理器后被调用，但是你无法回馈这个信号。

   订阅示例::

        def close_db_connection(sender, **extra):
            session.close()

        from flask import request_tearing_down
        appcontext_tearing_down.connect(close_db_connection, app)

   这还会传递一个 `exc` 关键字参数，如果这个参数存在的话。这个参数是引发崩溃的
   异常的引用。

.. data:: flask.appcontext_pushed
   :noindex:

   当一个应用的环境被压入时，应用会发送这个信号。这个信号通常用于在单元测试中
   临时钩接信息。例如可以用于改变 `g` 对象中现存的资源。

   用法示例::

        from contextlib import contextmanager
        from flask import appcontext_pushed

        @contextmanager
        def user_set(app, user):
            def handler(sender, **kwargs):
                g.user = user
            with appcontext_pushed.connected_to(handler, app):
                yield

   在测试代码中这样写::

        def test_user_me(self):
            with user_set(app, 'john'):
                c = app.test_client()
                resp = c.get('/users/me')
                assert resp.data == 'username=john'

   .. versionadded:: 0.10

.. data:: appcontext_popped

   当一个应用的环境被弹出时，应用会发送这个信号。这个信号通常写成
   :data:`appcontext_tearing_down` 信号。

   .. versionadded:: 0.10


.. data:: flask.message_flashed
   :noindex:

   当应用闪现一个消息时会发出这个信号。`message`参数是消息内容， `category`
   参数是消息类别。

   订阅示例::

        recorded = []
        def record(sender, message, category, **extra):
            recorded.append((message, category))

        from flask import message_flashed
        message_flashed.connect(record, app)

   .. versionadded:: 0.10
   
.. _blinker: http://pypi.python.org/pypi/blinker
