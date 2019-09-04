.. rst-class:: hide-header

.. rst-class:: hide-header

欢迎来到 Flask 的世界
=====================

.. image:: _static/flask-logo.png
    :alt: Flask: web development, one drop at a time
    :align: center
    :target: https://palletsprojects.com/p/flask/

欢迎阅读 Flask 的文档。推荐您先阅读《 :ref:`installation` 》，然后阅读
《 :ref:`quickstart` 》。《 :ref:`tutorial` 》比快速上手文档更详细一点，该
文档介绍了如何创建一个完整（尽管很小）的 Flask 应用。 《 :ref:`patterns` 》
中介绍了一些常用的解决方案。其余的文档详细介绍了 Flask 的每一个组件。
《 :ref:`api` 》提供了最详细的参考。

Flask 依赖 `Jinja`_ 模板引擎和 `Werkzeug`_ WSGI 套件。这两个库的文档请移步：

- `Jinja 文档 <http://jinja.pocoo.org/docs>`_
- `Werkzeug 文档 <https://werkzeug.palletsprojects.com/>`_

.. _Jinja: https://www.palletsprojects.com/p/jinja/
.. _Werkzeug: https://www.palletsprojects.com/p/werkzeug/


用户指南
--------

这部分文档是比较松散的，首先介绍了 Flask 的一些背景材料，
然后专注于一步一步地说明如何使用 Flask 进行 Web 开发。

.. toctree::
   :maxdepth: 2

   foreword
   advanced_foreword
   installation
   quickstart
   tutorial/index
   templating
   testing
   errorhandling
   logging
   config
   signals
   views
   appcontext
   reqcontext
   blueprints
   extensions
   cli
   server
   shell
   patterns/index
   deploying/index
   becomingbig

API 参考
-------------

这部分文档详细说明某个函数、类或方法。

.. toctree::
   :maxdepth: 2

   api

其他材料
----------------

这部分文档包括：设计要点、法律信息和变动记录。

.. toctree::
   :maxdepth: 2

   design
   htmlfaq
   security
   unicode
   extensiondev
   styleguide
   upgrading
   changelog
   license
   contributing

