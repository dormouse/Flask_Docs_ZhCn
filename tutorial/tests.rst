.. currentmodule:: flask

测试覆盖
=============

为应用写单元测试可以检查代码是否按预期执行。 Flask 提供了测试客户端，
可以模拟向应用发送请求并返回响应数据。

应当尽可能多地进行测试。函数中的代码只有在函数被调用的情况下才会运行。
分支中的代码，如 ``if`` 块中的代码，只有在符合条件的情况下才会运行。测试
应当覆盖每个函数和每个分支。

越接近 100% 的测试覆盖，越能够保证修改代码后不会出现意外。但是 100% 测试
覆盖不能保证应用没有错误。通常，测试不会覆盖用户如何在浏览器中与应用进行
交互。尽管如此，在开发过程中，测试覆盖仍然是非常重要的。

.. note::
    这部分内容在教程中是放在后面介绍的，但是在以后的项目中，应当在开发的
    时候进行测试。

我们使用 `pytest`_ 和 `coverage`_ 来进行测试和衡量代码。先安装它们：

.. code-block:: none

    $ pip install pytest coverage

.. _pytest: https://pytest.readthedocs.io/
.. _coverage: https://coverage.readthedocs.io/


配置和固件
------------------

测试代码位于 ``tests`` 文件夹中，该文件夹位于 ``flaskr`` 包的 *旁边* ，
而不是里面。 ``tests/conftest.py`` 文件包含名为 *fixtures* （固件）的配置
函数。每个测试都会用到这个函数。测试位于 Python 模块中，以 ``test_`` 开头，
并且模块中的每个测试函数也以 ``test_`` 开头。

每个测试会创建一个新的临时数据库文件，并产生一些用于测试的数据。写一个
SQL 文件来插入数据。

.. code-block:: sql
    :caption: ``tests/data.sql``

    INSERT INTO user (username, password)
    VALUES
      ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
      ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

    INSERT INTO post (title, body, author_id, created)
    VALUES
      ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');

``app`` 固件会调用工厂并为测试传递 ``test_config`` 来配置应用和数据库，而
不使用本地的开发配置。

.. code-block:: python
    :caption: ``tests/conftest.py``

    import os
    import tempfile

    import pytest
    from flaskr import create_app
    from flaskr.db import get_db, init_db

    with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
        _data_sql = f.read().decode('utf8')


    @pytest.fixture
    def app():
        db_fd, db_path = tempfile.mkstemp()

        app = create_app({
            'TESTING': True,
            'DATABASE': db_path,
        })

        with app.app_context():
            init_db()
            get_db().executescript(_data_sql)

        yield app

        os.close(db_fd)
        os.unlink(db_path)


    @pytest.fixture
    def client(app):
        return app.test_client()


    @pytest.fixture
    def runner(app):
        return app.test_cli_runner()

:func:`tempfile.mkstemp` 创建并打开一个临时文件，返回该文件描述符和路径。
``DATABASE`` 路径被重载，这样它会指向临时路径，而不是实例文件夹。设置好
路径之后，数据库表被创建，然后插入数据。测试结束后，临时文件会被关闭并
删除。

:data:`TESTING` 告诉 Flask 应用处在测试模式下。 Flask 会改变一些内部行为
以方便测试。其他的扩展也可以使用这个标志方便测试。

``client`` 固件调用
:meth:`app.test_client() <Flask.test_client>` 由 ``app`` 固件创建的应用
对象。测试会使用客户端来向应用发送请求，而不用启动服务器。

``runner`` 固件类似于 ``client`` 。
:meth:`app.test_cli_runner() <Flask.test_cli_runner>` 创建一个运行器，
可以调用应用注册的 Click 命令。

Pytest 通过匹配固件函数名称和测试函数的参数名称来使用固件。例如
下面要写 ``test_hello`` 函数有一个 ``client`` 参数。 Pytest 会匹配
``client`` 固件函数，调用该函数，把返回值传递给测试函数。


工厂
-------

工厂本身没有什么好测试的，其大部分代码会被每个测试用到。因此如果工厂代码
有问题，那么在进行其他测试时会被发现。

唯一可以改变的行为是传递测试配置。如果没传递配置，那么会有一些缺省配置可
用，否则配置会被重载。

.. code-block:: python
    :caption: ``tests/test_factory.py``

    from flaskr import create_app


    def test_config():
        assert not create_app().testing
        assert create_app({'TESTING': True}).testing


    def test_hello(client):
        response = client.get('/hello')
        assert response.data == b'Hello, World!'

在本教程开头的部分添加了一个 ``hello`` 路由作为示例。它返回
"Hello, World!" ，因此测试响应数据是否匹配。


数据库
--------

在一个应用环境中，每次调用 ``get_db`` 都应当返回相同的连接。退出环境后，
连接应当已关闭。

.. code-block:: python
    :caption: ``tests/test_db.py``

    import sqlite3

    import pytest
    from flaskr.db import get_db


    def test_get_close_db(app):
        with app.app_context():
            db = get_db()
            assert db is get_db()

        with pytest.raises(sqlite3.ProgrammingError) as e:
            db.execute('SELECT 1')

        assert 'closed' in str(e.value)

``init-db`` 命令应当调用 ``init_db`` 函数并输出一个信息。

.. code-block:: python
    :caption: ``tests/test_db.py``

    def test_init_db_command(runner, monkeypatch):
        class Recorder(object):
            called = False

        def fake_init_db():
            Recorder.called = True

        monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
        result = runner.invoke(args=['init-db'])
        assert 'Initialized' in result.output
        assert Recorder.called

这个测试使用 Pytest's ``monkeypatch`` 固件来替换 ``init_db`` 函数。
前文写的 ``runner`` 固件用于通过名称调用 ``init-db`` 命令。


验证
--------------

对于大多数视图，用户需要登录。在测试中最方便的方法是使用客户端制作一个
``POST`` 请求发送给 ``login`` 视图。与其每次都写一遍，不如写一个类，用
类的方法来做这件事，并使用一个固件把它传递给每个测试的客户端。

.. code-block:: python
    :caption: ``tests/conftest.py``

    class AuthActions(object):
        def __init__(self, client):
            self._client = client

        def login(self, username='test', password='test'):
            return self._client.post(
                '/auth/login',
                data={'username': username, 'password': password}
            )

        def logout(self):
            return self._client.get('/auth/logout')


    @pytest.fixture
    def auth(client):
        return AuthActions(client)

通过 ``auth`` 固件，可以在调试中调用 ``auth.login()`` 登录为
``test`` 用户。这个用户的数据已经在 ``app`` 固件中写入了数据。

``register`` 视图应当在 ``GET`` 请求时渲染成功。
在 ``POST`` 请求中，表单数据合法时，该视图应当重定向到登录 URL ，并且用户
的数据已在数据库中保存好。数据非法时，应当显示出错信息。

.. code-block:: python
    :caption: ``tests/test_auth.py``

    import pytest
    from flask import g, session
    from flaskr.db import get_db


    def test_register(client, app):
        assert client.get('/auth/register').status_code == 200
        response = client.post(
            '/auth/register', data={'username': 'a', 'password': 'a'}
        )
        assert 'http://localhost/auth/login' == response.headers['Location']

        with app.app_context():
            assert get_db().execute(
                "SELECT * FROM user WHERE username = 'a'",
            ).fetchone() is not None


    @pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', b'Username is required.'),
        ('a', '', b'Password is required.'),
        ('test', 'test', b'already registered'),
    ))
    def test_register_validate_input(client, username, password, message):
        response = client.post(
            '/auth/register',
            data={'username': username, 'password': password}
        )
        assert message in response.data

:meth:`client.get() <werkzeug.test.Client.get>` 制作一个 ``GET`` 请求并
由 Flask 返回 :class:`Response` 对象。类似的
:meth:`client.post() <werkzeug.test.Client.post>` 制作一个 ``POST`` 请求，
转换 ``data`` 字典为表单数据。

为了测试页面是否渲染成功，制作一个简单的请求，并检查是否返回
一个 ``200 OK`` :attr:`~Response.status_code` 。如果渲染失败，
Flask 会返回一个 ``500 Internal Server Error`` 代码。

当注册视图重定向到登录视图时， :attr:`~Response.headers` 会有一个包含登
录 URL 的 ``Location`` 头部。

:attr:`~Response.data` 以字节方式包含响应的身体。如果想要检测渲染页面中
的某个值，请在 ``data`` 中检测。字节值只能与字节值作比较，如果想比较文
本，请使用
:meth:`get_data(as_text=True) <werkzeug.wrappers.Response.get_data>` 。

``pytest.mark.parametrize`` 告诉 Pytest 以不同的参数运行同一个测试。
这里用于测试不同的非法输入和出错信息，避免重复写三次相同的代码。

``login`` 视图的测试与 ``register`` 的非常相似。后者是测试数据库中的数据，
前者是测试登录之后 :data:`session` 应当包含 ``user_id`` 。

.. code-block:: python
    :caption: ``tests/test_auth.py``

    def test_login(client, auth):
        assert client.get('/auth/login').status_code == 200
        response = auth.login()
        assert response.headers['Location'] == 'http://localhost/'

        with client:
            client.get('/')
            assert session['user_id'] == 1
            assert g.user['username'] == 'test'


    @pytest.mark.parametrize(('username', 'password', 'message'), (
        ('a', 'test', b'Incorrect username.'),
        ('test', 'a', b'Incorrect password.'),
    ))
    def test_login_validate_input(auth, username, password, message):
        response = auth.login(username, password)
        assert message in response.data

在 ``with`` 块中使用 ``client`` ，可以在响应返回之后操作环境变量，比如
:data:`session` 。 通常，在请求之外操作 ``session`` 会引发一个异常。

``logout`` 测试与 ``login`` 相反。注销之后， :data:`session` 应当不包含
``user_id`` 。

.. code-block:: python
    :caption: ``tests/test_auth.py``

    def test_logout(client, auth):
        auth.login()

        with client:
            auth.logout()
            assert 'user_id' not in session


博客
----

所有博客视图使用之前所写的 ``auth`` 固件。调用
``auth.login()`` ，并且客户端的后继请求会登录为
``test`` 用户。

``index`` 索引视图应当显示已添加的测试帖子数据。作为作者登录之后，应当有
编辑博客的连接。

当测试 ``index`` 视图时，还可以测试更多验证行为。当没有登录时，每个页面
显示登录或注册连接。当登录之后，应当有一个注销连接。

.. code-block:: python
    :caption: ``tests/test_blog.py``

    import pytest
    from flaskr.db import get_db


    def test_index(client, auth):
        response = client.get('/')
        assert b"Log In" in response.data
        assert b"Register" in response.data

        auth.login()
        response = client.get('/')
        assert b'Log Out' in response.data
        assert b'test title' in response.data
        assert b'by test on 2018-01-01' in response.data
        assert b'test\nbody' in response.data
        assert b'href="/1/update"' in response.data

用户必须登录后才能访问 ``create`` 、 ``update`` 和 ``delete`` 视图。帖子
作者才能访问 ``update`` 和 ``delete`` 。否则返回一个 ``403 Forbidden``
状态码。如果要访问 ``post`` 的 ``id`` 不存在，那么 ``update`` 和 ``delete``
应当返回 ``404 Not Found`` 。

.. code-block:: python
    :caption: ``tests/test_blog.py``

    @pytest.mark.parametrize('path', (
        '/create',
        '/1/update',
        '/1/delete',
    ))
    def test_login_required(client, path):
        response = client.post(path)
        assert response.headers['Location'] == 'http://localhost/auth/login'


    def test_author_required(app, client, auth):
        # change the post author to another user
        with app.app_context():
            db = get_db()
            db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
            db.commit()

        auth.login()
        # current user can't modify other user's post
        assert client.post('/1/update').status_code == 403
        assert client.post('/1/delete').status_code == 403
        # current user doesn't see edit link
        assert b'href="/1/update"' not in client.get('/').data


    @pytest.mark.parametrize('path', (
        '/2/update',
        '/2/delete',
    ))
    def test_exists_required(client, auth, path):
        auth.login()
        assert client.post(path).status_code == 404

对于 ``GET`` 请求， ``create`` 和 ``update`` 视图应当渲染和返回一个
``200 OK`` 状态码。当 ``POST`` 请求发送了合法数据后， ``create`` 应当在
数据库中插入新的帖子数据， ``update`` 应当修改数据库中现存的数据。当数据
非法时，两者都应当显示一个出错信息。

.. code-block:: python
    :caption: ``tests/test_blog.py``

    def test_create(client, auth, app):
        auth.login()
        assert client.get('/create').status_code == 200
        client.post('/create', data={'title': 'created', 'body': ''})

        with app.app_context():
            db = get_db()
            count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
            assert count == 2


    def test_update(client, auth, app):
        auth.login()
        assert client.get('/1/update').status_code == 200
        client.post('/1/update', data={'title': 'updated', 'body': ''})

        with app.app_context():
            db = get_db()
            post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
            assert post['title'] == 'updated'


    @pytest.mark.parametrize('path', (
        '/create',
        '/1/update',
    ))
    def test_create_update_validate(client, auth, path):
        auth.login()
        response = client.post(path, data={'title': '', 'body': ''})
        assert b'Title is required.' in response.data

``delete`` 视图应当重定向到索引 URL ，并且帖子应当从数据库中删除。

.. code-block:: python
    :caption: ``tests/test_blog.py``

    def test_delete(client, auth, app):
        auth.login()
        response = client.post('/1/delete')
        assert response.headers['Location'] == 'http://localhost/'

        with app.app_context():
            db = get_db()
            post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
            assert post is None


运行测试
-----------------

额外的配置可以添加到项目的 ``setup.cfg`` 文件。这些配置不是必需的，但是
可以使用测试更简洁明了。

.. code-block:: none
    :caption: ``setup.cfg``

    [tool:pytest]
    testpaths = tests

    [coverage:run]
    branch = True
    source =
        flaskr

使用 ``pytest`` 来运行测试。该命令会找到并且运行所有测试。

.. code-block:: none

    $ pytest

    ========================= test session starts ==========================
    platform linux -- Python 3.6.4, pytest-3.5.0, py-1.5.3, pluggy-0.6.0
    rootdir: /home/user/Projects/flask-tutorial, inifile: setup.cfg
    collected 23 items

    tests/test_auth.py ........                                      [ 34%]
    tests/test_blog.py ............                                  [ 86%]
    tests/test_db.py ..                                              [ 95%]
    tests/test_factory.py ..                                         [100%]

    ====================== 24 passed in 0.64 seconds =======================

如果有测试失败， pytest 会显示引发的错误。可以使用
``pytest -v`` 得到每个测试的列表，而不是一串点。

可以使用 ``coverage`` 命令代替直接使用 pytest 来运行测试，这样可以衡量测试
覆盖率。

.. code-block:: none

    $ coverage run -m pytest

在终端中，可以看到一个简单的覆盖率报告：

.. code-block:: none

    $ coverage report

    Name                 Stmts   Miss Branch BrPart  Cover
    ------------------------------------------------------
    flaskr/__init__.py      21      0      2      0   100%
    flaskr/auth.py          54      0     22      0   100%
    flaskr/blog.py          54      0     16      0   100%
    flaskr/db.py            24      0      4      0   100%
    ------------------------------------------------------
    TOTAL                  153      0     44      0   100%

还可以生成 HTML 报告，可以看到每个文件中测试覆盖了哪些行：

.. code-block:: none

    $ coverage html

这个命令在 ``htmlcov`` 文件夹中生成测试报告，然后在浏览器中打开
``htmlcov/index.html`` 查看。

下面请阅读 :doc:`deploy` 。
