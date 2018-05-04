.. _tutorial:

教程
========

.. toctree::
    :caption: Contents:
    :maxdepth: 1

    layout
    factory
    database
    views
    templates
    static
    blog
    install
    tests
    deploy
    next

本教程中我们将会创建一个名为 Flaskr 的具备基本功能的博客应用。应用用户可以
注册、登录、发贴和编辑或者删除自己的帖子。可以打包这个应用并且安装到其他电脑
上。

.. image:: flaskr_index.png
    :align: center
    :class: screenshot
    :alt: screenshot of index page

本文假设你已经熟悉 Python 。
不熟悉？那么建议先从学习或者复习 Python 文档的 `官方教程`_ 入手。

.. _官方教程: https://docs.python.org/3/tutorial/

本教程的目的是提供一个良好的起点，因此不会涵盖 Flask 的所有内容。如果想了解
Flask 能够做什么，可以通过 :ref:`quickstart` 作一个大概的了解，想深入了解的
话那就只有仔细阅读所有文档了。本教程只会涉及 Flask 和 Python 。在实际项目中
可以通过使用 :ref:`extensions` 或者其他的库，达到事半功倍的效果。

.. image:: flaskr_login.png
    :align: center
    :class: screenshot
    :alt: screenshot of login page

Flask 是非常灵活的，不需要使用任何特定的项目或者代码布局。但是对于初学者，
使用结构化的方法是有益无害的，亦即本教程会有一点样板的意思。本教程可以让
初学者避免一些常见的陷阱，并且完成后的应用可以方便的扩展。一旦熟悉了
Flask 之后就可以跳出这个结构，充分享受 Flask 的灵活性。

.. image:: flaskr_edit.png
    :align: center
    :class: screenshot
    :alt: screenshot of login page

:gh:`The tutorial project is available as an example in the Flask
repository <examples/tutorial>`, if you want to compare your project
with the final product as you follow the tutorial.

下面请阅读 :doc:`layout`.
