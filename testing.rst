测试 Flask 应用
==========================

   **未经测试的小猫，肯定不是一只好猫。**

谨以此句献给我的小猫。

Flask 为应用的测试提供了许多工具，本文我们就来聊一聊如何测试应用。

我们将使用 `pytest`_ 框架来设置并运行测试。

.. code-block:: text

    $ pip install pytest

.. _pytest: https://docs.pytest.org/

:doc:`tutorial </tutorial/index>` 介绍了如何 100% 测试覆盖示例 Flaskr
应用。关于特定测试的详细说明参见
:doc:`the tutorial on tests </tutorial/tests>` 。


识别测试
--------

测试通常位于 ``tests`` 文件夹中。测试可以是 Python 模块中以 ``test_``
开头的函数，也可以被组合到以 ``Test`` 开头的类中。

测试是一项复杂的工作。一般来说，尝试测试您自己编写的代码，而不是您使
用的库，因为它们已经过测试。 尝试将复杂的行为分解，并分别单独测试。


Fixtures
--------

Pytest *fixtures* 用于编写测试中的可重用代码片段。一个简单的 fixture
可以只返回一个值，复杂的可以进行初始化设置， yield 一个值，然后拆卸资
源。下面会谈到用于应用、测试客户端和 CLI 运行器的 fixture ，它们可以
放置在 ``tests/conftest.py`` 中。

如果您使用的是
:doc:`应用工厂 </patterns/appfactories>` ，那么可以定义一个 ``app``
fixture 来创建和配置一个应用实例。您可以在 ``yield`` 前后添加代码来初
始化和拆卸其他资源，例如创建和清除数据库。

如果不使用工厂，那么您已经有一个可以直接导入和配置的 app 对象，
您仍然可以使用 ``app`` fixture 来初始化设置和拆卸资源。

.. code-block:: python

    import pytest
    from my_project import create_app

    @pytest.fixture()
    def app():
        app = create_app()
        app.config.update({
            "TESTING": True,
        })

        # other setup can go here

        yield app

        # clean up / reset resources here


    @pytest.fixture()
    def client(app):
        return app.test_client()


    @pytest.fixture()
    def runner(app):
        return app.test_cli_runner()


用测试客户端发送请求
-------------------------------------

测试客户端向应用程序发出请求而不运行实时服务器。 Flask 的客户端扩展了
:doc:`Werkzeug 的客户端 <werkzeug:test>` ，请参阅文档以获取更多信息信
息。

``client`` 的方法与常见的 HTTP 请求方法相匹配，例如 ``client.get()``
和 ``client.post()`` 。他们接收很多参数用于构建请求；您可以在
:class:`~werkzeug.test.EnvironBuilder` 中找到全部文档。通常会使用
``path`` 、 ``query_string`` 、 ``headers`` 和 ``data`` 或 ``json`` 。

调用请求相应的方法，提供路由的路径就可以发送测试请求。然后检查返回的
:class:`~werkzeug.test.TestResponse` 对象，其包含响应数据和响应对象的
所有常见属性。通常可以看看 ``response.data`` ，它是视图返回在字节内容。
如果要使用文本， Werkzeug 2.1 提供了 ``response.text`` ，或者使用
``response.get_data(as_text=True)`` 也行。

.. code-block:: python

    def test_request_example(client):
        response = client.get("/posts")
        assert b"<h2>Hello, World!</h2>" in response.data


Pass a dict ``query_string={"key": "value", ...}`` to set arguments in
the query string (after the ``?`` in the URL). Pass a dict
``headers={}`` to set request headers.

To send a request body in a POST or PUT request, pass a value to
``data``. If raw bytes are passed, that exact body is used. Usually,
you'll pass a dict to set form data.


Form Data
~~~~~~~~~

To send form data, pass a dict to ``data``. The ``Content-Type`` header
will be set to ``multipart/form-data`` or
``application/x-www-form-urlencoded`` automatically.

If a value is a file object opened for reading bytes (``"rb"`` mode), it
will be treated as an uploaded file. To change the detected filename and
content type, pass a ``(file, filename, content_type)`` tuple. File
objects will be closed after making the request, so they do not need to
use the usual ``with open() as f:`` pattern.

It can be useful to store files in a ``tests/resources`` folder, then
use ``pathlib.Path`` to get files relative to the current test file.

.. code-block:: python

    from pathlib import Path

    # get the resources folder in the tests folder
    resources = Path(__file__).parent / "resources"

    def test_edit_user(client):
        response = client.post("/user/2/edit", data={
            "name": "Flask",
            "theme": "dark",
            "picture": (resources / "picture.png").open("rb"),
        })
        assert response.status_code == 200


JSON Data
~~~~~~~~~

To send JSON data, pass an object to ``json``. The ``Content-Type``
header will be set to ``application/json`` automatically.

Similarly, if the response contains JSON data, the ``response.json``
attribute will contain the deserialized object.

.. code-block:: python

    def test_json_data(client):
        response = client.post("/graphql", json={
            "query": """
                query User($id: String!) {
                    user(id: $id) {
                        name
                        theme
                        picture_url
                    }
                }
            """,
            variables={"id": 2},
        })
        assert response.json["data"]["user"]["name"] == "Flask"


Following Redirects
-------------------

By default, the client does not make additional requests if the response
is a redirect. By passing ``follow_redirects=True`` to a request method,
the client will continue to make requests until a non-redirect response
is returned.

:attr:`TestResponse.history <werkzeug.test.TestResponse.history>` is
a tuple of the responses that led up to the final response. Each
response has a :attr:`~werkzeug.test.TestResponse.request` attribute
which records the request that produced that response.

.. code-block:: python

    def test_logout_redirect(client):
        response = client.get("/logout")
        # Check that there was one redirect response.
        assert len(response.history) == 1
        # Check that the second request was to the index page.
        assert response.request.path == "/index"


Accessing and Modifying the Session
-----------------------------------

To access Flask's context variables, mainly
:data:`~flask.session`, use the client in a ``with`` statement.
The app and request context will remain active *after* making a request,
until the ``with`` block ends.

.. code-block:: python

    from flask import session

    def test_access_session(client):
        with client:
            client.post("/auth/login", data={"username": "flask"})
            # session is still accessible
            assert session["user_id"] == 1

        # session is no longer accessible

If you want to access or set a value in the session *before* making a
request, use the client's
:meth:`~flask.testing.FlaskClient.session_transaction` method in a
``with`` statement. It returns a session object, and will save the
session once the block ends.

.. code-block:: python

    from flask import session

    def test_modify_session(client):
        with client.session_transaction() as session:
            # set a user id without going through the login route
            session["user_id"] = 1

        # session is saved now

        response = client.get("/users/me")
        assert response.json["username"] == "flask"


.. _testing-cli:

Running Commands with the CLI Runner
------------------------------------

Flask provides :meth:`~flask.Flask.test_cli_runner` to create a
:class:`~flask.testing.FlaskCliRunner`, which runs CLI commands in
isolation and captures the output in a :class:`~click.testing.Result`
object. Flask's runner extends :doc:`Click's runner <click:testing>`,
see those docs for additional information.

Use the runner's :meth:`~flask.testing.FlaskCliRunner.invoke` method to
call commands in the same way they would be called with the ``flask``
command from the command line.

.. code-block:: python

    import click

    @app.cli.command("hello")
    @click.option("--name", default="World")
    def hello_command(name):
        click.echo(f"Hello, {name}!")

    def test_hello_command(runner):
        result = runner.invoke(args="hello")
        assert "World" in result.output

        result = runner.invoke(args=["hello", "--name", "Flask"])
        assert "Flask" in result.output


Tests that depend on an Active Context
--------------------------------------

You may have functions that are called from views or commands, that
expect an active :doc:`application context </appcontext>` or
:doc:`request context  </reqcontext>` because they access ``request``,
``session``, or ``current_app``. Rather than testing them by making a
request or invoking the command, you can create and activate a context
directly.

Use ``with app.app_context()`` to push an application context. For
example, database extensions usually require an active app context to
make queries.

.. code-block:: python

    def test_db_post_model(app):
        with app.app_context():
            post = db.session.query(Post).get(1)

Use ``with app.test_request_context()`` to push a request context. It
takes the same arguments as the test client's request methods.

.. code-block:: python

    def test_validate_user_edit(app):
        with app.test_request_context(
            "/user/2/edit", method="POST", data={"name": ""}
        ):
            # call a function that accesses `request`
            messages = validate_edit_user()

        assert messages["name"][0] == "Name cannot be empty."

Creating a test request context doesn't run any of the Flask dispatching
code, so ``before_request`` functions are not called. If you need to
call these, usually it's better to make a full request instead. However,
it's possible to call them manually.

.. code-block:: python

    def test_auth_token(app):
        with app.test_request_context("/user/2/edit", headers={"X-Auth-Token": "1"}):
            app.preprocess_request()
            assert g.user.name == "Flask"
