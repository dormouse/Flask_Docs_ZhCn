.. _fabric-deployment:

使用 Fabric 部署
=====================

`Fabric`_ 是一个 Python 工具，与 Makefiles 类似，但是能够在远程服务器上执行
命令。如果与适当的 Python 包（ :ref:`larger-applications` ）与优良的配置（
:ref:`config` ）相结合那么 `Fabric` 将是在外部服务器上部署 Flask 的利器。

在下文开始之前，有几点需要明确：

-   Fabric 1.0 需要要被安装到本地。本教程假设使用的是最新版本的 Fabric 。
-   应用已经是一个包，且有一个可用的 `setup.py` 文件（
    :ref:`distribute-deployment` ）。
-   在下面的例子中，我们假设远程服务器使用 `mod_wsgi` 。当然，你可以使用你自己
    喜欢的服务器，但是在示例中我们选择 Apache + `mod_wsgi` ，因为它们设置方便，
    且在没有 root 权限情况下可以方便的重载应用。

创建第一个 Fabfile
--------------------------

fabfile 是控制 Fabric 的东西，其文件名为 `fabfile.py` ，由 `fab` 命令执行。在
这个文件中定义的所有函数都会被视作 `fab` 子命令。这些命令将会在一个或多个主机上
运行。这些主机可以在 fabfile 中定义，也可以在命令行中定义。本例将在 fabfile 中
定义主机。

下面是第一个例子，比较级。它可以把当前的源代码上传至服务器，并安装到一个预先存在
的 virtual 环境::

    from fabric.api import *

    # 使用远程命令的用户名
    env.user = 'appuser'
    # 执行命令的服务器
    env.hosts = ['server1.example.com', 'server2.example.com']

    def pack():
        # 创建一个新的分发源，格式为 tar 压缩包
        local('python setup.py sdist --formats=gztar', capture=False)

    def deploy():
        # 定义分发版本的名称和版本号
        dist = local('python setup.py --fullname', capture=True).strip()
        # 把 tar 压缩包格式的源代码上传到服务器的临时文件夹
        put('dist/%s.tar.gz' % dist, '/tmp/yourapplication.tar.gz')
        # 创建一个用于解压缩的文件夹，并进入该文件夹
        run('mkdir /tmp/yourapplication')
        with cd('/tmp/yourapplication'):
            run('tar xzf /tmp/yourapplication.tar.gz')
            # 现在使用 virtual 环境的 Python 解释器来安装包
            run('/var/www/yourapplication/env/bin/python setup.py install')
        # 安装完成，删除文件夹
        run('rm -rf /tmp/yourapplication /tmp/yourapplication.tar.gz')
        # 最后 touch .wsgi 文件，让 mod_wsgi 触发应用重载
        run('touch /var/www/yourapplication.wsgi')

上例中的注释详细，应当是容易理解的。以下是 fabric 提供的最常用命令的简要说明：

-   `run` - 在远程服务器上执行一个命令
-   `local` - 在本地机器上执行一个命令
-   `put` - 上传文件到远程服务器上
-   `cd` - 在服务器端改变目录。必须与 `with` 语句联合使用。

运行 Fabfile
----------------

那么如何运行 fabfile 呢？答案是使用 `fab` 命令。要在远程服务器上部署当前版本的
代码可以使用这个命令::

    $ fab pack deploy

但是这个命令需要远程服务器上已经创建了 ``/var/www/yourapplication`` 文件夹，且
``/var/www/yourapplication/env`` 是一个 virtual 环境。更进一步，服务器上还没有
创建配置文件和 `.wsgi` 文件。那么，我们如何在一个新的服务器上创建一个基础环境
呢？

这个问题取决于你要设置多少台服务器。如果只有一台应用服务器（多数情况下），那么
在 fabfile 中创建命令有一点多余。当然，你可以这么做。这个命令可以称之为
`setup` 或 `bootstrap` 。在使用命令时显式传递服务器名称::

    $ fab -H newserver.example.com bootstrap

设置一个新服务器大致有以下几个步骤：

1.  在 ``/var/www`` 创建目录结构::

        $ mkdir /var/www/yourapplication
        $ cd /var/www/yourapplication
        $ virtualenv --distribute env

2.  上传一个新的 `application.wsgi` 文件和应用配置文件（如 `application.cfg` ）
    到服务器上。

3.  创建一个新的用于 `yourapplication` 的 Apache 配置并激活它。要确保激活
    `.wsgi` 文件变动监视，这样在 touch 的时候可以自动重载应用。（ 更多信息参见
    :ref:`mod_wsgi-deployment` ）

现在的问题是： `application.wsgi` 和 `application.cfg` 文件从哪里来？

WSGI 文件
-------------

WSGI 文件必须导入应用，并且还必须设置一个环境变量用于告诉应用到哪里去搜索配置。
示例::

    import os
    os.environ['YOURAPPLICATION_CONFIG'] = '/var/www/yourapplication/application.cfg'
    from yourapplication import app

应用本身必须像下面这样初始化自己才会根据环境变量搜索配置::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_config')
    app.config.from_envvar('YOURAPPLICATION_CONFIG')

这个方法在 :ref:`config` 一节已作了详细的介绍。

配置文件
----------------------

上文已谈到，应用会根据 `YOURAPPLICATION_CONFIG` 环境变量找到正确的配置文件。
因此我们应当把配置文件放在应用可以找到的地方。在不同的电脑上配置文件是不同的，
所以一般我们不对配置文件作版本处理。

一个流行的方法是在一个独立的版本控制仓库为不同的服务器保存不同的配置文件，然后
在所有服务器进行检出。然后在需要的地方使用配置文件的符号链接（例如：
``/var/www/yourapplication`` ）。

不管如何，我们这里只有一到两台服务器，因此我们可以预先手动上传配置文件。


第一次部署
----------------

现在我们可以进行第一次部署了。我已经设置好了服务器，因此服务器上应当已经有了
virtual 环境和已激活的 apache 配置。现在我们可以打包应用并部署它了::

    $ fab pack deploy

Fabric 现在会连接所有服务器并运行 fabfile 中的所有命令。首先它会打包应用得到一个
tar 压缩包。然后会执行分发，把源代码上传到所有服务器并安装。感谢 `setup.py`
文件，所需要的依赖库会自动安装到 virtual 环境。

下一步
----------

在前文的基础上，还有更多的方法可以全部署工作更加轻松：

-   创建一个初始化新服务器的 `bootstrap` 命令。它可以初始化一个新的 virtual
    环境、正确设置 apache 等等。
-   把配置文件放入一个独立的版本库中，把活动配置的符号链接放在适当的地方。
-   还可以把应用代码放在一个版本库中，在服务器上检出最新版本后安装。这样你可以
    方便的回滚到老版本。
-   挂接测试功能，方便部署到外部服务器进行测试。

使用 Fabric 是一件有趣的事情。你会发现在电脑上打出 ``fab deploy`` 是非常神奇的。
你可以看到你的应用被部署到一个又一个服务器上。

.. _Fabric: http://fabfile.org/
