.. _deploying-fastcgi:

FastCGI
=======

FastCGI 是部署 Flask 的途径之一,类似的部署途径还有 `nginx`_  、 `lighttpd`_ 和 
`cherokee`_ 。其他部署途径的信息参见 :ref:`deploying-uwsgi` 和
:ref:`deploying-wsgi-standalone` 。本文讲述的是使用 FastCGI 部署，因此先决条件
是要有一个 FastCGI 服务器。 `flup`_ 最流行的 FastCGI 服务器之一，我们将会在本文
中使用它。在阅读下文之前先安装好 `flup`_ 。

.. admonition:: 小心

   请务必把 ``app.run()`` 放在 ``if __name__ == '__main__':`` 内部或者放在单独
   的文件中，这样可以保证它不会被调用。因为，每调用一次就会开启一个本地 WSGI
   服务器。当我们使用 FastCGI 部署应用时，不需要使用本地服务器。


创建一个 `.fcgi` 文件
-----------------------

首先你必须创建 FastCGI 服务器配置文件，我们把它命名为 `yourapplication.fcgi`::

    #!/usr/bin/python
    from flup.server.fcgi import WSGIServer
    from yourapplication import app

    if __name__ == '__main__':
        WSGIServer(app).run()

如果使用的是 Apache ，那么使用了这个文件之后就可以正常工作了。但是如果使用的是
nginx 或老版本的 lighttpd ，那么需要显式地把接口传递给 FastCGI 服务器，即把接口
的路径传递给 :class:`~flup.server.fcgi.WSGIServer`::

    WSGIServer(application, bindAddress='/path/to/fcgi.sock').run()

这个路径必须与服务器配置中定义的路径一致。

把这个 `yourapplication.fcgi` 文件放在一个以后可以找得到的地方，最好是
`/var/www/yourapplication` 或类似的地方。

为了让服务器可以执行这个文件，请给文件加上执行位，确保这个文件可以执行：

.. sourcecode:: text

    # chmod +x /var/www/yourapplication/yourapplication.fcgi

配置 Apache
------------------

上面的例子对于基本的 Apache 部署已经够用了，但是你的 `.fcgi` 文件会暴露在应用的
URL 中，比如 example.com/yourapplication.fcgi/news/ 。有多种方法可以避免出现这
中情况。一个较好的方法是使用 ScriptAlias 配置指令::

    <VirtualHost *>
        ServerName example.com
        ScriptAlias / /path/to/yourapplication.fcgi/
    </VirtualHost>

如果你无法设置 ScriptAlias ，比如你使用的是一个共享的网络主机，那么你可以使用
WSGI 中间件把 yourapplication.fcgi 从 URL 中删除。你可以这样设置 .htaccess::

    <IfModule mod_fcgid.c>
       AddHandler fcgid-script .fcgi
       <Files ~ (\.fcgi)>
           SetHandler fcgid-script
           Options +FollowSymLinks +ExecCGI
       </Files>
    </IfModule>

    <IfModule mod_rewrite.c>
       Options +FollowSymlinks
       RewriteEngine On
       RewriteBase /
       RewriteCond %{REQUEST_FILENAME} !-f
       RewriteRule ^(.*)$ yourapplication.fcgi/$1 [QSA,L]
    </IfModule>

设置 yourapplication.fcgi::

    #!/usr/bin/python
    #: optional path to your local python site-packages folder
    import sys
    sys.path.insert(0, '<your_local_path>/lib/python2.6/site-packages')

    from flup.server.fcgi import WSGIServer
    from yourapplication import app

    class ScriptNameStripper(object):
       def __init__(self, app):
           self.app = app

       def __call__(self, environ, start_response):
           environ['SCRIPT_NAME'] = ''
           return self.app(environ, start_response)

    app = ScriptNameStripper(app)

    if __name__ == '__main__':
        WSGIServer(app).run()
    
配置 lighttpd
--------------------

一个 lighttpd 的基本 FastCGI 配置如下::

    fastcgi.server = ("/yourapplication.fcgi" =>
        ((
            "socket" => "/tmp/yourapplication-fcgi.sock",
            "bin-path" => "/var/www/yourapplication/yourapplication.fcgi",
            "check-local" => "disable",
            "max-procs" => 1
        ))
    )

    alias.url = (
        "/static/" => "/path/to/your/static"
    )

    url.rewrite-once = (
        "^(/static($|/.*))$" => "$1",
        "^(/.*)$" => "/yourapplication.fcgi$1"

请记住启用 FastCGI 、 alias 和 rewrite 模块。以上配置把应用绑定到
`/yourapplication` 。如果你想要让应用在根 URL 下运行，那么必须使用
:class:`~werkzeug.contrib.fixers.LighttpdCGIRootFix` 中间件来解决一个
lighttpd 缺陷。

请确保只有应用在根 URL 下运行时才使用上述中间件。更多信息请阅读 `FastCGI 和
Python <http://redmine.lighttpd.net/wiki/lighttpd/Docs:ModFastCGI>`_
（注意，已经不再需要把一个接口显式传递给 run() 了）。


配置 nginx
-----------------

在 nginx 上安装 FastCGI 应用有一些特殊，因为缺省情况下不传递 FastCGI 参数。

一个 nginx 的基本 FastCGI 配置如下::

    location = /yourapplication { rewrite ^ /yourapplication/ last; }
    location /yourapplication { try_files $uri @yourapplication; }
    location @yourapplication {
        include fastcgi_params;
	fastcgi_split_path_info ^(/yourapplication)(.*)$;
        fastcgi_param PATH_INFO $fastcgi_path_info;
        fastcgi_param SCRIPT_NAME $fastcgi_script_name;
        fastcgi_pass unix:/tmp/yourapplication-fcgi.sock;
    }

这个配置把应用绑定到 `/yourapplication` 。如果你想要在根 URL 下运行应用非常
简单，因为你不必指出如何计算出 `PATH_INFO` 和 `SCRIPT_NAME`::

    location / { try_files $uri @yourapplication; }
    location @yourapplication {
        include fastcgi_params;
        fastcgi_param PATH_INFO $fastcgi_script_name;
        fastcgi_param SCRIPT_NAME "";
        fastcgi_pass unix:/tmp/yourapplication-fcgi.sock;
    }

运行 FastCGI 进程
-------------------------

Nginx 和其他服务器不会载入 FastCGI 应用，你必须自己载入。 `Supervisor 可以管理
FastCGI 进程。
<http://supervisord.org/configuration.html#fcgi-program-x-section-settings>`_
在启动时你可以使用其他 FastCGI 进程管理器或写一个脚本来运行 `.fcgi` 文件，例如
使用一个 SysV ``init.d`` 脚本。如果是临时使用，你可以在一个 GNU screen 中运行
``.fcgi`` 脚本。运行细节参见 ``man screen`` ，同时请注意这是一个手动启动方法，
不会在系统重启时自动启动::

    $ screen
    $ /var/www/yourapplication/yourapplication.fcgi

调试
---------

在大多数服务器上， FastCGI 部署难以调试。通常服务器日志只会告诉你类似
“ premature end of headers ”的内容。为了调试应用，查找出错的原因，你必须切换
到正确的用户并手动执行应用。

下例假设你的应用是 `application.fcgi` ，且你的网络服务用户为 `www-data`::

    $ su www-data
    $ cd /var/www/yourapplication
    $ python application.fcgi
    Traceback (most recent call last):
      File "yourapplication.fcgi", line 4, in <module>
    ImportError: No module named yourapplication

上面的出错信息表示 "yourapplication" 不在 python 路径中。原因可能有：

-   使用了相对路径。在当前工作路径下路径出错。
-   当前网络服务器设置未正确设置环境变量。
-   使用了不同的 python 解释器。

.. _nginx: http://nginx.org/
.. _lighttpd: http://www.lighttpd.net/
.. _cherokee: http://www.cherokee-project.com/
.. _flup: http://trac.saddi.com/flup
