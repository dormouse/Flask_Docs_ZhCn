.. _server:

开发服务器
==================

.. currentmodule:: flask

自 Flask 0.11 开始有多种内建方法可以运行开发服务器。最好的方法是使用
:command:`flask` 命令行工具。当然，继续使用 :meth:`Flask.run` 亦可。


通过命令行使用开发服务器
------------------------

强烈推荐开发时使用 :command:`flask` 命令行脚本（ :ref:`cli` ），因为有强大
的重载功能，提供了超好的重载体验。基本用法如下::

    $ export FLASK_APP=my_application
    $ export FLASK_ENV=development
    $ flask run

这样做开始了开发环境（包括交互调试器和重载器），并在
*http://localhost:5000/* 提供服务。

通过使用不同 ``run`` 参数可以控制服务器的单独功能。例如禁用重载器::

    $ flask run --no-reload

.. note::

    在 Flask 1.0 版之前， :envvar:`FLASK_ENV` 环境不可用。开启调试模式
    需要使用 ``FLASK_DEBUG=1`` 。这样做还是有用的，但是建议如前文所述
    使用设置开发环境变量来实现。

通过代码使用开发服务器
------------------------

另一种方法是通过 :meth:`Flask.run` 方法启动应用，这样立即运行一个本地服务
器，与使用 :command:`flask` 脚本效果相同。

示例::

    if __name__ == '__main__':
        app.run()

通常情况下这样做不错，但是对于开发就不行了。正是基于这个原因自 Flask 0.11
版开始推荐使用 :command:`flask` 方法。这是因为重载的工作机制有一些奇怪的副
作用（如执行某些代码两次，有时会在没有消息的情况下崩溃，或者在某个语法或导
入错误发生时宕机）。

然而，它仍然是一个调用非自动重装应用程序的非常有效的方法。
