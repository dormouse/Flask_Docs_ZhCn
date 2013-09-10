.. _deferred-callbacks:

延迟的请求回调
==========================

Flask 的设计思路之一是：响应对象创建后被传递给一串回调函数，这些回调函数可以修改
或替换响应对象。当请求处理开始的时候，响应对象还没有被创建。响应对象是由一个视图
函数或者系统中的其他组件按需创建的。

但是当响应对象还没有创建时，我们如何修改响应对象呢？比如在一个请求前函数中，我们
需要根据响应对象设置一个 cookie 。

通常我们选择避开这种情形。例如可以尝试把应用逻辑移动到请求后函数中。但是，有时候
这个方法让人不爽，或者让代码变得很丑陋。

变通的方法是把一堆回调函数贴到 :data:`~flask.g` 对象上，并且在请求结束时调用这些
回调函数。这样你就可以在应用的任意地方延迟回调函数的执行。


装饰器
-------------

下面的装饰器是一个关键，它在 :data:`~flask.g` 对象上注册一个函数列表::

    from flask import g

    def after_this_request(f):
        if not hasattr(g, 'after_request_callbacks'):
            g.after_request_callbacks = []
        g.after_request_callbacks.append(f)
        return f


调用延迟的回调函数
--------------------

至此，通过使用 `after_this_request` 装饰器，使得函数在请求结束时可以被调用。现在
我们来实现这个调用过程。我们把这些函数注册为
:meth:`~flask.Flask.after_request` 回调函数::

    @app.after_request
    def call_after_request_callbacks(response):
        for callback in getattr(g, 'after_request_callbacks', ()):
            callback(response)
        return response


一个实例
-------------------

现在我们可以方便地随时随地为特定请求注册一个函数，让这个函数在请求结束时被调用。
例如，你可以在请求前函数中把用户的当前语言记录到 cookie 中::

    from flask import request

    @app.before_request
    def detect_user_language():
        language = request.cookies.get('user_lang')
        if language is None:
            language = guess_language_from_request()
            @after_this_request
            def remember_language(response):
                response.set_cookie('user_lang', language)
        g.language = language
