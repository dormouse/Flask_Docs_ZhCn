.. _shell:

在 Shell 中使用 Flask 
======================

.. versionadded:: 0.3

喜欢 Python 的原因之一是交互式的 shell ，它可以让你实时运行 Python 命令，并且
立即得到结果。 Flask 本身不带交互 shell ，因为它不需要特定的前期设置，只要在
shell 中导入你的应用就可以开始使用了。

有些辅助工具可以让你在 shell 中更舒服。在交互终端中最大的问题是你不会像浏览器
一样触发一个请求，这就意味着无法使用 :data:`~flask.g` 和 :data:`~flask.request`
等对象。那么如何在 shell 中测试依赖这些对象的代码呢？

这里有一些有用的辅助函数。请记住，这些辅助函数不仅仅只能用于 shell ，还可以用于
单元测试和其他需要假冒请求环境的情况下。

在读下去之前最好你已经读过 :ref:`request-context` 一节。

创建一个请求环境
--------------------------

在 shell 中创建一个正确的请求环境的最简便的方法是使用
:attr:`~flask.Flask.test_request_context` 方法。这个方法会创建一个
:class:`~flask.ctx.RequestContext` ：

>>> ctx = app.test_request_context()

通常你会使用 `with` 语句来激活请求对象，但是在 shell 中，可以简便地手动使用
:meth:`~flask.ctx.RequestContext.push` 和
:meth:`~flask.ctx.RequestContext.pop` 方法：

>>> ctx.push()

从这里开始，直到调用 `pop` 之前，你可以使用请求对象：

>>> ctx.pop()

发送Firing Before/After Request
---------------------------

By just creating a request context, you still don't have run the code that
is normally run before a request.  This might result in your database
being unavailable if you are connecting to the database in a
before-request callback or the current user not being stored on the
:data:`~flask.g` object etc.

This however can easily be done yourself.  Just call
:meth:`~flask.Flask.preprocess_request`:

>>> ctx = app.test_request_context()
>>> ctx.push()
>>> app.preprocess_request()

Keep in mind that the :meth:`~flask.Flask.preprocess_request` function
might return a response object, in that case just ignore it.

To shutdown a request, you need to trick a bit before the after request
functions (triggered by :meth:`~flask.Flask.process_response`) operate on
a response object:

>>> app.process_response(app.response_class())
<Response 0 bytes [200 OK]>
>>> ctx.pop()

The functions registered as :meth:`~flask.Flask.teardown_request` are
automatically called when the context is popped.  So this is the perfect
place to automatically tear down resources that were needed by the request
context (such as database connections).


Further Improving the Shell Experience
--------------------------------------

If you like the idea of experimenting in a shell, create yourself a module
with stuff you want to star import into your interactive session.  There
you could also define some more helper methods for common things such as
initializing the database, dropping tables etc.

Just put them into a module (like `shelltools` and import from there):

>>> from shelltools import *
