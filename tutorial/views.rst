.. _tutorial-views:

步骤 5 ：视图函数
==========================

现在数据库连接弄好了，接着开始写视图函数。我们共需要四个视图函数：

显示条目
--------

这个视图显示所有数据库中的条目。它绑定应用的根地址，并从数据库中读取 title 和
text 字段。 id 最大的记录（最新的条目）在最上面。从指针返回的记录集是一个包含
select 语句查询结果的元组。对于教程应用这样的小应用，做到这样就已经够好了。但是
你可能想要把结果转换为字典，具体做法参见 :ref:`easy-querying` 中的例子。

这个视图会把条目作为字典传递给 `show_entries.html` 模板，并返回渲染结果::

    @app.route('/')
    def show_entries():
        cur = g.db.execute('select title, text from entries order by id desc')
        entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
        return render_template('show_entries.html', entries=entries)

添加一个新条目
--------------

这个视图可以让一个登录后的用户添加一个新条目。本视图只响应 `POST` 请求，真正的
表单显示在 `show_entries` 页面中。如果一切顺利，我们会 :func:`~flask.flash`
一个消息给下一个请求并重定向回到 `show_entries` 页面::

    @app.route('/add', methods=['POST'])
    def add_entry():
        if not session.get('logged_in'):
            abort(401)
        g.db.execute('insert into entries (title, text) values (?, ?)',
                     [request.form['title'], request.form['text']])
        g.db.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('show_entries'))

注意，我们在本视图中检查了用户是否已经登录（即检查会话中是否有 `logged_in` 键，且
对应的值是否为 `True` ）。

.. admonition:: 安全性建议

   请像示例代码一样确保在构建 SQL 语句时使用问号。否则当你使用字符串构建 SQL 时
   容易遭到 SQL 注入攻击。更多内容参见 :ref:`sqlite3` 。

登录和注销
----------------

这些函数用于用户登录和注销。登录视图根据配置中的用户名和密码验证用户并在会话中
设置 `logged_in` 键值。如果用户通过验证，键值设为 `True` ，那么用户会被重定向到
`show_entries` 页面。另外闪现一个信息，告诉用户已登录成功。如果出现错误，模板会
提示错误信息，并让用户重新登录::

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            if request.form['username'] != app.config['USERNAME']:
                error = 'Invalid username'
            elif request.form['password'] != app.config['PASSWORD']:
                error = 'Invalid password'
            else:
                session['logged_in'] = True
                flash('You were logged in')
                return redirect(url_for('show_entries'))
        return render_template('login.html', error=error)

登出视图则正好相反，把键值从会话中删除。在这里我们使用了一个小技巧：如果你使用
字典的 :meth:`~dict.pop` 方法并且传递了第二个参数（键的缺省值），那么当字典中有
这个键时就会删除这个键，否则什么也不做。这样做的好处是我们不用检查用户是否已经
登录了。

::

    @app.route('/logout')
    def logout():
        session.pop('logged_in', None)
        flash('You were logged out')
        return redirect(url_for('show_entries'))

下面请阅读 :ref:`tutorial-templates` 。
