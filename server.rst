.. currentmodule:: flask

开发服务器
==================

Flask 提供了一个 ``run`` 命令，该命令用来以开发服务器运行应用。
在开发模式下，开发服务器提供交互式调试器，并在代码更改时重新加载。

.. warning::

    生产环境不要使用开发服务器。开发服务器仅供在本地开发期间使用，它在
    效率、稳定或安全方面是缺失的。

    有关部署选项，请参阅 :doc:`/deploying/index` 。 


通过命令行使用开发服务器
------------------------

推荐使用 ``flask run`` 命令行脚本运行开发服务器。这需要设置
``FLASK_APP`` 环境变量指向您的应用，且设置 ``FLASK_ENV=development`` ，
以用于启用开发模式。

.. tabs::

   .. group-tab:: Bash

      .. code-block:: text

         $ export FLASK_APP=hello
         $ export FLASK_ENV=development
         $ flask run

   .. group-tab:: Fish

      .. code-block:: text

         $ set -x FLASK_APP hello
         $ export FLASK_ENV=development
         $ flask run

   .. group-tab:: CMD

      .. code-block:: text

         > set FLASK_APP=hello
         > set FLASK_ENV=development
         > flask run

   .. group-tab:: Powershell

      .. code-block:: text

         > $env:FLASK_APP = "hello"
         > $env:FLASK_ENV = "development"
         > flask run

这样就启动了开发环境，包括交互调试器和重载器，并在
http://localhost:5000/ 提供服务。使用 ``flask run --help`` 命令可以查看
可用的选项， :doc:`/cli` 提供了关于配置和使用 CLI 的详细介绍。

.. note::

    Flask 1.0 版之前， ``FLASK_ENV`` 环境变量是不可用的，您需要导出
    ``FLASK_DEBUG=1`` 来开启调试模式。这样做仍能控制调试模式的开关，
    但是推荐使用前述的方法。


.. _address-already-in-use:

地址已被占用
~~~~~~~~~~~~~~~~~~~~~~

如果其他程序已经占用了 5000 端口，那么当服务器启动时会看到一个类似以
下的 ``OSError`` 信息：

-   ``OSError: [Errno 98] Address already in use``
-   ``OSError: [WinError 10013] An attempt was made to access a socket
    in a way forbidden by its access permissions``

解决这个问题有两个方法：要么找到并停止使用这个端口的其他程序，要么使用
``flask run --port 5001`` 来修改您自己的端口。

您可以使用 ``netstat`` 或者 ``lsof`` 来找到占用端口的进程，并使用系统
工具来停止该进程。下面的例子展示进程 id 6847 占用了 5000 端口。

.. tabs::

    .. tab:: ``netstat`` (Linux)

        .. code-block:: text

            $ netstat -nlp | grep 5000
            tcp 0 0 127.0.0.1:5000 0.0.0.0:* LISTEN 6847/python

    .. tab:: ``lsof`` (macOS / Linux)

        .. code-block:: text

            $ lsof -P -i :5000
            Python 6847 IPv4 TCP localhost:5000 (LISTEN)

    .. tab:: ``netstat`` (Windows)

        .. code-block:: text

            > netstat -ano | findstr 5000
            TCP 127.0.0.1:5000 0.0.0.0:0 LISTENING 6847

macOS Monterey 及更新的版本会自动启动一个占用 5000 端口的服务。要停用
这个服务的话，请进入系统设置、通用，然后停用“接力”。 


延迟加载或热加载
~~~~~~~~~~~~~~~~~~~~~

当重加载器使用 ``flask run`` 命令时，服务器将持续运行。哪怕您在代码中引
入了语法错误或其他初始化错误。访问网站时会交互式调试器中显示错误，而不
是使服务器崩溃。此功能称为“延迟加载”。

如果在调用 ``flask run`` 时已经存在语法错误，它将立即失败并显示回溯，而
不是等到网站被访问。 这是为了使错误最初更明显同时仍然允许服务器在重新加
载时处理错误。

要覆盖此行为并始终立即失败，即使在重新加载时，应当传递
``--eager-loading`` 参数。要始终保持服务器运行，即使在最初的调用中，传
递 ``--lazy-loading`` 参数。 


通过代码使用开发服务器
------------------------

另一种方法是在 Python 中通过 :meth:`Flask.run` 方法启动应用。这个方法接
受的参数与 CLI 的相似。主要的不同是重新加载时如果有错误，服务器会崩溃。

``debug=True`` 参数可以开启调试器和重载器，但是要开启开发模式仍需要设置
``FLASK_ENV=development`` 环境变量。

应当把调用放在 main 代码块中，否则当以后在生产环境中导入和运行应用时会
产生干扰。

.. code-block:: python

    if __name__ == "__main__":
        app.run(debug=True)

.. code-block:: text

    $ python hello.py
