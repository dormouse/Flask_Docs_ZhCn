.. _installation:

安装
====

Flask 依赖两个外部库： `Werkzeug <http://werkzeug.pocoo.org/>`_ 和 `Jinja2
<http://jinja.pocoo.org/2/>`_ 。Werkzeug 是一个 WSGI 套件。 WSGI 是 Web 应用与
多种服务器之前的标准 Python 接口，即用于开发，也用于部署。 Jinja2 是用于渲染
模板的。

那么如何快速在你的计算机上装好所有东西？本节会介绍多种方法，但是最强力的方法是
使用 virtualenv 。因此，我们先说 virtualenv 。

无论使用哪种方法安装，你都会需要 Python 2.5 或更高版本。因此请确保安装了最新的
Python 2.x 版本。直到本文写作之时 Python 3 的 WSGI 规范还未最终确定，因此 Flask
还不能支持 3.x 系列的 Python 。

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

Virtualenv 就是救星！它是基本原理是为每个项目安装一套 Python ，多套 Python
并存。但它不是真正地安装多套独立的 Python 拷贝，而是使用了一种巧妙的方法让不同
的项目处于各自独立的环境中。

让我们来看看 virtualenv 是如何运行的！

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

安装完 virtualenv ，打开一个 shell ，创建自己的环境。我通常创建一个包含 `env`
文件夹的项目文件夹::

    $ mkdir myproject
    $ cd myproject
    $ virtualenv env
    New python executable in env/bin/python
    Installing setuptools............done.

现在，每次需要使用项目时，必须先激活相应的环境。在 OS X 和 Linux 系统中运行::

    $ . env/bin/activate

（注意点和脚本名称之间有一个空格。点表示这个脚本必须运行在当前 shell 的背景中。
如果这个命令不能在你的 shell 中运行，请尝试把点替换为 ``source`` 。）

Windows 用户请运行下面的命令::

    $ env\scripts\activate

殊途同归，你现在进入你的 virtualenv （注意查看你的 shell 提示符已经改变了）。

现在可以开始在你的 virtualenv 中安装 Flask 了::

    $ easy_install Flask

几秒钟后就安装好了。


系统全局安装
------------

虽然这样做是可行的，但是我不推荐。只需要以 root 权限运行 `easy_install` 就可以
了::

    $ sudo easy_install Flask

（ Windows 系统中请在管理员 shell 中运行，去掉 `sudo` ）。


生活在边缘
------------------

如果你想要使用最新版的 Flask ，那么有两种方法：要么使用 `easy_install` 安装开发
版本，要么使用 git 检索。无论哪种方法，都推荐使用 virtualenv 。

在一个新的 virtualenv 中获得 git 检索，并在开发模式下运行::

    $ git clone http://github.com/mitsuhiko/flask.git
    Initialized empty Git repository in ~/dev/flask/.git/
    $ cd flask
    $ virtualenv env
    $ . env/bin/activate
    New python executable in env/bin/python
    Installing setuptools............done.
    $ python setup.py develop
    ...
    Finished processing dependencies for Flask

上述操作会
This will pull in the dependencies and activate the git head as the current
version inside the virtualenv.  Then you just have to ``git pull origin``
to get the latest version.

To just get the development version without git, do this instead::

    $ mkdir flask
    $ cd flask
    $ virtualenv env
    $ . env/bin/activate
    New python executable in env/bin/python
    Installing setuptools............done.
    $ easy_install Flask==dev
    ...
    Finished processing dependencies for Flask==dev

.. _windows-easy-install:

`easy_install` on Windows
-------------------------

On Windows, installation of `easy_install` is a little bit trickier because
slightly different rules apply on Windows than on Unix-like systems, but
it's not difficult.  The easiest way to do it is to download the
`ez_setup.py`_ file and run it.  The easiest way to run the file is to
open your downloads folder and double-click on the file.

Next, add the `easy_install` command and other Python scripts to the
command search path, by adding your Python installation's Scripts folder
to the `PATH` environment variable.  To do that, right-click on the
"Computer" icon on the Desktop or in the Start menu, and choose
"Properties".  Then, on Windows Vista and Windows 7 click on "Advanced System
settings"; on Windows XP, click on the "Advanced" tab instead.  Then click
on the "Environment variables" button and double click on the "Path"
variable in the "System variables" section.  There append the path of your
Python interpreter's Scripts folder; make sure you delimit it from
existing values with a semicolon.  Assuming you are using Python 2.6 on
the default path, add the following value::

    ;C:\Python26\Scripts

Then you are done.  To check that it worked, open the Command Prompt and
execute ``easy_install``.  If you have User Account Control enabled on
Windows Vista or Windows 7, it should prompt you for admin privileges.


.. _ez_setup.py: http://peak.telecommunity.com/dist/ez_setup.py
