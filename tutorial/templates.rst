.. currentmodule:: flask

模板
=========

应用已经写好验证视图，但是如果现在运行服务器的话，无论访问哪个 URL ，都会
看到一个 ``TemplateNotFound`` 错误。这是因为视图调用了
:func:`render_template` ，但是模板还没有写。模板文件会储存在 ``flaskr``
包内的 ``templates`` 文件夹内。


模板是包含静态数据和动态数据占位符的文件。模板使用指定的数据生成最终的文档。
Flask 使用 `Jinja`_ 模板库来渲染模板。

在教程的应用中会使用模板来渲染显示在用户浏览器中的 `HTML`_ 。在 Flask 中，
Jinja 被配置为 *自动转义* HTML 模板中的任何数据。即渲染用户的输入是安全的。
任何用户输入的可能出现歧意的字符，如 ``<`` 和 ``>`` ，会被 *转义* ，替换为
*安全* 的值。这些值在浏览器中看起来一样，但是没有副作用。

Jinja 看上去并且运行地很像 Python 。 Jinja 语句与模板中的静态数据通过特定的
分界符分隔。
任何位于 ``{{`` 和 ``}}`` 这间的东西是一个会输出到最终文档的静态式。
``{%`` 和 ``%}`` 之间的东西表示流程控制语句，如 ``if`` 和 ``for`` 。与
Python 不同，代码块使用分界符分隔，而不是使用缩进分隔。因为代码块内的
静态文本可以会改变缩进。

.. _Jinja: https://jinja.palletsprojects.com/templates/
.. _HTML: https://developer.mozilla.org/docs/Web/HTML


基础布局
---------------

应用中的每一个页面主体不同，但是基本布局是相同的。每个模板会 *扩展* 同一个
基础模板并重载相应的小节，而不是重写整个 HTML 结构。

.. code-block:: html+jinja
    :caption: ``flaskr/templates/base.html``

    <!doctype html>
    <title>{% block title %}{% endblock %} - Flaskr</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <nav>
      <h1>Flaskr</h1>
      <ul>
        {% if g.user %}
          <li><span>{{ g.user['username'] }}</span>
          <li><a href="{{ url_for('auth.logout') }}">Log Out</a>
        {% else %}
          <li><a href="{{ url_for('auth.register') }}">Register</a>
          <li><a href="{{ url_for('auth.login') }}">Log In</a>
        {% endif %}
      </ul>
    </nav>
    <section class="content">
      <header>
        {% block header %}{% endblock %}
      </header>
      {% for message in get_flashed_messages() %}
        <div class="flash">{{ message }}</div>
      {% endfor %}
      {% block content %}{% endblock %}
    </section>

:data:`g` 在模板中自动可用。
根据 ``g.user`` 是否被设置（在 ``load_logged_in_user`` 中进行），要么显示
用户名和注销连接，要么显示注册和登录连接。
:func:`url_for` 也是自动可用的，可用于生成视图的 URL ，而不用手动来指定。

在标题下面，正文内容前面，模板会循环显示 :func:`get_flashed_messages` 返回
的每个消息。在视图中使用 :func:`flash` 来处理出错信息，在模板中就可以这样
显示出出来。

模板中定义三个块，这些块会被其他模板重载。

#.  ``{% block title %}`` 会改变显示在浏览器标签和窗口中的标题。

#.  ``{% block header %}`` 类似于 ``title`` ，但是会改变页面的标题。

#.  ``{% block content %}`` 是每个页面的具体内容，如登录表单或者博客帖子。

其他模板直接放在 ``templates`` 文件夹内。为了更好地管理文件，属于某个蓝图
的模板会被放在与蓝图同名的文件夹内。


注册
--------

.. code-block:: html+jinja
    :caption: ``flaskr/templates/auth/register.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Register{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="username">Username</label>
        <input name="username" id="username" required>
        <label for="password">Password</label>
        <input type="password" name="password" id="password" required>
        <input type="submit" value="Register">
      </form>
    {% endblock %}

``{% extends 'base.html' %}`` 告诉 Jinja 这个模板基于基础模板，并且需要替换
相应的块。所有替换的内容必须位于 ``{% block %}`` 标签之内。

一个实用的模式是把 ``{% block title %}`` 放在 ``{% block header %}`` 内部。
这里不但可以设置 ``title`` 块，还可以把其值作为 ``header`` 块的内容，
一举两得。

``input`` 标记使用了 ``required`` 属性。这是告诉浏览器这些字段是必填的。
如果用户使用不支持这个属性的旧版浏览器或者不是浏览器的东西创建的请求，
那么你还是要在视图中验证输入数据。总是在服务端中完全验证数据，即使客户端
已经做了一些验证，这一点非常重要。


登录
------

本模板除了标题和提交按钮外与注册模板相同。

.. code-block:: html+jinja
    :caption: ``flaskr/templates/auth/login.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Log In{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="username">Username</label>
        <input name="username" id="username" required>
        <label for="password">Password</label>
        <input type="password" name="password" id="password" required>
        <input type="submit" value="Log In">
      </form>
    {% endblock %}


注册一个用户
---------------

现在验证模板已写好，你可以注册一个用户了。
请确定服务器还在运行（如果没有请使用 ``flask run`` ），然后
访问 http://127.0.0.1:5000/auth/register 。

在不填写表单的情况，尝试点击 "Register" 按钮，浏览器会显示出错信息。尝试在
``register.html`` 中删除 ``required`` 属性后再次点击 "Register" 按钮。
页面会重载并显示来自于视图中的 :func:`flash` 的出错信息，而不是浏览器显示
出错信息。

填写用户名和密码后会重定向到登录页面。尝试输入错误的用户名，或者输入正常的
用户名和错误的密码。如果登录成功，那么会看到一个出错信息，因为还没有写登录
后要转向的 ``index`` 视图。

下面请阅读 :doc:`static` 。
