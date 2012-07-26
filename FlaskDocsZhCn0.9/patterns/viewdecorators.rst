视图装饰器
===============

Python 有一个非常有趣的功能：函数装饰器。这个功能可以使网络应用干净整洁。 Flask
中的每个视图都是一个装饰器，它可以被注入额外的功能。你可以已经用过了
:meth:`~flask.Flask.route` 装饰器。但是，你有可能需要使用你自己的装饰器。假设有
一个视图，只有已经登录的用户才能使用。如果用户访问时没有登录，则会被重定向到
登录页面。这种情况下就是使用装饰器的绝佳机会。


检查登录装饰器
------------------------

让我们来实现这个装饰器。装饰器是一个返回函数的函数。听上去复杂，其实很简单。只要
记住一件事：装饰器用于更新函数的 `__name__` 、 `__module__` 和其他属性。这一点很
容易忘记，但是你不必人工更新函数属性，可以使用一个类似于装饰器的函数（
:func:`functools.wraps` ）。

下面是检查登录装饰器的例子。假设登录页面为 ``'login'`` ，当前用户被储存在
`g.user` 中，如果还没有登录，其值为 `None`::

    from functools import wraps
    from flask import g, request, redirect, url_for

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function

如何使用这个装饰器呢？把这个装饰器放在最靠近函数的地方就行了。当使用更进一步的
装饰器时，请记住要把 :meth:`~flask.Flask.route` 装饰器放在最外面::

    @app.route('/secret_page')
    @login_required
    def secret_page():
        pass

缓存装饰器
-----------------

假设有一个视图函数需要消耗昂贵的计算成本，因此你需要在一定时间内缓存这个视图的
计算结果。这种情况下装饰器是一个好的选择。我们假设你像 :ref:`caching-pattern`
方案中一样设置了缓存。

下面是一个示例缓存函数。它根据一个特定的前缀（实际上是一个格式字符串）和请求的
当前路径生成缓存键。注意，我们先使用了一个函数来创建装饰器，这个装饰器用于装饰
函数。听起来拗口吧，确实有一点复杂，但是下面的示例代码还是很容易读懂的。

被装饰代码按如下步骤工作

1. 基于基础路径获得当前请求的唯一缓存键。
2. 从缓存中获取键值。如果获取成功则返回获取到的值。
3. 否则调用原来的函数，并把返回值存放在缓存中，直至过期（缺省值为五分钟）。

代码::

    from functools import wraps
    from flask import request

    def cached(timeout=5 * 60, key='view/%s'):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = key % request.path
                rv = cache.get(cache_key)
                if rv is not None:
                    return rv
                rv = f(*args, **kwargs)
                cache.set(cache_key, rv, timeout=timeout)
                return rv
            return decorated_function
        return decorator

注意，以上代码假设存在一个可用的实例化的 `cache` 对象，更多信息参见
:ref:`caching-pattern` 方案。


模板装饰器
--------------------

不久前， TurboGear 的人发明了模板装饰器这个通用模式。其工作原理是返回一个字典，
这个字典包含从视图传递给模板的值，模板自动被渲染。以下三个例子的功能是相同的::

    @app.route('/')
    def index():
        return render_template('index.html', value=42)

    @app.route('/')
    @templated('index.html')
    def index():
        return dict(value=42)

    @app.route('/')
    @templated()
    def index():
        return dict(value=42)

正如你所见，如果没有提供模板名称，那么就会使用 URL 映射的端点（把点转换为斜杠）
加上 ``'.html'`` 。如果提供了，那么就会使用所提供的模板名称。当装饰器函数返回
时，返回的字典就被传送到模板渲染函数。如果返回的是 `None` ，就会使用空字典。如果
返回的不是字典，那么就会直接传递原封不动的返回值。这样就可以仍然使用重定向函数或
返回简单的字符串。

以下是装饰器的代码::

    from functools import wraps
    from flask import request

    def templated(template=None):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                template_name = template
                if template_name is None:
                    template_name = request.endpoint \
                        .replace('.', '/') + '.html'
                ctx = f(*args, **kwargs)
                if ctx is None:
                    ctx = {}
                elif not isinstance(ctx, dict):
                    return ctx
                return render_template(template_name, **ctx)
            return decorated_function
        return decorator


端点装饰器
------------------

当你想要使用 werkzeug 路由系统，以便于获得更强的灵活性时，需要和
:class:`~werkzeug.routing.Rule` 中定义的一样，把端点映射到视图函数。这样就需要
用的装饰器了。例如::

    from flask import Flask
    from werkzeug.routing import Rule

    app = Flask(__name__)                                                          
    app.url_map.add(Rule('/', endpoint='index'))                                   

    @app.endpoint('index')                                                         
    def my_index():                                                                
        return "Hello world"     



