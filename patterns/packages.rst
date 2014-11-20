.. _larger-applications:

大型应用
===================

对于大型应用来说使用包代替模块是一个好主意。使用包非常简单。假设有一个小应用如
下::

    /yourapplication
        /yourapplication.py
        /static
            /style.css
        /templates
            layout.html
            index.html
            login.html
            ...

简单的包
---------------

要把上例中的小应用装换为大型应用只要在现有应用中创建一个名为 `yourapplication`
的新文件夹，并把所有东西都移动到这个文件夹内。然后把 `yourapplication.py` 更名
为 `__init__.py` 。（请首先删除所有 `.pyc` 文件，否则基本上会出问题）

修改完后应该如下例::

    /yourapplication
        /yourapplication
            /__init__.py
            /static
                /style.css
            /templates
                layout.html
                index.html
                login.html
                ...

但是现在如何运行应用呢？原本的 ``python yourapplication/__init__.py`` 无法运行
了。因为 Python 不希望包内的模块成为启动文件。但是这不是一个大问题，只要在
`yourapplication` 文件夹旁添加一个 `runserver.py` 文件就可以了，其内容如下::

    from yourapplication import app
    app.run(debug=True)

我们从中学到了什么？现在我们来重构一下应用以适应多模块。只要记住以下几点：

1. `Flask` 应用对象必须位于  `__init__.py` 文件中。这样每个模块就可以安全地导入
   了，且  `__name__` 变量会解析到正确的包。
2. 所有视图函数（在顶端有 :meth:`~flask.Flask.route` 的）必须在 `__init__.py`
   文件中被导入。不是导入对象本身，而是导入视图模块。请 **在应用对象创建之后**
   导入视图对象。
   
`__init__.py` 示例::

    from flask import Flask
    app = Flask(__name__)

    import yourapplication.views

`views.py` 内容如下::

    from yourapplication import app

    @app.route('/')
    def index():
        return 'Hello World!'

最终全部内容如下::

    /yourapplication
        /runserver.py
        /yourapplication
            /__init__.py
            /views.py
            /static
                /style.css
            /templates
                layout.html
                index.html
                login.html
                ...

.. admonition:: 回环导入

   回环导入是指两个模块互相导入，本例中我们添加的 `views.py` 就与 `__init__.py`
   相互依赖。每个 Python 程序员都讨厌回环导入。一般情况下回环导入是个坏主意，但
   在这里一点问题都没有。原因是我们没有真正使用 `__init__.py` 中的视图，只是
   保证模块被导入，并且我们在文件底部才这样做。

   但是这种方式还是有些问题，因为没有办法使用装饰器。要找到解决问题的灵感请参阅
   :ref:`becomingbig` 一节。

.. _working-with-modules:

使用蓝图
-----------------------

对于大型应用推荐把应用分隔为小块，每个小块使用蓝图辅助执行。关于这个主题的介绍
请参阅 :ref:`blueprints` 一节 。
