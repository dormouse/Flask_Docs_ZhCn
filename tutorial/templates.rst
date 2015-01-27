.. _tutorial-templates:

步骤 6 ：模板
=====================

现在开始写模板。如果我们现在访问 URL ，那么会得到一个 Flask 无法找到模板文件的
异常。 Flask 使用 `Jinja2`_ 模板语法并默认开启自动转义。也就是说除非用
:class:`~flask.Markup` 标记一个值或在模板中使用 ``|safe`` 过滤器，否则 Jinja2 
会把如 ``<`` 或 ``>`` 之类的特殊字符转义为与其 XML 等价字符。

我们还使用了模板继承以保存所有页面的布局统一。

请把以下模板放在 `templates` 文件夹中：

.. _Jinja2: http://jinja.pocoo.org/2/documentation/templates

layout.html
-----------

这个模板包含 HTML 骨架、头部和一个登录链接（如果用户已登录则变为一个注销链接
）。如果有闪现信息，那么还会显示闪现信息。 ``{% block body %}`` 块会被子模板中
同名（ ``body`` ）的块替换。

:class:`~flask.session` 字典在模板中也可以使用。你可以使用它来检验用户是否已经
登录。注意，在 Jinja 中可以访问对象或字典的不存在的属性和成员。如例子中的
``'logged_in'`` 键不存在时代码仍然能正常运行： 

.. sourcecode:: html+jinja

    <!doctype html>
    <title>Flaskr</title>
    <link rel=stylesheet type=text/css href="{{ url_for('static', filename='style.css') }}">
    <div class=page>
      <h1>Flaskr</h1>
      <div class=metanav>
      {% if not session.logged_in %}
        <a href="{{ url_for('login') }}">log in</a>
      {% else %}
        <a href="{{ url_for('logout') }}">log out</a>
      {% endif %}
      </div>
      {% for message in get_flashed_messages() %}
        <div class=flash>{{ message }}</div>
      {% endfor %}
      {% block body %}{% endblock %}
    </div>

show_entries.html
-----------------

这个模板扩展了上述的 `layout.html` 模板，用于显示信息。注意， `for` 遍历了我们
通过 :func:`~flask.render_template` 函数传递的所有信息。模板还告诉表单使用
`POST` 作为 `HTTP` 方法向 `add_entry` 函数提交数据：

.. sourcecode:: html+jinja

    {% extends "layout.html" %}
    {% block body %}
      {% if session.logged_in %}
        <form action="{{ url_for('add_entry') }}" method=post class=add-entry>
          <dl>
            <dt>Title:
            <dd><input type=text size=30 name=title>
            <dt>Text:
            <dd><textarea name=text rows=5 cols=40></textarea>
            <dd><input type=submit value=Share>
          </dl>
        </form>
      {% endif %}
      <ul class=entries>
      {% for entry in entries %}
        <li><h2>{{ entry.title }}</h2>{{ entry.text|safe }}
      {% else %}
        <li><em>Unbelievable.  No entries here so far</em>
      {% endfor %}
      </ul>
    {% endblock %}

login.html
----------

最后是简单显示用户登录表单的登录模板：

.. sourcecode:: html+jinja

    {% extends "layout.html" %}
    {% block body %}
      <h2>Login</h2>
      {% if error %}<p class=error><strong>Error:</strong> {{ error }}{% endif %}
      <form action="{{ url_for('login') }}" method=post>
        <dl>
          <dt>Username:
          <dd><input type=text name=username>
          <dt>Password:
          <dd><input type=password name=password>
          <dd><input type=submit value=Login>
        </dl>
      </form>
    {% endblock %}

下面请阅读 :ref:`tutorial-css` 。
