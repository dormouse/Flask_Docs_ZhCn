.. _deferred-callbacks:

延迟的请求回调
==========================

Flask 的设计思路之一是：响应对象创建后被传递给一串回调函数，这些回调函数可
以修改或替换响应对象。当请求处理开始的时候，响应对象还没有被创建。响应对象
是由一个视图函数或者系统中的其他组件按需创建的。

但是当响应对象还没有创建时，我们如何修改响应对象呢？比如在一个
:meth:`~flask.Flask.before_request` 回调函数中，我们需要根据响应对象设置一
个 cookie 。

通常我们选择避开这种情形。例如可以尝试把应用逻辑移动到
:meth:`~flask.Flask.after_request` 回调函数中。但是，有时候
这个方法让人不爽，或者让代码变得很丑陋。

变通的方法使用 :func:`~flask.after_this_request` 回调函数，该函数只在当前
请求后执行。这样你就可以在应用的任意地方延迟回调函数的执行。

在请求中的任何时候，可以注册在请求结束时将被调用的函数。例如，下例在
:meth:`~flask.Flask.before_request` 回调函数中在 cookie 中记住了当前用户的
语言::

    from flask import request, after_this_request

    @app.before_request
    def detect_user_language():
        language = request.cookies.get('user_lang')

        if language is None:
            language = guess_language_from_request()

            # when the response exists, set a cookie with the language
            @after_this_request
            def remember_language(response):
                response.set_cookie('user_lang', language)

        g.language = language
