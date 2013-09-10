URL 处理器
==========

.. versionadded:: 0.7

Flask 0.7 引入了 URL 处理器，其作用是为你处理大量包含相同部分的 URL 。假设你有
许多 URL 都包含语言代码，但是又不想在每个函数中都重复处理这个语言代码，那么就可
可以使用 URL 处理器。

在与蓝图配合使用时， URL 处理器格外有用。下面我们分别演示在应用中和蓝图中使用
URL 处理器。

国际化应用的 URL
----------------

假设有应用如下::

    from flask import Flask, g

    app = Flask(__name__)

    @app.route('/<lang_code>/')
    def index(lang_code):
        g.lang_code = lang_code
        ...

    @app.route('/<lang_code>/about')
    def about(lang_code):
        g.lang_code = lang_code
        ...

上例中出现了大量的重复：必须在每一个函数中把语言代码赋值给 :data:`~flask.g`
对象。当然，如果使用一个装饰器可以简化这个工作。但是，当你需要生成由一个函数
指向另一个函数的 URL 时，还是得显式地提供语言代码，相当麻烦。

我们使用 :func:`~flask.Flask.url_defaults` 函数来简化这个问题。这个函数可以自动
把值注入到 :func:`~flask.url_for` 。以下代码检查在 URL 字典中是否存在语言代码，
端点是否需要一个名为 ``'lang_code'`` 的值::

    @app.url_defaults
    def add_language_code(endpoint, values):
        if 'lang_code' in values or not g.lang_code:
            return
        if app.url_map.is_endpoint_expecting(endpoint, 'lang_code'):
            values['lang_code'] = g.lang_code

URL 映射的 :meth:`~werkzeug.routing.Map.is_endpoint_expecting` 方法可用于检查
端点是否需要提供一个语言代码。

上例的逆向函数是 :meth:`~flask.Flask.url_value_preprocessor` 。这些函数在请求
匹配后立即根据 URL 的值执行代码。它们可以从 URL 字典中取出值，并把取出的值放在
其他地方::

    @app.url_value_preprocessor
    def pull_lang_code(endpoint, values):
        g.lang_code = values.pop('lang_code', None)

这样就不必在每个函数中把 `lang_code` 赋值给 :data:`~flask.g` 了。你还可以作
进一步改进：写一个装饰器把语言代码作为 URL 的前缀。但是更好的解决方式是使用
蓝图。一旦 ``'lang_code'`` 从值的字典中弹出，它就不再传送给视图函数了。精简后的
代码如下::

    from flask import Flask, g

    app = Flask(__name__)

    @app.url_defaults
    def add_language_code(endpoint, values):
        if 'lang_code' in values or not g.lang_code:
            return
        if app.url_map.is_endpoint_expecting(endpoint, 'lang_code'):
            values['lang_code'] = g.lang_code

    @app.url_value_preprocessor
    def pull_lang_code(endpoint, values):
        g.lang_code = values.pop('lang_code', None)

    @app.route('/<lang_code>/')
    def index():
        ...

    @app.route('/<lang_code>/about')
    def about():
        ...

国际化的蓝图 URL
--------------------------------

因为蓝图可以自动给所有 URL 加上一个统一的前缀，所以应用到每个函数就非常方便了。
更进一步，因为蓝图 URL 预处理器不需要检查 URL 是否真的需要要一个
``'lang_code'`` 参数，所以可以去除 :meth:`~flask.Flask.url_defaults` 函数中的
逻辑判断::

    from flask import Blueprint, g

    bp = Blueprint('frontend', __name__, url_prefix='/<lang_code>')

    @bp.url_defaults
    def add_language_code(endpoint, values):
        values.setdefault('lang_code', g.lang_code)

    @bp.url_value_preprocessor
    def pull_lang_code(endpoint, values):
        g.lang_code = values.pop('lang_code')

    @bp.route('/')
    def index():
        ...

    @bp.route('/about')
    def about():
        ...
