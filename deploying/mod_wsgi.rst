mod_wsgi
========

`mod_wsgi`_ 是一个与 `Apache httpd`_ 服务器集成的 WSGI 服务器。
现代 `mod_wsgi-express`_ 命令使得配置和启动服务器变得很容易，不需要编
写 Apache httpd 配置。

*   与 Apache httpd 紧密结合。
*   直接支持 Windows 。
*   需要一个编译器和 Apache 开发头文件来安装。
*   不需要设置反向代理。

本文概述运行 mod_wsgi-express 的基础知识，不涉及更复杂的 httpd 安装和
配置。详细内容请务必阅读 `mod_wsgi-express`_ 、 `mod_wsgi`_ 和
`Apache httpd`_ 文档。

.. _mod_wsgi-express: https://pypi.org/project/mod-wsgi/
.. _mod_wsgi: https://modwsgi.readthedocs.io/
.. _Apache httpd: https://httpd.apache.org/


安装
----------

安装 ``mod_wsgi`` 需要一个编译器和 Apache 服务器和开发头文件。否则会
出错。如何安装它们取决于你使用的操作系统和软件包管理器。

创建一个虚拟环境，安装应用，然后安装 ``mod_wsgi`` 。

.. code-block:: text

    $ cd hello-app
    $ python -m venv venv
    $ . venv/bin/activate
    $ pip install .  # install your application
    $ pip install mod_wsgi


运行
-------

``mod_wsgi-express`` 的唯一参数是指定一个包含你的 Flask 应用的脚本，
它必须被称为 ``application`` 。你可以写一个小脚本，用这个名字导入你的
应用。如果使用应用程序工厂模式，那么需要创建它。

.. code-block:: python
    :caption: ``wsgi.py``

    from hello import app

    application = app

.. code-block:: python
    :caption: ``wsgi.py``

    from hello import create_app

    application = create_app()

现在运行 ``mod_wsgi-express start-server`` 命令。

.. code-block:: text

    $ mod_wsgi-express start-server wsgi.py --processes 4

``--processes`` 选项指定了要运行的工作进程的数量，起始值可以是
``CPU * 2`` 。

每个请求的日志不会显示在终端。如果有错误发生，其信息将被写入启动服务
器时显示的错误日志文件中。


外部绑定
------------------

与这些文档中的其他 WSGI 服务器不同， mod_wsgi 可以作为 root 用户运行，
绑定到特权端口，如 80 和 443。但是，它必须被配置为将权限下放属于不同
用户和组的工作者进程。

例如，如果你创建了一个 ``hello`` 用户和组，你应该以该用户身份安装你的
虚拟环境和应用，然后告诉 mod_wsgi 在启动后放权给该用户。

.. code-block:: text

    $ sudo /home/hello/venv/bin/mod_wsgi-express start-server \
        /home/hello/wsgi.py \
        --user hello --group hello --port 80 --processes 4
