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

发送请求前/后动作
---------------------------

仅仅创建一个请求环境还是不够的，需要在请求前运行的代码还是没有运行。比如，在
请求前可以会需要转接数据库，或者把用户信息储存在 :data:`~flask.g` 对象中。

使用 :meth:`~flask.Flask.preprocess_request` 可以方便地模拟请求前/后动作：

>>> ctx = app.test_request_context()
>>> ctx.push()
>>> app.preprocess_request()

请记住， :meth:`~flask.Flask.preprocess_request` 函数可以会返回一个响应对象。
如果返回的话请忽略它。

如果要关闭一个请求，那么你需要在请求后函数（由
:meth:`~flask.Flask.process_response` 触发）作用于响应对象前关闭：

>>> app.process_response(app.response_class())
<Response 0 bytes [200 OK]>
>>> ctx.pop()

:meth:`~flask.Flask.teardown_request` 函数会在环境弹出后自动执行。我们可以使用
这些函数来销毁请求环境所需要使用的资源（如数据库连接）。


在 Shell 中玩得更爽
--------------------------------------

如果你喜欢在 shell 中的感觉，那么你可以创建一个导入有关东西的模块，在模块中还
可以定义一些辅助方法，如初始化数据库或者删除表等等。假设这个模块名为
`shelltools` ，那么在开始时你可以：

>>> from shelltools import *
