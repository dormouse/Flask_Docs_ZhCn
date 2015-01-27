.. _tutorial-introduction:

Flaskr 介绍
==================

我们把教程中的博客应用称为 flaskr ，当然你也可以随便取一个没有 web-2.0 气息的
名字  ;)  它的基本功能如下：

1. 让用户可以根据配置文件中的信息登录和注销。只支持一个用户。
2. 用户登录以后可以添加新的博客条目。条目由文本标题和支持 HTML 代码的内容组成。
   因为我们信任用户，所以不对内容中的 HTML 进行净化处理。
3. 页面以倒序（新的在上面）显示所有条目。并且用户登录以后可以在这个页面添加新
   的条目。

我们直接在应用中使用 SQLite3 ，因为在这种规模的应用中 SQlite3 已经够用了。如果
是大型应用，那么就有必要使用能够好的处理数据库连接的 `SQLAlchemy`_ 了，它可以
同时对应多种数据库，并做其他更多的事情。如果你的数据更适合使用 NoSQL 数据库，
那么也可以考虑使用某种流行的 NoSQL 数据库。

这是教程应用完工后的截图：

.. image:: ../_static/flaskr.png
   :align: center
   :class: screenshot
   :alt: screenshot of the final application

下面请阅读 :ref:`tutorial-folders` 。

.. _SQLAlchemy: http://www.sqlalchemy.org/

