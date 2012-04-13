自定义出错页面
==================

Flask 有一个方便的 :func:`~flask.abort` 函数，它可以通过一个 HTTP 出错代码退出
一个请求。它还提供一个包含基本说明的出错页面，页面显示黑白的文本，很朴素。

用户可以根据错误代码或多或少知道发生了什么错误。


常见出错代码
------------------

以下出错代码是用户常见的，即使应用正常也会出现这些出错代码：

*404 Not Found*
    这是一个古老的“朋友，你使用了一个错误的 URL ”信息。这个信息出现得如此
    频繁，以至于连刚上网的新手都知道 404 代表：该死的，我要看的东西不见了。
    一个好的做法是确保 404 页面上有一些真正有用的东西，至少要有一个返回首页
    的链接。

*403 Forbidden*
    如果你的网站上有某种权限控制，那么当用户访问未获授权内容时应当发送 403
    代码。因此请确保当用户尝试访问未获授权内容时得到正确的反馈。

*410 Gone*
    你知道 "404 Not Found" 有一个名叫 "410 Gone" 的兄弟吗？很少有人使用这个
    代码。如果资源以前曾经存在过，但是现在已经被删除了，那么就应该使用 410
    代码，而不是 404 。如果你不是在数据库中把文档永久地删除，而只是给文档打
    了一个删除标记，那么请为用户考虑，应当使用 410 代码，并显示信息告知用户
    要找的东西已经删除。

*500 Internal Server Error*
    这个代码通常表示程序出错或服务器过载。强烈建议把这个页面弄得友好一点，
    因为你的应用 *迟早* 会出现故障的（参见 :ref:`application-errors` ）。


出错处理器
--------------

一个出错处理器是一个函数，就像一个视图函数一样。与视图函数不同之处在于出错处理器
在出现错误时被调用，且传递错误。错误大多数是一个
:exc:`~werkzeug.exceptions.HTTPException` ，但是有一个例外：当出现内部服务器错误
时会把异常实例传递给出错处理器。

出错处理器使用 :meth:`~flask.Flask.errorhandler` 装饰器注册，注册时应提供异常的
出代码。请记住， Flask *不会* 为你设置出错代码，因此请确保在返回响应时，同时提供
HTTP 状态代码。

以下是一个处理 "404 Page Not Found" 异常的示例::

    from flask import render_template

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

示例模板：

.. sourcecode:: html+jinja

   {% extends "layout.html" %}
   {% block title %}Page Not Found{% endblock %}
   {% block body %}
     <h1>Page Not Found</h1>
     <p>What you were looking for is just not there.
     <p><a href="{{ url_for('index') }}">go somewhere nice</a>
   {% endblock %}
