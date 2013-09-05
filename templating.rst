模板
====

Flask 使用 Jinja2 作为默认模板引擎。你完全可以使用其它模板引擎。但是不管你使用
哪种模板引擎，都必须安装 Jinja2 。因为使用 Jinja2 可以让 Flask 使用更多依赖于
这个模板引擎的扩展。

本文只是简单介绍如何在 Flask 中使用 Jinja2 。如果要详细了解这个模板引擎的语法，
请查阅 `Jinja2 模板官方文档
<http://jinja.pocoo.org/2/documentation/templates>`_ 。

Jinja 设置
----------

在 Flask 中， Jinja2 默认配置如下：

-   在扩展名为 ``.html`` 、 ``.htm`` 、 ``.xml`` 和 ``.xhtml`` 的模板中开启自动
    转义。
-   在模板中可以使用 ``{% autoescape %}`` 来手动设置是否转义。
-   Flask 在 Jinja2 环境中加入一些全局函数和辅助对象，以增强模板的功能。

标准环境
----------------

缺省情况下，以下全局变量可以在 Jinja2 模板中使用：

.. data:: config
   :noindex:

   当前配置对象 （ :data:`flask.config` ）

   .. versionadded:: 0.6

   .. versionchanged:: 0.10
      此版本开始，这个变量总是可用，甚至是在被导入的模板中。

.. data:: request
   :noindex:

   当前请求对象 （ :class:`flask.request` ）。在没有活动请求环境情况下渲染模块
   时，这个变量不可用。

.. data:: session
   :noindex:

   当前会话对象 （ :class:`flask.session` ）。在没有活动请求环境情况下渲染模块
   时，这个变量不可用。

.. data:: g
   :noindex:

   请求绑定的全局变量 （ :data:`flask.g` ）。在没有活动请求环境情况下渲染模块
   时，这个变量不可用。

.. function:: url_for
   :noindex:

   :func:`flask.url_for` 函数。

.. function:: get_flashed_messages
   :noindex:

   :func:`flask.get_flashed_messages` 函数。

.. admonition:: Jinja 环境行为

   这些添加到环境中的变量不是全局变量。与真正的全局变量不同的是这些变量在已导入
   的模板的环境中是不可见的。这样做是基于性能的原因，同时也考虑让代码更有条理。
   
   那么对你来说又有什么意义呢？假设你需要导入一个宏，这个宏需要访问请求对象，
   那么你有两个选择：

   1.   显式地把请求或都该请求有用的属性作为参数传递给宏。
   2.   导入 "with context" 宏。

   导入方式如下：

   .. sourcecode:: jinja

      {% from '_helpers.html' import my_macro with context %}

标准过滤器
----------------

在 Flask 中的模板中添加了以下 Jinja2 本身没有的过滤器：

.. function:: tojson
   :noindex:

   这个函数可以把对象转换为 JSON 格式。如果你要动态生成 JavaScript ，那么这个
   函数非常有用。

   注意，在 `script` 标记内部不能转义，因此在 Flask 0.10 之前的版本中，如果要在
   `script` 标记内部使用这个函数必须用 ``|safe`` 关闭转义：

   .. sourcecode:: html+jinja

       <script type=text/javascript>
           doSomethingWith({{ user.username|tojson|safe }});
       </script>

控制自动转义
------------------------

自动转义是指自动对特殊字符进行转义。特殊字符是指 HTML （ 或 XML 和 XHTML ）中的
``&`` 、 ``>`` 、 ``<`` 、 ``"`` 和 ``'`` 。因为这些特殊字符代表了特殊的意思，
所以如果要在文本中使用它们就必须把它们替换为“实体”。如果不转义，那么用户就
无法使用这些字符，而且还会带来安全问题。（参见 :ref:`xss` ）

有时候，如需要直接把 HTML 植入页面的时候，可能会需要在模板中关闭自动转义功能。
这个可以直接植入的 HTML 一般来自安全的来源，例如一个把标记语言转换为 HTML 的
转换器。

有三种方法可以控制自动转义：

-   在 Python 代码中，可以在把 HTML 字符串传递给模板之前，用
    :class:`~flask.Markup` 对象封装。一般情况下推荐使用这个方法。
-   在模板中，使用 ``|safe`` 过滤器显式把一个字符串标记为安全的 HTML
    （例如： ``{{ myvariable|safe }}`` ）。
-   临时关闭整个系统的自动转义。

在模板中关闭自动转义系统可以使用 ``{% autoescape %}`` 块：

.. sourcecode:: html+jinja

    {% autoescape false %}
        <p>autoescaping is disabled here
        <p>{{ will_not_be_escaped }}
    {% endautoescape %}

在这样做的时候，要非常小心块中的变量的安全性。

.. _registering-filters:

注册过滤器
-------------------

有两种方法可以在 Jinja2 中注册你自己的过滤器。要么手动把它们放入应用的
:attr:`~flask.Flask.jinja_env` 中，要么使用
:meth:`~flask.Flask.template_filter` 装饰器。

下面两个例子功能相同，都是倒序一个对象::

    @app.template_filter('reverse')
    def reverse_filter(s):
        return s[::-1]

    def reverse_filter(s):
        return s[::-1]
    app.jinja_env.filters['reverse'] = reverse_filter

装饰器的参数是可选的，如果不给出就使用函数名作为过滤器名。一旦注册完成后，你就
可以在模板中像 Jinja2 的内建过滤器一样使用过滤器了。例如，假设在环境中你有一个
名为 `mylist` 的 Pyhton 列表::

    {% for x in mylist | reverse %}
    {% endfor %}

环境处理器
------------------

环境处理器的作用是把新的变量自动引入模板环境中。环境处理器在模板被渲染前运行，
因此可以把新的变量自动引入模板环境中。它是一个函数，返回值是一个字典。在应用的
所有模板中，这个字典将与模板环境合并::

    @app.context_processor
    def inject_user():
        return dict(user=g.user)

上例中的环境处理器创建了一个值为 `g.user` 的 `user` 变量，并把这个变量加入了
模板环境中。这个例子只是用于说明工作原理，不是非常有用，因为在模板中， `g` 总是
存在的。

传递值不仅仅局限于变量，还可以传递函数（ Python 提供传递函数的功能）::

    @app.context_processor
    def utility_processor():
        def format_price(amount, currency=u'€'):
            return u'{0:.2f}{1}'.format(amount, currency)
        return dict(format_price=format_price)

上例中的环境处理器把 `format_price` 函数传递给了所有模板::

    {{ format_price(0.33) }}

你还可以把 `format_price` 创建为一个模板过滤器（参见
:ref:`registering-filters` ），这里只是演示如何在一个环境处理器中传递函数。

