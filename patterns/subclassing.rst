继承 Flask
=================

:class:`~flask.Flask` 类可以被继承。

例如，这样可以通过继承重载请求参数如何保留其顺序::

    from flask import Flask, Request
    from werkzeug.datastructures import ImmutableOrderedMultiDict
    class MyRequest(Request):
        """Request subclass to override request parameter storage"""
        parameter_storage_class = ImmutableOrderedMultiDict
    class MyFlask(Flask):
        """Flask subclass using the custom request class"""
        request_class = MyRequest

推荐以这种方式重载或者增强 Flask 的内部功能。
