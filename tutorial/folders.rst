.. _tutorial-folders:

步骤 0 ：创建文件夹
============================

在开始之前需要为应用创建下列文件夹::

    /flaskr
        /static
        /templates

`flaskr` 文件夹不是一个 Python 包，只是一个用来存放我们文件的地方。我们将把以后
要用到的数据库模式和主模块放在这个文件夹中。 `static` 文件夹中的文件是用于供
应用用户通过 `HTTP` 访问的文件，主要是 CSS 和 javascript 文件。 Flask 将会在
`templates` 文件夹中搜索 `Jinja2`_ 模板，所有在教程中的模板都放在
`templates` 文件夹中。

下面请阅读 :ref:`tutorial-schema` 。

.. _Jinja2: http://jinja.pocoo.org/2/
