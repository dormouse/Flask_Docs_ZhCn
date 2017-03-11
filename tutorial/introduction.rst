.. _tutorial-introduction:

Flaskr 介绍
===========

本教程会演示开发一个名为 Flaskr 的博客应用，当然你也可以随便取一个没有 web-2.0
气息的名字  ;)  它的基本功能如下：

1. 让用户可以根据配置文件中的信息登录和注销。只支持一个用户。
2. 用户登录以后可以添加新的博客条目。条目由文本标题和支持 HTML 代码的内容组成。
   因为我们信任用户，所以不对内容中的 HTML 进行净化处理。
3. 页面以倒序（新的在上面）显示所有条目。并且用户登录以后可以在这个页面添加新
   的条目。

因为应用的规模很小，所以我们在应用中直接使用 SQLite3 。
如果应用的规模比较大，那么直接操作数据库就不合适了，建议使用 `SQLAlchemy`_
来操作数据库，因为其可以更好地管理数据库，并且可以同时对应多种数据库。如果
你的数据更适合使用 NoSQL 数据库，那么也可以考虑使用某种流行的 NoSQL 数据库。

这是教程应用完工后的截图：

.. image:: ../_static/flaskr.png
   :align: center
   :class: screenshot
   :alt: screenshot of the final application

下面请阅读 :ref:`tutorial-folders` 。

.. _SQLAlchemy: http://www.sqlalchemy.org/

