.. _patterns:

Flask 方案
==================

有一些东西是大多数网络应用都会用到的。比如许多应用都会使用关系型数据库和用户
验证，在请求之前连接数据库并得到当前登录用户的信息，在请求之后关闭数据库连接。

更多用户贡献的代码片断和方案参见 `Flask 代码片断归档
<http://flask.pocoo.org/snippets/>`_ 。

.. toctree::
   :maxdepth: 2

   packages
   appfactories
   appdispatch
   apierrors
   urlprocessors
   distribute
   fabric
   sqlite3
   sqlalchemy
   fileuploads
   caching
   viewdecorators
   wtforms
   templateinheritance
   flashing
   jquery
   errorpages
   lazyloading
   mongokit
   favicon
   streaming
   deferredcallbacks
   methodoverrides
   requestchecksum
   celery
