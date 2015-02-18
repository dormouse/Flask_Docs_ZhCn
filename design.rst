.. _design:

Flask 的设计思路
================

为什么 Flask 要这样做，而不是那样做？如果你对这点好奇，那么本节可以满足
你的好奇心。当与其他框架直接进行比较时， Flask 的设计思路乍看可能显得武断
并且令人吃惊，下面我们就来看看为什么在设计的时候进行这样决策。


显式的应用对象
--------------

一个基于 WSGI 的 Python web 应用必须有一个实现实际的应用的中心调用对象。
在 Flask 中，中心调用对象是一个 :class:`~flask.Flask` 类的实例。每个 Flask
应用必须创建一个该类的实例，并且把模块的名称传递给该实例。但是为什么 Flask
不自动把这些事都做好呢？

下面的代码::

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'Hello World!'

如果没有一个显式的应用对象，那么会是这样的::

    from hypothetical_flask import route

    @route('/')
    def index():
        return 'Hello World!'

使用对象的主要有三个原因。最重要的一个原因是显式对象可以保证实例的唯一性。
有很多方法可以用单个应用对象来冒充多应用，比如维护一个应用堆栈，但是这样
将会导致一些问题，这里我就不展开了。现在的问题是：一个微框架何时会需要
多应用？最好的回答是当进行单元测试的时候。在进行测试时，创建一个最小应用
用于测试特定的功能，是非常有用的。当这个最小应用的应用对象被删除时，将会
释放其占用的所有资源。

另外当使用显式对象时，你可以继承基类（ :class:`~flask.Flask` ），
以便于修改特定的功能。如果不使用显式对象，那么就无从下手了。

第二个原因也很重要，那就是 Flask 需要包的名称。当你创建一个 Flask 实例时，
通常会传递 `__name__` 作为包的名称。 Flask 根据包的名称来载入也模块相关
的正确资源。通过 Python 杰出的反射功能，就可以找到模板和静态文件（参见
:meth:`~flask.Flask.open_resource` ）。很显然，有其他的框架不需要任何配置
就可以载入与模块相关的模板。但其前提是必须使用当前工作目录，这是一个不可靠
的实现方式。当前工作目录是进程级的，如果有多个应用使用同一个进程（ web
服务器可能在你不知情的情况下这样做），那么当前工作目录就不可用了。还有更
糟糕的情况：许多 web 服务器把文档根目录作为当前工作目录，如果你的应用所在
的目录不是文档根目录，那么就会出错。

第三个原因是“显式比隐式更好”。这个对象就是你的 WSGI 应用，你不必再记住其他
东西。如果你要实现一个 WSGI 中间件，那么只要封装它就可以了（还有更好的
方式，可以不丢失应用对象的引用，参见： :meth:`~flask.Flask.wsgi_app` ）。

再者，只有这样设计才能使用工厂函数来创建应用，方便单元测试和类似的工作
（参见： :ref:`app-factories` ）。

The Routing System
------------------

Flask uses the Werkzeug routing system which was designed to
automatically order routes by complexity.  This means that you can declare
routes in arbitrary order and they will still work as expected.  This is a
requirement if you want to properly implement decorator based routing
since decorators could be fired in undefined order when the application is
split into multiple modules.

Another design decision with the Werkzeug routing system is that routes
in Werkzeug try to ensure that URLs are unique.  Werkzeug will go quite far
with that in that it will automatically redirect to a canonical URL if a route
is ambiguous.


One Template Engine
-------------------

Flask decides on one template engine: Jinja2.  Why doesn't Flask have a
pluggable template engine interface?  You can obviously use a different
template engine, but Flask will still configure Jinja2 for you.  While
that limitation that Jinja2 is *always* configured will probably go away,
the decision to bundle one template engine and use that will not.

Template engines are like programming languages and each of those engines
has a certain understanding about how things work.  On the surface they
all work the same: you tell the engine to evaluate a template with a set
of variables and take the return value as string.

But that's about where similarities end.  Jinja2 for example has an
extensive filter system, a certain way to do template inheritance, support
for reusable blocks (macros) that can be used from inside templates and
also from Python code, uses Unicode for all operations, supports
iterative template rendering, configurable syntax and more.  On the other
hand an engine like Genshi is based on XML stream evaluation, template
inheritance by taking the availability of XPath into account and more.
Mako on the other hand treats templates similar to Python modules.

When it comes to connecting a template engine with an application or
framework there is more than just rendering templates.  For instance,
Flask uses Jinja2's extensive autoescaping support.  Also it provides
ways to access macros from Jinja2 templates.

A template abstraction layer that would not take the unique features of
the template engines away is a science on its own and a too large
undertaking for a microframework like Flask.

Furthermore extensions can then easily depend on one template language
being present.  You can easily use your own templating language, but an
extension could still depend on Jinja itself.


Micro with Dependencies
-----------------------

Why does Flask call itself a microframework and yet it depends on two
libraries (namely Werkzeug and Jinja2).  Why shouldn't it?  If we look
over to the Ruby side of web development there we have a protocol very
similar to WSGI.  Just that it's called Rack there, but besides that it
looks very much like a WSGI rendition for Ruby.  But nearly all
applications in Ruby land do not work with Rack directly, but on top of a
library with the same name.  This Rack library has two equivalents in
Python: WebOb (formerly Paste) and Werkzeug.  Paste is still around but
from my understanding it's sort of deprecated in favour of WebOb.  The
development of WebOb and Werkzeug started side by side with similar ideas
in mind: be a good implementation of WSGI for other applications to take
advantage.

Flask is a framework that takes advantage of the work already done by
Werkzeug to properly interface WSGI (which can be a complex task at
times).  Thanks to recent developments in the Python package
infrastructure, packages with dependencies are no longer an issue and
there are very few reasons against having libraries that depend on others.


Thread Locals
-------------

Flask uses thread local objects (context local objects in fact, they
support greenlet contexts as well) for request, session and an extra
object you can put your own things on (:data:`~flask.g`).  Why is that and
isn't that a bad idea?

Yes it is usually not such a bright idea to use thread locals.  They cause
troubles for servers that are not based on the concept of threads and make
large applications harder to maintain.  However Flask is just not designed
for large applications or asynchronous servers.  Flask wants to make it
quick and easy to write a traditional web application.

Also see the :ref:`becomingbig` section of the documentation for some
inspiration for larger applications based on Flask.


What Flask is, What Flask is Not
--------------------------------

Flask will never have a database layer.  It will not have a form library
or anything else in that direction.  Flask itself just bridges to Werkzeug
to implement a proper WSGI application and to Jinja2 to handle templating.
It also binds to a few common standard library packages such as logging.
Everything else is up for extensions.

Why is this the case?  Because people have different preferences and
requirements and Flask could not meet those if it would force any of this
into the core.  The majority of web applications will need a template
engine in some sort.  However not every application needs a SQL database.

The idea of Flask is to build a good foundation for all applications.
Everything else is up to you or extensions.
