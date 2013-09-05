.. _deploying-uwsgi:

uWSGI
=====

uWSGI 也是部署 Flask 的途径之一,类似的部署途径还有 `nginx`_ 、 `lighttpd`_ 和
`cherokee`_ 。其他部署途径的信息参见 :ref:`deploying-fastcgi` 和
:ref:`deploying-wsgi-standalone` 。使用 uWSGI 协议来部署 WSGI 应用的先决条件是
需要一个 uWSGI 服务器。 uWSGI 既是一个协议也是一个服务器。如果作为一个服务器，
它可以服务于 uWSGI 、 FastCGI 和 HTTP 协议。

最流行的 uWSGI 服务器是 `uwsgi`_ ，本文将使用它来举例，请先安装它。

.. admonition:: 小心

   请务必把 ``app.run()`` 放在 ``if __name__ == '__main__':`` 内部或者放在单独
   的文件中，这样可以保证它不会被调用。因为，每调用一次就会开启一个本地 WSGI
   服务器。当我们使用 uWSGI 部署应用时，不需要使用本地服务器。


使用 uwsgi 启动你的应用
----------------------------

`uwsgi` 是基于 python 模块中的 WSGI 调用的。假设 Flask 应用名称为 myapp.py ，
可以使用以下命令：

.. sourcecode:: text

    $ uwsgi -s /tmp/uwsgi.sock --module myapp --callable app

或者这个命令也行：

.. sourcecode:: text

    $ uwsgi -s /tmp/uwsgi.sock -w myapp:app

配置 nginx
-----------------

一个 nginx 的基本 uWSGI 配置如下::

    location = /yourapplication { rewrite ^ /yourapplication/; }
    location /yourapplication { try_files $uri @yourapplication; }
    location @yourapplication {
      include uwsgi_params;
      uwsgi_param SCRIPT_NAME /yourapplication;
      uwsgi_modifier1 30;
      uwsgi_pass unix:/tmp/uwsgi.sock;
    }

这个配置把应用绑定到 `/yourapplication` 。如果你想要在根 URL 下运行应用非常
简单，因为你不必指出 WSGI `PATH_INFO` 或让 uwsgi 修改器来使用它::

    location / { try_files $uri @yourapplication; }
    location @yourapplication {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/uwsgi.sock;
    }

.. _nginx: http://nginx.org/
.. _lighttpd: http://www.lighttpd.net/
.. _cherokee: http://www.cherokee-project.com/
.. _uwsgi: http://projects.unbit.it/uwsgi/
