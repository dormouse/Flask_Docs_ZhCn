项目布局
==============

创建并进入项目文件夹:

.. code-block:: none

    mkdir flask-tutorial
    cd flask-tutorial

接下来按照 :doc:`安装简介 </installation>` 设置一个 Python 虚拟环境，然后
为项目安装 Flask 。

本教程假定项目文件夹名称为 ``flask-tutorial`` ，本教程中代码块的顶端的文件
名是基于该文件夹的相对名称。

----

一个最简单的 Flask 应用可以是单个文件。

.. code-block:: python
    :caption: ``hello.py``

    from flask import Flask

    app = Flask(__name__)


    @app.route('/')
    def hello():
        return 'Hello, World!'

然而，当项目越来越大的时候，把所有代码放在单个文件中就有点不堪重负了。
Python 项目使用 *包* 来管理代码，把代码分为不同的模块，然后在需要的地方导入
模块。本教程也会按这一方式管理代码。

教程项目包含如下内容:

* ``flaskr/`` ，一个包含应用代码和文件的 Python 包。
* ``tests/`` ，一个包含测试模块的文件夹。
* ``venv/`` ，一个 Python 虚拟环境，用于安装 Flask 和其他依赖的包。
* 告诉 Python 如何安装项目的安装文件。
* 版本控制配置，如 `git`_ 。不管项目大小，应当养成使用版本控制的习惯。
* 项目需要的其他文件。

.. _git: https://git-scm.com/

最后，项目布局如下：

.. code-block:: none

    /home/user/Projects/flask-tutorial
    ├── flaskr/
    │   ├── __init__.py
    │   ├── db.py
    │   ├── schema.sql
    │   ├── auth.py
    │   ├── blog.py
    │   ├── templates/
    │   │   ├── base.html
    │   │   ├── auth/
    │   │   │   ├── login.html
    │   │   │   └── register.html
    │   │   └── blog/
    │   │       ├── create.html
    │   │       ├── index.html
    │   │       └── update.html
    │   └── static/
    │       └── style.css
    ├── tests/
    │   ├── conftest.py
    │   ├── data.sql
    │   ├── test_factory.py
    │   ├── test_db.py
    │   ├── test_auth.py
    │   └── test_blog.py
    ├── venv/
    ├── setup.py
    └── MANIFEST.in

如果使用了版本控制，那么运行项目时产生的临时文件应当忽略。编辑代码时，编辑器
产生的临时文件也应当忽略。基本原则是：不是你自己写的文件就可以忽略。例如，
如果使用 git ，那么 :file:`.gitignore` 内容如下:

.. code-block:: none
    :caption: ``.gitignore``

    venv/

    *.pyc
    __pycache__/

    instance/

    .pytest_cache/
    .coverage
    htmlcov/

    dist/
    build/
    *.egg-info/

下面请阅读 :doc:`factory` 。
