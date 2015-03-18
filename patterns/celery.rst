基于 Celery 的后台任务
=============================

Celery 是一个 Python 编写的是一个异步任务队列/基于分布式消息传递的作业队列。
以前它有一个 Flask 的集成，但是从版本 3 开始，它进行了一些内部的重构，已经
不需要这个集成了。本文主要说明如何在 Flask 中正确使用 Celery 。本文假设你
已经阅读过了其官方文档中的 `Celery 入门
<http://docs.celeryproject.org/en/master/getting-started/first-steps-with-celery.html>`_

安装 Celery
-----------------

Celery 在 Python 包索引（ PyPI ）上榜上有名，因此可以使用 ``pip`` 或
``easy_install`` 之类标准的 Python 工具来安装::

    $ pip install celery

配置 Celery
------------------

你首先需要有一个 Celery 实例，这个实例称为 celery 应用。其地位就相当于 Flask 中
:class:`~flask.Flask` 一样。这个实例被用作所有 Celery 相关事务的入口，例如创建
任务、管理工人等等。因此它必须可以被其他模块导入。

例如，你可以把它放在一个 ``tasks`` 模块中。这样不需要重新配置，你就可以使用
tasks 的子类，增加 Flask 应用环境的支持，并钩接 Flask 的配置。

只要如下这样就可以在 Falsk 中使用 Celery 了::

    from celery import Celery

    def make_celery(app):
        celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
        celery.conf.update(app.config)
        TaskBase = celery.Task
        class ContextTask(TaskBase):
            abstract = True
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
        celery.Task = ContextTask
        return celery

这个函数创建了一个新的 Celery 对象，使用了应用配置中的 broker ，并从 Flask 配置
中升级了 Celery 的其余配置。然后创建了一个任务子类，在一个应用环境中包装了任务
执行。

最小的例子
---------------

基于上文，以下是一个在 Flask 中使用 Celery 的最小例子::

    from flask import Flask

    app = Flask(__name__)
    app.config.update(
        CELERY_BROKER_URL='redis://localhost:6379',
        CELERY_RESULT_BACKEND='redis://localhost:6379'
    )
    celery = make_celery(app)


    @celery.task()
    def add_together(a, b):
        return a + b

这个任务现在可以在后台调用了：

>>> result = add_together.delay(23, 42)
>>> result.wait()
65

运行 Celery 工人
-------------------------

至此，如果你已经按上文一步一步执行，你会失望地发现你的 ``.wait()`` 不会真正
返回。这是因为你还没有运行 celery 。你可以这样以工人方式运行 celery::

    $ celery -A your_application worker

把 ``your_application`` 字符串替换为你创建 `celery` 对像的应用包或模块。
