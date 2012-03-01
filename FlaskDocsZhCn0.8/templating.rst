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

缺省情况下，以下全局变更可以在 Jinja2 模板中使用：

.. data:: config
   :noindex:

   当前配置对象 （ :data:`flask.config` ）

   .. versionadded:: 0.6

.. data:: request
   :noindex:

   当前请求对象 （ :class:`flask.request` ）

.. data:: session
   :noindex:

   当前会话对象 （ :class:`flask.session` ）

.. data:: g
   :noindex:

   请求绑定的全局变量 （ :data:`flask.g` ）

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

   注意，在 `script` 标记内部不能转义，因此如果要在 `script` 标记内部使用这个
   函数必须用 ``|safe`` 关闭转义：

   .. sourcecode:: html+jinja

       <script type=text/javascript>
           doSomethingWith({{ user.username|tojson|safe }});
       </script>

   ``|tojson`` 过滤器会自动处理正斜杠。

控制自动转义
------------------------

自动转义是指自动对特殊字符进行转义。特殊字符是指 HTML （ 或 XML 和 XHTML ）中的
``&`` 、 ``>`` 、 ``<`` 、 ``"`` 和 ``'`` 。因为这些特殊字符代表了特殊的意思，
所以如果要在文本中使用它们就必须把它们替换为“实体”。如果不转义，那么用户就
无法使用这些字符，而且还会带来安全问题。（参见 :ref:`xss` ）

有时候可能会需要在模板中关闭自动转义功能。
比如一想要直接把 HTML 植入页面的情况
下。
Sometimes however you will need to disable autoescaping in templates.
This can be the case if you want to explicitly inject HTML into pages, for
example if they come from a system that generate secure HTML like a
markdown to HTML converter.

There are three ways to accomplish that:

-   In the Python code, wrap the HTML string in a :class:`~flask.Markup`
    object before passing it to the template.  This is in general the
    recommended way.
-   Inside the template, use the ``|safe`` filter to explicitly mark a
    string as safe HTML (``{{ myvariable|safe }}``)
-   Temporarily disable the autoescape system altogether.

To disable the autoescape system in templates, you can use the ``{%
autoescape %}`` block:

.. sourcecode:: html+jinja

    {% autoescape false %}
        <p>autoescaping is disabled here
        <p>{{ will_not_be_escaped }}
    {% endautoescape %}

Whenever you do this, please be very cautious about the variables you are
using in this block.

Registering Filters
-------------------

If you want to register your own filters in Jinja2 you have two ways to do
that.  You can either put them by hand into the
:attr:`~flask.Flask.jinja_env` of the application or use the
:meth:`~flask.Flask.template_filter` decorator.

The two following examples work the same and both reverse an object::

    @app.template_filter('reverse')
    def reverse_filter(s):
        return s[::-1]

    def reverse_filter(s):
        return s[::-1]
    app.jinja_env.filters['reverse'] = reverse_filter

In case of the decorator the argument is optional if you want to use the
function name as name of the filter.

Context Processors
------------------

To inject new variables automatically into the context of a template
context processors exist in Flask.  Context processors run before the
template is rendered and have the ability to inject new values into the
template context.  A context processor is a function that returns a
dictionary.  The keys and values of this dictionary are then merged with
the template context::

    @app.context_processor
    def inject_user():
        return dict(user=g.user)

The context processor above makes a variable called `user` available in
the template with the value of `g.user`.  This example is not very
interesting because `g` is available in templates anyways, but it gives an
idea how this works.
