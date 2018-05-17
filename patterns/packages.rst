.. _larger-applications:

大型应用
===================

对于大型应用来说使用包代替模块是一个好主意。使用包非常简单。假设有一个小应
用如下::

    /yourapplication
        yourapplication.py
        /static
            style.css
        /templates
            layout.html
            index.html
            login.html
            ...

:ref:`教程项目 <tutorial>` 就是这样的结构，参见
:gh:`示例代码 <examples/tutorial>` 。


简单的包
---------------

要把上例中的小应用装换为大型应用只要在现有应用中创建一个新的
:file:`yourapplication` 文件夹，并把所有东西都移动到这个文件夹内。然后把
:file:`yourapplication.py` 更名为 :file:`__init__.py` 。（请首先删除所有
``.pyc`` 文件，否则基本上会出问题）

修改完后应该如下例::

    /yourapplication
        /yourapplication
            __init__.py
            /static
                style.css
            /templates
                layout.html
                index.html
                login.html
                ...

但是现在如何运行应用呢？原本的 ``python yourapplication/__init__.py`` 无法
运行了。因为 Python 不希望包内的模块成为启动文件。但是这不是一个大问题，只
要在 :file:`yourapplication` 文件夹旁添加一个 :file:`runserver.py` 文件就
可以了，其内容如下::

    from setuptools import setup

    setup(
        name='yourapplication',
        packages=['yourapplication'],
        include_package_data=True,
        install_requires=[
            'flask',
        ],
    )

为了运行应用，需要导出一个环境变量，告诉 Flask 应用实例的位置::

    export FLASK_APP=yourapplication

如果位于项目文件夹之外，请确保提供绝对路径。同样可以这样打开开发功能::

    export FLASK_ENV=development

为了安装并运行应用，需要执行以下命令::

    pip install -e .
    flask run

我们从中学到了什么？现在我们来重构一下应用以适应多模块。只要记住以下几点：

1. `Flask` 应用对象必须位于 :file:`__init__.py` 文件中。这样每个模块就可以
   安全地导入了，且  `__name__` 变量会解析到正确的包。
2. 所有视图函数（在顶端有 :meth:`~flask.Flask.route` 的）必须在
   :file:`__init__.py` 文件中被导入。不是导入对象本身，而是导入视图模块。
   请 **在应用对象创建之后** 导入视图对象。
   
:file:`__init__.py` 示例::

    from flask import Flask
    app = Flask(__name__)

    import yourapplication.views

:file:`views.py` 内容如下::

    from yourapplication import app

    @app.route('/')
    def index():
        return 'Hello World!'

最终全部内容如下::

    /yourapplication
        setup.py
        /yourapplication
            __init__.py
            views.py
            /static
                style.css
            /templates
                layout.html
                index.html
                login.html
                ...

.. admonition:: 回环导入

   回环导入是指两个模块互相导入，本例中我们添加的 :file:`views.py` 就
   与 :file:`__init__.py` 相互依赖。每个 Python 程序员都讨厌回环导入。
   一般情况下回环导入是个坏主意，但在这里一点问题都没有。原因是我们没
   有真正使用 :file:`__init__.py` 中的视图，只是保证模块被导入，并且我
   们在文件底部才这样做。

   但是这种方式还是有些问题，因为没有办法使用装饰器。要找到解决问题的
   灵感请参阅 :ref:`becomingbig` 一节。

.. _working-with-modules:

使用蓝图
-----------------------

对于大型应用推荐把应用分隔为小块，每个小块使用蓝图辅助执行。关于这个主题的
介绍请参阅 :ref:`blueprints` 一节 。

