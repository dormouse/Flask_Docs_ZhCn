.. _tutorial:

教程
====

想要用 Python 和 Flask 开发应用吗？让我们通过一个实例来学习。在本教程中我们
将会创建一个微博应用。这个应用只支持单一用户，并且只能创建文本内容，没有订阅
和评论功能。这个应用虽然简单，但是学习之后可以初步掌握 Falsk 的开发。这个应用
只用到了 Flask 自身，并且使用 SQLite 作为数据库（ SQLite 是 Python 自带的），
不依赖其他东西。

如果你想要事先下载完整的源代码或者用于比较，请查看 `示例源代码`_ 。

.. _示例源代码:
   https://github.com/pallets/flask/tree/master/examples/flaskr/

.. toctree::
   :maxdepth: 2

   introduction
   folders
   schema
   setup
   packaging
   dbcon
   dbinit
   views
   templates
   css
   testing
