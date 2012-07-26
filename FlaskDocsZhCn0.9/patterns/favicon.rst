添加一个页面图标
================

一个“页面图标”是浏览器在标签或书签中使用的图标，它可以给你的网站加上一个唯一
的标示，方便区别于其他网站。

那么如何给一个 Flask 应用添加一个页面图标呢？首先，显而易见的，需要一个图标。
图标应当是 16 X 16 像素的 ICO 格式文件。这不是规定的，但却是一个所有浏览器都
支持的事实上的标准。把 ICO 文件命名为 :file:`favicon.ico` 并放入静态 文件目录
中。

现在我们要让浏览器能够找到你的图标，正确的做法是在你的 HTML 中添加一个链接。
示例：

.. sourcecode:: html+jinja

    <link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">

对于大多数浏览器来说，这样就完成任务了，但是一些老古董不支持这个标准。老的标准
是把名为“ favicon.ico ”的图标放在服务器的根目录下。如果你的应用不是挂接在域的
根目录下，那么你需要定义网页服务器在根目录下提供这个图标，否则就无计可施了。
如果你的应用位于根目录下，那么你可以简单地进行重定向::

    app.add_url_rule('/favicon.ico',
                     redirect_to=url_for('static', filename='favicon.ico'))

如果想要保存额外的重定向请求，那么还可以使用
:func:`~flask.send_from_directory` 函数来写一个视图::

    import os
    from flask import send_from_directory

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

上例中的 MIME 类型可以省略，浏览器会自动猜测类型。但是我们在例子中明确定义了，
省去了额外的猜测，反正这个类型是不变的。

上例会通过你的应用来提供图标，如果可能的话，最好配置你的专用服务器来提供图标，
配置方法参见网页服务器的文档。

另见
--------

* Wikipedia 上的 `页面图标 <http://en.wikipedia.org/wiki/Favicon>`_ 词条

