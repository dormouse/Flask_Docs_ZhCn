调试应用程序错误
============================


在生产环境中
-------------

**在生产环境中，不要运行开发服务器，或启用内置调试器。** 调试器允许执行
来自浏览器的任意 Python 代码。 它由一个 pin 保护，但是在安全方面这是不
可依赖的。

使用错误记录工具，比如 :ref:`error-logging-tools` 中提到的 Sentry ，
或者如 :doc:`/logging` 中提到的，开启日志记录和通知。

如果您有权访问服务器， ``request.remote_addr`` 匹配您的 IP, 则可以添加
一些代码来启动外部调试器。一些 IDE 调试器还具有远程模式，因此可以在服务
器上设置断点与本地互动。 只能临时启用调试器。 



内置调试器
---------------------

内置的 Werkzeug 开发服务器提供一个调试器，当请求中出现无法处置的错误时
会显示一个交互回溯。这个调试器应当仅在开发时使用。

.. image:: _static/debugger.png
   :align: center
   :class: screenshot
   :alt: screenshot of debugger in action

.. warning::

    调试器允许执行来自浏览器的任意 Python 代码。虽然它由一个 pin 保护，
    但仍然存在巨大安全风险。不要在生产环境中运行开发服务器或调试器。

把 ``FLASK_ENV`` 环境变更设置为 ``development`` ，运行开发服务器，即可
开启调试器。这样， Flask 就处于调试模式下，一些错误处理的方式会被改变，
并且调试器和重载器会开启。

.. tabs::

   .. group-tab:: Bash

      .. code-block:: text

         $ export FLASK_ENV=development
         $ flask run

   .. group-tab:: Fish

      .. code-block:: text

         $ set -x FLASK_ENV development
         $ flask run

   .. group-tab:: CMD

      .. code-block:: text

         > set FLASK_ENV=development
         > flask run

   .. group-tab:: Powershell

      .. code-block:: text

         > $env:FLASK_ENV = "development"
         > flask run

``FLASK_ENV`` 只能被设置为环境变量。当以 Python 代码方式运行时，可以
通过传递 ``debug=True`` 来开启调试模式，这是与前述方式基本等价的。调试
模式可以由 ``FLASK_ENV`` 和 ``FLASK_DEBUG`` 环境变量分别控制。

.. code-block:: python

    app.run(debug=True)

:doc:`/server` 和 :doc:`/cli` 有更多关于运行调试器、调试模式和开发模式
的内容。更多关于调试器的信息参见
`Werkzeug 文档 <https://werkzeug.palletsprojects.com/debug/>`__ 。


外部调试器
------------------

外部调试器，例如 IDE 提供的调试器，可以提供比内置调试器更强大的调试体验。
他们还可以用于在出错之前的请求期间进行单步代码调试。有些甚至具有远程
模式，可以调试在另一台机器上运行的代码。

当使用外部调试器时，应用程序应仍处于调试模式。如果产生干扰，那么可以
禁用内置调试器和重新加载器。

从命令行运行： 

.. tabs::

   .. group-tab:: Bash

      .. code-block:: text

         $ export FLASK_ENV=development
         $ flask run --no-debugger --no-reload

   .. group-tab:: Fish

      .. code-block:: text

         $ set -x FLASK_ENV development
         $ flask run --no-debugger --no-reload

   .. group-tab:: CMD

      .. code-block:: text

         > set FLASK_ENV=development
         > flask run --no-debugger --no-reload

   .. group-tab:: Powershell

      .. code-block:: text

         > $env:FLASK_ENV = "development"
         > flask run --no-debugger --no-reload

从 Python 运行：

.. code-block:: python

    app.run(debug=True, use_debugger=False, use_reloader=False)

禁用调试器和重载器不是必须的，但是如果不禁用的话，要注意以下问题。
如果内置调试器没有禁用，那么它会早于外部调试器捕获未处理的异常。如果
重载器没有禁用，那么在调试期间代码发生改变时会导致意外重新加载。 
