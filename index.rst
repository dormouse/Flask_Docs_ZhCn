.. rst-class:: hide-header

欢迎来到 Flask 的世界
=====================

.. image:: _static/flask-horizontal.png
    :align: center

欢迎阅读 Flask 文档。Flask 是一个轻量级 WSGI 网络应用框架，旨在让用户
快速、轻松上手，并能扩展到复杂的应用程序。

推荐您先从《 :doc:`installation` 》入手，然后阅读
《 :doc:`quickstart` 》。更详细一些的《 :doc:`tutorial/index` 》介绍
了如何创建一个完整（尽管很小）的 Flask 应用。《 :doc:`patterns/index` 》
中介绍了一些常用的解决方案。其余的文档详细介绍了 Flask 的每一个组件。
《 :doc:`api` 》提供了最详细的参考。

Flask 依赖 `Werkzeug`_ WSGI 套件、 `Jinja`_ 模板引擎和 `Click`_ CLI 套
件。查找信息时请不要忘了查阅它们的文档。

.. _Werkzeug: https://werkzeug.palletsprojects.com
.. _Jinja: https://jinja.palletsprojects.com
.. _Click: https://click.palletsprojects.com


用户指南
--------

Flask 提供了配置和约定，以及合理的默认值，以开始使用。文档的这一部分
解释了 Flask 框架的不同部分以及如何使用、定制和扩展。除了 Flask 本身，
社区维护的扩展可以添加更多功能。

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   tutorial/index
   templating
   testing
   errorhandling
   debugging
   logging
   config
   signals
   views
   lifecycle
   appcontext
   reqcontext
   blueprints
   extensions
   cli
   server
   shell
   patterns/index
   web-security
   deploying/index
   async-await


API 参考
-------------

这部分文档详细说明某个函数、类或方法。

.. toctree::
   :maxdepth: 2

   api

其他材料
----------------

.. toctree::
   :maxdepth: 2

   design
   extensiondev
   contributing
   license
   changes

