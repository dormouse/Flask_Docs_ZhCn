.. _tutorial-folders:

步骤 0 ：创建文件夹
============================

在开始之前需要为应用创建下列文件夹::

    /flaskr
        /flaskr
            /static
            /templates

本教程中的应用会以 Python 包的方式来安装和运行。我们推荐各位以 Python 包的方式来安装和运行
Flask 应用。在后面的教程中，可以学习如何运行 ``flaskr`` 应用。现在，我们首先创建应用所在的
文件夹，学习一下基本的应用结构。在接下来的几个步骤中，将会学习创建数据库模式和主模块。

简要说明一下， :file:`static` 文件夹中的文件是用于供用户通过 `HTTP` 访问的文件，主要是 CSS
和 Javascript 文件。 Flask 将会在 :file:`templates` 文件夹中搜索应用的模板， Flask 所
使用的模板都是用 `Jinja2`_ 编写的。在后面教程中将会学习如何写模板。

下面请阅读 :ref:`tutorial-schema` 。

.. _Jinja2: http://jinja.pocoo.org/
