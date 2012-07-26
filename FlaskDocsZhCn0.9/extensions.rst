Flask 扩展
================

Flask 扩展以各种方式扩展了 Flask 的功能，比如增强对数据库的支持等等。

查找扩展
------------------

Flask 扩展都列在 `Flask 扩展注册`_ 中，并且可以使用 ``easy_install`` 或 ``pip``
下载。如果你把一个扩展作为依赖添加到你的 ``requirements.rst`` 或 ``setup.py``
文件，那么它们可以使用一个简单的命令安装或随着应用一起安装。

使用扩展
----------------

扩展一般都有说明如何使用的文档，这些文档应该和扩展一起发行。扩展如何运行没有
统一的要求，但是一般在常见位置导入扩展。假设一个扩展称为
``Flask-Foo`` 或 ``Foo-Flask`` ，那么总是可以导入 ``flask.ext.foo``::

    from flask.ext import foo

Flask 0.8 以前的版本
--------------------

如果你正在使用 Flask 0.7 版本或更早版本， :data:`flask.ext` 包是不存在的。你
必须根据扩展的发行方式导入 ``flaskext.foo`` 或 ``flask_foo`` 。如果你要开发一个
支持 Flask 0.7 版本或更早版本的应用，那么你应当还是从 :data:`flask.ext` 包中
导入。我们提供了一个兼容模块用以兼容老版本的 Flask ，你可以从 github 下载：
`flaskext_compat.py`_

使用方法如下::

    import flaskext_compat
    flaskext_compat.activate()

    from flask.ext import foo

一旦 ``flaskext_compat`` 模块被激活， :data:`flask.ext` 就会存在，就可以从这个
包导入扩展。

.. _Flask 扩展注册: http://flask.pocoo.org/extensions/
.. _flaskext_compat.py: https://github.com/mitsuhiko/flask/raw/master/scripts/flaskext_compat.py
