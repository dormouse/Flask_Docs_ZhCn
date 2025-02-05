测试 Flask 应用
==========================

   **未经测试的小猫，肯定不是一只好猫。**

谨以此句献给我的小猫。

Flask 为应用的测试提供了许多工具，本文我们就来聊一聊如何测试应用。

我们将使用 `pytest`_ 框架来设置并运行测试。

.. code-block:: text

    $ pip install pytest

.. _pytest: https://docs.pytest.org/

:doc:`教程 </tutorial/index>` 介绍了如何 100% 测试覆盖示例 Flaskr
应用。关于特定测试的详细说明参见
:doc:`教程中的测试一节 </tutorial/tests>` 。


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

在查询字符串中设置参数（ URL 中 ``?`` 后面的内容）的方法是传递一个
``query_string={"key": "value", ...}`` 字典 。设置请求头部的方法是传
递一个 ``headers={}`` 字典。

在一个 POST 或者 PUT 请求中发送一个请求正文的方法是把值传递给
``data`` 。如果传递的是原始字节，那么就会原封不动地作为请求正文。但
是，通常的做法是传递一个字典，设置表单数据。


表单数据
~~~~~~~~~

把一个字典传递给 ``data`` ，可以设置表单数据。 ``Content-Type`` 头部
会自动设置为 ``multipart/form-data`` 或者
``application/x-www-form-urlencoded`` 。

如果值是一个以读取字节模式（ ``"rb"`` ）打开的文件对象，那么会被作为
一个上传文件对待。其文件名和内容类型会被自动侦测，传递一个
``(file, filename, content_type)`` 元组可以改变它们。
文件对象会在生成请求后自动关闭，所以无需使用常见的
``with open() as f:`` 模式。

一个比较实用的技巧是把文件放在 ``tests/resources`` 文件夹中，然后使用
``pathlib.Path`` 来获取其相对于当前测试文件的相对路径。

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


JSON 数据
~~~~~~~~~

把一个对象传递给 ``json`` ，可以发送 JSON 数据，
``Content-Type`` 头部会被自动设置为 ``application/json`` 。

同样，如果响应包含 JSON 数据，那么 ``response.json`` 属性将包含反序列
化的对象。

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


追随重定向
-------------------

:attr:`TestResponse.history <werkzeug.test.TestResponse.history>` is
a tuple of the responses that led up to the final response. Each
response has a :attr:`~werkzeug.test.TestResponse.request` attribute
which records the request that produced that response.

默认情况下，如果响应是一个重定向，客户端不会发出额外的请求。如果将
``follow_redirects=True`` 传递给请求方法，客户端将继续发出请求，直到
返回一个非重定向响应。

:attr:`TestResponse.history <werkzeug.test.TestResponse.history>`
是一个记录了所有响应的元组。每个响应都有一个
:attr:`~werkzeug.test.TestResponse.request` 属性，其记录了产生该响应
的请求。

.. code-block:: python

    def test_logout_redirect(client):
        response = client.get("/logout", follow_redirects=True)
        # Check that there was one redirect response.
        assert len(response.history) == 1
        # Check that the second request was to the index page.
        assert response.request.path == "/index"


访问和修改会话
----------------------------------

访问 Flask 的情境变量，主要是 :data:`~flask.session` ，可以在一个
``with`` 语句中使用客户端。应用程序和请求情境在生成一个请求
*之后* 会保持活动状态，直到 ``with`` 块结束。

.. code-block:: python

    from flask import session

    def test_access_session(client):
        with client:
            client.post("/auth/login", data={"username": "flask"})
            # session is still accessible
            assert session["user_id"] == 1

        # session is no longer accessible

如果要在生成请求 *之前* 访问和设置会话中的值，那么可以在一个 ``with``
语句中使用客户端的
:meth:`~flask.testing.FlaskClient.session_transaction` 方法。
这样会返回一个会话对象，并且在块结束时会保存会话。

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

使用 CLI 运行器运行命令
------------------------------------

Flask 提供 :meth:`~flask.Flask.test_cli_runner` 方法用以创建
:class:`~flask.testing.FlaskCliRunner` 类，它可以独立运行 CLI 命令，
并在 :class:`~click.testing.Result` 对象中获取输出。
Flask 的运行器扩展了 :doc:`Click 的运行器 <click:testing>` ，更多内容
详见其文档。

使用运行器的 :meth:`~flask.testing.FlaskCliRunner.invoke` 方法来
调用命令的方式与在命令下使用 ``flask`` 命令调用的方式相同。

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


依赖于活动状态情境的测试
--------------------------------------

有些从视图或命令调用的函数，因为需要访问 ``request`` ` ``session``
或者 ``current_app`` ，所有希望有一个活动的 
:doc:`应用情境 </appcontext>` 或者 :doc:`请求情境 </reqcontext>` 。
这时你可以直接创建并激活一个情境，而不是通过制作一个请求或调用命令来
进行测试。

使用 ``with app.app_context()`` 来推送应用情境。例如，数据库扩展通常
需要一个活动的应用情境来进行查询。

.. code-block:: python

    def test_db_post_model(app):
        with app.app_context():
            post = db.session.query(Post).get(1)

使用 ``with app.test_request_context()`` 来推送请求情境。它的参数与
测试客户端的请求方法一样。

.. code-block:: python

    def test_validate_user_edit(app):
        with app.test_request_context(
            "/user/2/edit", method="POST", data={"name": ""}
        ):
            # call a function that accesses `request`
            messages = validate_edit_user()

        assert messages["name"][0] == "Name cannot be empty."

创建一个测试请求情境不会运行任何 Flask 调度代码，所以不会调用
``before_request`` 函数。如果你需要调用，那么通常最好使用一个完整请求。
当然，手动调用也是可以的。

.. code-block:: python

    def test_auth_token(app):
        with app.test_request_context("/user/2/edit", headers={"X-Auth-Token": "1"}):
            app.preprocess_request()
            assert g.user.name == "Flask"
