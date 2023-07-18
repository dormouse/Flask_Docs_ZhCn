项目可安装化
============================

项目可安装化是指创建一个 *wheel* 文件，以使项目可以安装到其他环境中，就
像在你的项目环境中安装 Flask 一样。这样可以使你的项目如同其他库一样进行
部署，使用标准的 Python 工具来管理项目。

可安装化还可以带来如下好处，这些好处在教程中可以不太明显或者初学者可
能没注意到：

*   现在， Python 和 Flask 能够理解如何 ``flaskr`` 包，是因为你是在项
    目文件夹中运行的。可安装化后，可以从任何地方导入项目并运行。

*   可以和其他包一样管理项目的依赖，即使用
    ``pip install yourproject.whl`` 来安装项目并安装相关依赖。

*   测试工具可以分离测试环境和开发环境。

.. note::
    这些内容会在随后的教程中说明，但是在以后的项目中应当以此为项目的
    起点。


描述项目
--------------------

``pyproject.toml`` 文件描述项目及其构建方法。

.. code-block:: toml
    :caption: ``pyproject.toml``

    [project]
    name = "flaskr"
    version = "1.0.0"
    dependencies = [
        "flask",
    ]

    [build-system]
    requires = ["setuptools"]
    build-backend = "setuptools.build_meta"

setuptools 构建后端需要 ``MANIFEST.in`` 文件来说明需要包含的非 Python
文件。

.. code-block:: none
    :caption: ``MANIFEST.in``

    include flaskr/schema.sql
    graft flaskr/static
    graft flaskr/templates
    global-exclude *.pyc

这告诉构建器复制所有 ``static`` 和 ``templates`` 文件夹中的文件，
``schema.sql`` 文件，但是排除所有字节文件。

更多内容和参数参见 `官方打包教程`_  和 `官方打包指南`_ 。

.. _官方打包教程: https://packaging.python.org/tutorials/packaging-projects/
.. _官方打包指南: https://packaging.python.org/guides/distributing-packages-using-setuptools/
 

安装项目
-------------------

使用 ``pip`` 在虚拟环境中安装项目。

.. code-block:: none

    $ pip install -e .

这个命令告诉 pip 在当前文件夹中寻找 ``pyproject.toml`` 并在 *编辑* 或
*开发* 模式下安装。编辑模式是指当改变本地代码后，只需要重新项目。比如
改变了项目依赖之类的元数据的情况下。

可以通过 ``pip list`` 来查看项目的安装情况。

.. code-block:: none

    $ pip list

    Package        Version   Location
    -------------- --------- ----------------------------------
    click          6.7
    Flask          1.0
    flaskr         1.0.0     /home/user/Projects/flask-tutorial
    itsdangerous   0.24
    Jinja2         2.10
    MarkupSafe     1.0
    pip            9.0.3
    setuptools     39.0.1
    Werkzeug       0.14.1
    wheel          0.30.0


至此，没有改变项目运行的方式， ``--app`` 还是被设置为 ``flaskr`` ，
还是使用 ``flask run`` 运行应用。不同的是可以在任何地方运行应用，而不
仅仅是在 ``flask-tutorial`` 目录下。

下面请阅读 :doc:`tests` 。
