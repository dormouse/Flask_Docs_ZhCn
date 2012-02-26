.. _quickstart:

快速上手
==========

渴望开始了吧？本文会给你好好介绍如何上手 Flask 。这里假定你已经安装好了
Flask ，如果没装请参考《 :ref:`installation` 》。


一个最小的应用
---------------------

一个最小的 Flask 应用如下::

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello World!'

    if __name__ == '__main__':
        app.run()

把它保存为 `hello.py` 或其他类似名称并用你的 Python 解释器运行这个文件。请不要
使用 `flask.py` 作为应用名称，这会与 Flask 本身发生冲突。

::

    $ python hello.py
     * Running on http://127.0.0.1:5000/

在浏览器中打开 `http://127.0.0.1:5000/ <http://127.0.0.1:5000/>`_ ，你应该可以
看到你的问候了。

那么这些代码是什么意思？

1. 首先我们导入了 :class:`~flask.Flask` 类。这个类的实例将会成为我们的 WSGI
   应用。第一个参数是应用模块的名称。如果你使用一个单一模块（就像本例），那么
   应当使用 `__name__` ，因为名称会根据这个模块是按应用开始还是作为一个模块导入
   而发生变化（可能是 ``'__main__'`` ，也可能实际导入的名称）。更多内容详见
   :class:`~flask.Flask` 文档。
2. 接着我们创建了一个实例，向它传递模块 / 包的名称。这样是为了让 Flask 知道可以
   在哪里找到模板和静态文件等东西。
3. 然后我们使用 :meth:`~flask.Flask.route` 装饰器来告诉 Flask 触发函数的 URL 。
4. 函数名称可用于生成相关联的 URL ，并返回需要在用户浏览器中显示的信息。
5. 最后，使用 :meth:`~flask.Flask.run` 函数来运行本地服务器和我们的应用。
   ``if __name__ == '__main__':`` 确保服务器只会在使用 Python 解释器运行代码的
   情况下运行，而不会在作为模块导入时运行。

按 control-C 可以停止服务器。

.. _public-server:

.. admonition:: 外部可见的服务器。

   如果运行服务器，会发现只有你自己的电脑可以使用服务，而网络中的其他电脑不行。
   缺省设置就是这样的，因为在调试模式下应用的用户可以执行你的电脑中的任意
   Python 代码。如果你关闭了 `调试` 或信任你网络中的用户，那么可以让服务器被
   公开访问。

   只要像这样改变 :meth:`~flask.Flask.run` 方法的调用::

       app.run(host='0.0.0.0')

   这行代码告诉你的操作系统在一个公开的 IP 上监听。


调试模式
----------

虽然 :meth:`~flask.Flask.run` 方法可以方便地启动一个本地开发服务器，但是每次
修改应用之后都需要手动重启服务器。这样不是很方便， Flask 可以做得更好。如果你
打开调试模式，那么服务器会在修改应用之后自动重启，并且当应用出错时还会提供一个
有用的调试器。

打开调试模式有两种方法，一种是在应用对象上设置标志::

    app.debug = True
    app.run()

另一种是作为参数传递给 run 方法::

    app.run(debug=True)

两种方法的效果相同。

.. admonition:: 注意

   虽然交互调试器不能在分布环境下工作（这使得它基本不可能用于生产环境），但是
   它允许执行任意代码，这样会成为一个重大安全隐患。因此， **绝对不能在生产环境中
   使用调试器** 。

运行的调试器的截图：

.. image:: _static/debugger.png
   :align: center
   :class: screenshot
   :alt: screenshot of debugger in action

.. admonition:: 与其他调试器一起工作

   调试器之间会相互干扰。如果你正在使用其他调试器 （如 PyDev 或 IntelliJ ），
   那么可能需要设置 ``app.debug = False`` 。


路由
-------

现代 web 应用都使用漂亮的 URL ，有助于人们记忆，对于使用网速较慢的移动设备尤其
有利。如果用户可以不通过点击首页而直达所需要的页面，那么这个网页会更得到用户的
青睐，提高回头率。

如前文所述， :meth:`~flask.Flask.route` 装饰器用于把一个函数绑定到一个 URL 。
下面是一些基本的例子::

    @app.route('/')
    def index():
        return 'Index Page'

    @app.route('/hello')
    def hello():
        return 'Hello World'

但是能做的不仅仅是这些！你可以动态变化 URL 的某些部分，还可以为一个函数指定多个
规则。

变更规则
``````````````

通过 URL 的一部分标记为 ``<variable_name>`` 就可以在 URL 中添加变量。标记的部分
会作为关键字参数传递给函数。通过使用 ``<converter:variable_name>`` ，可以选择性
的加上一个转换器，为变量指定规则。请看下面的例子::

    @app.route('/user/<username>')
    def show_user_profile(username):
        # show the user profile for that user
        pass

    @app.route('/post/<int:post_id>')
    def show_post(post_id):
        # show the post with the given id, the id is an integer
        pass

现有的转换器有：

=========== ===========================================
`int`       接受整数
`float`     接受浮点数
`path`      和缺省情况相同，但也接受斜杠
=========== ===========================================

.. admonition:: 唯一的 URL / 重定向行为

   Flask 的 URL 规则都是基于 Werkzeug 的路由模块的。其背后的理念是保证漂亮的
   外观和唯一的 URL 。这个理念来自于 Apache 和更早期的服务器。

   假设有如下两条规则::

        @app.route('/projects/')
        def projects():
            pass

        @app.route('/about')
        def about():
            pass

   它们看上去很相近，不同之处在于 URL *定义* 中尾部的斜杠。第一个例子中
   `prjects` 的 URL 是中规中举的，尾部有一个斜杠，看起来就如同一个文件夹。访问
   一个没有斜杠结尾的 URL 时 Flask 会自动进行重定向，帮你在尾部加上一个斜杠。

   但是在第二个例子中， URL 没有尾部斜杠，因此其行为表现与一个文件类似。如果
   访问这个 URL 时添加了尾部斜杠就会得到一个 404 错误。

   为什么这样做？因为这样可以使用户在忘记使用尾部斜杠时继续访问相关的 URL 。
   这种重定向行为与 Apache 和其他服务器一致。同时， URL 仍保持唯一，帮助搜索
   引擎不重复索引同一页面。


.. _url-building:

URL 构建
````````````

如果可以匹配 URL ，那么也可以生成 URL 吗？当然可以。 :func:`~flask.url_for`
函数就是用于构建指定函数的 URL 的。它把函数名称作为第一个参数，其余参数对应
URL 中的变量。未知变量将添加到 URL 中作为查询参数。举例：

>>> from flask import Flask, url_for
>>> app = Flask(__name__)
>>> @app.route('/')
... def index(): pass
...
>>> @app.route('/login')
... def login(): pass
...
>>> @app.route('/user/<username>')
... def profile(username): pass
...
>>> with app.test_request_context():
...  print url_for('index')
...  print url_for('login')
...  print url_for('login', next='/')
...  print url_for('profile', username='John Doe')
...
/
/login
/login?next=/
/user/John%20Doe

（例子中还使用下文要讲到的 :meth:`~flask.Flask.test_request_context` 方法。这个
方法的作用是告诉 Flask 我们正在处理一个请求，而实际上也许我们正处在交互
Python shell 之中，并没有真正的请求。详见下面的 :ref:`context-locals` ）。

为什么不在把 URL 写死在模板中，反而要动态构建？有三个很好的理由： 

1. 反向解析通常比硬编码 URL 更直观。同时，更重要的是你可以只在一个地方改变
   URL ，而不用到处乱找。
2. URL 创建会为你处理特殊字符的转义和 Unicode 数据，不用你操心。
3. 如果你的应用是放在 URL 根路径之外的地方（如在 ``/myapplication`` 中，不在
   ``/`` 中）， :func:`~flask.url_for` 会为你妥善处理。


HTTP 方法
````````````

HTTP （ web 应用使用的协议）) knows different methods
to access URLs.  By default a route only answers to `GET` requests, but
that can be changed by providing the `methods` argument to the
:meth:`~flask.Flask.route` decorator.  Here are some examples::

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            do_the_login()
        else:
            show_the_login_form()

If `GET` is present, `HEAD` will be added automatically for you.  You
don't have to deal with that.  It will also make sure that `HEAD` requests
are handled like the `HTTP RFC`_ (the document describing the HTTP
protocol) demands, so you can completely ignore that part of the HTTP
specification.  Likewise as of Flask 0.6, `OPTIONS` is implemented for you
as well automatically.

You have no idea what an HTTP method is?  Worry not, here is a quick
introduction to HTTP methods and why they matter:

The HTTP method (also often called "the verb") tells the server what the
clients wants to *do* with the requested page.  The following methods are
very common:

`GET`
    The browser tells the server to just *get* the information stored on
    that page and send it.  This is probably the most common method.

`HEAD`
    The browser tells the server to get the information, but it is only
    interested in the *headers*, not the content of the page.  An
    application is supposed to handle that as if a `GET` request was
    received but to not deliver the actual content.  In Flask you don't
    have to deal with that at all, the underlying Werkzeug library handles
    that for you.

`POST`
    The browser tells the server that it wants to *post* some new
    information to that URL and that the server must ensure the data is
    stored and only stored once.  This is how HTML forms are usually
    transmitting data to the server.

`PUT`
    Similar to `POST` but the server might trigger the store procedure
    multiple times by overwriting the old values more than once.  Now you
    might be asking why is this useful, but there are some good reasons
    to do it this way.  Consider that the connection gets lost during
    transmission: in this situation a system between the browser and the
    server might receive the request safely a second time without breaking
    things.  With `POST` that would not be possible because it must only
    be triggered once.

`DELETE`
    Remove the information at the given location.

`OPTIONS`
    Provides a quick way for a client to figure out which methods are
    supported by this URL.  Starting with Flask 0.6, this is implemented
    for you automatically.

Now the interesting part is that in HTML4 and XHTML1, the only methods a
form can submit to the server are `GET` and `POST`.  But with JavaScript
and future HTML standards you can use the other methods as well.  Furthermore
HTTP has become quite popular lately and browsers are no longer the only
clients that are using HTTP. For instance, many revision control system
use it.

.. _HTTP RFC: http://www.ietf.org/rfc/rfc2068.txt

Static Files
------------

Dynamic web applications need static files as well.  That's usually where
the CSS and JavaScript files are coming from.  Ideally your web server is
configured to serve them for you, but during development Flask can do that
as well.  Just create a folder called `static` in your package or next to
your module and it will be available at `/static` on the application.

To generate URLs to that part of the URL, use the special ``'static'`` URL
name::

    url_for('static', filename='style.css')

The file has to be stored on the filesystem as ``static/style.css``.

Rendering Templates
-------------------

Generating HTML from within Python is not fun, and actually pretty
cumbersome because you have to do the HTML escaping on your own to keep
the application secure.  Because of that Flask configures the `Jinja2
<http://jinja.pocoo.org/2/>`_ template engine for you automatically.

To render a template you can use the :func:`~flask.render_template`
method.  All you have to do is to provide the name of the template and the
variables you want to pass to the template engine as keyword arguments.
Here's a simple example of how to render a template::

    from flask import render_template

    @app.route('/hello/')
    @app.route('/hello/<name>')
    def hello(name=None):
        return render_template('hello.html', name=name)

Flask will look for templates in the `templates` folder.  So if your
application is a module, that folder is next to that module, if it's a
package it's actually inside your package:

**Case 1**: a module::

    /application.py
    /templates
        /hello.html

**Case 2**: a package::

    /application
        /__init__.py
        /templates
            /hello.html

For templates you can use the full power of Jinja2 templates.  Head over
to the the official `Jinja2 Template Documentation
<http://jinja.pocoo.org/2/documentation/templates>`_ for more information.

Here is an example template:

.. sourcecode:: html+jinja

    <!doctype html>
    <title>Hello from Flask</title>
    {% if name %}
      <h1>Hello {{ name }}!</h1>
    {% else %}
      <h1>Hello World!</h1>
    {% endif %}

Inside templates you also have access to the :class:`~flask.request`,
:class:`~flask.session` and :class:`~flask.g` [#]_ objects
as well as the :func:`~flask.get_flashed_messages` function.

Templates are especially useful if inheritance is used.  If you want to
know how that works, head over to the :ref:`template-inheritance` pattern
documentation.  Basically template inheritance makes it possible to keep
certain elements on each page (like header, navigation and footer).

Automatic escaping is enabled, so if name contains HTML it will be escaped
automatically.  If you can trust a variable and you know that it will be
safe HTML (because for example it came from a module that converts wiki
markup to HTML) you can mark it as safe by using the
:class:`~jinja2.Markup` class or by using the ``|safe`` filter in the
template.  Head over to the Jinja 2 documentation for more examples.

Here is a basic introduction to how the :class:`~jinja2.Markup` class works:

>>> from flask import Markup
>>> Markup('<strong>Hello %s!</strong>') % '<blink>hacker</blink>'
Markup(u'<strong>Hello &lt;blink&gt;hacker&lt;/blink&gt;!</strong>')
>>> Markup.escape('<blink>hacker</blink>')
Markup(u'&lt;blink&gt;hacker&lt;/blink&gt;')
>>> Markup('<em>Marked up</em> &raquo; HTML').striptags()
u'Marked up \xbb HTML'

.. versionchanged:: 0.5

   Autoescaping is no longer enabled for all templates.  The following
   extensions for templates trigger autoescaping: ``.html``, ``.htm``,
   ``.xml``, ``.xhtml``.  Templates loaded from a string will have
   autoescaping disabled.

.. [#] Unsure what that :class:`~flask.g` object is? It's something in which
   you can store information for your own needs, check the documentation of
   that object (:class:`~flask.g`) and the :ref:`sqlite3` for more
   information.


Accessing Request Data
----------------------

For web applications it's crucial to react to the data a client sent to
the server.  In Flask this information is provided by the global
:class:`~flask.request` object.  If you have some experience with Python
you might be wondering how that object can be global and how Flask
manages to still be threadsafe.  The answer are context locals:


.. _context-locals:

Context Locals
``````````````

.. admonition:: Insider Information

   If you want to understand how that works and how you can implement
   tests with context locals, read this section, otherwise just skip it.

Certain objects in Flask are global objects, but not of the usual kind.
These objects are actually proxies to objects that are local to a specific
context.  What a mouthful.  But that is actually quite easy to understand.

Imagine the context being the handling thread.  A request comes in and the
webserver decides to spawn a new thread (or something else, the
underlying object is capable of dealing with other concurrency systems
than threads as well).  When Flask starts its internal request handling it
figures out that the current thread is the active context and binds the
current application and the WSGI environments to that context (thread).
It does that in an intelligent way that one application can invoke another
application without breaking.

So what does this mean to you?  Basically you can completely ignore that
this is the case unless you are doing something like unittesting.  You
will notice that code that depends on a request object will suddenly break
because there is no request object.  The solution is creating a request
object yourself and binding it to the context.  The easiest solution for
unittesting is by using the :meth:`~flask.Flask.test_request_context`
context manager.  In combination with the `with` statement it will bind a
test request so that you can interact with it.  Here is an example::

    from flask import request

    with app.test_request_context('/hello', method='POST'):
        # now you can do something with the request until the
        # end of the with block, such as basic assertions:
        assert request.path == '/hello'
        assert request.method == 'POST'

The other possibility is passing a whole WSGI environment to the
:meth:`~flask.Flask.request_context` method::

    from flask import request

    with app.request_context(environ):
        assert request.method == 'POST'

The Request Object
``````````````````

The request object is documented in the API section and we will not cover
it here in detail (see :class:`~flask.request`). Here is a broad overview of
some of the most common operations.  First of all you have to import it from
the `flask` module::

    from flask import request

The current request method is available by using the
:attr:`~flask.request.method` attribute.  To access form data (data
transmitted in a `POST` or `PUT` request) you can use the
:attr:`~flask.request.form` attribute.  Here is a full example of the two
attributes mentioned above::

    @app.route('/login', methods=['POST', 'GET'])
    def login():
        error = None
        if request.method == 'POST':
            if valid_login(request.form['username'],
                           request.form['password']):
                return log_the_user_in(request.form['username'])
            else:
                error = 'Invalid username/password'
        # this is executed if the request method was GET or the
        # credentials were invalid

What happens if the key does not exist in the `form` attribute?  In that
case a special :exc:`KeyError` is raised.  You can catch it like a
standard :exc:`KeyError` but if you don't do that, a HTTP 400 Bad Request
error page is shown instead.  So for many situations you don't have to
deal with that problem.

To access parameters submitted in the URL (``?key=value``) you can use the
:attr:`~flask.request.args` attribute::

    searchword = request.args.get('q', '')

We recommend accessing URL parameters with `get` or by catching the
`KeyError` because users might change the URL and presenting them a 400
bad request page in that case is not user friendly.

For a full list of methods and attributes of the request object, head over
to the :class:`~flask.request` documentation.


File Uploads
````````````

You can handle uploaded files with Flask easily.  Just make sure not to
forget to set the ``enctype="multipart/form-data"`` attribute on your HTML
form, otherwise the browser will not transmit your files at all.

Uploaded files are stored in memory or at a temporary location on the
filesystem.  You can access those files by looking at the
:attr:`~flask.request.files` attribute on the request object.  Each
uploaded file is stored in that dictionary.  It behaves just like a
standard Python :class:`file` object, but it also has a
:meth:`~werkzeug.datastructures.FileStorage.save` method that allows you to store that
file on the filesystem of the server.  Here is a simple example showing how
that works::

    from flask import request

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            f = request.files['the_file']
            f.save('/var/www/uploads/uploaded_file.txt')
        ...

If you want to know how the file was named on the client before it was
uploaded to your application, you can access the
:attr:`~werkzeug.datastructures.FileStorage.filename` attribute.  However please keep in
mind that this value can be forged so never ever trust that value.  If you
want to use the filename of the client to store the file on the server,
pass it through the :func:`~werkzeug.utils.secure_filename` function that
Werkzeug provides for you::

    from flask import request
    from werkzeug import secure_filename

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            f = request.files['the_file']
            f.save('/var/www/uploads/' + secure_filename(f.filename))
        ...

For some better examples, checkout the :ref:`uploading-files` pattern.

Cookies
```````

To access cookies you can use the :attr:`~flask.Request.cookies`
attribute.  To set cookies you can use the
:attr:`~flask.Response.set_cookie` method of response objects.  The
:attr:`~flask.Request.cookies` attribute of request objects is a
dictionary with all the cookies the client transmits.  If you want to use
sessions, do not use the cookies directly but instead use the
:ref:`sessions` in Flask that add some security on top of cookies for you.

Reading cookies::

    from flask import request

    @app.route('/')
    def index():
        username = request.cookies.get('username')
        # use cookies.get(key) instead of cookies[key] to not get a
        # KeyError if the cookie is missing.

Storing cookies::

    from flask import make_response

    @app.route('/')
    def index():
        resp = make_response(render_template(...))
        resp.set_cookie('username', 'the username')
        return resp

Note that cookies are set on response objects.  Since you normally you
just return strings from the view functions Flask will convert them into
response objects for you.  If you explicitly want to do that you can use
the :meth:`~flask.make_response` function and then modify it.

Sometimes you might want to set a cookie at a point where the response
object does not exist yet.  This is possible by utilizing the
:ref:`deferred-callbacks` pattern.

For this also see :ref:`about-responses`.

Redirects and Errors
--------------------

To redirect a user to somewhere else you can use the
:func:`~flask.redirect` function. To abort a request early with an error
code use the :func:`~flask.abort` function.  Here an example how this works::

    from flask import abort, redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login')
    def login():
        abort(401)
        this_is_never_executed()

This is a rather pointless example because a user will be redirected from
the index to a page they cannot access (401 means access denied) but it
shows how that works.

By default a black and white error page is shown for each error code.  If
you want to customize the error page, you can use the
:meth:`~flask.Flask.errorhandler` decorator::

    from flask import render_template

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page_not_found.html'), 404

Note the ``404`` after the :func:`~flask.render_template` call.  This
tells Flask that the status code of that page should be 404 which means
not found.  By default 200 is assumed which translates to: all went well.

.. _about-responses:

About Responses
---------------

The return value from a view function is automatically converted into a
response object for you.  If the return value is a string it's converted
into a response object with the string as response body, an ``200 OK``
error code and a ``text/html`` mimetype.  The logic that Flask applies to
converting return values into response objects is as follows:

1.  If a response object of the correct type is returned it's directly
    returned from the view.
2.  If it's a string, a response object is created with that data and the
    default parameters.
3.  If a tuple is returned the response object is created by passing the
    tuple as arguments to the response object's constructor.
4.  If neither of that works, Flask will assume the return value is a
    valid WSGI application and converts that into a response object.

If you want to get hold of the resulting response object inside the view
you can use the :func:`~flask.make_response` function.

Imagine you have a view like this:

.. sourcecode:: python

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html'), 404

You just need to wrap the return expression with
:func:`~flask.make_response` and get the result object to modify it, then
return it:

.. sourcecode:: python

    @app.errorhandler(404)
    def not_found(error):
        resp = make_response(render_template('error.html'), 404)
        resp.headers['X-Something'] = 'A value'
        return resp

.. _sessions:

Sessions
--------

Besides the request object there is also a second object called
:class:`~flask.session` that allows you to store information specific to a
user from one request to the next.  This is implemented on top of cookies
for you and signs the cookies cryptographically.  What this means is that
the user could look at the contents of your cookie but not modify it,
unless they know the secret key used for signing.

In order to use sessions you have to set a secret key.  Here is how
sessions work::

    from flask import Flask, session, redirect, url_for, escape, request

    app = Flask(__name__)

    @app.route('/')
    def index():
        if 'username' in session:
            return 'Logged in as %s' % escape(session['username'])
        return 'You are not logged in'

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        return '''
            <form action="" method="post">
                <p><input type=text name=username>
                <p><input type=submit value=Login>
            </form>
        '''

    @app.route('/logout')
    def logout():
        # remove the username from the session if its there
        session.pop('username', None)
        return redirect(url_for('index'))

    # set the secret key.  keep this really secret:
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

The here mentioned :func:`~flask.escape` does escaping for you if you are
not using the template engine (like in this example).

.. admonition:: How to generate good secret keys

   The problem with random is that it's hard to judge what random is.  And
   a secret key should be as random as possible.  Your operating system
   has ways to generate pretty random stuff based on a cryptographic
   random generator which can be used to get such a key:

   >>> import os
   >>> os.urandom(24)
   '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

   Just take that thing and copy/paste it into your code and you're done.

Message Flashing
----------------

Good applications and user interfaces are all about feedback.  If the user
does not get enough feedback they will probably end up hating the
application.  Flask provides a really simple way to give feedback to a
user with the flashing system.  The flashing system basically makes it
possible to record a message at the end of a request and access it next
request and only next request.  This is usually combined with a layout
template that does this.

To flash a message use the :func:`~flask.flash` method, to get hold of the
messages you can use :func:`~flask.get_flashed_messages` which is also
available in the templates.  Check out the :ref:`message-flashing-pattern`
for a full example.

Logging
-------

.. versionadded:: 0.3

Sometimes you might be in a situation where you deal with data that
should be correct, but actually is not.  For example you may have some client
side code that sends an HTTP request to the server but it's obviously
malformed.  This might be caused by a user tempering with the data, or the
client code failing.  Most of the time, it's okay to reply with ``400 Bad
Request`` in that situation, but sometimes that won't do and the code has
to continue working.

You may still want to log that something fishy happened.  This is where
loggers come in handy.  As of Flask 0.3 a logger is preconfigured for you
to use.

Here are some example log calls::

    app.logger.debug('A value for debugging')
    app.logger.warning('A warning occurred (%d apples)', 42)
    app.logger.error('An error occurred')

The attached :attr:`~flask.Flask.logger` is a standard logging
:class:`~logging.Logger`, so head over to the official `logging
documentation <http://docs.python.org/library/logging.html>`_ for more
information.

Hooking in WSGI Middlewares
---------------------------

If you want to add a WSGI middleware to your application you can wrap the
internal WSGI application.  For example if you want to use one of the
middlewares from the Werkzeug package to work around bugs in lighttpd, you
can do it like this::

    from werkzeug.contrib.fixers import LighttpdCGIRootFix
    app.wsgi_app = LighttpdCGIRootFix(app.wsgi_app)
