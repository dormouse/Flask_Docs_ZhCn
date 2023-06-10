Flask 方案
==================

一些功能和交互是大多数网络应用都会用到的。比如许多应用都会使用关系型
数据库和用户验证，在请求之前连接数据库并得到当前登录用户的信息，在请
求之后关闭数据库连接。

这些方案有些超出 Flask 自身的范围了，但是 Flask 可以方便的实现这些方
案。以下是一些常见的方案：

.. toctree::
   :maxdepth: 2

   packages
   appfactories
   appdispatch
   urlprocessors
   sqlite3
   sqlalchemy
   fileuploads
   caching
   viewdecorators
   wtforms
   templateinheritance
   flashing
   javascript
   lazyloading
   mongoengine
   favicon
   streaming
   deferredcallbacks
   methodoverrides
   requestchecksum
   celery
   subclassing
   singlepageapplications
