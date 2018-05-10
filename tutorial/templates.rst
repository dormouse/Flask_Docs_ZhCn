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

.. _Jinja: http://jinja.pocoo.org/docs/templates/
.. _HTML: https://developer.mozilla.org/docs/Web/HTML


The Base Layout
---------------

Each page in the application will have the same basic layout around a
different body. Instead of writing the entire HTML structure in each
template, each template will *extend* a base template and override
specific sections.

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

:data:`g` is automatically available in templates. Based on if
``g.user`` is set (from ``load_logged_in_user``), either the username
and a log out link are displayed, otherwise links to register and log in
are displayed. :func:`url_for` is also automatically available, and is
used to generate URLs to views instead of writing them out manually.

After the page title, and before the content, the template loops over
each message returned by :func:`get_flashed_messages`. You used
:func:`flash` in the views to show error messages, and this is the code
that will display them.

There are three blocks defined here that will be overridden in the other
templates:

#.  ``{% block title %}`` will change the title displayed in the
    browser's tab and window title.

#.  ``{% block header %}`` is similar to ``title`` but will change the
    title displayed on the page.

#.  ``{% block content %}`` is where the content of each page goes, such
    as the login form or a blog post.

The base template is directly in the ``templates`` directory. To keep
the others organized, the templates for a blueprint will be placed in a
directory with the same name as the blueprint.


Register
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

``{% extends 'base.html' %}`` tells Jinja that this template should
replace the blocks from the base template. All the rendered content must
appear inside ``{% block %}`` tags that override blocks from the base
template.

A useful pattern used here is to place ``{% block title %}`` inside
``{% block header %}``. This will set the title block and then output
the value of it into the header block, so that both the window and page
share the same title without writing it twice.

The ``input`` tags are using the ``required`` attribute here. This tells
the browser not to submit the form until those fields are filled in. If
the user is using an older browser that doesn't support that attribute,
or if they are using something besides a browser to make requests, you
still want to validate the data in the Flask view. It's important to
always fully validate the data on the server, even if the client does
some validation as well.


Log In
------

This is identical to the register template except for the title and
submit button.

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


Register A User
---------------

Now that the authentication templates are written, you can register a
user. Make sure the server is still running (``flask run`` if it's not),
then go to http://127.0.0.1:5000/auth/register.

Try clicking the "Register" button without filling out the form and see
that the browser shows an error message. Try removing the ``required``
attributes from the ``register.html`` template and click "Register"
again. Instead of the browser showing an error, the page will reload and
the error from :func:`flash` in the view will be shown.

Fill out a username and password and you'll be redirected to the login
page. Try entering an incorrect username, or the correct username and
incorrect password. If you log in you'll get an error because there's
no ``index`` view to redirect to yet.

Continue to :doc:`static`.
