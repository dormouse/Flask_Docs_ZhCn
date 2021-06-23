信号
=======

.. versionadded:: 0.6

Flask 自 0.6 版本开始在内部支持信号。信号功能由优秀的 `blinker`_ 库提供支持，
如果没有安装该库就无法使用信号功能，但不影响其他功能。

什么是信号？当核心框架的其他地方或另一个 Flask 扩展中发生动作时，信号通过
发送通知来帮助你解耦应用。简言之，信号允许某个发送者通知接收者有事情发生了。

Flask 自身有许多信号，其他扩展可能还会带来更多信号。请记住，信号使用目的是
通知接收者，不应该鼓励接收者修改数据。你会注意到信号的功能与一些内建的装饰
器类似（如 :data:`~flask.request_started` 与
:meth:`~flask.Flask.before_request` 非常相似），但是它们的工作原理不同。例如
核心的 :meth:`~flask.Flask.before_request` 处理器以一定的顺序执行，并且可以
提前退出请求，返回一个响应。相反，所有的信号处理器是乱序执行的，并且不修改任
何数据。

信号的最大优势是可以安全快速的订阅。比如，在单元测试中这些临时订阅十分有用。
假设你想知道请求需要渲染哪个模块，信号可以给你答案。

订阅信号
----------------------

使用信号的 :meth:`~blinker.base.Signal.connect` 方法可以订阅该信号。该方法
的第一个参数是当信号发出时所调用的函数。第二个参数是可选参数，定义一个发送
者。使用 :meth:`~blinker.base.Signal.disconnect` 方法可以退订信号。

所有核心 Flask 信号的发送者是应用本身。因此当订阅信号时请指定发送者，除非
你真的想要收听应用的所有信号。当你正在开发一个扩展时，尤其要注意这点。

下面是一个情境管理器的辅助工具，可用于在单元测试中辨别哪个模板被渲染了，哪
些变量被传递给了模板::

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

在 with 代码块中，所有由 `app` 渲染的模板会被记录在 `templates` 变量中。每
当有模板被渲染，模板对象及环境就会追加到变量中。

另外还有一个方便的辅助方法（ :meth:`~blinker.base.Signal.connected_to` ）。
它允许临时把一个使用环境对象的函数订阅到一个信号。因为环境对象的返回值不能
被指定，所以必须把列表作为参数::

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

如果想要在你自己的应用中使用信号，那么可以直接使用 blinker 库。最常见的,也
是最推荐的方法是在自定义的 :class:`~blinker.base.Namespace` 中命名信号::

    from blinker import Namespace
    my_signals = Namespace()

现在可以像这样创建新的信号::

    model_saved = my_signals.signal('model-saved')

信号的名称应当是唯一的，并且应当简明以便于调试。可以通过
:attr:`~blinker.base.NamedSignal.name` 属性获得信号的名称。

.. admonition:: 扩展开发者注意

   如果你正在编写一个 Flask 扩展，并且想要妥善处理 blinker 安装缺失的情况，
   那么可以使用 :class:`flask.signals.Namespace` 类。

.. _signals-sending:

发送信号
---------------

如果想要发送信号，可以使用 :meth:`~blinker.base.Signal.send` 方法。它的第
一个参数是一个发送者，其他参数是要发送给订阅者的东西，其他参数是可选的::

    class Model(object):
        ...

        def save(self):
            model_saved.send(self)

请谨慎选择发送者。如果是一个发送信号的类，请把 `self` 作为发送者。如果发送
信号的是一个随机的函数，那么可以把 ``current_app._get_current_object()``
作为发送者。

.. admonition:: 传递代理作为发送者

   不要把 :data:`~flask.current_app` 作为发送者传递给信号。请使用
   ``current_app._get_current_object()`` 。因为 :data:`~flask.current_app`
   是一个代理，不是实际的应用对象。

信号与 Flask 的请求环境
-----------------------------------

信号在接收时，完全支持 :doc:`reqcontext` 。在
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
        print f'Template {template.name} is rendered with {context}'


核心信号
------------

所有内置信号请参阅 :ref:`core-signals-list` 。


.. _blinker: https://pypi.org/project/blinker/
