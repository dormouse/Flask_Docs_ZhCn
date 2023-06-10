快速上手
==========

等久了吧？本文会给您好好介绍如何上手 Flask 。
这里假定您已经安装好了 Flask ，否则请先阅读《 :doc:`installation` 》。


一个最小的应用
---------------------

一个最小的 Flask 应用如下：

.. code-block:: python

    from flask import Flask

    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"

那么，这些代码是什么意思呢？

1. 首先我们导入了 :class:`~flask.Flask` 类。该类的实例将会成为我们的
   WSGI 应用。
2. 接着我们创建一个该类的实例。第一个参数是应用模块或者包的名称。
   ``__name__`` 是一个适用于大多数情况的快捷方式。有了这个参数，
   Flask 才能知道在哪里可以找到模板和静态文件等东西。
3. 然后我们使用 :meth:`~flask.Flask.route` 装饰器来告诉 Flask 触发函
   数的 URL 。
4. 函数返回需要在用户浏览器中显示的信息。默认的内容类型是 HTML ，因此
   字符串中的 HTML 会被浏览器渲染。

把它保存为 :file:`hello.py` 或其他类似名称。请不要使用
:file:`flask.py` 作为应用名称，这会与 Flask 本身发生冲突。

可以使用 ``flask`` 命令或者 ``python -m flask`` 来运行这个应
用。你需要使用 ``--app`` 选项告诉 Flask 哪里可以找到应用。

.. code-block:: text

    $ flask --app hello run
     * Serving Flask app 'hello'
     * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)

.. admonition:: 应用发现行为

    作为一个捷径，如果文件名为 ``app.py`` 或者 ``wsgi.py`` ，那么您不
    需要使用 ``--app`` 。详见 :doc:`/cli` 。

这样就启动了一个非常简单的内建的服务器。这个服务器用于测试应该是足够
了，但是用于生产可能是不够的。关于部署的有关内容参见
:doc:`deploying/index` 。

现在在浏览器中打开 http://127.0.0.1:5000/ ，应该可以看到 Hello World!
字样。

如果其他程序已经占用了 5000 端口，那么在尝试启动服务器时会看到
``OSError: [Errno 98]`` 或者 ``OSError: [WinError 10013]`` ，
如何解决这个问题请参阅 :ref:`address-already-in-use` 。

.. _public-server:

.. admonition:: 外部可见的服务器

   运行服务器后，会发现只有您自己的电脑可以使用服务，而网络中的其他电
   脑却不行。缺省设置就是这样的，因为在调试模式下该应用的用户可以执行
   您电脑中的任意 Python 代码。

   如果您关闭了调试器或信任您网络中的用户，那么可以让服务器被公开访问。
   只要在命令行上简单的加上 ``--host=0.0.0.0`` 即可::

       $ flask run --host=0.0.0.0

   这行代码告诉您的操作系统监听所有公开的 IP 。


调试模式
----------

``flask run`` 命令不只可以启动开发服务器。如果您打开调试模式，那么服
务器会在修改应用代码之后自动重启，并且当请求过程中发生错误时还会在浏
览器中提供一个交互调试器。

.. image:: _static/debugger.png
    :align: center
    :class: screenshot
    :alt: The interactive debugger in action.

.. warning::

    调试器允许执行来自浏览器的任意 Python 代码。虽然它由一个 pin 保护，
    但仍然存在巨大安全风险。不要在生产环境中运行开发服务器或调试器。

如果要打开调试模式，请使用 ``--debug`` 选项。

.. code-block:: text

    $ flask --app hello run --debug
     * Serving Flask app 'hello'
     * Debug mode: on
     * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: nnn-nnn-nnn

另见：

-   :doc:`/server` 和 :doc:`/cli` 包含有关调试模式运行的内容。
-   :doc:`/debugging` 包含有关内置调试器和其他调试器的内容。
-   :doc:`/logging` 和 :doc:`/errorhandling` 包含有关日志记录和显示友
    好的出错信息页面的内容


HTML 转义
-------------

当返回 HTML （ Flask 中的默认响应类型）时，为了防止注入攻击，所有用户
提供的值在输出渲染前必须被转义。使用 Jinja （这个稍后会介绍）渲染的
HTML 模板会自动执行此操作。

在下面展示的 :func:`~markupsafe.escape` 可以手动转义。因为保持简洁的
原因，在多数示例中它被省略了，但您应该始终留心处理不可信的数据。

.. code-block:: python

    from markupsafe import escape

    @app.route("/<name>")
    def hello(name):
        return f"Hello, {escape(name)}!"

如果一个用户想要提交其名称为 ``<script>alert("bad")</script>`` ，那么
宁可转义为文本，也好过在浏览器中执行脚本。

路由中的 ``<name>`` 从 URL 中捕获值并将其传递给视图函数。这些变量规则
见下文。


路由
-------

现代 web 应用都使用有意义的 URL ，这样有助于用户记忆，网页会更得到用
户的青睐，提高回头率。

使用 :meth:`~flask.Flask.route` 装饰器来把函数绑定到 URL::

    @app.route('/')
    def index():
        return 'Index Page'

    @app.route('/hello')
    def hello():
        return 'Hello, World'

但是能做的不仅仅是这些！您可以动态变化 URL 的某些部分，
还可以为一个函数指定多个规则。

变量规则
``````````````

通过把 URL 的一部分标记为 ``<variable_name>`` 就可以在 URL 中添加变量。
标记的部分会作为关键字参数传递给函数。通过使用
``<converter:variable_name>`` ，可以选择性的加上一个转换器，为变量指
定规则。请看下面的例子::

    from markupsafe import escape

    @app.route('/user/<username>')
    def show_user_profile(username):
        # show the user profile for that user
        return f'User {escape(username)}'

    @app.route('/post/<int:post_id>')
    def show_post(post_id):
        # show the post with the given id, the id is an integer
        return f'Post {post_id}'

    @app.route('/path/<path:subpath>')
    def show_subpath(subpath):
        # show the subpath after /path/
        return f'Subpath {escape(subpath)}'

转换器类型：

========== ==========================================
``string`` （缺省值） 接受任何不包含斜杠的文本
``int``    接受正整数
``float``  接受正浮点数
``path``   类似 ``string`` ，但可以包含斜杠
``uuid``   接受 UUID 字符串
========== ==========================================


唯一的 URL / 重定向行为
``````````````````````````````````

以下两条规则的不同之处在于是否使用尾部的斜杠。::

    @app.route('/projects/')
    def projects():
        return 'The project page'

    @app.route('/about')
    def about():
        return 'The about page'

``projects`` 的 URL 是中规中矩的，尾部有一个斜杠，看起来就如同一个文
件夹。访问一个没有斜杠结尾的 URL （ ``/projects`` ）时 Flask 会自动进
行重定向，帮您在尾部加上一个斜杠（ ``/projects/`` ）。

``about`` 的 URL 没有尾部斜杠，因此其行为表现与一个文件类似。如果访问
这个 URL 时添加了尾部斜杠（ ``/about/`` ）就会得到一个 404
“未找到” 错误。这样可以保持 URL 唯一，并有助于搜索引擎重复索引同一
页面。


.. _url-building:

URL 构建
````````````

:func:`~flask.url_for` 函数用于构建指定函数的 URL。它把函数名称作为第
一个参数。它可以接受任意个关键字参数，每个关键字参数对应 URL 中的变量。
未知变量将添加到 URL 中作为查询参数。

为什么不在把 URL 写死在模板中，而要使用反转函数
:func:`~flask.url_for` 动态构建？

1. 反转通常比硬编码 URL 的描述性更好。
2. 您可以只在一个地方改变 URL ，而不用到处乱找。
3. URL 创建会为您处理特殊字符的转义，比较直观。
4. 生产的路径总是绝对路径，可以避免相对路径产生副作用。
5. 如果您的应用是放在 URL 根路径之外的地方（如在 ``/myapplication``
   中，不在 ``/`` 中）， :func:`~flask.url_for` 会为您妥善处理。

例如，这里我们使用 :meth:`~flask.Flask.test_request_context` 方法来尝
试使用 :func:`~flask.url_for` 。
:meth:`~flask.Flask.test_request_context` 告诉 Flask 正在处理一个请求，
而实际上也许我们正处在交互 Python shell 之中，并没有真正的请求。参见
:ref:`context-locals` 。

.. code-block:: python

    from flask import url_for

    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'index'

    @app.route('/login')
    def login():
        return 'login'

    @app.route('/user/<username>')
    def profile(username):
        return f'{username}\'s profile'

    with app.test_request_context():
        print(url_for('index'))
        print(url_for('login'))
        print(url_for('login', next='/'))
        print(url_for('profile', username='John Doe'))

.. code-block:: text

    /
    /login
    /login?next=/
    /user/John%20Doe


HTTP 方法
````````````
Web 应用使用不同的 HTTP 方法处理 URL 。当您使用 Flask 时，应当熟悉
HTTP 方法。缺省情况下，一个路由只回应 ``GET`` 请求。可以使用
:meth:`~flask.Flask.route` 装饰器的 ``methods`` 参数来处理不同的 HTTP
方法。
::

    from flask import request

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            return do_the_login()
        else:
            return show_the_login_form()

上例中把路由的所有方法都放在同一个函数中，当每个方法都使用一些共同的
数据时，这样是有用的。

你也可以把不同方法所对应的视图分别放在独立的函数中。 Flask 为每个常用
的 HTTP 方法提供了捷径，如 :meth:`~flask.Flask.get` 、
:meth:`~flask.Flask.post` 等等。

.. code-block:: python

    @app.get('/login')
    def login_get():
        return show_the_login_form()

    @app.post('/login')
    def login_post():
        return do_the_login()

如果当前使用了 ``GET`` 方法， Flask 会自动添加 ``HEAD`` 方法支持，并
且同时还会按照 `HTTP RFC`_ 来处理 ``HEAD`` 请求。同样， ``OPTIONS``
也会自动实现。

.. _HTTP RFC: https://www.ietf.org/rfc/rfc2068.txt

静态文件
------------

动态的 web 应用也需要静态文件，一般是 CSS 和 JavaScript 文件。理想情
况下您的服务器已经配置好了为您的提供静态文件的服务。但是在开发过程中，
Flask 也能做好这项工作。只要在您的包或模块旁边创建一个名为
:file:`static` 的文件夹就行了。静态文件位于应用的 ``/static`` 中。

使用特定的 ``'static'`` 端点就可以生成相应的 URL ::

    url_for('static', filename='style.css')

这个静态文件在文件系统中的位置应该是 :file:`static/style.css` 。

渲染模板
--------

在 Python 内部生成 HTML 不好玩，且相当笨拙。因为您必须自己负责 HTML
转义，以确保应用的安全。因此， Flask 自动为您配置
`Jinja2 <https://palletsprojects.com/p/jinja/>`_ 模板引擎。

模板可被用于生成任何类型的文本文件。对于 web 应用来说，主要用于生成
HTML 页面，但是也可以生成 markdown 、用于电子邮件的纯文本等等。

HTML 、 CSS 和其他 web API ，请参阅 `MDN Web 文档`_ 。

.. _MDN Web 文档: https://developer.mozilla.org/

使用 :func:`~flask.render_template` 方法可以渲染模板，您只要提供模板
名称和需要作为参数传递给模板的变量就行了。下面是一个简单的模板渲染例
子::

    from flask import render_template

    @app.route('/hello/')
    @app.route('/hello/<name>')
    def hello(name=None):
        return render_template('hello.html', name=name)

Flask 会在 :file:`templates` 文件夹内寻找模板。因此，如果您的应用是一
个模块，那么模板文件夹应该在模块旁边；如果是一个包，那么就应该在包里
面：

**情形 1** : 一个模块::

    /application.py
    /templates
        /hello.html

**情形 2** : 一个包::

    /application
        /__init__.py
        /templates
            /hello.html

您可以充分使用 Jinja2 模板引擎的威力。更多内容，详见官方
`Jinja2 模板文档 <https://jinja.palletsprojects.com/templates/>`_ 。

模板示例：

.. sourcecode:: html+jinja

    <!doctype html>
    <title>Hello from Flask</title>
    {% if name %}
      <h1>Hello {{ name }}!</h1>
    {% else %}
      <h1>Hello, World!</h1>
    {% endif %}

在模板内部可以像使用 :func:`~flask.url_for` 和
:func:`~flask.get_flashed_messages` 函数一样访问
:data:`~flask.Flask.config` 、 :class:`~flask.request`
、 :class:`~flask.session` 和 :class:`~flask.g` [#]_ 对象。

模板在继承使用的情况下尤其有用。其工作原理参见
:doc:`patterns/templateinheritance` 。简单的说，模板继承可以使每个页
面的特定元素（如页头、导航和页尾）保持一致。

自动转义默认开启。因此，如果 ``name`` 包含 HTML ，那么会被自动转义。
如果您可以信任某个变量，且知道它是安全的 HTML （例如变量来自一个把
wiki 标记转换为 HTML 的模块），那么可以使用
:class:`~markupsafe.Markup` 类把它标记为安全的，或者在模板中使用
``|safe`` 过滤器。更多例子参见 Jinja 2 文档。

下面 :class:`~markupsafe.Markup` 类的基本使用方法::

    >>> from markupsafe import Markup
    >>> Markup('<strong>Hello %s!</strong>') % '<blink>hacker</blink>'
    Markup('<strong>Hello &lt;blink&gt;hacker&lt;/blink&gt;!</strong>')
    >>> Markup.escape('<blink>hacker</blink>')
    Markup('&lt;blink&gt;hacker&lt;/blink&gt;')
    >>> Markup('<em>Marked up</em> &raquo; HTML').striptags()
    'Marked up » HTML'

.. versionchanged:: 0.5

   自动转义不再为所有模板开启，只为扩展名为 ``.html`` 、 ``.htm`` 、
   ``.xml`` 和 ``.xhtml`` 开启。从字符串载入的模板会关闭自动转义。

.. [#] 不确定 :class:`~flask.g` 对象是什么？它是某个可以根据需要储存
   信息的东西，详见 :class:`~flask.g` 对象的文档和
   :doc:`patterns/sqlite3` 。


操作请求数据
----------------------

对于 web 应用来说对客户端向服务器发送的数据作出响应很重要。在 Flask
中由全局对象 :class:`~flask.request` 来提供请求信息。如果您有一些
Python 基础，那么可能 会奇怪：既然这个对象是全局的，怎么还能保持线程
安全？答案是本地环境：

.. _context-locals:

本地环境
``````````````

.. admonition:: 内部信息

   如果您想了解工作原理和如何使用本地环境进行测试，那么请阅读本节，
   否则可以跳过本节。

某些对象在 Flask 中是全局对象，但不是通常意义下的全局对象。这些对象实
际上是特定环境下本地对象的代理。真拗口！但还是很容易理解的。

设想现在处于处理线程的环境中。一个请求进来了，服务器决定生成一个新线
程（或者叫其他什么名称的东西，这个下层的东西能够处理包括线程在内的并
发系统）。当 Flask 开始其内部请求处理时会把当前线程作为活动环境，并把
当前应用和 WSGI 环境绑定到这个环境（线程）。它以一种聪明的方式使得一
个应用可以在不中断的情况下调用另一个应用。

这对您有什么用？基本上您可以完全不必理会。这个只有在做单元测试时才有
用。在测试时会遇到由于没有请求对象而导致依赖于请求的代码会突然崩溃的
情况。对策是自己创建一个请求对象并绑定到环境。最简单的单元测试解决方
案是使用 :meth:`~flask.Flask.test_request_context` 环境管理器。通过使
用 ``with`` 语句可以绑定一个测试请求，以便于交互。例如::

    from flask import request

    with app.test_request_context('/hello', method='POST'):
        # now you can do something with the request until the
        # end of the with block, such as basic assertions:
        assert request.path == '/hello'
        assert request.method == 'POST'

另一种方式是把整个 WSGI 环境传递给
:meth:`~flask.Flask.request_context` 方法::

    with app.request_context(environ):
        assert request.method == 'POST'

请求对象
``````````````````

请求对象在 API 一节中有详细说明这里不细谈（参见
:class:`~flask.Request` ）。这里简略地谈一下最常见的操作。首先，您必
须从 ``flask`` 模块导入请求对象::

    from flask import request

通过使用 :attr:`~flask.Request.method` 属性可以操作当前请求方法，通过
使用 :attr:`~flask.Request.form` 属性处理表单数据（在 ``POST`` 或者
``PUT`` 请求中传输的数据）。以下是使用上述两个属性的例子::

    @app.route('/login', methods=['POST', 'GET'])
    def login():
        error = None
        if request.method == 'POST':
            if valid_login(request.form['username'],
                           request.form['password']):
                return log_the_user_in(request.form['username'])
            else:
                error = 'Invalid username/password'
        # the code below is executed if the request method
        # was GET or the credentials were invalid
        return render_template('login.html', error=error)

当 ``form`` 属性中不存在这个键时会发生什么？会引发一个
:exc:`KeyError` 。如果您不像捕捉一个标准错误一样捕捉 :exc:`KeyError` ，
那么会显示一个 HTTP 400 Bad Request 错误页面。因此，多数情况下您不必
处理这个问题。

要操作 URL （如 ``?key=value`` ）中提交的参数可以使用
:attr:`~flask.Request.args` 属性::

    searchword = request.args.get('key', '')


用户可能会改变 URL 导致出现一个 400 请求出错页面，这样降低了用户友好
度。因此，我们推荐使用 `get` 或通过捕捉 :exc:`KeyError` 来访问 URL
参数。

完整的请求对象方法和属性参见 :class:`~flask.Request` 文档。

文件上传
````````````

用 Flask 处理文件上传很容易，只要确保不要忘记在您的 HTML 表单中设置
``enctype="multipart/form-data"`` 属性就可以了。否则浏览器将不会传送
您的文件。

已上传的文件被储存在内存或文件系统的临时位置。您可以通过请求对象
:attr:`~flask.request.files` 属性来访问上传的文件。每个上传的文件都储
存在这个字典型属性中。这个属性基本和标准 Python :class:`file` 对象一
样，另外多出一个用于把上传文件保存到服务器的文件系统中的
:meth:`~werkzeug.datastructures.FileStorage.save` 方法。下例展示其如
何运作::

    from flask import request

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            f = request.files['the_file']
            f.save('/var/www/uploads/uploaded_file.txt')
        ...

如果想要知道文件上传之前其在客户端系统中的名称，可以使用
:attr:`~werkzeug.datastructures.FileStorage.filename` 属性。但是请牢
记这个值是可以伪造的，永远不要信任这个值。如果想要把客户端的文件名作
为服务器上的文件名，可以通过 Werkzeug 提供的
:func:`~werkzeug.utils.secure_filename` 函数::

    from werkzeug.utils import secure_filename

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            file = request.files['the_file']
            file.save(f"/var/www/uploads/{secure_filename(file.filename)}")
        ...

更好的例子参见 :doc:`patterns/fileuploads` 。

Cookies
```````
要访问 cookies ，可以使用 :attr:`~flask.Request.cookies` 属性。可以使
用响应对象 的 :attr:`~flask.Response.set_cookie` 方法来设置 cookies 。
请求对象的 :attr:`~flask.Request.cookies` 属性是一个包含了客户端传输
的所有 cookies 的字典。在 Flask 中，如果使用 :ref:`sessions` ，那么就
不要直接使用 cookies ，因为 :ref:`sessions` 比较安全一些。

读取 cookies::

    from flask import request

    @app.route('/')
    def index():
        username = request.cookies.get('username')
        # use cookies.get(key) instead of cookies[key] to not get a
        # KeyError if the cookie is missing.

储存 cookies::

    from flask import make_response

    @app.route('/')
    def index():
        resp = make_response(render_template(...))
        resp.set_cookie('username', 'the username')
        return resp

注意， cookies 设置在响应对象上。通常只是从视图函数返回字符串， Flask
会把它们转换为响应对象。如果您想显式地转换，那么可以使用
:meth:`~flask.make_response` 函数，然后再修改它。

使用 doc:`patterns/deferredcallbacks` 方案可以在没有响应对象的情况下
设置一个 cookie 。

另见 :ref:`about-responses` 。

重定向和错误
--------------------

使用 :func:`~flask.redirect` 函数可以重定向。使用
:func:`~flask.abort` 可以更早退出请求，并返回错误代码::

    from flask import abort, redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login')
    def login():
        abort(401)
        this_is_never_executed()

上例实际上是没有意义的，它让一个用户从索引页重定向到一个无法访问的页
面（401 表示禁止访问）。但是上例可以说明重定向和出错跳出是如何工作的。

缺省情况下每种出错代码都会对应显示一个黑白的出错页面。使用
:meth:`~flask.Flask.errorhandler` 装饰器可以定制出错页面::

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page_not_found.html'), 404

注意 :func:`~flask.render_template` 后面的 ``404`` ，这表示页面对就的
出错代码是 404 ，即页面不存在。缺省情况下 200 表示：一切正常。

详见 :doc:`errorhandling` 。

.. _about-responses:

关于响应
---------------

视图函数的返回值会自动转换为一个响应对象。如果返回值是一个字符串，那
么会被转换为一个包含作为响应体的字符串、一个 ``200 OK`` 出错代码 和一
个 :mimetype:`text/html` 类型的响应对象。如果返回值是一个字典或者列表，
那么会调用 :func:`jsonify` 来产生一个响应。以下是转换的规则：

1.  如果视图返回的是一个响应对象，那么就直接返回它。
2.  如果返回的是一个字符串，那么根据这个字符串和缺省参数生成一个用于
    返回的响应对象。
3.  如果返回的是一个迭代器或者生成器，那么返回字符串或者字节，作为流
    响应对待。
4.  如果返回的是一个字典或者列表，那么使用
    :func:`~flask.json.jsonify` 创建一个响应对象。
5.  如果返回的是一个元组，那么元组中的项目可以提供额外的信息。元组中
    必须至少包含一个项目，且项目应当由 ``(response, status)`` 、
    ``(response, headers)`` 或者 ``(response, status, headers)``  组
    成。 ``status`` 的值会重载状态代码， ``headers`` 是一个由额外头部
    值组成的列表或字典。
6.  如果以上都不是，那么 Flask 会假定返回值是一个有效的 WSGI 应用并把
    它转换为一个响应对象。

如果想要在视图内部掌控响应对象的结果，那么可以使用
:func:`~flask.make_response` 函数。

设想有如下视图::

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html'), 404

可以使用 :func:`~flask.make_response` 包裹返回表达式，获得响应对象，
并对该对象进行修改，然后再返回::

    @app.errorhandler(404)
    def not_found(error):
        resp = make_response(render_template('error.html'), 404)
        resp.headers['X-Something'] = 'A value'
        return resp


JSON 格式的 API
````````````````

JSON 格式的响应是常见的，用 Flask 写这样的 API 是很容易上手的。如果从
视图返回一个 ``dict`` 或者 ``list`` ，那么它会被转换为一个 JSON 响应。

.. code-block:: python

    @app.route("/me")
    def me_api():
        user = get_current_user()
        return {
            "username": user.username,
            "theme": user.theme,
            "image": url_for("user_image", filename=user.image),
        }

如果 ``dict`` 还不能满足需求，还需要创建其他类型的 JSON 格式响应，可
以使用 :func:`~flask.json.jsonify` 函数。该函数会序列化任何支持的
JSON 数据类型。也可以研究研究 Flask 社区扩展，以支持更复杂的应用。

.. code-block:: python

    @app.route("/users")
    def users_api():
        users = get_all_users()
        return [user.to_json() for user in users]

这是一个向 :func:`~flask.json.jsonify` 函数传递数据的捷径，可以序列化
任何支持的 JSON 数据类型。这也意味着在字典和列表中的所有数据必须可以
被序列化。

对于复杂的数据类型，如数据库模型，你需要使用序列化库先把数据转换为合
法的 JSON 类型。有许多库，以及社区维护的 Flask API 扩展可以处理复杂数
据类型，

.. _sessions:

会话
--------
除了请求对象之外还有一种称为 :class:`~flask.session` 的对象，允许您在
不同请求之间储存信息。这个对象相当于用密钥签名加密的 cookie ，即用户
可以查看您的 cookie ，但是如果没有密钥就无法修改它。

使用会话之前您必须设置一个密钥。举例说明::

    from flask import session

    # Set the secret key to some random bytes. Keep this really secret!
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    @app.route('/')
    def index():
        if 'username' in session:
            return f'Logged in as {session["username"]}'
        return 'You are not logged in'

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        return '''
            <form method="post">
                <p><input type=text name=username>
                <p><input type=submit value=Login>
            </form>
        '''

    @app.route('/logout')
    def logout():
        # remove the username from the session if it's there
        session.pop('username', None)
        return redirect(url_for('index'))

.. admonition:: 如何生成一个好的密钥

    生成随机数的关键在于一个好的随机种子，因此一个好的密钥应当有足够
    的随机性。操作系统可以有多种方式基于密码随机生成器来生成随机数据。
    使用下面的命令可以快捷的为 :attr:`Flask.secret_key` （ 或者
    :data:`SECRET_KEY` ）生成值::

        $ python -c 'import secrets; print(secrets.token_hex())'
        '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'

基于 cookie 的会话的说明： Flask 会取出会话对象中的值，把值序列化后储
存到 cookie 中。在打开 cookie 的情况下，如果需要查找某个值，但是这个
值在请求中没有持续储存的话，那么不会得到一个清晰的出错信息。请检查页
面响应中的 cookie 的大小是否与网络浏览器所支持的大小一致。

除了缺省的客户端会话之外，还有许多 Flask 扩展支持服务端会话。


消息闪现
----------------

一个好的应用和用户接口都有良好的反馈，否则到后来用户就会讨厌这个应用。
Flask 通过闪现系统来提供了一个易用的反馈方式。闪现系统的基本工作原理
是在请求结束时记录一个消息，提供且只提供给下一个请求使用。通常通过一
个布局模板来展现闪现的消息。

:func:`~flask.flash`  用于闪现一个消息。在模板中，使用
:func:`~flask.get_flashed_messages` 来操作消息。完整的例子参见
:doc:`patterns/flashing` 。

日志
-------

.. versionadded:: 0.3

有时候可能会遇到数据出错需要纠正的情况。例如因为用户篡改了数据或客户
端代码出错而导致一个客户端代码向服务器发送了明显错误的 HTTP 请求。多
数时候在类似情况下返回 ``400 Bad Request`` 就没事了，但也有不会返回的
时候，而代码还得继续运行下去。

这时候就需要使用日志来记录这些不正常的东西了。自从 Flask 0.3 后就已经
为您配置好了一个日志工具。

以下是一些日志调用示例::

    app.logger.debug('A value for debugging')
    app.logger.warning('A warning occurred (%d apples)', 42)
    app.logger.error('An error occurred')

:attr:`~flask.Flask.logger` 是一个标准的日志
:class:`~logging.Logger` 类，更多信息详见官方的 :mod:`logging` 文档。

参见 :doc:`errorhandling` 。


集成 WSGI 中间件
---------------------------

如果想要在应用中添加一个 WSGI 中间件，那么可以用应用的 ``wsgi_app``
属性来包装。例如，假设需要在 Nginx 后面使用
:class:`~werkzeug.middleware.proxy_fix.ProxyFix` 中间件，那么可以这样
做::

    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
 
用 ``app.wsgi_app`` 来包装，而不用 ``app`` 包装，意味着 ``app`` 仍旧
指向您的 Flask 应用，而不是指向中间件。这样可以继续直接使用和配置
``app`` 。

使用 Flask 扩展
----------------------

扩展是帮助完成公共任务的包。例如 Flask-SQLAlchemy 为在 Flask 中轻松使
用 SQLAlchemy 提供支持。

更多关于 Flask 扩展的内容请参阅 :doc:`extensions` 。

部署到网络服务器
-------------------------

已经准备好部署您的新 Flask 应用了？请移步 :doc:`deploying/index` 。
