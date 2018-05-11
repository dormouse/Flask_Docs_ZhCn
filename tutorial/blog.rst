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


与验证蓝图不同，博客蓝图没有
``url_prefix`` 。因此 ``index`` 视图会用于 ``/`` ， ``create`` 会用于
``/create`` ，以此类推。博客是 Flaskr 的主要功能，因此把博客索引作为主
索引是合理的。

但是，下文的 ``index`` 视图的端点会被定义为 ``blog.index`` 。一些验证视图
会指定向普通的 ``index`` 端点。
我们使用 :meth:`app.add_url_rule() <Flask.add_url_rule>`
关联端点名称 ``'index'`` 和 ``/`` URL ，这样
``url_for('index')`` 或 ``url_for('blog.index')`` 都会有效，都会生成同样的
``/`` URL 。

在其他应用中，可能会在工厂中给博客蓝图一个 ``url_prefix`` 并定义一个独立的
``index`` 视图，类似前文中的 ``hello`` 视图。在这种情况下
``index`` 和 ``blog.index`` 的端点和 URL 会有所不同。


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

.. _Jinja for 循环: http://jinja.pocoo.org/docs/templates/#for


创建
------

``create`` 视图与 ``register`` 视图原理相同。要么显示表单，要么发送内容
已通过验证且内容已加入数据库，或者显示一个出错信息。

先前写的 ``login_required`` 装饰器用于
decorator you wrote earlier is used on the blog
views. A user must be logged in to visit these views, otherwise they
will be redirected to the login page.

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


Update
------

Both the ``update`` and ``delete`` views will need to fetch a ``post``
by ``id`` and check if the author matches the logged in user. To avoid
duplicating code, you can write a function to get the ``post`` and call
it from each view.

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
            abort(404, "Post id {0} doesn't exist.".format(id))

        if check_author and post['author_id'] != g.user['id']:
            abort(403)

        return post

:func:`abort` will raise a special exception that returns an HTTP status
code. It takes an optional message to show with the error, otherwise a
default message is used. ``404`` means "Not Found", and ``403`` means
"Forbidden". (``401`` means "Unauthorized", but you redirect to the
login page instead of returning that status.)

The ``check_author`` argument is defined so that the function can be
used to get a ``post`` without checking the author. This would be useful
if you wrote a view to show an individual post on a page, where the user
doesn't matter because they're not modifying the post.

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

Unlike the views you've written so far, the ``update`` function takes
an argument, ``id``. That corresponds to the ``<int:id>`` in the route.
A real URL will look like ``/1/update``. Flask will capture the ``1``,
ensure it's an :class:`int`, and pass it as the ``id`` argument. If you
don't specify ``int:`` and instead do ``<id>``, it will be a string.
To generate a URL to the update page, :func:`url_for` needs to be passed
the ``id`` so it knows what to fill in:
``url_for('blog.update', id=post['id'])``. This is also in the
``index.html`` file above.

The ``create`` and ``update`` views look very similar. The main
difference is that the ``update`` view uses a ``post`` object and an
``UPDATE`` query instead of an ``INSERT``. With some clever refactoring,
you could use one view and template for both actions, but for the
tutorial it's clearer to keep them separate.

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

This template has two forms. The first posts the edited data to the
current page (``/<id>/update``). The other form contains only a button
and specifies an ``action`` attribute that posts to the delete view
instead. The button uses some JavaScript to show a confirmation dialog
before submitting.

The pattern ``{{ request.form['title'] or post['title'] }}`` is used to
choose what data appears in the form. When the form hasn't been
submitted, the original ``post`` data appears, but if invalid form data
was posted you want to display that so the user can fix the error, so
``request.form`` is used instead. :data:`request` is another variable
that's automatically available in templates.


Delete
------

The delete view doesn't have its own template, the delete button is part
of ``update.html`` and posts to the ``/<id>/delete`` URL. Since there
is no template, it will only handle the ``POST`` method then redirect
to the ``index`` view.

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

Congratulations, you've now finished writing your application! Take some
time to try out everything in the browser. However, there's still more
to do before the project is complete.

Continue to :doc:`install`.
