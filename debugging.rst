调试应用程序错误
============================


在生产环境中
-------------

**在生产环境中，不要运行开发服务器，或启用内置调试器。** 调试器允许执
行来自浏览器的任意 Python 代码。 它由一个 pin 保护，但是在安全方面这
是不可依赖的。

使用错误记录工具，比如 :ref:`error-logging-tools` 中提到的 Sentry ，
或者如 :doc:`/logging` 中提到的，开启日志记录和通知。

如果您有权访问服务器， ``request.remote_addr`` 匹配您的 IP, 则可以添
加一些代码来启动外部调试器。一些 IDE 调试器还具有远程模式，因此可以在
服务器上设置断点与本地互动。 只能临时启用调试器。 



内置调试器
---------------------

内置的 Werkzeug 开发服务器提供一个调试器，当请求中出现无法处置的错误
时会显示一个交互回溯。这个调试器应当仅在开发时使用。

.. image:: _static/debugger.png
   :align: center
   :class: screenshot
   :alt: screenshot of debugger in action

.. warning::

    调试器允许执行来自浏览器的任意 Python 代码。虽然它由一个 pin 保护，
    但仍然存在巨大安全风险。不要在生产环境中运行开发服务器或调试器。

当开发服务器在调试模式下运行时调试器默认是开启的。


.. code-block:: text
 
    $ flask --app hello run --debug
 

当以 Python 代码方式运行时，可以通过传递 ``debug=True`` 来开启调试模
式，这是与前述方式基本等价的。

.. code-block:: python

    app.run(debug=True)

:doc:`/server` 和 :doc:`/cli` 有更多关于运行调试器、调试模式和开发模
式的内容。更多关于调试器的信息参见
`Werkzeug 文档 <https://werkzeug.palletsprojects.com/debug/>`__ 。


外部调试器
------------------

外部调试器，例如 IDE 提供的调试器，可以提供比内置调试器更强大的调试体
验。他们还可以用于在出错之前的请求期间进行单步代码调试。有些甚至具有
远程模式，可以调试在另一台机器上运行的代码。

当使用外部调试器时，应用程序应仍处于调试模式。如果产生干扰，那么可以
禁用内置调试器和重新加载器。

.. code-block:: text
 
    $ flask --app hello run --debug --no-debugger --no-reload

从 Python 运行：

.. code-block:: python

    app.run(debug=True, use_debugger=False, use_reloader=False)

禁用调试器和重载器不是必须的，但是如果不禁用的话，要注意以下问题。
如果内置调试器没有禁用，那么它会早于外部调试器捕获未处理的异常。如果
重载器没有禁用，那么在调试期间代码发生改变时会导致意外重新加载。 
