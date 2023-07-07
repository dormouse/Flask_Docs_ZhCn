信号
=======

信号是一种在应用和每个请求的生命周期中，向订阅者通知特定事件的轻量级方
式。当一个事件发生时，发射信号，信号调用所有订阅者。

信号是由 `Blinker`_ 库实现的，详情参见其文档。 Flask 提供了一些内置的信
号。扩展可以提供他们自己的信号。

许多信号使用类似的名称镜像了 Flask 的基于装饰器的回调。例如，
:data:`.request_started` 信号类似于 :meth:`~.Flask.before_request` 装饰
器。与处理器相比，信号的优势在于它们可以被临时订阅，并且不能直接影响应
用程序。这对于测试、度量、审计等方面非常有用。例如，如果你想知道哪个请
求的哪个部分使用什么模板渲染，那么就可以使用一个信号来通知你。


核心信号
------------

所有内建信号列表参见 :ref:`core-signals-list` 。 :doc:`lifecycle` 也描
述了信号和装饰器的执行顺序。


订阅信号
----------------------

使用信号的 :meth:`~blinker.base.Signal.connect` 方法可以订阅该信号。该
方法的第一个参数是当信号发出时所调用的函数。第二个参数是可选参数，定义
一个发送者。使用 :meth:`~blinker.base.Signal.disconnect` 方法可以退订信
号。

所有核心 Flask 信号的发送者是应用本身。因此当订阅信号时请指定发送者，除
非你真的想要收听应用的所有信号。当你正在开发一个扩展时，尤其要注意这点。

下面是一个情境管理器的辅助工具，可用于在单元测试中辨别哪个模板被渲染了，
哪些变量被传递给了模板::

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

在 with 代码块中，所有由 `app` 渲染的模板会被记录在 `templates` 变量中。
每当有模板被渲染，模板对象及环境就会追加到变量中。

另外还有一个方便的辅助方法（ :meth:`~blinker.base.Signal.connected_to`
）。它允许临时把一个使用环境对象的函数订阅到一个信号。因为环境对象的返
回值不能被指定，所以必须把列表作为参数::

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


创建信号
----------------

如果想要在你自己的应用中使用信号，那么可以直接使用 blinker 库。最常见的,
也是最推荐的方法是在自定义的 :class:`~blinker.base.Namespace` 中命名信
号::

    from blinker import Namespace
    my_signals = Namespace()

现在可以像这样创建新的信号::

    model_saved = my_signals.signal('model-saved')

信号的名称应当是唯一的，并且应当简明以便于调试。可以通过
:attr:`~blinker.base.NamedSignal.name` 属性获得信号的名称。

.. admonition:: 扩展开发者注意

   如果你正在编写一个 Flask 扩展，并且想要妥善处理 blinker 安装缺失的情
   况，那么可以使用 :class:`flask.signals.Namespace` 类。

.. _signals-sending:


发送信号
---------------

如果想要发送信号，可以使用 :meth:`~blinker.base.Signal.send` 方法。它的
第一个参数是一个发送者，其他参数是要发送给订阅者的东西，其他参数是可选
的::

    class Model(object):
        ...

        def save(self):
            model_saved.send(self)

请谨慎选择发送者。如果是一个发送信号的类，请把 `self` 作为发送者。如果
发送信号的是一个随机的函数，那么可以把
``current_app._get_current_object()`` 作为发送者。

.. admonition:: 传递代理作为发送者

   不要把 :data:`~flask.current_app` 作为发送者传递给信号。请使用
   ``current_app._get_current_object()`` 。因为
   :data:`~flask.current_app` 是一个代理，不是实际的应用对象。

信号与 Flask 的请求环境
-----------------------------------

信号在接收时，完全支持 :doc:`reqcontext` 。在
:data:`~flask.request_started` 和 :data:`~flask.request_finished` 本地
环境变量始终可用。因此你可以依赖 :class:`flask.g` 及其他本地环境变量。
请注意在 :ref:`signals-sending` 中所述的限制和
:data:`~flask.request_tearing_down` 信号。


信号订阅装饰器
------------------------------------

你可以通过使用 :meth:`~blinker.base.NamedSignal.connect_via` 装饰器轻松
订阅信号::

    from flask import template_rendered

    @template_rendered.connect_via(app)
    def when_template_rendered(sender, template, context, **extra):
        print(f'Template {template.name} is rendered with {context}')

.. _blinker: https://pypi.org/project/blinker/
