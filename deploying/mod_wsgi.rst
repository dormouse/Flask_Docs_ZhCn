.. _mod_wsgi-deployment:

mod_wsgi (Apache)
=================

如果你正在使用 `Apache`_ 网络服务器，那么建议使用 `mod_wsgi`_ 。

.. admonition:: 小心

   请务必把 ``app.run()`` 放在 ``if __name__ == '__main__':`` 内部或者放在单独
   的文件中，这样可以保证它不会被调用。因为，每调用一次就会开启一个本地 WSGI
   服务器。当我们使用 mod_wsgi 部署应用时，不需要使用本地服务器。

.. _Apache: http://httpd.apache.org/

安装 `mod_wsgi`
---------------------

可以使用包管理器或编译的方式安装 `mod_wsgi` 。在 UNIX 系统中如何使用源代码安装
请阅读 mod_wsgi `安装介绍`_ 。

如果你使用的是 Ubuntu/Debian ，那么可以使用如下命令安装：

.. sourcecode:: text

    # apt-get install libapache2-mod-wsgi

在 FreeBSD 系统中，可以通过编译 `www/mod_wsgi` port 或使用 pkg_add 来安装
`mod_wsgi` ：

.. sourcecode:: text

    # pkg_add -r mod_wsgi

如果你使用 pkgsrc ，那么可以通过编译 `www/ap2-wsgi` 包来安装 `mod_wsgi` 。

如果你遇到子进程段错误的话，不要理它，重启服务器就可以了。

创建一个 `.wsgi` 文件
-----------------------

为了运行应用，你需要一个 `yourapplication.wsgi` 文件。这个文件包含 `mod_wsgi`
开始时需要运行的代码，通过代码可以获得应用对象。文件中的 `application` 对象就
是以后要使用的应用。

对于大多数应用来说，文件包含以下内容就可以了::

    from yourapplication import app as application

如果你的应用没有创建函数，只是一个独立的实例，那么可以直接把实例导入为
`application` 。

把文件放在一个以后可以找得到的地方（例如 `/var/www/yourapplication` ），并确保
`yourapplication` 和所有需要使用的库都位于 pythonpath 中。如果你不想在整个系统
中安装，建议使用 `virtual python`_ 实例。请记住，最好把应用安装到虚拟环境中。
有一个可选项是在 `.wsgi` 文件中，在导入前加入路径::

    import sys
    sys.path.insert(0, '/path/to/the/application')


配置 Apache
------------------

最后一件事是为你的应用创建一个 Apache 配置文件。基于安全原因，在下例中我们告诉
`mod_wsgi` 使用另外一个用户运行应用：

.. sourcecode:: apache

    <VirtualHost *>
        ServerName example.com

        WSGIDaemonProcess yourapplication user=user1 group=group1 threads=5
        WSGIScriptAlias / /var/www/yourapplication/yourapplication.wsgi

        <Directory /var/www/yourapplication>
            WSGIProcessGroup yourapplication
            WSGIApplicationGroup %{GLOBAL}
            Order deny,allow
            Allow from all
        </Directory>
    </VirtualHost>

注意： WSGIDaemonProcess 在 Windows 中不会被执行， 使用上面的配置 Apache 会拒绝
运行。在 Windows 系统下，请使用下面内容：

.. sourcecode:: apache

	<VirtualHost *>
		ServerName example.com
		WSGIScriptAlias / C:\yourdir\yourapp.wsgi
		<Directory C:\yourdir>
			Order deny,allow
			Allow from all
		</Directory>
	</VirtualHost>

更多信息参见 `mod_wsgi 维基`_ 。

.. _mod_wsgi: http://code.google.com/p/modwsgi/
.. _安装介绍: http://code.google.com/p/modwsgi/wiki/QuickInstallationGuide
.. _virtual python: http://pypi.python.org/pypi/virtualenv
.. _mod_wsgi 维基: http://code.google.com/p/modwsgi/wiki/

故障排除
---------------

如果你的应用无法运行，请按以下指导排除故障：

**问题：** 应用无法运行，出错记录显示 SystemExit ignored
    应用文件中有 ``app.run()`` 调用，但没有放在 ``if __name__ == '__main__':``
    块内。要么把这个调用放入块内，要么把它放在一个单独的 `run.py` 文件中。

**问题：** 权限错误
    有可以是因为使用了错误的用户运行应用。请检查用户及其所在的组
    （ `WSGIDaemonProcess` 的 ``user`` 和 ``group`` 参数）是否有权限访问应用
    文件夹。

**问题：** 打印时应用歇菜
    请记住 mod_wsgi 不允许使用 :data:`sys.stdout` 和 :data:`sys.stderr` 。把
    `WSGIRestrictStdout` 设置为 ``off`` 可以去掉这个保护：

    .. sourcecode:: apache

        WSGIRestrictStdout Off

    或者你可以在 .wsgi 文件中把标准输出替换为其他的流::

        import sys
        sys.stdout = sys.stderr

**问题：** 访问资源时遇到 IO 错误
    你的应用可能是一个独立的 .py 文件，且你把它符号连接到了 site-packages
    文件夹。这样是不对的，你应当要么把文件夹放到 pythonpath 中，要么把你的应用
    转换为一个包。

    产生这种错误的原因是对于非安装包来说，模块的文件名用于定位资源，如果使用
    符号连接的话就会定位到错误的文件名。

支持自动重载
-------------------------------

为了辅助部署工具，你可以激活自动重载。这样，一旦 `.wsgi` 文件有所变动，
`mod_wsgi` 就会自动重新转入所有守护进程。

在 `Directory` 一节中加入以下指令就可以实现自动重载：

.. sourcecode:: apache

   WSGIScriptReloading On

使用虚拟环境
---------------------------------

使用虚拟环境的优点是不必全局安装应用所需要的依赖，这样我们就可以更好地按照自己
的需要进行控制。如果要在虚拟环境下使用 mod_wsgi ，那么我们要对 `.wsgi` 略作
改变。

在你的 `.wsgi` 文件顶部加入下列内容::

    activate_this = '/path/to/env/bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))

以上代码会根据虚拟环境的设置载入相关路径。请记住路径必须是绝对路径。
