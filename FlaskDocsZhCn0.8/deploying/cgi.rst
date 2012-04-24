CGI
===

如果其他的部署方式都不管用，那么就只能使用 CGI 了。 CGI 适应于所有主流服务器，
但是其性能稍弱。

这也是在 Google 的 `App Engine`_ 使用 Flask 应用的方法，其执行方式类似于
CGI 环境。

.. admonition:: 小心

   请务必把 ``app.run()`` 放在 ``if __name__ == '__main__':`` 内部或者放在单独
   的文件中，这样可以保证它不会被调用。因为，每调用一次就会开启一个本地 WSGI
   服务器。当我们使用 CGI 或 App Engine 部署应用时，不需要使用本地服务器。

创建一个 `.cgi` 文件
----------------------

首先，你需要创建 CGI 应用文件。我们把它命名为 `yourapplication.cgi`::

    #!/usr/bin/python
    from wsgiref.handlers import CGIHandler
    from yourapplication import app

    CGIHandler().run(app)

服务器设置
------------

设置服务器通常有两种方法。一种是把
`.cgi` 复制为 `cgi-bin` （并且使用 `mod_rewrite` 或其他类似东西来改写 URL ）；
另一种是把服务器直接指向文件。

例如，如果使用 Apache ，那么可以把如下内容放入配置中：

.. sourcecode:: apache

    ScriptAlias /app /path/to/the/application.cgi

更多信息参见你所使用的服务器的文档。

.. _App Engine: http://code.google.com/appengine/
