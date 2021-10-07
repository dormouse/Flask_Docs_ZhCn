测试 Flask 应用
==========================

   **未经测试的小猫，肯定不是一只好猫。**

这句话的出处不详（译者注：这句是译者献给小猫的），也不一定完全正确，但是基
本上是正确的。未经测试的应用难于改进现有的代码，因此其开发者会越改进越抓狂。
反之，经过自动测试的代码可以安全的改进，并且可以在测试过程中立即发现错误。

Flask 提供的测试渠道是使用 Werkzeug 的 :class:`~werkzeug.test.Client` 类，
并为你处理本地环境。你可以结合这个渠道使用你喜欢的测试工具。

本文使用 `pytest`_ 包作为测试的基础框架。你可以像这样使用 ``pip`` 来安装它::

    $ pip install pytest

.. _pytest: https://docs.pytest.org/


应用
----

首先，我们需要一个用来测试的应用。我们将使用 :doc:`tutorial/index` 中的
应用。如果你还没有这个应用，可以从
:gh:`the examples <examples/tutorial>` 下载。

为了能够正确地导入 ``flaskr`` 模块，我们需要在 ``tutorial`` 文件夹中运
行 ``pip install -e`` 。

测试骨架
--------------------

首先我们在应用的根文件夹中添加一个测试文件夹。然后创建一个 Python 文件来储
存测试内容（ :file:`test_flaskr.py` ）。名称类似 ``test_*.py`` 的文件会被
pytest 自动发现。

接着，我们创建一个名为 :func:`client` 的 `pytest 固件`_ ，用来配置调试应用
并初始化一个新的数据库::

    import os
    import tempfile

    import pytest

    from flaskr import create_app
    from flaskr.db import init_db


    @pytest.fixture
    def client():
        db_fd, db_path = tempfile.mkstemp()
        app = create_app({'TESTING': True, 'DATABASE': db_path})

        with app.test_client() as client:
            with app.app_context():
                init_db()
            yield client

        os.close(db_fd)
        os.unlink(db_path)

这个客户端固件会被每个独立的测试调用。它提供了一个简单的应用接口，用于向应
用发送请求，还可以为我们追踪 cookie 。

在配置中， ``TESTING`` 配置标志是被激活的。这样在处理请求过程中，错误
捕捉被关闭，以利于在测试过程得到更好的错误报告。

因为 SQLite3 是基于文件系统的，所以我们可以方便地使用 :mod:`tempfile` 模块
创建一个临时数据库并初始化它。 :func:`~tempfile.mkstemp` 函数返回两个东西：
一个低级别的文件句柄和一个随机文件名。这个文件名后面将作为我们的数据库名称。
我们必须把句柄保存到 `db_fd` 中，以便于以后用 :func:`os.close` 函数来关闭
文件。

为了在测试后删除数据库，固件关闭并删除了文件。

如果现在进行测试，那么会输出以下内容::

    $ pytest

    ================ test session starts ================
    rootdir: ./flask/examples/flaskr, inifile: setup.cfg
    collected 0 items

    =========== no tests ran in 0.07 seconds ============

虽然没有运行任何实际测试，但是已经可以知道我们的 ``flaskr`` 应用没有语法错
误。否则在导入时会引发异常并中断运行。

.. _pytest 固件:
   https://docs.pytest.org/en/latest/fixture.html

第一个测试
--------------

现在开始测试应用的功能。当我们访问应用的根 URL （ / ）时应该显示
“ No entries here so far ”。在 :file:`test_flaskr.py` 文件中新增一个测试
函数来测试这个功能::

    def test_empty_db(client):
        """Start with a blank database."""

        rv = client.get('/')
        assert b'No entries here so far' in rv.data

注意，我们的调试函数都是以 `test` 开头的。这样 `pytest`_ 就会自动识别这
些是用于测试的函数并运行它们。

通过使用 ``client.get`` ，可以向应用的指定 URL 发送 HTTP ``GET`` 请求，
其返回的是一个 :class:`~flask.Flask.response_class` 对象。我们可以使用
:attr:`~werkzeug.wrappers.Response.data` 属性来检查应用的返回值（字符串
类型）。在本例中，我们检查输出是否包含 ``'No entries here so far'`` 。

再次运行测试，会看到通过了一个测试::

    $ pytest -v

    ================ test session starts ================
    rootdir: ./flask/examples/flaskr, inifile: setup.cfg
    collected 1 items

    tests/test_flaskr.py::test_empty_db PASSED

    ============= 1 passed in 0.10 seconds ==============

登录和注销
------------------

我们应用的主要功能必须登录以后才能使用，因此必须测试应用的登录和注销。测试
的方法是使用规定的数据（用户名和密码）向应用发出登录和注销的请求。因为登录
和注销后会重定向到别的页面，因此必须告诉客户端使用 `follow_redirects` 追踪
重定向。

在 :file:`test_flaskr.py` 文件中添加以下两个函数::

    def login(client, username, password):
        return client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)


    def logout(client):
        return client.get('/logout', follow_redirects=True)

现在可以方便地测试登录成功、登录失败和注销功能了。下面为新增的测试函数::

    def test_login_logout(client):
        """Make sure login and logout works."""

        username = flaskr.app.config["USERNAME"]
        password = flaskr.app.config["PASSWORD"]

        rv = login(client, username, password)
        assert b'You were logged in' in rv.data

        rv = logout(client)
        assert b'You were logged out' in rv.data

        rv = login(client, f"{username}x", password)
        assert b'Invalid username' in rv.data

        rv = login(client, username, f'{password}x')
        assert b'Invalid password' in rv.data

测试添加消息
--------------------

我们还要测试添加消息功能。添加如下测试函数::

    def test_messages(client):
        """Test that messages work."""

        login(client, flaskr.app.config['USERNAME'], flaskr.app.config['PASSWORD'])
        rv = client.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

这里我们验证了 HTML 出现在文本中，但是不出现在标题中，符合我们的预期。

运行测试，应当显示通过了三个测试::

    $ pytest -v

    ================ test session starts ================
    rootdir: ./flask/examples/flaskr, inifile: setup.cfg
    collected 3 items

    tests/test_flaskr.py::test_empty_db PASSED
    tests/test_flaskr.py::test_login_logout PASSED
    tests/test_flaskr.py::test_messages PASSED

    ============= 3 passed in 0.23 seconds ==============


其他测试技巧
--------------------

除了使用上述测试客户端外，还可以联合 ``with`` 语句使用
:meth:`~flask.Flask.test_request_context` 方法来临时激活一个请求环境。在这
个环境中可以像在视图函数中一样操作 :class:`~flask.request` 、
:class:`~flask.g` 和 :class:`~flask.session` 对象。示例::

    from flask import Flask, request

    app = Flask(__name__)

    with app.test_request_context('/?name=Peter'):
        assert request.path == '/'
        assert request.args['name'] == 'Peter'

所有其他与环境绑定的对象也可以这样使用。

如果要使用不同的配置来测试应用，而且没有什么好的测试方法，那么可以考虑使用
应用工厂（参见 :doc:`patterns/appfactories` ）。

注意，在测试请求环境中
:meth:`~flask.Flask.before_request` 和 :meth:`~flask.Flask.after_request`
不会被自动调用。但是当调试请求环境离开 ``with`` 块时会执行
:meth:`~flask.Flask.teardown_request` 函数。如果需要
:meth:`~flask.Flask.before_request` 函数和正常情况下一样被调用，那么需要自
己调用 :meth:`~flask.Flask.preprocess_request` ::

    app = Flask(__name__)

    with app.test_request_context('/?name=Peter'):
        app.preprocess_request()
        ...

在这函数中可以打开数据库连接或者根据应用需要打开其他类似东西。

如果想调用 :meth:`~flask.Flask.after_request` 函数，那么必须调用
:meth:`~flask.Flask.process_response` ，并把响应对象传递给它::

    app = Flask(__name__)

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

在测试时可以很很方便地重载用户而不用改动代码。可以先像下面这样钩接
:data:`flask.appcontext_pushed` 信号::

    from contextlib import contextmanager
    from flask import appcontext_pushed, g

    @contextmanager
    def user_set(app, user):
        def handler(sender, **kwargs):
            g.user = user
        with appcontext_pushed.connected_to(handler, app):
            yield

然后使用它::

    from flask import json, jsonify

    @app.route('/users/me')
    def users_me():
        return jsonify(username=g.user.username)

    with user_set(app, my_user):
        with app.test_client() as c:
            resp = c.get('/users/me')
            data = json.loads(resp.data)
            assert data['username'] == my_user.username


保持环境
--------

.. versionadded:: 0.4

有时候这种情形是有用的：触发一个常规请求，但是保持环境以便于做一点额外的事
情。在 Flask 0.4 之后可以在 ``with`` 语句中使用
:meth:`~flask.Flask.test_client` 来实现::

    app = Flask(__name__)

    with app.test_client() as c:
        rv = c.get('/?tequila=42')
        assert request.args['tequila'] == '42'

如果你在没有 ``with`` 的情况下使用 :meth:`~flask.Flask.test_client` ，那么
``assert`` 会出错失败。因为无法在请求之外访问 `request` 。


访问和修改会话
--------------

.. versionadded:: 0.8

有时候在测试客户端中访问和修改会话是非常有用的。通常有两方法。如果你想测试
会话中的键和值是否正确，你可以使用 :data:`flask.session`::

    with app.test_client() as c:
        rv = c.get('/')
        assert session['foo'] == 42

但是这个方法无法修改会话或在请求发出前访问会话。自 Flask 0.8 开始，我们提供了
“会话处理”，用打开测试环境中会话和修改会话。最后会话被保存，准备好被客户端
测试。处理后的会话独立于后端实际使用的会话::

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['a_key'] = 'a value'

        # once this is reached the session was stored and ready to be used by the client
        c.get(...)

注意在这种情况下必须使用 ``sess`` 对象来代替 :data:`flask.session` 代理。
``sess`` 对象本身可以提供相同的接口。


测试 JSON API
-------------

.. versionadded:: 1.0

Flask 对 JSON 的支持非常好，并且是一个创建 JSON API 的流行选择。使用 JSON
生成请求和在响应中检查 JSON 数据非常方便::

    from flask import request, jsonify

    @app.route('/api/auth')
    def auth():
        json_data = request.get_json()
        email = json_data['email']
        password = json_data['password']
        return jsonify(token=generate_token(email, password))

    with app.test_client() as c:
        rv = c.post('/api/auth', json={
            'email': 'flask@example.com', 'password': 'secret'
        })
        json_data = rv.get_json()
        assert verify_token(email, json_data['token'])

在测试客户端方法中传递 ``json`` 参数，设置请求数据为 JSON 序列化对象，并设
置内容类型为 ``application/json`` 。可以使用 ``get_json`` 从请求或者响应中
获取 JSON 数据。


.. _testing-cli:

测试 CLI 命令
--------------------

Click 来自于 `测试工具`_ ，可用于测试 CLI 命令。一个
:class:`~click.testing.CliRunner` 独立运行命令并通过
:class:`~click.testing.Result` 对象捕获输出。

Flask 提供 :meth:`~flask.Flask.test_cli_runner` 来创建一个
:class:`~flask.testing.FlaskCliRunner` ，以自动传递 Flask 应用给 CLI 。用
它的 :meth:`~flask.testing.FlaskCliRunner.invoke` 方法调用命令，与在命令行
中调用一样::

    import click

    @app.cli.command('hello')
    @click.option('--name', default='World')
    def hello_command(name):
        click.echo(f'Hello, {name}!')

    def test_hello():
        runner = app.test_cli_runner()

        # invoke the command directly
        result = runner.invoke(hello_command, ['--name', 'Flask'])
        assert 'Hello, Flask' in result.output

        # or by name
        result = runner.invoke(args=['hello'])
        assert 'World' in result.output

在上面的例子中，通过名称引用命令的好处是可以验证命令是否在应用中已正确注册
过。

如果要在不运行命令的情况下测试运行参数解析，可以使用
其 :meth:`~click.BaseCommand.make_context` 方法。这样有助于测试复杂验证规
则和自定义类型::

    def upper(ctx, param, value):
        if value is not None:
            return value.upper()

    @app.cli.command('hello')
    @click.option('--name', default='World', callback=upper)
    def hello_command(name):
        click.echo(f'Hello, {name}!')

    def test_hello_params():
        context = hello_command.make_context('hello', ['--name', 'flask'])
        assert context.params['name'] == 'FLASK'

.. _click: https://click.palletsprojects.com/
.. _测试工具: https://click.palletsprojects.com/testing/
