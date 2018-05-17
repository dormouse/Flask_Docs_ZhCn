实现 API 异常 
===========================

在 Flask 上实现 RESTful API 很普通。开发人员遇到最头疼的一件事是意识到内建
的异常对 API 没有足够的表达能力，并且它们触发的 :mimetype:`text/html` 的内
容类型对于 API 消费者来说如同鸡肋。

对于非法使用 API 来说，比仅仅对信号错误使用 ``abort`` 更好的是，实现你自己
的异常类型并为之安装一个错误处理器，这样更符合用户的预期。


简单异常类
----------------------

基本的思路是引入一个新异常，提供具有高可读性的信息、错误状态码和一些为错误
提供更多情境的负载。

下面是一个简单的例子::

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

现在，一个视图可以引发带有消息的异常。通过 `payload` 参数，可以以字典方式
提供一些额外的负载。


注册一个错误处理器
----------------------------

此时，视图可以引发异常，但会立即导致内部服务器错误。原因是没有为这个错误类
注册处理器。注册示例如下::

    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

在视图中的用法
--------------

以下是视图使用示例::

    @app.route('/foo')
    def get_foo():
        raise InvalidUsage('This view is gone', status_code=410)
