部署产品
====================

本文假设你要把应用部署到一个服务器上。本文只是给出如何创建发行文件并进行安
装的概览，但是不会具体讨论使用哪种服务器或者软件。你可以在用于开发的电脑中
设置一个新的虚拟环境，以便于尝试下面的内容。但是建议不要用于部署一个真正的
公开应用。以多种不同方式部署应用的列表参见 :doc:`/deploying/index` 。


构建和安装
-----------------

当需要把应用部署到其他地方时，需要构建一个发行文件。当前 Python 的标准发行
文件是 *wheel* 格式的，扩展名为 ``.whl`` 。先确保已经安装好 wheel 库：

.. code-block:: none

    $ pip install wheel

用 Python 运行 ``setup.py`` 会得到一个命令行工具，以使用构建相关命令。
``bdist_wheel`` 命令会构建一个 wheel 发行文件。

.. code-block:: none

    $ python setup.py bdist_wheel

构建的文件为 ``dist/flaskr-1.0.0-py3-none-any.whl`` 。文件名由项目名称、版
本号和一些关于项目安装要求的标记组成，形如：
{project name}-{version}-{python tag}-{abi tag}-{platform tag} 。

复制这个文件到另一台机器， :ref:`创建一个新的虚拟环境 <install-create-env>`
，然后用 ``pip`` 安装这个文件。

.. code-block:: none

    $ pip install flaskr-1.0.0-py3-none-any.whl

Pip 会安装项目和相关依赖。

既然这是一个不同的机器，那么需要再次运行 ``init-db`` 命令，在实例文件夹中
创建数据库。

.. tabs::

   .. group-tab:: Bash

      .. code-block:: text

         $ export FLASK_APP=flaskr
         $ flask init-db

   .. group-tab:: CMD

      .. code-block:: text

         > set FLASK_APP=flaskr
         > flask init-db

   .. group-tab:: Powershell

      .. code-block:: text

         > $env:FLASK_APP = "flaskr"
         > flask init-db

当 Flask 探测到它已被安装（不在编辑模式下），它会与前文不同，使用
``venv/var/flaskr-instance`` 作为实例文件夹。


配置密钥
------------------------

在教程开始的时候给了 :data:`SECRET_KEY` 一个缺省值。在产品中我们应当设置一
些随机内容。否则网络攻击者就可以使用公开的 ``'dev'`` 键来修改会话
cookie ，或者其他任何使用密钥的东西。

可以使用下面的命令输出一个随机密钥：

.. code-block:: none

    $ python -c 'import os; print(os.urandom(16))'

    b'_5#y2L"F4Q8z\n\xec]/'

在实例文件夹创建一个 ``config.py`` 文件。工厂会读取这个文件，如果该文件存
在的话。提制生成的值到该文件中。

.. code-block:: python
    :caption: ``venv/var/flaskr-instance/config.py``

    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

其他必须的配置也可以写入该文件中。 Flaskr 只需要 ``SECRET_KEY`` 即可。


运行产品服务器
----------------------------

当运行公开服务器而不是进行开发的时候，应当不使用内建的开发服务器
（ ``flask run`` ）。开发服务器由 Werkzeug 提供，目的是为了方便开发，但是
不够高效、稳定和安全。

替代地，应当选用一个产品级的 WSGI 服务器。例如，使用 `Waitress`_ 。首先在
虚拟环境中安装它：

.. code-block:: none

    $ pip install waitress

需要把应用告知 Waitree ，但是方式与 ``flask run`` 那样使用 ``FLASK_APP`` 
不同。需要告知 Waitree 导入并调用应用工厂来得到一个应用对象。

.. code-block:: none

    $ waitress-serve --call 'flaskr:create_app'

    Serving on http://0.0.0.0:8080

以多种不同方式部署应用的列表参见 :doc:`/deploying/index` 。使用 Waitress
只是一个示例，选择它是因为它同时支持 Windows 和 Linux 。还有其他许多 WSGI
服务器和部署选项可供选择。

.. _Waitress: https://docs.pylonsproject.org/projects/waitress/en/stable/

下面请阅读 :doc:`next` 。
