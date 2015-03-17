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


路由系统
--------

Flask 使用 Werkzeug 路由系统，该系统是自动根据复杂度来为路由排序的。也就是
说你可以以任意顺序来声明路由，路由系统仍然能够正常工作。为什么要实现这个
功能？因为当应用被切分成多个模块时，基于路由的装饰器会以乱序触发，所以这个
功能是必须的。

另一点是 Werkzeug 路由系统必须确保 URL 是唯一的，并且会把模糊路由重定向到
标准的 URL 。


唯一模板引擎
------------

Flask 原生只使用 Jinja2 模板引擎。为什么不设计一个可插拔的模板引擎接口？
当然，你可以在 Flask 中使用其他模板引擎，但是当前 Flask 原生只会支持
Jinja2 。将来也许 Flask 会使用其他引擎，但是永远只会绑定一个模板引擎。

模板引擎与编程语言类似，每个引擎都有自己的一套工作方式。表面上它们都看
上去差不多：你把一套变量丢给引擎，然后得到字符串形式的模板。

但是相似之处也仅限于此。例如 Jinja2 有丰富的过滤系统、有一定的模板继承
能力、支持从模板内或者 Python 代码内复用块（宏）、所有操作都使用
Unicode 、支持迭代模板渲染以及可配置语法等等。而比如 Genshi 基于 XML 流
赋值，其模板继承基于 XPath 的能力。再如 Mako 使用类似 Python 模块的方式
来处理模板。

当一个应用或者框架与一个模板引擎结合在一起的时候，事情就不只是渲染模板
这么简单了。例如， Flask 使用了 Jinja2 的强大的自动转义功能。同时 Flask
也为 Jinja2 提供了在模板中操作宏的途径。

一个不失模板引擎独特性的模板抽象层本身就是一门学问，因此这不是一个 Flask
之类的微框架应该考虑的事情。

此外，只使用一个模板语言可以方便扩展。你可以使用你自己的模板语言，但扩展
仍然使用 Jinja 。


我依赖所以我微
--------------

为什么 Flask 依赖两个库（ Werkzeug 和 Jinja2 ），但还是自称是微框架？
为什么不可以呢？如果我们看一看 Web 开发的另一大阵营 Ruby ，那么可以发现
一个与 WSGI 十分相似的协议。这个协议被称为 Rack ，除了名称不同外，基本
可以视作 Ruby 版的 WSGI 。但是几乎所有 Ruby 应用都不直接使用 Rack 协议，
而是使用一个相同名字的库。在 Python 中，与 Rack 库等价的有 WebOb
（前身是 Paste ）和 Werkzeug 两个库。 Paste 任然可用，但是个人认为正逐步
被 WebOb 取代。WebOb 和 Werkzeug 的开发初衷都是：做一个 WSGI 协议的出色
实现，让其他应用受益。

正应为 Werkzeug 出色地实现了 WSGI 协议（有时候这是一个复杂的任务），使得
依赖于 Werkzeug 的 Flask 受益良多。同时要感谢 Python 包管理的近期开发，
包依赖问题已经解决，几乎没有理由不使用包依赖的方式。


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
