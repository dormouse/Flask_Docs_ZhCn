.. currentmodule:: flask

博客蓝图
==============

博客蓝图与验证蓝图所使用的技术一样。博客页面应当列出所有的帖子，允许已登录
用户创建帖子，并允许帖子作者修改和删除帖子。

当你完成每个视图时，请保持开发服务器运行。当你保存修改后，请尝试在浏览器中
访问 URL ，并进行测试。

蓝图
-------------

定义蓝图并注册到应用工厂。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    from flask import (
        Blueprint, flash, g, redirect, render_template, request, url_for
    )
    from werkzeug.exceptions import abort

    from flaskr.auth import login_required
    from flaskr.db import get_db

    bp = Blueprint('blog', __name__)

使用 :meth:`app.register_blueprint() <Flask.register_blueprint>` 在工厂中
导入和注册蓝图。将新代码放在工厂函数的尾部，返回应用之前。

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    def create_app():
        app = ...
        # existing code omitted

        from . import blog
        app.register_blueprint(blog.bp)
        app.add_url_rule('/', endpoint='index')

        return app


与验证蓝图不同，博客蓝图没有 ``url_prefix`` 。因此 ``index`` 视图会用于
``/`` ， ``create`` 会用于 ``/create`` ，以此类推。博客是 Flaskr 的主要
功能，因此把博客索引作为主索引是合理的。

但是，下文的 ``index`` 视图的端点会被定义为 ``blog.index`` 。一些验证视图
会指定向普通的 ``index`` 端点。 我们使用
:meth:`app.add_url_rule() <Flask.add_url_rule>` 关联端点名称 ``'index'``
和 ``/`` URL ，这样 ``url_for('index')`` 或 ``url_for('blog.index')``
都会有效，会生成同样的 ``/`` URL 。

在其他应用中，可能会在工厂中给博客蓝图一个 ``url_prefix`` 并定义一个独立的
``index`` 视图，类似前文中的 ``hello`` 视图。在这种情况下 ``index`` 和
``blog.index`` 的端点和 URL 会有所不同。


索引
-----

索引会显示所有帖子，最新的会排在最前面。为了在结果中包含 ``user`` 表中的
作者信息，使用了一个 ``JOIN`` 。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/')
    def index():
        db = get_db()
        posts = db.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        ).fetchall()
        return render_template('blog/index.html', posts=posts)

.. code-block:: html+jinja
    :caption: ``flaskr/templates/blog/index.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Posts{% endblock %}</h1>
      {% if g.user %}
        <a class="action" href="{{ url_for('blog.create') }}">New</a>
      {% endif %}
    {% endblock %}

    {% block content %}
      {% for post in posts %}
        <article class="post">
          <header>
            <div>
              <h1>{{ post['title'] }}</h1>
              <div class="about">by {{ post['username'] }} on {{ post['created'].strftime('%Y-%m-%d') }}</div>
            </div>
            {% if g.user['id'] == post['author_id'] %}
              <a class="action" href="{{ url_for('blog.update', id=post['id']) }}">Edit</a>
            {% endif %}
          </header>
          <p class="body">{{ post['body'] }}</p>
        </article>
        {% if not loop.last %}
          <hr>
        {% endif %}
      {% endfor %}
    {% endblock %}

当用户登录后， ``header`` 块添加了一个指向 ``create`` 视图的连接。当用户是
博客作者时，可以看到一个“ Edit ”连接，指向 ``update`` 视图。
``loop.last`` 是一个 `Jinja for 循环`_ 内部可用的特殊变量，它用于在每个
博客帖子后面显示一条线来分隔帖子，最后一个帖子除外。

.. _Jinja for 循环: https://jinja.palletsprojects.com/templates/#for


创建
------

``create`` 视图与 ``register`` 视图原理相同。要么显示表单，要么发送内容
已通过验证且内容已加入数据库，或者显示一个出错信息。

先前写的 ``login_required`` 装饰器用在了博客视图中，这样用户必须登录以后
才能访问这些视图，否则会被重定向到登录页面。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/create', methods=('GET', 'POST'))
    @login_required
    def create():
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            error = None

            if not title:
                error = 'Title is required.'

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'INSERT INTO post (title, body, author_id)'
                    ' VALUES (?, ?, ?)',
                    (title, body, g.user['id'])
                )
                db.commit()
                return redirect(url_for('blog.index'))

        return render_template('blog/create.html')

.. code-block:: html+jinja
    :caption: ``flaskr/templates/blog/create.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}New Post{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="title">Title</label>
        <input name="title" id="title" value="{{ request.form['title'] }}" required>
        <label for="body">Body</label>
        <textarea name="body" id="body">{{ request.form['body'] }}</textarea>
        <input type="submit" value="Save">
      </form>
    {% endblock %}


更新
------

``update`` 和 ``delete`` 视图都需要通过 ``id`` 来获取一个 ``post`` ，并且
检查作者与登录用户是否一致。为避免重复代码，可以写一个函数来获取 ``post`` ，
并在每个视图中调用它。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    def get_post(id, check_author=True):
        post = get_db().execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()

        if post is None:
            abort(404, f"Post id {id} doesn't exist.")

        if check_author and post['author_id'] != g.user['id']:
            abort(403)

        return post

:func:`abort` 会引发一个特殊的异常，返回一个 HTTP 状态码。它有一个可选参数，
用于显示出错信息，若不使用该参数则返回缺省出错信息。 ``404`` 表示“未找到”，
``403`` 代表“禁止访问”。（ ``401`` 表示“未授权”，但是我们重定向到登录
页面来代替返回这个状态码）

``check_author`` 参数的作用是函数可以用于在不检查作者的情况下获取一个
``post`` 。这主要用于显示一个独立的帖子页面的情况，因为这时用户是谁没有关系，
用户不会修改帖子。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/<int:id>/update', methods=('GET', 'POST'))
    @login_required
    def update(id):
        post = get_post(id)

        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            error = None

            if not title:
                error = 'Title is required.'

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'UPDATE post SET title = ?, body = ?'
                    ' WHERE id = ?',
                    (title, body, id)
                )
                db.commit()
                return redirect(url_for('blog.index'))

        return render_template('blog/update.html', post=post)

和所有以前的视图不同， ``update`` 函数有一个 ``id`` 参数。该参数对应路由中
的 ``<int:id>`` 。一个真正的 URL 类似 ``/1/update`` 。 Flask 会捕捉到 URL
中的 ``1`` ，确保其为一个 :class:`int` ，并将其作为 ``id`` 参数传递给视图。
如果没有指定 ``int:`` 而是仅仅写了 ``<id>`` ，那么将会传递一个字符串。
要生成一个指向更新页面的 URL ，需要传递 ``id`` 参数给 :func:`url_for` ：
``url_for('blog.update', id=post['id'])`` 。前文的 ``index.html`` 文件中
同样如此。

``create`` 和 ``update`` 视图看上去是相似的。
主要的不同之处在于
``update`` 视图使用了一个 ``post`` 对象和一个
``UPDATE`` 查询代替了一个 ``INSERT`` 查询。作为一个明智的重构者，可以使用
一个视图和一个模板来同时完成这两项工作。但是作为一个初学者，把它们分别处理
要清晰一些。

.. code-block:: html+jinja
    :caption: ``flaskr/templates/blog/update.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Edit "{{ post['title'] }}"{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="title">Title</label>
        <input name="title" id="title"
          value="{{ request.form['title'] or post['title'] }}" required>
        <label for="body">Body</label>
        <textarea name="body" id="body">{{ request.form['body'] or post['body'] }}</textarea>
        <input type="submit" value="Save">
      </form>
      <hr>
      <form action="{{ url_for('blog.delete', id=post['id']) }}" method="post">
        <input class="danger" type="submit" value="Delete" onclick="return confirm('Are you sure?');">
      </form>
    {% endblock %}

这个模板有两个表单。第一个提交已编辑过的数据给当前页面（ ``/<id>/update`` ）。
另一个表单只包含一个按钮。它指定一个 ``action`` 属性，指向删除视图。这个按钮
使用了一些 JavaScript 用以在提交前显示一个确认对话框。

参数 ``{{ request.form['title'] or post['title'] }}`` 用于选择在表单显示什么
数据。当表单还未提交时，显示原 ``post`` 数据。但是，如果提交了非法数据，然后
需要显示这些非法数据以便于用户修改时，就显示 ``request.form`` 中的数据。
:data:`request` 是又一个自动在模板中可用的变量。


删除
------

删除视图没有自己的模板。删除按钮已包含于 ``update.html`` 之中，该按钮指向
``/<id>/delete`` URL 。既然没有模板，该视图只处理 ``POST`` 方法并重定向到
``index`` 视图。

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/<int:id>/delete', methods=('POST',))
    @login_required
    def delete(id):
        get_post(id)
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?', (id,))
        db.commit()
        return redirect(url_for('blog.index'))

恭喜，应用写完了！花点时间在浏览器中试试这个应用吧。然而，构建一个完整的
应用还有一些工作要做。

下面请阅读 :doc:`install` 。
