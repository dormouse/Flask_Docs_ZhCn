.. _deployment:


生产部署
==================

应用开发完成以后，需要把它提供给用户使用。当你在本地开发时，可以会使用
内置的开发服务器，调试器和重载器。但是这些不应该在生产环境下使用。相
反，你应该使用专业的 WSGI 服务器或者托管平台。这里作个简单介绍。

“生产”意味着“不是开发”，这条规则适用于无论你是为数以百万计的用户
公开提供应用程序，还是在本地为单个用户私下提供服务。 **在生产部署时，
不要使用开发服务器。开发服务器只适用于在本地开发，它不安全、不稳定也不
高效。**


自主部署选项
--------------

Flask 是一个 WSGI *应用* 。一个 WSGI *服务器* 被用来运行应用，将传入的
HTTP 请求转换为标准的 WSGI 响应，并将流出的 WSGI 响应转换为 HTTP 响应。

以下文档的主要目标是让你熟悉使用生产 WSGI 服务器运行 WSGI 应用程序所
涉及的概念。
WSGI 服务器和 HTTP 服务器多种多样，有很多配置的可能性。
下面的页面讨论了最常见的服务器，并展示了运行每个服务器的基础知识。
下一节将讨论可以为你管理这些服务器的平台。

.. toctree::
    :maxdepth: 1

    gunicorn
    waitress
    mod_wsgi
    uwsgi
    gevent
    eventlet
    asgi

WSGI 服务器包含内置的 HTTP 服务器。但是专业的 HTTP 服务器会可能更快，
更有效或者更强大。在 WSGI 服务器前面设置一个 HTTP 服务器，我们称之为
“反向代理”。
 

.. toctree::
    :maxdepth: 1

    proxy_fix
    nginx
    apache-httpd

这个列表并不详尽，你应该根据应用需求评估这些和其他的服务器，不同的服
务器有不同的能力、配置和支持。


托管平台
-----------------

有许多托管平台提供网络服务，不需要你维护自己的服务器、网络、域名等。
一些托管平台可能会提供一定的免费使用时间或者带宽。其中许多都使用上述
的 WSGI 服务器之一，或类似的接口。下面的链接是一些最常见的托管平台，
有针对 Flask 、 WSGI 或 Python 的说明。

- `PythonAnywhere <https://help.pythonanywhere.com/pages/Flask/>`_
- `Google App Engine <https://cloud.google.com/appengine/docs/standard/python3/building-app>`_
- `Google Cloud Run <https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service>`_
- `AWS Elastic Beanstalk <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html>`_
- `Microsoft Azure <https://docs.microsoft.com/en-us/azure/app-service/quickstart-python>`_

这个列表并不详尽，你应该根据应用需求评估这些和其他的服务器，不同的平
台有不同的功能、配置、价格和支持。

当使用大多数平台前，你可能需要先阅读 :doc:`proxy_fix` 。
