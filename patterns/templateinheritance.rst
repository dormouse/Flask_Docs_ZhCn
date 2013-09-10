.. _template-inheritance:

模板继承
========

Jinja 最有力的部分就是模板继承。模板继承允许你创建一个基础“骨架”模板。这个模板
中包含站点的常用元素，定义可以被子模板继承的 **块** 。

听起来很复杂其实做起来简单，看看下面的例子就容易理解了。


基础模板
-------------

这个模板的名称是 ``layout.html`` ，它定义了一个简单的 HTML 骨架，用于显示一个
简单的两栏页面。“子”模板的任务是用内容填充空的块：

.. sourcecode:: html+jinja

    <!doctype html>
    <html>
      <head>
        {% block head %}
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <title>{% block title %}{% endblock %} - My Webpage</title>
        {% endblock %}
      </head>
      <body>
        <div id="content">{% block content %}{% endblock %}</div>
        <div id="footer">
          {% block footer %}
          &copy; Copyright 2010 by <a href="http://domain.invalid/">you</a>.
          {% endblock %}
        </div>
      </body>
    </html>


在这个例子中， ``{% block %}`` 标记定义了四个可以被子模板填充的块。 `block`
标记告诉模板引擎这是一个可以被子模板重载的部分。

子模板
--------------

子模板示例：

.. sourcecode:: html+jinja

    {% extends "layout.html" %}
    {% block title %}Index{% endblock %}
    {% block head %}
      {{ super() }}
      <style type="text/css">
        .important { color: #336699; }
      </style>
    {% endblock %}
    {% block content %}
      <h1>Index</h1>
      <p class="important">
        Welcome on my awesome homepage.
    {% endblock %}

这里 ``{% extends %}`` 标记是关键，它告诉模板引擎这个模板“扩展”了另一个模板，
当模板系统评估这个模板时会先找到父模板。这个扩展标记必须是模板中的第一个标记。
如果要使用父模板中的块内容，请使用 ``{{ super() }}`` 。
