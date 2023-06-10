流内容
==================

有时候你会需要把大量数据传送到客户端，不在内存中保存这些数据。当你想把
运行中产生的数据不经过文件系统，而是直接发送给客户端时，应当怎么做呢？

答案是使用生成器和直接响应。

基本用法
-----------

下面是一个在运行中产生大量 CSV 数据的基本视图函数。其技巧是调用一个内联
函数生成数据，把这个函数传递给一个响应对象::

    @app.route('/large.csv')
    def generate_large_csv():
        def generate():
            for row in iter_all_rows():
                yield f"{','.join(row)}\n"
        return generate(), {"Content-Type": "text/csv"}

每个 ``yield`` 表达式被直接传送给浏览器。注意，有一些 WSGI 中间件可能会
打断流内容，因此在使用分析器或者其他工具的调试环境中要小心一些。

模板中的流内容
------------------------

Jinja2 模板引擎支持逐片渲染模板，返回一个字符串的迭代器。
Flask 提供
:func:`~flask.stream_template` 和
:func:`~flask.stream_template_string`
函数方便使用。

.. code-block:: python

    from flask import stream_template

    @app.get("/timeline")
    def timeline():
        return stream_template("timeline.html")

渲染流产生的部分倾向于与模板中的语句块相匹配。


情境中的流内容
----------------------

:data:`~flask.request` 在生成器运行时将不会被激活，因为此时视图已经返
回。如果你试图访问 ``request`` ，你会得到一个 ``RuntimeError`` 。

如果你的生成器函数依赖于 ``request`` 中的数据，那么应当使用
:func:`~flask.stream_with_context` 包装器。这将在生成器运行时
保持请求情境的活性。

.. code-block:: python

    from flask import stream_with_context, request
    from markupsafe import escape

    @app.route('/stream')
    def streamed_response():
        def generate():
            yield '<p>Hello '
            yield escape(request.args['name'])
            yield '!</p>'
        return stream_with_context(generate())

它也可以被用作装饰器。

.. code-block:: python

    @stream_with_context
    def generate():
        ...

    return generate()

如果一个请求激活，那么 :func:`~flask.stream_template` 和
:func:`~flask.stream_template_string` 函数自动使用
:func:`~flask.stream_with_context` 。
