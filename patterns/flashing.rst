.. _message-flashing-pattern:

消息闪现
================

一个好的应用和用户界面都需要良好的反馈。如果用户得不到足够的反馈，那么应用最终
会被用户唾弃。 Flask 的闪现系统提供了一个良好的反馈方式。闪现系统的基本工作方式
是：在且只在下一个请求中访问上一个请求结束时记录的消息。一般我们结合布局模板来
使用闪现系统。

简单的例子
---------------

以下是一个完整的示例::

    from flask import Flask, flash, redirect, render_template, \
         request, url_for

    app = Flask(__name__)
    app.secret_key = 'some_secret'

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            if request.form['username'] != 'admin' or \
               request.form['password'] != 'secret':
                error = 'Invalid credentials'
            else:
                flash('You were successfully logged in')
                return redirect(url_for('index'))
        return render_template('login.html', error=error)

    if __name__ == "__main__":
        app.run()

以下是实现闪现的 ``layout.html`` 模板：

.. sourcecode:: html+jinja

   <!doctype html>
   <title>My Application</title>
   {% with messages = get_flashed_messages() %}
     {% if messages %}
       <ul class=flashes>
       {% for message in messages %}
         <li>{{ message }}</li>
       {% endfor %}
       </ul>
     {% endif %}
   {% endwith %}
   {% block body %}{% endblock %}

以下是 index.html 模板：

.. sourcecode:: html+jinja

   {% extends "layout.html" %}
   {% block body %}
     <h1>Overview</h1>
     <p>Do you want to <a href="{{ url_for('login') }}">log in?</a>
   {% endblock %}

login 模板：

.. sourcecode:: html+jinja

   {% extends "layout.html" %}
   {% block body %}
     <h1>Login</h1>
     {% if error %}
       <p class=error><strong>Error:</strong> {{ error }}
     {% endif %}
     <form action="" method=post>
       <dl>
         <dt>Username:
         <dd><input type=text name=username value="{{
             request.form.username }}">
         <dt>Password:
         <dd><input type=password name=password>
       </dl>
       <p><input type=submit value=Login>
     </form>
   {% endblock %}

闪现消息的类别
------------------------

.. versionadded:: 0.3

闪现消息还可以指定类别，如果没有指定，那么缺省的类别为 ``'message'`` 。不同的
类别可以给用户提供更好的反馈。例如错误消息可以使用红色背景。

使用 :func:`~flask.flash` 函数可以指定消息的类别::

    flash(u'Invalid password provided', 'error')

模板中的 :func:`~flask.get_flashed_messages` 函数也应当返回类别，显示消息的循环
也要略作改变：

.. sourcecode:: html+jinja

   {% with messages = get_flashed_messages(with_categories=true) %}
     {% if messages %}
       <ul class=flashes>
       {% for category, message in messages %}
         <li class="{{ category }}">{{ message }}</li>
       {% endfor %}
       </ul>
     {% endif %}
   {% endwith %}

上例展示如何根据类别渲染消息，还可以给消息加上前缀，如
``<strong>Error:</strong>`` 。

过滤闪现消息
------------------------

.. versionadded:: 0.9

你可以视情况通过传递一个类别列表来过滤 :func:`~flask.get_flashed_messages` 的
结果。这个功能有助于在不同位置显示不同类别的消息。

.. sourcecode:: html+jinja

    {% with errors = get_flashed_messages(category_filter=["error"]) %}
    {% if errors %}
    <div class="alert-message block-message error">
      <a class="close" href="#">×</a>
      <ul>
        {%- for msg in errors %}
        <li>{{ msg }}</li>
        {% endfor -%}
      </ul>
    </div>
    {% endif %}
    {% endwith %}

