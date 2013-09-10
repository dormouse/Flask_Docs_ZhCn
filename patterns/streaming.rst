流内容
==================

有时候你会需要把大量数据传送到客户端，不在内存中保存这些数据。当你想把运行中产生
的数据不经过文件系统，而是直接发送给客户端时，应当怎么做呢？

答案是使用生成器和直接响应。

基本用法
-----------

下面是一个在运行中产生大量 CSV 数据的基本视图函数。其技巧是调用一个内联函数生成
数据，把这个函数传递给一个响应对象::

    from flask import Response

    @app.route('/large.csv')
    def generate_large_csv():
        def generate():
            for row in iter_all_rows():
                yield ','.join(row) + '\n'
        return Response(generate(), mimetype='text/csv')

每个 ``yield`` 表达式被直接传送给浏览器。注意，有一些 WSGI 中间件可能会打断流
内容，因此在使用分析器或者其他工具的调试环境中要小心一些。

模板中的流内容
------------------------

Jinja2 模板引擎也支持分片渲染模板。这个功能不是直接被 Flask 支持的，因为它太
特殊了，但是你可以方便地自已来做::

    from flask import Response

    def stream_template(template_name, **context):
        app.update_template_context(context)
        t = app.jinja_env.get_template(template_name)
        rv = t.stream(context)
        rv.enable_buffering(5)
        return rv

    @app.route('/my-large-page.html')
    def render_large_template():
        rows = iter_all_rows()
        return Response(stream_template('the_template.html', rows=rows))

上例的技巧是从 Jinja2 环境中获得应用的模板对象，并调用
:meth:`~jinja2.Template.stream` 来代替 :meth:`~jinja2.Template.render` ，返回
一个流对象来代替一个字符串。由于我们绕过了 Flask 的模板渲染函数使用了模板对象
本身，因此我们需要调用 :meth:`~flask.Flask.update_template_context` ，以确保
更新被渲染的内容。这样，模板遍历流内容。由于每次产生内容后，服务器都会把内容
发送给客户端，因此可能需要缓存来保存内容。我们使用了
``rv.enable_buffering(size)`` 来进行缓存。 ``5`` 是一个比较明智的缺省值。

环境中的流内容
----------------------

.. versionadded:: 0.9

注意，当你生成流内容时，请求环境已经在函数执行时消失了。 Flask 0.9 为你提供了
一点帮助，让你可以在生成器运行期间保持请求环境::

    from flask import stream_with_context, request, Response

    @app.route('/stream')
    def streamed_response():
        def generate():
            yield 'Hello '
            yield request.args['name']
            yield '!'
        return Response(stream_with_context(generate()))

如果没有使用 :func:`~flask.stream_with_context` 函数，那么就会引发
:class:`RuntimeError` 错误。

