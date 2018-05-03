.. _quickstart:

快速上手
==========

等久了吧？本文会给你好好介绍如何上手 Flask 。
这里假定你已经安装好了 Flask ，否则请先阅读《 :ref:`installation` 》。

一个最小的应用
---------------------

一个最小的 Flask 应用如下::

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

那么，这些代码是什么意思呢？

1. 首先我们导入了 :class:`~flask.Flask` 类。
   该类的实例将会成为我们的 WSGI 应用。
2. 接着我们创建一个该类的实例。第一个参数是应用模块或者包的名称。如果你使用
   一个单一模块（就像本例），那么应当使用 ``__name__`` ，因为名称会根据这个
   模块是按应用方式使用还是作为一个模块导入而发生变化（可能是 '__main__' ，
   也可能是实际导入的名称）。这个参数是必需的，这样 Flask 才能知道在哪里可以
   找到模板和静态文件等东西。更多内容详见 :class:`~flask.Flask` 文档。
3. 然后我们使用 :meth:`~flask.Flask.route` 装饰器来告诉 Flask 触发函数的 URL 。
4. 函数名称被用于生成相关联的 URL 。函数最后返回需要在用户浏览器中显示的信息。

把它保存为 :file:`hello.py` 或其他类似名称。请不要使用 :file:`flask.py`
作为应用名称，这会与 Flask 本身发生冲突。

可以使用 :command:`flask` 命令或者 python 的 ``-m`` 开关来运行这个应用。在
运行应用之前，需要在终端里导出 ``FLASK_APP`` 环境变量::

    $ export FLASK_APP=hello.py
    $ flask run
     * Running on http://127.0.0.1:5000/

如果是在 Windows 下，那么导出环境变量的语法取决于使用的是哪种命令行解释器。
在 Command Prompt 下::

    C:\path\to\app>set FLASK_APP=hello.py

在 PowerShell 下::

    PS C:\path\to\app> $env:FLASK_APP = "hello.py"

还可以使用 :command:`python -m flask`::

    $ export FLASK_APP=hello.py
    $ python -m flask run
     * Running on http://127.0.0.1:5000/

这样就启动了一个非常简单的内建的服务器。这个服务器用于测试应该是足够了。但是
用于生产可以是不够的。关于部署的有关内容参见《 :ref:`deployment` 》。

现在在浏览器中打开 `http://127.0.0.1:5000/ <http://127.0.0.1:5000/>`_ ，应该
可以看到 Hello World! 字样。

.. _public-server:

.. admonition:: 外部可见的服务器

   运行服务器后，会发现只有你自己的电脑可以使用服务，而网络中的其他电脑却
   不行。缺省设置就是这样的，因为在调试模式下该应用的用户可以执行你电脑中
   的任意 Python 代码。

   如果你关闭了调试器或信任你网络中的用户，那么可以让服务器被公开访问。
   只要在命令行上简单的加上 ``--host=0.0.0.0`` 即可::

       flask run --host=0.0.0.0

   这行代码告诉你的操作系统监听所有公开的 IP 。


如果服务器不能启动怎么办
---------------------------------------

假如运行 :command:`python -m flask` 命令失败或者 :command:`flask` 命令不存在，
那么可能会有多种原因导致失败。首先应该检查错误信息。

老版本的 Flask
````````````````````
版本低于 0.11 的 Flask ，启动应用的方式是不同的。简单的说就是
:command:`flask` 和 :command:`python -m flask` 命令都无法使用。在这种情况有
两个选择：一是升级 Flask 到更新的版本，二是参阅《 :ref:`server` 》，学习其他
启动服务器的方法。

非法导入名称
```````````````````
``FLASK_APP`` 环境变量中储存的是模块的名称，运行 :command:`flask run` 命令就
会导入这个模块。如果模块的名称不对，那么就会出现导入错误。出现错误的时机是在
应用开始的时候。如果调试模式打开的情况下，会在运行到应用开始的时候出现导入
错误。出错信息会告诉你尝试导入哪个模块时出错，为什么会出错。

最常见的错误是因为拼写错误而没有真正创建一个 ``app`` 对象。

.. _debug-mode:

调试模式
----------

（只需要记录出错信息和追踪堆栈？参见 :ref:`application-errors` ）

虽然 :command:`flask` 命令可以方便地启动一个本地开发服务器，但是每次应用代码
修改之后都需要手动重启服务器。这样不是很方便， Flask 可以做得更好。如果你打开
调试模式，那么服务器会在修改应用代码之后自动重启，并且当应用出错时还会提供一个
有用的调试器。

如果需要打开所有开发功能（包括调试模式），那么要在运行服务器之前导出
``FLASK_ENV`` 环境变量并把其设置为 ``development``::

    $ export FLASK_ENV=development
    $ flask run

（在 Windows 下需要使用 ``set`` 来代替 ``export`` 。）

这样可以实现以下功能：

1.  激活调试器。
2.  激活自动重载。
3.  打开 Flask 应用的调试模式。

还可以通过导出 ``FLASK_DEBUG=1`` 来单独控制调试模式的开关。

:ref:`server` 文档中还有更多的参数说明。

.. admonition:: Attention

   虽然交互调试器不能在分布环境下工作（这使得它基本不可能用于生产环境），但是
   它允许执行任意代码，这样会成为一个重大安全隐患。因此， **绝对不能在生产环境
   中使用调试器** 。

运行中的调试器截图：

.. image:: _static/debugger.png
   :align: center
   :class: screenshot
   :alt: screenshot of debugger in action

更多关于调试器的信息参见 `Werkzeug documentation`_ 。

.. _Werkzeug documentation: http://werkzeug.pocoo.org/docs/debug/#using-the-debugger

想使用其他调试器？请参阅 :ref:`working-with-debuggers` 。


路由
-------

现代 web 应用都使用有意义的 URL ，这样有助于用户记忆，网页会更得到用户的青睐，
提高回头率。

使用 :meth:`~flask.Flask.route` 装饰器来把函数绑定到 URL::

    @app.route('/')
    def index():
        return 'Index Page'

    @app.route('/hello')
    def hello():
        return 'Hello, World'

但是能做的不仅仅是这些！你可以动态变化 URL 的某些部分，
还可以为一个函数指定多个规则。

变量规则
``````````````

通过把 URL 的一部分标记为 ``<variable_name>`` 就可以在 URL 中添加变量。标记的
部分会作为关键字参数传递给函数。通过使用 ``<converter:variable_name>`` ，可以
选择性的加上一个转换器，为变量指定规则。请看下面的例子::

    @app.route('/user/<username>')
    def show_user_profile(username):
        # show the user profile for that user
        return 'User %s' % username

    @app.route('/post/<int:post_id>')
    def show_post(post_id):
        # show the post with the given id, the id is an integer
        return 'Post %d' % post_id

    @app.route('/path/<path:subpath>')
    def show_subpath(subpath):
        # show the subpath after /path/
        return 'Subpath %s' % subpath

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

The following two rules differ in their use of a trailing slash. ::

    @app.route('/projects/')
    def projects():
        return 'The project page'

    @app.route('/about')
    def about():
        return 'The about page'

The canonical URL for the ``projects`` endpoint has a trailing slash.
It's similar to a folder in a file system. If you access the URL without
a trailing slash, Flask redirects you to the canonical URL with the
trailing slash.

The canonical URL for the ``about`` endpoint does not have a trailing
slash. It's similar to the pathname of a file. Accessing the URL with a
trailing slash produces a 404 "Not Found" error. This helps keep URLs
unique for these resources, which helps search engines avoid indexing
the same page twice.


.. _url-building:

URL Building
````````````

To build a URL to a specific function, use the :func:`~flask.url_for` function.
It accepts the name of the function as its first argument and any number of
keyword arguments, each corresponding to a variable part of the URL rule.
Unknown variable parts are appended to the URL as query parameters.

Why would you want to build URLs using the URL reversing function
:func:`~flask.url_for` instead of hard-coding them into your templates?

1. Reversing is often more descriptive than hard-coding the URLs.
2. You can change your URLs in one go instead of needing to remember to
    manually change hard-coded URLs.
3. URL building handles escaping of special characters and Unicode data
    transparently.
4. The generated paths are always absolute, avoiding unexpected behavior
   of relative paths in browsers.
5. If your application is placed outside the URL root, for example, in
    ``/myapplication`` instead of ``/``, :func:`~flask.url_for` properly
    handles that for you.

For example, here we use the :meth:`~flask.Flask.test_request_context` method
to try out :func:`~flask.url_for`. :meth:`~flask.Flask.test_request_context`
tells Flask to behave as though it's handling a request even while we use a
Python shell. See :ref:`context-locals`. ::

    from flask import Flask, url_for

    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'index'

    @app.route('/login')
    def login():
        return 'login'

    @app.route('/user/<username>')
    def profile(username):
        return '{}'s profile'.format(username)

    with app.test_request_context():
        print(url_for('index'))
        print(url_for('login'))
        print(url_for('login', next='/'))
        print(url_for('profile', username='John Doe'))

    /
    /login
    /login?next=/
    /user/John%20Doe

HTTP Methods
````````````

Web applications use different HTTP methods when accessing URLs. You should
familiarize yourself with the HTTP methods as you work with Flask. By default,
a route only answers to ``GET`` requests. You can use the ``methods`` argument
of the :meth:`~flask.Flask.route` decorator to handle different HTTP methods.
::

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            return do_the_login()
        else:
            return show_the_login_form()

If ``GET`` is present, Flask automatically adds support for the ``HEAD`` method
and handles ``HEAD`` requests according to the the `HTTP RFC`_. Likewise,
``OPTIONS`` is automatically implemented for you.

.. _HTTP RFC: https://www.ietf.org/rfc/rfc2068.txt

Static Files
------------

Dynamic web applications also need static files.  That's usually where
the CSS and JavaScript files are coming from.  Ideally your web server is
configured to serve them for you, but during development Flask can do that
as well.  Just create a folder called :file:`static` in your package or next to
your module and it will be available at ``/static`` on the application.

To generate URLs for static files, use the special ``'static'`` endpoint name::

    url_for('static', filename='style.css')

The file has to be stored on the filesystem as :file:`static/style.css`.

Rendering Templates
-------------------

Generating HTML from within Python is not fun, and actually pretty
cumbersome because you have to do the HTML escaping on your own to keep
the application secure.  Because of that Flask configures the `Jinja2
<http://jinja.pocoo.org/>`_ template engine for you automatically.

To render a template you can use the :func:`~flask.render_template`
method.  All you have to do is provide the name of the template and the
variables you want to pass to the template engine as keyword arguments.
Here's a simple example of how to render a template::

    from flask import render_template

    @app.route('/hello/')
    @app.route('/hello/<name>')
    def hello(name=None):
        return render_template('hello.html', name=name)

Flask will look for templates in the :file:`templates` folder.  So if your
application is a module, this folder is next to that module, if it's a
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
to the official `Jinja2 Template Documentation
<http://jinja.pocoo.org/docs/templates>`_ for more information.

Here is an example template:

.. sourcecode:: html+jinja

    <!doctype html>
    <title>Hello from Flask</title>
    {% if name %}
      <h1>Hello {{ name }}!</h1>
    {% else %}
      <h1>Hello, World!</h1>
    {% endif %}

Inside templates you also have access to the :class:`~flask.request`,
:class:`~flask.session` and :class:`~flask.g` [#]_ objects
as well as the :func:`~flask.get_flashed_messages` function.

Templates are especially useful if inheritance is used.  If you want to
know how that works, head over to the :ref:`template-inheritance` pattern
documentation.  Basically template inheritance makes it possible to keep
certain elements on each page (like header, navigation and footer).

Automatic escaping is enabled, so if ``name`` contains HTML it will be escaped
automatically.  If you can trust a variable and you know that it will be
safe HTML (for example because it came from a module that converts wiki
markup to HTML) you can mark it as safe by using the
:class:`~jinja2.Markup` class or by using the ``|safe`` filter in the
template.  Head over to the Jinja 2 documentation for more examples.

Here is a basic introduction to how the :class:`~jinja2.Markup` class works::

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

For web applications it's crucial to react to the data a client sends to
the server.  In Flask this information is provided by the global
:class:`~flask.request` object.  If you have some experience with Python
you might be wondering how that object can be global and how Flask
manages to still be threadsafe.  The answer is context locals:


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
web server decides to spawn a new thread (or something else, the
underlying object is capable of dealing with concurrency systems other
than threads).  When Flask starts its internal request handling it
figures out that the current thread is the active context and binds the
current application and the WSGI environments to that context (thread).
It does that in an intelligent way so that one application can invoke another
application without breaking.

So what does this mean to you?  Basically you can completely ignore that
this is the case unless you are doing something like unit testing.  You
will notice that code which depends on a request object will suddenly break
because there is no request object.  The solution is creating a request
object yourself and binding it to the context.  The easiest solution for
unit testing is to use the :meth:`~flask.Flask.test_request_context`
context manager.  In combination with the ``with`` statement it will bind a
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
it here in detail (see :class:`~flask.Request`). Here is a broad overview of
some of the most common operations.  First of all you have to import it from
the ``flask`` module::

    from flask import request

The current request method is available by using the
:attr:`~flask.Request.method` attribute.  To access form data (data
transmitted in a ``POST`` or ``PUT`` request) you can use the
:attr:`~flask.Request.form` attribute.  Here is a full example of the two
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
        # the code below is executed if the request method
        # was GET or the credentials were invalid
        return render_template('login.html', error=error)

What happens if the key does not exist in the ``form`` attribute?  In that
case a special :exc:`KeyError` is raised.  You can catch it like a
standard :exc:`KeyError` but if you don't do that, a HTTP 400 Bad Request
error page is shown instead.  So for many situations you don't have to
deal with that problem.

To access parameters submitted in the URL (``?key=value``) you can use the
:attr:`~flask.Request.args` attribute::

    searchword = request.args.get('key', '')

We recommend accessing URL parameters with `get` or by catching the
:exc:`KeyError` because users might change the URL and presenting them a 400
bad request page in that case is not user friendly.

For a full list of methods and attributes of the request object, head over
to the :class:`~flask.Request` documentation.


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
    from werkzeug.utils import secure_filename

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

Note that cookies are set on response objects.  Since you normally
just return strings from the view functions Flask will convert them into
response objects for you.  If you explicitly want to do that you can use
the :meth:`~flask.make_response` function and then modify it.

Sometimes you might want to set a cookie at a point where the response
object does not exist yet.  This is possible by utilizing the
:ref:`deferred-callbacks` pattern.

For this also see :ref:`about-responses`.

Redirects and Errors
--------------------

To redirect a user to another endpoint, use the :func:`~flask.redirect`
function; to abort a request early with an error code, use the
:func:`~flask.abort` function::

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

See :ref:`error-handlers` for more details.

.. _about-responses:

About Responses
---------------

The return value from a view function is automatically converted into a
response object for you.  If the return value is a string it's converted
into a response object with the string as response body, a ``200 OK``
status code and a :mimetype:`text/html` mimetype.  The logic that Flask applies to
converting return values into response objects is as follows:

1.  If a response object of the correct type is returned it's directly
    returned from the view.
2.  If it's a string, a response object is created with that data and the
    default parameters.
3.  If a tuple is returned the items in the tuple can provide extra
    information.  Such tuples have to be in the form ``(response, status,
    headers)`` or ``(response, headers)`` where at least one item has
    to be in the tuple.  The ``status`` value will override the status code
    and ``headers`` can be a list or dictionary of additional header values.
4.  If none of that works, Flask will assume the return value is a
    valid WSGI application and convert that into a response object.

If you want to get hold of the resulting response object inside the view
you can use the :func:`~flask.make_response` function.

Imagine you have a view like this::

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html'), 404

You just need to wrap the return expression with
:func:`~flask.make_response` and get the response object to modify it, then
return it::

    @app.errorhandler(404)
    def not_found(error):
        resp = make_response(render_template('error.html'), 404)
        resp.headers['X-Something'] = 'A value'
        return resp

.. _sessions:

Sessions
--------

In addition to the request object there is also a second object called
:class:`~flask.session` which allows you to store information specific to a
user from one request to the next.  This is implemented on top of cookies
for you and signs the cookies cryptographically.  What this means is that
the user could look at the contents of your cookie but not modify it,
unless they know the secret key used for signing.

In order to use sessions you have to set a secret key.  Here is how
sessions work::

    from flask import Flask, session, redirect, url_for, escape, request

    app = Flask(__name__)

    # Set the secret key to some random bytes. Keep this really secret!
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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

The :func:`~flask.escape` mentioned here does escaping for you if you are
not using the template engine (as in this example).

.. admonition:: How to generate good secret keys

    A secret key should be as random as possible. Your operating system has
    ways to generate pretty random data based on a cryptographic random
    generator. Use the following command to quickly generate a value for
    :attr:`Flask.secret_key` (or :data:`SECRET_KEY`)::

        $ python -c 'import os; print(os.urandom(16))'
        b'_5#y2L"F4Q8z\n\xec]/'

A note on cookie-based sessions: Flask will take the values you put into the
session object and serialize them into a cookie.  If you are finding some
values do not persist across requests, cookies are indeed enabled, and you are
not getting a clear error message, check the size of the cookie in your page
responses compared to the size supported by web browsers.

Besides the default client-side based sessions, if you want to handle
sessions on the server-side instead, there are several
Flask extensions that support this.

Message Flashing
----------------

Good applications and user interfaces are all about feedback.  If the user
does not get enough feedback they will probably end up hating the
application.  Flask provides a really simple way to give feedback to a
user with the flashing system.  The flashing system basically makes it
possible to record a message at the end of a request and access it on the next
(and only the next) request.  This is usually combined with a layout
template to expose the message.

To flash a message use the :func:`~flask.flash` method, to get hold of the
messages you can use :func:`~flask.get_flashed_messages` which is also
available in the templates.  Check out the :ref:`message-flashing-pattern`
for a full example.

Logging
-------

.. versionadded:: 0.3

Sometimes you might be in a situation where you deal with data that
should be correct, but actually is not.  For example you may have some client-side
code that sends an HTTP request to the server but it's obviously
malformed.  This might be caused by a user tampering with the data, or the
client code failing.  Most of the time it's okay to reply with ``400 Bad
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
documentation <https://docs.python.org/library/logging.html>`_ for more
information.

Read more on :ref:`application-errors`.

Hooking in WSGI Middlewares
---------------------------

If you want to add a WSGI middleware to your application you can wrap the
internal WSGI application.  For example if you want to use one of the
middlewares from the Werkzeug package to work around bugs in lighttpd, you
can do it like this::

    from werkzeug.contrib.fixers import LighttpdCGIRootFix
    app.wsgi_app = LighttpdCGIRootFix(app.wsgi_app)

Using Flask Extensions
----------------------

Extensions are packages that help you accomplish common tasks. For
example, Flask-SQLAlchemy provides SQLAlchemy support that makes it simple
and easy to use with Flask.

For more on Flask extensions, have a look at :ref:`extensions`.

Deploying to a Web Server
-------------------------

Ready to deploy your new Flask app? Go to :ref:`deployment`.
