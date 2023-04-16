nginx
=====

`nginx`_ 是一个快速的、生产级别的 HTTP 服务器。当使用 :doc:`index` 中
列出的 WSGI 服务器之一作为应用服务器时，在它前面放置一个专用的 HTTP
服务器通常是好的，甚至是必要的。这个“反向代理”可以比 WSGI 服务器更
好地处理进入的请求、 TLS 和其他安全和性能问题。

Nginx 可以使用你的系统包管理器安装，或者在 Windows 下使用预制的可执行
文件。安装和运行 Nginx 本身并不在本文档的讨论范围之内。本文概述了配置
Nginx 作为代理的基础知识。请务必阅读其文档，以了解更详细的内容。

.. _nginx: https://nginx.org/


域名
-----------

获取和配置域名不在本文件的讨论范围之内。一般来说，你会从注册商那里购
买一个域名，在托管商那里支付服务器空间的费用。然后将你的注册商指向主
机提供商的名称服务器。

为了模拟这一点，你也可以编辑你的 ``hosts`` 文件， Linux 系统中位于
``/etc/hosts`` ，添加一行，将名称与本地 IP 关联。

现代 Linux 系统可以被配置为将任何以 ``.localhost`` 结尾的域名与本地
IP 关联，而不需要将其添加到 ``hosts`` 文件中。

.. code-block:: python
    :caption: ``/etc/hosts``

    127.0.0.1 hello.localhost


配置
-------------

Linux 系统中， nginx 的配置位于 ``/etc/nginx/nginx.conf`` 。根据你的
操作系统，它可能有所不同。查看文档并查找 ``nginx.conf`` 。

删除或注释掉任何现有的 ``server`` 部分。添加一个 ``server`` 小节，
并使用 ``proxy_pass`` 指令来指向 WSGI 服务器正在监听的地址。我们假设
WSGI 服务器正在监听 ``http://127.0.0.1:8000`` 。

.. code-block:: nginx
    :caption: ``/etc/nginx.conf``

    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://127.0.0.1:8000/;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Prefix /;
        }
    }

然后 :doc:`proxy_fix` 以让你的应用使用这些头部。
