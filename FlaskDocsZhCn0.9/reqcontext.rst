.. _request-context:

请求环境
===================

本文讲述 Flask 0.7 版本的运行方式，与旧版本的运行方式基本相同，但也有一些细微的
差别。

建议你在阅读本文之前，先阅读 :ref:`app-context` 。

深入本地环境
--------------------------

假设有一个工具函数，这个函数返回用户重定向的 URL （包括 URL 的 ``next`` 参数、
或 HTTP 推荐 和索引页面）::

    from flask import request, url_for

    def redirect_url():
        return request.args.get('next') or \
               request.referrer or \
               url_for('index')

如上例所示，这个函数访问了请求对象。如果你在一个普通的 Python 解释器中运行这个
函数，那么会看到如下异常：

>>> redirect_url()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'NoneType' object has no attribute 'request'

这是因为现在我们没有一个可以访问的请求。所以我们只能创建一个请求并绑定到当前
环境中。 :attr:`~flask.Flask.test_request_context` 方法可以创建一个
:class:`~flask.ctx.RequestContext` ：

>>> ctx = app.test_request_context('/?next=http://example.com/')

这个环境有两种使用方法：一种是使用 `with` 语句；另一种是调用
:meth:`~flask.ctx.RequestContext.push` 和
:meth:`~flask.ctx.RequestContext.pop` 方法：

>>> ctx.push()

现在可以使用请求对象了：

>>> redirect_url()
u'http://example.com/'

直到你调用 `pop` ：

>>> ctx.pop()

可以把请求环境理解为一个堆栈，可以多次压入和弹出，可以方便地执行一个像内部
重定向之类的东西。

关于在 Python 解释器中使用请求环境的更多内容参见 :ref:`shell` 。

环境的工作原理
---------------------

如果深入 Flask WSGI 应用内部，那么会找到类似如下代码::

    def wsgi_app(self, environ):
        with self.request_context(environ):
            try:
                response = self.full_dispatch_request()
            except Exception, e:
                response = self.make_response(self.handle_exception(e))
            return response(environ, start_response)

:meth:`~Flask.request_context` 方法返回一个新的
:class:`~flask.ctx.RequestContext` 对象，并且使用 `with` 语句把这个对象绑定
到环境。在 `with` 语句块中，在同一个线程中调用的所有东西可以访问全局请求
（:data:`flask.request` 或其他）。

请求环境的工作方式就像一个堆栈，栈顶是当前活动请求。
:meth:`~flask.ctx.RequestContext.push` 把环境压入堆栈中，而
:meth:`~flask.ctx.RequestContext.pop` 把环境弹出。弹出的同时，会执行应用的
:func:`~flask.Flask.teardown_request` 函数。

另一件要注意的事情是：请求环境会在压入时自动创建一个
:ref:`应用环境 <app-context>` 。在此之前，应用没有应用环境。

.. _callbacks-and-errors:

回调和错误处理
--------------------

如果在请求处理的过程中发生错误，那么 Flask 会如何处理呢？自 Flask 0.7 版本之后，
处理方式有所改变。这是为了更方便地反映到底发生了什么情况。新的处理方式非常简单：

1.  在每个请求之前，会执行所有 :meth:`~flask.Flask.before_request` 函数。如果
    其中一个函数返回一个响应，那么其他函数将不再调用。但是在任何情况下，这个
    返回值将会替代视图的返回值。

2.  如果 :meth:`~flask.Flask.before_request` 函数均没有响应，那么就会进行正常的
    请求处理，匹配相应的视图，返回响应。

3.  接着，视图的返回值会转换为一个实际的响应对象并交给
    :meth:`~flask.Flask.after_request` 函数处理。在处理过程中，这个对象可能会被
    替换或修改。

4.  请求处理的最后一环是执行 :meth:`~flask.Flask.teardown_request` 函数。这类
    函数在任何情况下都会被执行，甚至是在发生未处理异常或请求预处理器没有执行（
    例如在测试环境下，有时不想执行）的情况下。

那么如果出错了会怎么样？在生产模式下，如果一个异常未被主要捕获处理，那么会调用
500 内部服务器处理器。在开发模式下，引发的异常不再被进一步处理，会提交给 WSGI
服务器。因此，需要使用交互调试器来查看调试信息。

Flask 0.7 版本的重大变化是内部服务器错误不再由请求后回调函数来处理，并且请求后
回调函数也不保证一定被执行。这样使得内部调试代码更整洁、更易懂和更容易定制。

同时还引入了新的卸载函数，这个函数在请求结束时一定会执行。

卸载回调函数
------------------

卸载回调函数的特殊之处在于其调用的时机是不固定的。严格地说，调用时机取决于
其绑定的 :class:`~flask.ctx.RequestContext` 对象的生命周期。当请求环境弹出时就
会调用 :meth:`~flask.Flask.teardown_request` 函数。

请求环境的生命周期是会变化的，当请求环境位于测试客户端中的 with 语句中或者在
命令行下使用请求环境时，其生命周期会被延长。因此知道生命周期是否被延长是很重要
的::

    with app.test_client() as client:
        resp = client.get('/foo')
        # 到这里还没有调用卸载函数。即使这时响应已经结束，并且已经
        # 获得响应对象，还是不会调用卸载函数。

    # 只有到这里才会调用卸载函数。另外，如果另一个请求在客户端中被
    # 激发，也会调用卸载函数。

在使用命令行时，可以清楚地看到运行方式：

>>> app = Flask(__name__)
>>> @app.teardown_request
... def teardown_request(exception=None):
...     print 'this runs after request'
...
>>> ctx = app.test_request_context()
>>> ctx.push()
>>> ctx.pop()
this runs after request
>>>

记牢记：卸载函数在任何情况下都会被执行，甚至是在请求预处理回调函数没有执行，
但是发生异常的情况下。有的测试系统可能会临时创建一个请求环境，但是不执行
预处理器。请正确使用卸载处理器，确保它们不会执行失败。

.. _notes-on-proxies:

关于代理
----------------

部分 Flask 提供的对象是其他对象的代理。使用代理的原因是代理对象共享于不同的
线程，它们在后台根据需要把实际的对象分配给不同的线程。

多数情况下，你不需要关心这个。但是也有例外，在下列情况有下，知道对象是一个代理
对象是有好处的：

-   想要执行真正的实例检查的情况。因为代理对象不会假冒被代理对象的对象类型，
    因此，必须检查被代理的实际对象（参见下面的 `_get_current_object` ）。
-   对象引用非常重要的情况（例如发送 :ref:`signals` ）。

如果想要访问被代理的对象，可以使用
:meth:`~werkzeug.local.LocalProxy._get_current_object` 方法::

    app = current_app._get_current_object()
    my_signal.send(app)

出错时的环境保存
-----------------------------

不管是否出错，在请求结束时，请求环境会被弹出，并且所有相关联的数据会被销毁。
但是在开发过程中，可能需要在出现异常时保留相关信息。在 Flask 0.6 版本及更早的
版本中，在发生异常时，请求环境不会被弹出，以便于交互调试器提供重要信息。

自 Flask 0.7 版本开始，可以通过设置 ``PRESERVE_CONTEXT_ON_EXCEPTION`` 配置变量
来更好地控制环境的保存。缺省情况下，这个配置变更与 ``DEBUG`` 变更关联。如果在
调试模式下，那么环境会被保留，而在生产模式下则不保留。

不要在生产环境下强制激活 ``PRESERVE_CONTEXT_ON_EXCEPTION`` ，因为这会在出现异常
时导致应用内存溢出。但是在调试模式下使用这个变更是十分有用的，你可以获得在生产
模式下出错时的环境。
