.. _deployment:

部署方式
==================

Flask 应用可以采用多种方式部署。在开发时，你可以使用内置的服务器，但是在生产环境
下你就应当选择功能完整的服务器。下面为你提供几个可用的选择。

除了下面提到的服务器之外，如果你使用了其他的 WSGI 服务器，那么请阅读其文档中与
使用 WSGI 应用相关的部分。因为 :class:`Flask` 应用对象的实质就是一个 WSGI 应用。

如果需要快速体验，请参阅《快速上手》中的 :ref:`quickstart_deployment` 。

.. toctree::
   :maxdepth: 2

   mod_wsgi
   wsgi-standalone
   uwsgi
   fastcgi
   cgi

