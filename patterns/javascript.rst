JavaScript 、 ``fetch`` 和 JSON
==================================

你可以想要在数据改变时动态改变局部 HTML 页面，而不是重载整个页面。
如果要实现这个功能，那么就不应当提交一个 HTML ``<form>`` ，直接执行重
定向来重新渲染模板。你可以添加 `JavaScript`_ ，调用 |fetch|_ ，替换页
面上的内容。

|fetch|_ 是现代的、内置的 JavaScript 解决方案，用于从页面上进行请求。
你可能听说过其他的“ AJAX ”方法和库，如 |XHR|_ 或 `jQuery`_ 。这些在
现代浏览器中已经不再需要了。当然你可以根据应用需求选择使用它们或其他
库。本文将只关注内置的 JavaScript 功能。

.. _JavaScript: https://developer.mozilla.org/Web/JavaScript
.. |fetch| replace:: ``fetch()``
.. _fetch: https://developer.mozilla.org/Web/API/Fetch_API
.. |XHR| replace:: ``XMLHttpRequest()``
.. _XHR: https://developer.mozilla.org/Web/API/XMLHttpRequest
.. _jQuery: https://jquery.com/


渲染模板
-------------------

了解模板和 JavaScript 之间的区别是很重要的。模板是在响应被发送到用户
浏览器之前，在服务器上渲染的。 JavaScript 在用户的浏览器中运行的，在
模板被渲染和发送之后。因此，我们不可能使用 JavaScript 来影响如何渲染
Jinja 模板，但有可能将数据渲染到将要运行的 JavaScript 中。

为了在渲染模板时向 JavaScript 提供数据，可以在 ``<script>`` 块中使用
:func:`~jinja-filters.tojson` 过滤器。这将使数据转换为有效的
JavaScript 对象，并确保任何不安全的 HTML 字符被安全渲染。如果你不使用
``tojson`` 过滤器，你会在浏览器控制台中得到一个 ``SyntaxError`` 。

.. code-block:: python

    data = generate_report()
    return render_template("report.html", chart_data=data)

.. code-block:: jinja

    <script>
        const chart_data = {{ chart_data|tojson }}
        chartLib.makeChart(chart_data)
    </script>

一个不太常见的模式是将数据添加到一个 HTML 标签的 ``data-`` 属性中。在
这种情况下，你必须在值周围使用单引号，而不是双引号，否则就会产生无效
的或不安全的 HTML 。

.. code-block:: jinja

    <div data-chart='{{ chart_data|tojson }}'></div>


生成 URL
---------------

从服务器上获取数据到 JavaScript 的另一种方法是为数据提出一个
请求。首先，你需要知道要请求的URL。

生成 URL 的最简单方法是当渲染模板时，继续使用 :func:`~flask.url_for` 。
例如：

.. code-block:: javascript

    const user_url = {{ url_for("user", id=current_user.id)|tojson }}
    fetch(user_url).then(...)

然而，你可能只能根据 JavaScript 中的信息来生成 URL 。如上所述，
JavaScript 是在用户的浏览器中运行的，而不是模板的一部分，所以不能使用
``url_for`` 。

在这种情况下，你需要知道“ root URL ”，即你的应用是在哪个 URL 下运行
的。在简单的设置中，一般是 ``/`` ，但也可能是其他的，比如
``https://example.com/myapp/`` 。

如何告诉 JavaScript 代码 root URL ？一个简单方法是在渲染时将其设置为
全局变量，然后在从 JavaScript 生成 URL 时使用它。

.. code-block:: javascript

    const SCRIPT_ROOT = {{ request.script_root|tojson }}
    let user_id = ...  // do something to get a user id from the page
    let user_url = `${SCRIPT_ROOT}/user/${user_id}`
    fetch(user_url).then(...)


使用 ``fetch`` 提出请求
-------------------------------

|fetch|_ 接收两个参数，一个 URL 和一个带有其他选项的对象，它返回一个
|Promise|_ 。我们不会涉及所有可用的选项，将只在 promise 上使用
``then()`` ，而不是其他回调或 ``await`` 语法。阅读链接的 MDN 文档，了
解更多信息。

默认情况下，使用 GET 方法。如果响应包含 JSON ，那么可以被用于
``then()`` 回调链。

.. code-block:: javascript

    const room_url = {{ url_for("room_detail", id=room.id)|tojson }}
    fetch(room_url)
        .then(response => response.json())
        .then(data => {
            // data is a parsed JSON object
        })

要发送数据，请使用一个数据方法，如 POST ，并传递 ``body`` 选项。最常
见的数据类型是表单数据或 JSON 数据。

要发送表单数据，请传递一个已填充的 |FormData|_ 对象。这个对象使用使用
与 HTML 表单相同的格式，可以在 Flask 视图中用 ``request.form`` 访问。

.. code-block:: javascript

    let data = new FormData()
    data.append("name", "Flask Room")
    data.append("description", "Talk about Flask here.")
    fetch(room_url, {
        "method": "POST",
        "body": data,
    }).then(...)

一般来说，最好将请求数据作为表单数据发送，就像提交 HTML 表单时那样。
JSON 可以表示更复杂的数据，但除非必要，否则最好坚持使用更简单的格式。
当发送 JSON 数据时，必须同时发送 ``Content-Type: application/json``
头，否则 Flask 会返回一个 400 错误。

.. code-block:: javascript

    let data = {
        "name": "Flask Room",
        "description": "Talk about Flask here.",
    }
    fetch(room_url, {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(data),
    }).then(...)

.. |Promise| replace:: ``Promise``
.. _Promise: https://developer.mozilla.org/Web/JavaScript/Reference/Global_Objects/Promise
.. |FormData| replace:: ``FormData``
.. _FormData: https://developer.mozilla.org/en-US/docs/Web/API/FormData


跟随重定向
-------------------

一个响应可能是一个重定向，例如，如果你用 JavaScript 而不是传统的 HTML
表单登录，并且你的视图返回了一个重定向而不是 JSON 。 JavaScript 请求
是跟随重定向的，但是并不改变页面。如果你想改变页面，那么可以检查响应
并手动重定向。

.. code-block:: javascript

    fetch("/login", {"body": ...}).then(
        response => {
            if (response.redirected) {
                window.location = response.url
            } else {
                showLoginError()
            }
        }
    )


替换内容
-----------------

响应可能是新的 HTML ，要么是添加或替换页面的一部分，要么是一个全新的
页面。一般来说，如果你要返回整个页面，那么最好用前文所述的重定向来处
理。下面的例子展示如何用请求返回的 HTML 替换 ``<div>`` 。

.. code-block:: html

    <div id="geology-fact">
        {{ include "geology_fact.html" }}
    </div>
    <script>
        const geology_url = {{ url_for("geology_fact")|tojson }}
        const geology_div = getElementById("geology-fact")
        fetch(geology_url)
            .then(response => response.text)
            .then(text => geology_div.innerHTML = text)
    </script>


从视图返回 JSON
----------------------

如果要从你的 API 视图返回一个 JSON 对象，那么可以从视图直接返回一个字
典，它会自动序列化为 JSON 。

.. code-block:: python

    @app.route("/user/<int:id>")
    def user_detail(id):
        user = User.query.get_or_404(id)
        return {
            "username": User.username,
            "email": User.email,
            "picture": url_for("static", filename=f"users/{id}/profile.png"),
        }

如果你需要返回其他 JSON 类型，那么可以使用
:func:`~flask.json.jsonify` 函数，它会用给定的数据创建一个响应对象，
并序列化为 JSON 。

.. code-block:: python

    from flask import jsonify

    @app.route("/users")
    def user_list():
        users = User.query.order_by(User.name).all()
        return jsonify([u.to_json() for u in users])

在 JSON 响应中返回文件数据通常不是一个好主意。
JSON 不能直接表示二进制数据，所以它必须经过 base64 编码。
这可能会很慢，占用更多的带宽，而且不容易缓存。

相反，应当使用一个视图来提供文件，并在 JSON 中包含一个指向所需要文件
的 URL 。然后，在获得 JSON 后，客户端提出一个单独请求得到链接的资源。


在视图中接收 JSON
-----------------------

使用 :data:`~flask.request` 对象的 :attr:`~flask.Request.json` 属性，
将请求的主体解码为JSON。如果主体不是有效的 JSON ，或者
``Content-Type`` 头没有设置为 ``application/json`` ，就会出现 400 Bad
Request 错误。

.. code-block:: python

    from flask import request

    @app.post("/user/<int:id>")
    def user_update(id):
        user = User.query.get_or_404(id)
        user.update_from_json(request.json)
        db.session.commit()
        return user.to_json()
