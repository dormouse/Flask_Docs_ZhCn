基于 Celery 的后台任务
=============================

如果应用有一个长时间运行的任务，如处理上传数据或者发送电子邮件，而你不想在
请求中等待任务结束，那么可以使用任务队列发送必须的数据给另一个进程。这样就
可以在后台运行任务，立即返回请求。

Celery 是强大的任务队列库，它可以用于简单的后台任务，也可用于复杂的多阶段
应用的计划。本文主要说明如何在 Flask 中配置使用 Celery 。本文假设你
已经阅读过了其官方文档中的 `Celery 入门
<https://celery.readthedocs.io/en/latest/getting-started/first-steps-with-celery.html>`_ 。


安装
-----------------

Celery 是一个独立的 Python 包。使用 pip 从 PyPI 安装::

    $ pip install celery

配置
------------------

你首先需要有一个 Celery 实例，这个实例称为 celery 应用。其地位就相当于
Flask 中 :class:`~flask.Flask` 一样。这个实例被用作所有 Celery 相关事务的
入口，如创建任务和管理工人，因此它必须可以被其他模块导入。

例如，你可以把它放在一个 ``tasks`` 模块中。这样不需要重新配置，你就可以使用
tasks 的子类，增加 Flask 应用情境的支持，并钩接 Flask 的配置。

只要如下这样就可以在 Falsk 中使用 Celery 了::

    from celery import Celery

    def make_celery(app):
        celery = Celery(
            app.import_name,
            backend=app.config['CELERY_RESULT_BACKEND'],
            broker=app.config['CELERY_BROKER_URL']
        )
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask
        return celery

这个函数创建了一个新的 Celery 对象，使用了应用配置中的 broker ，并从 Flask
配置中更新了 Celery 的其余配置。然后创建了一个任务子类，在一个应用情境中包
装了任务执行。

一个示例任务
---------------

让我们来写一个任务，该任务把两个数字相加并返回结果。我们配置 Celery 的
broker ，后端使用 Redis 。使用上文的工厂创建一个 ``celery`` 应用，并用它定
义任务。::

    from flask import Flask

    flask_app = Flask(__name__)
    flask_app.config.update(
        CELERY_BROKER_URL='redis://localhost:6379',
        CELERY_RESULT_BACKEND='redis://localhost:6379'
    )
    celery = make_celery(flask_app)

    @celery.task()
    def add_together(a, b):
        return a + b

这个任务现在可以在后台调用了::

    result = add_together.delay(23, 42)
    result.wait()  # 65

运行 Celery 工人
-------------------------

至此，如果你已经按上文一步一步执行，你会失望地发现你的 ``.wait()`` 不会真正
返回。这是因为还需要运行一个 Celery 工人来接收和执行任务。::

    $ celery -A your_application.celery worker

把 ``your_application`` 字符串替换为你创建 `celery` 对像的应用包或模块。

现在工人已经在运行中，一旦任务结束， ``wait`` 就会返回结果。
