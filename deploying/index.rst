.. _deployment:

部署方式
==================

虽然轻便且易于使用，但是 **Flask 的内建服务器不适用于生产** ，它也不能很好
的扩展。本文主要说明在生产环境下正确使用 Flask 的一些方法。

如果想要把 Flask 应用部署到这里没有列出的 WSGI 服务器，请查询其文档中关于
如何使用 WSGI 的部分，只要记住： :class:`Flask` 应用对象实质上是一个 WSGI
应用。

托管选项
--------------

托管于：

- `Heroku <https://devcenter.heroku.com/articles/getting-started-with-python>`_
- `OpenShift <https://developers.openshift.com/en/python-flask.html>`_
- `Webfaction <http://flask.pocoo.org/snippets/65/>`_
- `Google App Engine <https://cloud.google.com/appengine/docs/standard/python/getting-started/python-standard-env>`_
- `AWS Elastic Beanstalk <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html>`_
- `Localtunnel <http://flask.pocoo.org/snippets/89/>`_
- `Azure (IIS) <https://azure.microsoft.com/documentation/articles/web-sites-python-configure/>`_
- `PythonAnywhere <https://help.pythonanywhere.com/pages/Flask/>`_

自主部署选项
-------------------

.. toctree::
   :maxdepth: 2

   wsgi-standalone
   uwsgi
   mod_wsgi
   fastcgi
   cgi
