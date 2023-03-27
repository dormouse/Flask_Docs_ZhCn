Apache httpd
============

`Apache httpd`_ 是一个快速、生产级的 HTTP 服务器。当使用 :doc:`index`
中所列的 WSGI 服务器作为你的应用程序的服务器时，通常在前端放置一个专
门的 HTTP 服务器是十分必要的。相较于 WSGI 服务器，这个“反向代理”可
以更好地处理传入的请求、 TLS 和其他安全以及性能问题。

httpd 可以用你的系统包管理器安装，在 Windows 下也可以用预编译的可执行
文件安装。安装和运行 httpd 本身不在本文档的讨论范围。本页只是概述代理
你的应用程序的 httpd 的基本配置。请务必阅读 httpd 的文档以了解其具体
可用功能。

.. _Apache httpd: https://httpd.apache.org/


Domain Name
-----------

Acquiring and configuring a domain name is outside the scope of this
doc. In general, you will buy a domain name from a registrar, pay for
server space with a hosting provider, and then point your registrar
at the hosting provider's name servers.

To simulate this, you can also edit your ``hosts`` file, located at
``/etc/hosts`` on Linux. Add a line that associates a name with the
local IP.

Modern Linux systems may be configured to treat any domain name that
ends with ``.localhost`` like this without adding it to the ``hosts``
file.


域名
-----------

如何获取和配置域名不在本文的讨论范围之内。一般来说，你会从注册商那里
购买一个域名，在托管商那里支付服务器空间的费用，然后将你的注册商指向
主机提供商的名称服务器。

为了模拟这一点，也可以编辑你的 ``hosts`` 文件，在文件中添加一行，将名
称与本地 IP 关联。 Linux 系统中这个文件位于 ``/etc/hosts`` 。

现代 Linux 系统中，可以通过配置，将任何以 ``.localhost`` 结尾的域名指
向本地 IP ，而不用修改 ``hosts`` 文件。

.. code-block:: python
    :caption: ``/etc/hosts``

    127.0.0.1 hello.localhost


配置
-------------

Linux 系统中， httpd 的配置位于 ``/etc/httpd/conf/httpd.conf`` 。
不同的系统中，位置可以会不同。具体请查阅文档，并查找 ``httpd.conf`` 。

删除或者注释任何现存的 ``DocumentRoot`` 指令，并添加以下内容。这里假
设 WSGI 服务在本地监听 ``http://127.0.0.1:8000`` 。

.. code-block:: apache
    :caption: ``/etc/httpd/conf/httpd.conf``

    LoadModule proxy_module modules/mod_proxy.so
    LoadModule proxy_http_module modules/mod_proxy_http.so
    ProxyPass / http://127.0.0.1:8000/
    RequestHeader set X-Forwarded-Proto http
    RequestHeader set X-Forwarded-Prefix /

``LoadModule`` 所在行可能已经存在。如果存在，那么请确保它们没有被注释，
不要手动添加。

使用 :doc:`proxy_fix` 可以使你的应用程序使用 ``X-Forwarded`` 头。
``X-Forwarded-For`` 和 ``X-Forwarded-Host`` 由 ``ProxyPass`` 自动设置。
