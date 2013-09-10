实现 API 异常处理
===========================

在 Flask 上经常会执行 RESTful API 。开发者首先会遇到的问题之一是用于 API 的内建
异常处理不给力，回馈的内容不是很有用。

对于非法使用 API ，比使用 ``abort`` 更好的解决方式是实现你自己的异常处理类型，
并安装相应句柄，输出符合用户格式要求的出错信息。

简单的异常类
----------------------

基本的思路是引入一个新的异常，回馈一个合适的可读性高的信息、一个状态码和一些
可选的负载，给错误提供更多的环境内容。

以下是一个简单的示例::

    from flask import jsonify

    class InvalidUsage(Exception):
        status_code = 400

        def __init__(self, message, status_code=None, payload=None):
            Exception.__init__(self)
            self.message = message
            if status_code is not None:
                self.status_code = status_code
            self.payload = payload

        def to_dict(self):
            rv = dict(self.payload or ())
            rv['message'] = self.message
            return rv

这样一个视图就可以抛出带有出错信息的异常了。另外，还可以通过 `payload` 参数以
字典的形式提供一些额外的负载。

注册一个错误处理句柄
----------------------------

现在，视图可以抛出异常，但是会立即引发一个内部服务错误。这是因为没有为这个错误
处理类注册句柄。句柄增加很容易，例如::

    @app.errorhandler(InvalidAPIUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

在视图中的用法
--------------

以下是如何在视图中使用该功能::

    @app.route('/foo')
    def get_foo():
        raise InvalidUsage('This view is gone', status_code=410)
