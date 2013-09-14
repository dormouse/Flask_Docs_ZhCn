.. _installation:

安装
====

Flask 依赖两个外部库： `Werkzeug <http://werkzeug.pocoo.org/>`_ 和 `Jinja2
<http://jinja.pocoo.org/2/>`_ 。Werkzeug 是一个 WSGI 套件。 WSGI 是 Web 应用与
多种服务器之间的标准 Python 接口，即用于开发，也用于部署。 Jinja2 是用于渲染
模板的。

那么如何快速在你的计算机上装好所有东西？本节会介绍多种方法，但是最强力的方法是
使用 virtualenv 。因此，我们先说 virtualenv 。

无论使用哪种方法安装，你都会需要 Python 2.6 或更高版本。因此请确保安装了最新的
Python 2.x 版本。在 Python 3 下使用 Flask 请参阅 :ref:`python3_support` 。

.. _virtualenv:

virtualenv
----------

如果可以使用 shell ，那么可能 Virtualenv 是你在开发环境和生产环境都想使用的
东西。

virtualenv 有什么用？如果你象我一样热爱 Python ，那么除了基于 Flask 的项目外
还会有其他项目用到 Python 。当项目越来越多时就会面对使用不同版本的 Python 的
问题，或者至少会遇到使用不同版本的 Python 库的问题。摆在你面前的是：库常常不能
向后兼容，更不幸的是任何成熟的应用都不是零依赖。如果两个项目依赖出现冲突，
怎么办？

Virtualenv 就是救星！它的基本原理是为每个项目安装一套 Python ，多套 Python
并存。但它不是真正地安装多套独立的 Python 拷贝，而是使用了一种巧妙的方法让不同
的项目处于各自独立的环境中。让我们来看看 virtualenv 是如何运行的！

如果你使用 Mac OS X 或 Linux ，那么可以使用下面两条命令中任意一条::

    $ sudo easy_install virtualenv

或更高级的::

    $ sudo pip install virtualenv

上述命令中的任意一条就可以安装好 virtualenv 。也可以使用软件包管理器，在
Ubuntu 系统中可以试试::

    $ sudo apt-get install python-virtualenv

如果你使用 Windows 且无法使用 `easy_install` ，那么你必须先安装它，安装方法详见
《 :ref:`windows-easy-install` 》。安装好以后运行上述命令，但是要去掉 `sudo`
前缀。

安装完 virtualenv ，打开一个 shell ，创建自己的环境。我通常创建一个包含 `venv`
文件夹的项目文件夹::

    $ mkdir myproject
    $ cd myproject
    $ virtualenv venv
    New python executable in env/bin/python
    Installing setuptools............done.

现在，每次需要使用项目时，必须先激活相应的环境。在 OS X 和 Linux 系统中运行::

    $ . venv/bin/activate

Windows 用户请运行下面的命令::

    $ venv\scripts\activate

殊途同归，你现在进入你的 virtualenv （注意查看你的 shell 提示符已经改变了）。

现在可以开始在你的 virtualenv 中安装 Flask 了::

    $ pip install Flask

几秒钟后就安装好了。


系统全局安装
------------

虽然这样做是可行的，虽然我不推荐。只需要以 root 权限运行 `pip` 就可以了::

    $ sudo pip install Flask

（ Windows 系统中请在管理员 shell 中运行，去掉 `sudo` ）。


生活在边缘
------------------

如果你想要使用最新版的 Flask ，那么有两种方法：要么使用 `pip` 安装开发版本，
要么使用 git 检索。无论哪种方法，都推荐使用 virtualenv 。

在一个新的 virtualenv 中获得 git 检索，并在开发模式下运行::

    $ git clone http://github.com/mitsuhiko/flask.git
    Initialized empty Git repository in ~/dev/flask/.git/
    $ cd flask
    $ virtualenv venv --distribute
    New python executable in venv/bin/python
    Installing distribute............done.
    $ . venv/bin/activate
    $ python setup.py develop
    ...
    Finished processing dependencies for Flask

上述操作会安装相关依赖库并在 virtualenv 中激活 git 头作为当前版本。然后只要
使用 ``git pull origin`` 命令就可以安装最新版本的 Flask 了。

如果不使用 git ，那么可以这样获得开发版本::

    $ mkdir flask
    $ cd flask
    $ virtualenv venv --distribute
    $ . venv/bin/activate
    New python executable in venv/bin/python
    Installing distribute............done.
    $ pip install Flask==dev
    ...
    Finished processing dependencies for Flask==dev

.. _windows-easy-install:

在 Windows 系统中使用 `pip` 和 `distribute`
--------------------------------------------

在 Windows 系统中，安装 `easy_install` 稍微有点麻烦，但还是比较简单的。最简单的
方法是下载并运行 `ez_setup.py`_ 文件。最简单的运行文件的方法是打开下载文件所在
文件夹，双击这个文件。

接下来，通过把 Python 代码所在文件夹添加到 `PATH` 环境变量的方法把
`easy_install` 命令和其他 Python 代码添加到命令搜索目录。操作方法：用鼠标右键
点击桌面上或者开始菜单中的“我的电脑”图标，在弹出的菜单中点击“属性”。然后
点击“高级系统设置”（如果是 Windows XP ，则点击“高级”分页）。接着点击“环境
变量”按钮，双击“系统变量”一节中的“ Path ”变量。这样就可以添加 Python 代码
所在的文件夹了。 注意，与已经存在的值之间要用分号分隔。假设你在缺省路径安装了
Python 2.7 ，那么就应该添加如下内容::

    ;C:\Python27\Scripts

至此安装完成。要检验安装是否正确可以打开命令提示符，并运行 ``easy_install``
命令。如果你使用 Windows Vista 或 Windows 7 ，并打开了权限控制，会提示你需要
管理员权限。

至此，你安装好了 ``easy_install`` ，接下来就可以用它来安装 ``pip`` 了::

    > easy_install pip

.. _ez_setup.py: http://peak.telecommunity.com/dist/ez_setup.py
