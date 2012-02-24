前言
====

在使用 Flask 前请阅读本文。本文有助于理解 Flask 的用途和目的，以便于决策是否
应当使用 Flask 。

“微”是什么意思？
-----------------------

对我来说，微框架中的“微”字不仅仅代表框架本身的简单和轻量，同时还意味着较高的
自由度。 Flask 替你选定了一个模板引擎，但是不会替你选定数据储存的方式或者其他
东西。

同时“微”字不代表整个框架只能塞在一个 Python 文件内。

Flask 的设计思路之一是简单的任务应当保持简单并且不会占用很多代码，同时还不能
限制住自己。因此有些人可能会对我们的一些设计选择感到惊讶或不正统。例如， Flask
内部使用了本地线程对象，因此用不着为了线程安全的原因而在一个请求之内把对象在
函数之间来回传递。虽然这个设计选择很容易实现，并且可以节省大量时间，但是在非常
大的项目中会出现问题。因为这些本地线程对象会在同一线程中的任何地方发生变化。
为了解决这个问题，我们不是把本地线程隐藏起来，而是接受它们，并且提供请多工具以
便于你更好的使用它们。

Flask 是按惯例配置的，这意味着很多事情是预先设定的。例如，按照惯例，模板和静态
文件是放在应用的 Python 源代码树的子目录内的。虽然这是可以改变的，但通常没有
必要。

The main reason however why Flask is called a "microframework" is the idea
to keep the core simple but extensible.  There is no database abstraction
layer, no form validation or anything else where different libraries
already exist that can handle that.  However Flask knows the concept of
extensions that can add this functionality into your application as if it
was implemented in Flask itself.  There are currently extensions for
object relational mappers, form validation, upload handling, various open
authentication technologies and more.

Since Flask is based on a very solid foundation there is not a lot of code
in Flask itself.  As such it's easy to adapt even for lage applications
and we are making sure that you can either configure it as much as
possible by subclassing things or by forking the entire codebase.  If you
are interested in that, check out the :ref:`becomingbig` chapter.

If you are curious about the Flask design principles, head over to the
section about :ref:`design`.

Web Development is Dangerous
----------------------------

I'm not joking.  Well, maybe a little.  If you write a web
application, you are probably allowing users to register and leave their
data on your server.  The users are entrusting you with data.  And even if
you are the only user that might leave data in your application, you still
want that data to be stored securely.

Unfortunately, there are many ways the security of a web application can be
compromised.  Flask protects you against one of the most common security
problems of modern web applications: cross-site scripting (XSS).  Unless
you deliberately mark insecure HTML as secure, Flask and the underlying
Jinja2 template engine have you covered.  But there are many more ways to
cause security problems.

The documentation will warn you about aspects of web development that
require attention to security.  Some of these security concerns
are far more complex than one might think, and we all sometimes underestimate
the likelihood that a vulnerability will be exploited, until a clever
attacker figures out a way to exploit our applications.  And don't think
that your application is not important enough to attract an attacker.
Depending on the kind of attack, chances are that automated bots are
probing for ways to fill your database with spam, links to malicious
software, and the like.

So always keep security in mind when doing web development.

The Status of Python 3
----------------------

Currently the Python community is in the process of improving libraries to
support the new iteration of the Python programming language.  While the
situation is greatly improving there are still some issues that make it
hard for us to switch over to Python 3 just now.  These problems are
partially caused by changes in the language that went unreviewed for too
long, partially also because we have not quite worked out how the lower
level API should change for the unicode differences in Python3.

Werkzeug and Flask will be ported to Python 3 as soon as a solution for
the changes is found, and we will provide helpful tips how to upgrade
existing applications to Python 3.  Until then, we strongly recommend
using Python 2.6 and 2.7 with activated Python 3 warnings during
development.  If you plan on upgrading to Python 3 in the near future we
strongly recommend that you read `How to write forwards compatible
Python code <http://lucumr.pocoo.org/2011/1/22/forwards-compatible-python/>`_.
