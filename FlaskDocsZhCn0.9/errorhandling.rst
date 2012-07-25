.. _application-errors:

掌握应用错误
===========================

.. versionadded:: 0.3

应用出错，服务器出错。或早或晚，你会遇到产品出错。即使你的代码是百分百正确，
还是会时常看见出错。为什么？因为其他相关东西会出错。以下是一些在代码完全正确的
条件下服务器出错的情况：

-   客户端已经中断了请求，但应用还在读取数据。
-   数据库已经过载，无法处理查询。
-   文件系统没有空间。
-   硬盘完蛋了。
-   后台服务过载。
-   使用的库出现程序错误。
-   服务器与另一个系统的网络连接出错。

以上只是你会遇到的问题的一小部分。那么如果处理这些问题呢？如果你的应用运行在
生产环境下，那么缺省情况下 Flask 会显示一个简单的出错页面，并把出错情况记录到
:attr:`~flask.Flask.logger` 。

但要做得还不只这些，下面介绍一些更好的出错处理方法。


报错邮件
------------

如果应用在生产环境（在你的服务器中一般使用生产环境）下运行，那么缺省情况下不会
看到任何日志信息。为什么？因为 Flask 是一个零配置的框架。既然没有配置，那么日志
放在哪里呢？显然， Flask 不能来随便找一个地放给用户存放日志，因为如果用户在这个
位置没有创建文件的权限就糟了。同时，对于大多数小应用来说，没人会去看日志。

事实上，我现在可以负责任地说除非调试一个用户向你报告的错误，你是不会去看应用的
日志文件的。你真下需要的是出错的时候马上给你发封电子邮件，及时提醒你，以便于
进行处理。

Flask 使用 Python 内置的日志系统，它可以发送你需要的错误报告电子邮件。以下是
如何配置 Flask 日志记录器发送错误报告电子邮件的例子::

    ADMINS = ['yourname@example.com']
    if not app.debug:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler('127.0.0.1',
                                   'server-error@example.com',
                                   ADMINS, 'YourApplication Failed')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

这个例子是什么意思？我们创建了一个新的 :class:`~logging.handlers.SMTPHandler`
类。这个类会使用邮件服务器 ``127.0.0.1`` 向 *server-error@example.com* 的
`ADMINS` 发送主题为 "YourApplication Failed" 的 电子邮件。如果你的邮件服务器
需要认证，这是可行的，详见 :class:`~logging.handlers.SMTPHandler` 的文档。

我们还定义了只报送错误及错误以上级别的信息。因为我们不想得到警告或其他没用的
日志，比如请求处理日志。

在你的产品中使用它们前，请查看一下 :ref:`logformat` ，以了解错误报告邮件的更多
信息，磨刀不误砍柴功。


日志文件
-----------------

报错邮件有了，可能还需要记录警告信息。这是一个好习惯，有利于除错。请注意，在
核心系统中 Flask 本身不会发出任何警告。因此，在有问题时发出警告只能自力更生了。

虽然有许多日志记录系统，但不是每个系统都能做好基本日志记录的。以下可能是最值得
关注的：

-   :class:`~logging.FileHandler` - 把日志信息记录到文件系统中的一个文件。
-   :class:`~logging.handlers.RotatingFileHandler` - 把日志信息记录到文件系统中
    的一个文件，当信息达到一定数量后反转。
-   :class:`~logging.handlers.NTEventLogHandler` - 把日志信息记录到 Windows 的
    事件日志中。如果你的应用部署在 Windows 下，就用这个吧。
-   :class:`~logging.handlers.SysLogHandler` - 把日志记录到一个 UNIX 系统日志。

一旦你选定了日志记录器之后，使用方法类似上一节所讲的 SMTP 处理器，只是记录的
级别应当低一点（我推荐 `WARNING` 级别）::

    if not app.debug:
        import logging
        from themodule import TheHandlerYouWant
        file_handler = TheHandlerYouWant(...)
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

.. _logformat:

控制日志格式
--------------------------

缺省情况下一个处理器只会把信息字符串写入一个文件或把信息作为电子邮件发送给你。
但是一个日志应当记录更多的信息，因些应该认真地配置日志记录器。一个好的日志不光
记录为什么会出错，更重要的是记录错在哪里。

格式化器使用一个格式化字符串作为实例化时的构造参数，这个字符串中的格式变量会在
日志记录时自动转化。

举例:

电子邮件
````````

::

    from logging import Formatter
    mail_handler.setFormatter(Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    '''))

日志文件
````````````

::

    from logging import Formatter
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))


复杂日志格式
``````````````````````

以下是格式化字符串中一种重要的格式变量。注意，这并不包括全部格式变量，更多变更
参见 :mod:`logging` 包的官方文档。

.. tabularcolumns:: |p{3cm}|p{12cm}|

+------------------+----------------------------------------------------+
| 格式变量         | 说明                                               |
+==================+====================================================+
| ``%(levelname)s``| 文字形式的日志等级                                 |
|                  | （ ``'DEBUG'`` 、 ``'INFO'`` 、 ``'WARNING'`` 、   |
|                  | ``'ERROR'`` 和 ``'CRITICAL'`` ）。                 |
+------------------+----------------------------------------------------+
| ``%(pathname)s`` | 调用日志的源文件的完整路径（如果可用）。           |
+------------------+----------------------------------------------------+
| ``%(filename)s`` | 调用日志的源文件文件名。                           |
+------------------+----------------------------------------------------+
| ``%(module)s``   | 调用日志的模块名。                                 |
+------------------+----------------------------------------------------+
| ``%(funcName)s`` | 调用日志的函数名。                                 |
+------------------+----------------------------------------------------+
| ``%(lineno)d``   | 调用日志的代码的行号（如果可用）。                 |
+------------------+----------------------------------------------------+
| ``%(asctime)s``  | 调用日志的时间，缺省格式为                         |
|                  | ``"2003-07-08 16:49:45,896"`` （逗号后面的数字为   |
|                  | 毫秒）。通过重载                                   |
|                  | :meth:`~logging.Formatter.formatTime` 方法可以改变 |
|                  | 格式。                                             |
+------------------+----------------------------------------------------+
| ``%(message)s``  | 日志记录的消息，同 ``msg % args`` 。               |
+------------------+----------------------------------------------------+

如果要进一步定制格式，可以使用格式化器的子类。格式化器有三个有趣的方法：

:meth:`~logging.Formatter.format`:
    处理实际的格式化。它接收一个 :class:`~logging.LogRecord` 对象，返回格式化后
    的字符串。
:meth:`~logging.Formatter.formatTime`:
    它用于 `asctime` 格式变量。重载它可以改变时间格式。
:meth:`~logging.Formatter.formatException`
    它用于异常格式化。接收一个 :attr:`~sys.exc_info` 元组并且必须返回一个
    字符串。缺省情况下它够用了，不必重载。

更多信息参见官方文档。


其他库
---------------

至此，我们只配置了应用本身的日志记录器。其他库可能同样需要记录日志。例如，
SQLAlchemy 在其核心中大量使用日志。在 :mod:`logging` 包中有一个方法可以一次性
地配置所有日志记录器，但我不推荐这么做。因为当你在同一个 Python 解释器中同时
运行两个独立的应用时就无法使用不同的日志设置了。

相反，我建议使用 :func:`~logging.getLogger` 函数来鉴别是哪个日志记录器，并获取
相应的处理器::

    from logging import getLogger
    loggers = [app.logger, getLogger('sqlalchemy'),
               getLogger('otherlibrary')]
    for logger in loggers:
        logger.addHandler(mail_handler)
        logger.addHandler(file_handler)


排除应用错误
============================

:ref:`application-errors` 一文所讲的是如何为生产应用设置日志和出错通知。本文要
讲的是部署中配置调试的要点和如何使用全功能的 Python 调试器深挖错误。


有疑问时，请手动运行
---------------------------

在生产环境中，配置应用时出错？如果你可以通过 shell 来访问主机，那么请首先在部署
环境中验证是否可以通过 shell 手动运行你的应用。请确保验证时使用的帐户与配置的
相同，这样可以排除用户权限引发的错误。你可以在你的生产服务器上，使用 Flask 内建
的开发服务器，并且设置 `debug=True` ，这样有助于找到配置问题。但是，请
**只能在可控的情况下临时这样做** ，绝不能在生产时使用 `debug=True` 。

.. _working-with-debuggers:

使用调试器
----------------------

为了更深入的挖掘错误，追踪代码的执行， Flask 提供一个开箱即用的调试器（参见
:ref:`debug-mode` ）。如果你需要使用其他 Python 调试器，请注意调试器之间的干扰
问题。在使用你自己的调试器前要做一些参数调整：

* ``debug``        - 是否开启调试模式并捕捉异常
* ``use_debugger`` - 是否使用 Flask 内建的调试器
* ``use_reloader`` - 出现异常后是否重载或者派生进程

``debug`` 必须设置为 True （即必须捕获异常），另两个随便。

如果你正在使用 Aptana 或 Eclipse 排错，那么 ``use_debugger`` 和
``use_reloader`` 都必须设置为 False 。

一个有用的配置模式如下（当然要根据你的应用调整缩进）::

   FLASK:
       DEBUG: True
       DEBUG_WITH_APTANA: True

然后，在应用入口（ main.py ），修改如下::

   if __name__ == "__main__":
       # 为了让 aptana 可以接收到错误，设置 use_debugger=False
       app = create_app(config="config.yaml")

       if app.debug: use_debugger = True
       try:
           # 如果使用其他调试器，应当关闭 Flask 的调试器。
           use_debugger = not(app.config.get('DEBUG_WITH_APTANA'))
       except:
           pass
       app.run(use_debugger=use_debugger, debug=app.debug,
               use_reloader=use_debugger, host='0.0.0.0')

