使用 WTForms 进行表单验证
============================

当你必须处理浏览器提交的表单数据时，视图代码很快会变得难以阅读。有一些库可以
简化这个工作，其中之一便是 `WTForms`_ ，下面我们将介绍这个库。如果你必须处理
许多表单，那么应当尝试使用这个库。

如果要使用 WTForms ，那么首先要把表单定义为类。我推荐把应用分割为多个模块（
:ref:`larger-applications` ），并为表单添加一个独立的模块。

.. admonition:: 使用一个扩展获得大部分 WTForms 的功能

   `Flask-WTF`_ 扩展可以实现本方案的所有功能，并且还提供一些小的辅助工具。使用
   这个扩展可以更好的使用表单和 Flask 。你可以从 `PyPI
   <http://pypi.python.org/pypi/Flask-WTF>`_ 获得这个扩展。

.. _Flask-WTF: http://packages.python.org/Flask-WTF/

表单
---------

下面是一个典型的注册页面的示例::

    from wtforms import Form, BooleanField, TextField, PasswordField, validators

    class RegistrationForm(Form):
        username = TextField('Username', [validators.Length(min=4, max=25)])
        email = TextField('Email Address', [validators.Length(min=6, max=35)])
        password = PasswordField('New Password', [
            validators.Required(),
            validators.EqualTo('confirm', message='Passwords must match')
        ])
        confirm = PasswordField('Repeat Password')
        accept_tos = BooleanField('I accept the TOS', [validators.Required()])

视图
-----------

在视图函数中，表单用法示例如下::

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            user = User(form.username.data, form.email.data,
                        form.password.data)
            db_session.add(user)
            flash('Thanks for registering')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

注意，这里我们默认视图使用了 SQLAlchemy （ :ref:`sqlalchemy-pattern` ），当然这
不是必须的。请根据你的实际情况修改代码。

请记住以下几点：

1. 如果数据是通过 HTTP `POST` 方法提交的，请根据 :attr:`~flask.request.form` 的
   值创建表单。如果是通过 `GET` 方法提交的，则相应的是
   :attr:`~flask.request.args` 。
2. 调用 :func:`~wtforms.form.Form.validate` 函数来验证数据。如果验证通过，则
   函数返回 `True` ，否则返回 `False` 。
3. 通过 `form.<NAME>.data` 可以访问表单中单个值。

模板中的表单
------------------

现在我们来看看模板。把表单传递给模板后就可以轻松渲染它们了。看一看下面的示例
模板就可以知道有多轻松了。 WTForms 替我们完成了一半表单生成工作。为了做得更好，
我们可以写一个宏，通过这个宏渲染带有一个标签的字段和错误列表（如果有的话）。

以下是一个使用宏的示例 `_formhelpers.html` 模板：

.. sourcecode:: html+jinja

    {% macro render_field(field) %}
      <dt>{{ field.label }}
      <dd>{{ field(**kwargs)|safe }}
      {% if field.errors %}
        <ul class=errors>
        {% for error in field.errors %}
          <li>{{ error }}</li>
        {% endfor %}
        </ul>
      {% endif %}
      </dd>
    {% endmacro %}

上例中的宏接受一堆传递给 WTForm 字段函数的参数，为我们渲染字段。参数会作为 HTML
属性插入。例如你可以调用 ``render_field(form.username, class='username')`` 来
为输入元素添加一个类。注意： WTForms 返回标准的 Python unicode 字符串，因此我们
必须使用 `|safe` 过滤器告诉 Jinja2 这些数据已经经过 HTML 转义了。

以下是使用了上面的 `_formhelpers.html` 的 `register.html` 模板：

.. sourcecode:: html+jinja

    {% from "_formhelpers.html" import render_field %}
    <form method=post action="/register">
      <dl>
        {{ render_field(form.username) }}
        {{ render_field(form.email) }}
        {{ render_field(form.password) }}
        {{ render_field(form.confirm) }}
        {{ render_field(form.accept_tos) }}
      </dl>
      <p><input type=submit value=Register>
    </form>

更多关于 WTForms 的信息请移步 `WTForms 官方网站`_ 。

.. _WTForms: http://wtforms.simplecodes.com/
.. _WTForms 官方网站: http://wtforms.simplecodes.com/
