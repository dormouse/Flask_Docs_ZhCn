.. _testing:

测试 Flask 应用
==========================

   **未经测试的小猫，肯定不是一只好猫。**

这句话的出处不详（译者注：这句是译者献给小猫的），也不一定完全正确，但是基本上
是正确的。未经测试的应用难于改进现有的代码，因此其开发者会越改进越抓狂。反之，
经过自动测试的代码可以安全的改进，并且如果可以测试过程中立即发现错误。

Flask 提供的测试渠道是公开 Werkzeug 的 :class:`~werkzeug.test.Client` ，为你
处理本地环境。你可以结合这个渠道使用你喜欢的测试工具。本文使用的测试工具是随着
Python 一起安装好的 :mod:`unittest` 包。

应用
---------------

首先，我们需要一个用来测试的应用。我们将使用 :ref:`tutorial` 中的应用。如果你还
没有这个应用，可以下载 `示例代码`_ 。

.. _示例代码:
   http://github.com/mitsuhiko/flask/tree/master/examples/flaskr/

测试骨架
--------------------

为了测试应用，我们添加了一个新的模块 (`flaskr_tests.py`) 并创建了如下测试骨架::

    import os
    import flaskr
    import unittest
    import tempfile

    class FlaskrTestCase(unittest.TestCase):

        def setUp(self):
            self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
            flaskr.app.config['TESTING'] = True
            self.app = flaskr.app.test_client()
            flaskr.init_db()

        def tearDown(self):
            os.close(self.db_fd)
            os.unlink(flaskr.app.config['DATABASE'])

    if __name__ == '__main__':
        unittest.main()

:meth:`~unittest.TestCase.setUp` 方法中会创建一个新的测试客户端并初始化一个新的
数据库。在每个独立的测试函数运行前都会调用这个方法。
:meth:`~unittest.TestCase.tearDown` 方法的功能是在测试结束后关闭文件，并在文件
系统中删除数据库文件。另外在设置中 ``TESTING`` 标志开启的，这意味着在请求时关闭
错误捕捉，以便于在执行测试请求时得到更好的错误报告。

测试客户端会给我们提供一个简单的应用接口。我们可以通过这个接口向应用发送测试
请求。客户端还可以追踪 cookies 。

因为 SQLite3 是基于文件系统的，所以我们可以方便地使用临时文件模块来创建一个临时
数据库并初始化它。 :func:`~tempfile.mkstemp` 函数返回两个东西：一个低级别的文件
句柄和一个随机文件名。这个文件名后面将作为我们的数据库名称。我们必须把句柄保存
到 `db_fd` 中，以便于以后用 :func:`os.close` 函数来关闭文件。

如果现在进行测试，那么会输出以下内容::

    $ python flaskr_tests.py

    ----------------------------------------------------------------------
    Ran 0 tests in 0.000s

    OK

虽然没有运行任何实际测试，但是已经可以知道我们的 flaskr 应用没有语法错误。
否则在导入时会引发异常并中断运行。

第一个测试
--------------

现在开始测试应用的功能。当我们访问应用的根 URL （ ``/`` ）时应该显示
“ No entries here so far ”。我们新增了一个新的测试方法来测试这个功能::

    class FlaskrTestCase(unittest.TestCase):

        def setUp(self):
            self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
            self.app = flaskr.app.test_client()
            flaskr.init_db()

        def tearDown(self):
            os.close(self.db_fd)
            os.unlink(flaskr.app.config['DATABASE'])

        def test_empty_db(self):
            rv = self.app.get('/')
            assert 'No entries here so far' in rv.data

注意，我们的调试函数都是以 `test` 开头的。这样 :mod:`unittest` 就会自动识别这些
是用于测试的函数并运行它们。

通过使用 `self.app.get` ，可以向应用的指定 URL 发送 HTTP `GET` 请求，其返回的是
一个 `~flask.Flask.response_class` 对象。我们可以使用
:attr:`~werkzeug.wrappers.BaseResponse.data` 属性来检查应用的返回值（字符串
类型）。在本例中，我们检查输出是否包含 ``'No entries here so far'`` 。

再次运行测试，会看到通过了一个测试::

    $ python flaskr_tests.py
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.034s

    OK

登录和注销
------------------

我们应用的主要功能必须登录以后才能使用，因此必须测试应用的登录和注销。测试的
方法是使用规定的数据（用户名和密码）向应用发出登录和注销的请求。因为登录和注销
后会重定向到别的页面，因此必须告诉客户端使用 `follow_redirects` 追踪重定向。

在 `FlaskrTestCase` 类中添加以下两个方法::

   def login(self, username, password):
       return self.app.post('/login', data=dict(
           username=username,
           password=password
       ), follow_redirects=True)

   def logout(self):
       return self.app.get('/logout', follow_redirects=True)

现在可以方便地测试登录成功、登录失败和注销功能了。下面为新增的测试代码::

   def test_login_logout(self):
       rv = self.login('admin', 'default')
       assert 'You were logged in' in rv.data
       rv = self.logout()
       assert 'You were logged out' in rv.data
       rv = self.login('adminx', 'default')
       assert 'Invalid username' in rv.data
       rv = self.login('admin', 'defaultx')
       assert 'Invalid password' in rv.data

测试增加条目功能
--------------------

我们还要测试增加条目功能。添加以下测试代码::

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data

这里我们检查了博客内容中允许使用 HTML ，但标题不可以。应用设计思路就是这样的。

运行测试，现在通过了三个测试::

    $ python flaskr_tests.py
    ...
    ----------------------------------------------------------------------
    Ran 3 tests in 0.332s

    OK

关于更复杂的 HTTP 头部和状态码测试参见 `MiniTwit 示例`_ 。这个示例的源代码中
包含了更大的测试套件。


.. _MiniTwit 示例:
   http://github.com/mitsuhiko/flask/tree/master/examples/minitwit/


其他测试技巧
--------------------

除了使用上述测试客户端外，还可以在 `with` 语句中使用
:meth:`~flask.Flask.test_request_context` 方法来临时激活一个请求环境。在这个
环境中可以像以视图函数中一样操作 :class:`~flask.request` 、:class:`~flask.g`
和 :class:`~flask.session` 对象。示例::

    app = flask.Flask(__name__)

    with app.test_request_context('/?name=Peter'):
        assert flask.request.path == '/'
        assert flask.request.args['name'] == 'Peter'

其他与环境绑定的对象也可以这样使用。

如果你必须使用不同的配置来测试应用，而且没有什么好的测试方法，那么可以考虑使用
应用工厂（参见 :ref:`app-factories` ）。

注意，在测试请求环境中
:meth:`~flask.Flask.before_request` 函数和
:meth:`~flask.Flask.after_request` 函数不会被自动调用。但是当调试请求环境离开
`with` 块时会执行 :meth:`~flask.Flask.teardown_request` 函数。如果需要
:meth:`~flask.Flask.before_request` 函数和正常情况下一样被调用，那么你必须调用
:meth:`~flask.Flask.preprocess_request` ::

    app = flask.Flask(__name__)

    with app.test_request_context('/?name=Peter'):
        app.preprocess_request()
        ...

在这函数中可以打开数据库连接或者根据应用需要打开其他类似东西。

如果想调用 :meth:`~flask.Flask.after_request` 函数，那么必须调用
:meth:`~flask.Flask.process_response` ，并把响应对象传递给它::

    app = flask.Flask(__name__)

    with app.test_request_context('/?name=Peter'):
        resp = Response('...')
        resp = app.process_response(resp)
        ...

这个例子中的情况基本没有用处，因为在这种情况下可以直接开始使用测试客户端。

.. _faking-resources:

伪造资源和环境
----------------------------

.. versionadded:: 0.10

通常情况下，我们会把用户认证信息和数据库连接储存到应用环境或者
:attr:`flask.g` 对象中，并在第一次使用前准备好，然后在断开时删除。假设应用中
得到当前用户的代码如下::

    def get_user():
        user = getattr(g, 'user', None)
        if user is None:
            user = fetch_current_user_from_database()
            g.user = user
        return user

在测试时可以很很方便地重载用户而不用改动代码。可以先象下面这样钩接
:data:`flask.appcontext_pushed` 信号::

    from contextlib import contextmanager
    from flask import appcontext_pushed

    @contextmanager
    def user_set(app, user):
        def handler(sender, **kwargs):
            g.user = user
        with appcontext_pushed.connected_to(handler, app):
            yield

然后使用::

    from flask import json, jsonify

    @app.route('/users/me')
    def users_me():
        return jsonify(username=g.user.username)

    with user_set(app, my_user):
        with app.test_client() as c:
            resp = c.get('/users/me')
            data = json.loads(resp.data)
            self.assert_equal(data['username'], my_user.username)

保持环境
--------------------------

.. versionadded:: 0.4

有时候这种情形是有用的：触发一个常规请求，但是保持环境以便于做一点额外 的事情。
在 Flask 0.4 之后可以在 `with` 语句中使用 :meth:`~flask.Flask.test_client` 来
实现::

    app = flask.Flask(__name__)

    with app.test_client() as c:
        rv = c.get('/?tequila=42')
        assert request.args['tequila'] == '42'

如果你在没有 `with` 的情况下使用 :meth:`~flask.Flask.test_client` ，那么
`assert` 会出错失败。因为无法在请求之外访问 `request` 。


访问和修改会话
--------------------------------

.. versionadded:: 0.8

有时候在测试客户端中访问和修改会话是非常有用的。通常有两方法。如果你想测试会话中
的键和值是否正确，你可以使用 :data:`flask.session`::

    with app.test_client() as c:
        rv = c.get('/')
        assert flask.session['foo'] == 42

但是这个方法无法修改会话或在请求发出前访问会话。自 Flask 0.8 开始，我们提供了
“会话处理”，用打开测试环境中会话和修改会话，最后保存会话。处理后的会话独立于
后端实际使用的会话::

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['a_key'] = 'a value'

        # 运行到这里时，会话已被保存

注意在这种情况下必须使用 ``sess`` 对象来代替 :data:`flask.session` 代理。
``sess`` 对象本身可以提供相同的接口。
