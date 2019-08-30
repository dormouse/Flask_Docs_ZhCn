.. _deploying-uwsgi:

uWSGI
=====

uWSGI 也是部署 Flask 的途径之一,类似的部署途径还有 `nginx`_ 、 `lighttpd`_ 和
`cherokee`_ 。其他部署途径的信息参见 :doc:`fastcgi` 和 :doc:`wsgi-standalone` 。
使用 uWSGI 协议来部署 WSGI 应用的先决条件是需要一个 uWSGI 服务器。 uWSGI
既是一个协议也是一个服务器。如果作为一个服务器，它可以服务于 uWSGI 、 FastCGI
和 HTTP 协议。

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

    $ uwsgi -s /tmp/yourapplication.sock --manage-script-name --mount /yourapplication=myapp:app

``--manage-script-name`` 会把 ``SCRIPT_NAME`` 处理移向 uwsgi ， 因为 uwsgi
会更智能一些。与 ``--mount`` 联用可以把向 ``/yourapplication`` 发送的请求
重定向到 ``myapp:app`` 。如果应用可以在根级别访问，那么可以使用单个 ``/``
来代替 ``/yourapplication`` 。 ``myapp`` 指 flask 应用的文件名称（不含扩展
名）或者提供 ``app`` 的模块名称。 ``app`` 在应用内部可被调用（通常是
``app = Flask(__name__)`` ）。

如果要把应用部署于一个虚拟环境，则还需要加上
``--virtualenv /path/to/virtual/environment`` 。可能还需要根据项目所使用的
Python 版本相应地加上 ``--plugin python`` 或者 ``--plugin python3`` 。

配置 nginx
-----------------

一个 nginx 的基本 uWSGI 配置如下::

    location = /yourapplication { rewrite ^ /yourapplication/; }
    location /yourapplication { try_files $uri @yourapplication; }
    location @yourapplication {
      include uwsgi_params;
      uwsgi_pass unix:/tmp/yourapplication.sock;
    }

这个配置把应用绑定到 ``/yourapplication`` 。如果你想要在根 URL 下运行应用
非常简单::

    location / { try_files $uri @yourapplication; }
    location @yourapplication {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/yourapplication.sock;
    }

.. _nginx: https://nginx.org/
.. _lighttpd: https://www.lighttpd.net/
.. _cherokee: http://cherokee-project.com/
.. _uwsgi: https://uwsgi-docs.readthedocs.io/en/latest/
