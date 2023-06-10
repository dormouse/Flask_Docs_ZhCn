使用 Celery 的后台任务
============================

如果你的应用有一个长时间运行的任务，比如处理上传数据或者发送电子邮件，
而你又不希望在请求中等待任务结束，那么可以使用任务队列发送必须的数据
给另一个进程。这样就可以在后台运行任务，立即返回请求。

`Celery`_ 是强大的任务队列库，它可以用于简单的后台任务，也可用于复杂
的多阶段应用和时间表。本文主要说明如何在 Flask 中配置使用 Celery 。本
文假设你已经阅读过了其官方文档中的 `Celery 入门`_

.. _Celery: https://celery.readthedocs.io
.. _Celery 入门: https://celery.readthedocs.io/en/latest/getting-started/first-steps-with-celery.html

Flask 仓库包含基于本文的
`例子 <https://github.com/pallets/flask/tree/main/examples/celery>`_
。该例子还展示了如何使用 JavaScript 来提交任务，并对进度和结果进行投
票。


安装
-----------------

从 PyPI 安装 Celery ，下面使用 pip 示例：

.. code-block:: text

    $ pip install celery


整合 Celery 与 Flask
---------------------------

你可以在不与 Flask 整合的情况下使用 Celery ，但是通过 Flask 的配置来
使用它，并让任务访问 Flask 应用是很方便的。

Celery 与 Flask 类似，有一个 ``Celery`` 应用对象，它有配置和注册任务。
在创建 Flask 应用的同时，使用下面的代码来创建和配置一个 Celery 应用。

.. code-block:: python

    from celery import Celery, Task

    def celery_init_app(app: Flask) -> Celery:
        class FlaskTask(Task):
            def __call__(self, *args: object, **kwargs: object) -> object:
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery_app = Celery(app.name, task_cls=FlaskTask)
        celery_app.config_from_object(app.config["CELERY"])
        celery_app.set_default()
        app.extensions["celery"] = celery_app
        return celery_app

这将创建并返回一个 ``Celery`` 应用程序对象。Celery `configuration`_
取自 Flask 配置中的 ``CELERY`` 键。 Celery 应用程序被设置为默认的，因
此在每次请求时都能看到它。 当 Flask 应用情境激活时， ``Task`` 子类自
动运行任务函数，使得像数据库连接这样的服务是可用的。

.. _configuration: https://celery.readthedocs.io/en/stable/userguide/configuration.html

这里有一个基本的 ``example.py`` ，它将 Celery 配置为使用 Redis 进行通
信。我们启用了一个结果后端，但默认情况下忽略结果。这使得我们可以只在
需要时才存储结果。

.. code-block:: python

    from flask import Flask

    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    celery_app = celery_init_app(app)

把 ``celery worker`` 命令指向这里，它将找到 ``celery_app`` 对象。

.. code-block:: text

    $ celery -A example worker --loglevel INFO

You can also run the ``celery beat`` command to run tasks on a schedule. See Celery's
docs for more information about defining schedules.

.. code-block:: text

    $ celery -A example beat --loglevel INFO

你也可以运行 ``celery beat`` 命令来按计划运行任务。关于定义时间表的更
多信息，请参阅 Celery 的文档。

.. code-block:: text

    $ celery -A example beat --loglevel INFO


应用工厂
-------------------

当使用 Flask 应用工厂模式时，应在工厂内部调用 ``celery_init_app``
函数。这将 ``app.extensions["celery"]`` 设置为 Celery 应用对象。该
对象可用于从 Flask 应用中获取 Celery 应用，这里的 Flask 应用是从工厂
返回的。

.. code-block:: python

    def create_app() -> Flask:
        app = Flask(__name__)
        app.config.from_mapping(
            CELERY=dict(
                broker_url="redis://localhost",
                result_backend="redis://localhost",
                task_ignore_result=True,
            ),
        )
        app.config.from_prefixed_env()
        celery_init_app(app)
        return app

为了使用 ``celery`` 命令， Celery 需要一个 app 对象，但该对象不再是直
接可用的。需要创建一个 ``make_celery.py`` 文件，调用 Flask 应用工厂并
从返回的 Flask 应用中获取 Celery 应用。

.. code-block:: python

    from example import create_app

    flask_app = create_app()
    celery_app = flask_app.extensions["celery"]

把 ``celery`` 命令指向这个文件。

.. code-block:: text

    $ celery -A make_celery worker --loglevel INFO
    $ celery -A make_celery beat --loglevel INFO


定义任务
--------------

使用 ``@celery_app.task`` 来装饰任务函数需要访问 ``celery_app`` 对象。
而在使用工厂模式时，该对象是不可用的。这也意味着被装饰的任务与特定的
Flask 和 Celery 应用实例绑定，在测试过程中，如果你改变测试的配置，这
可能是一个问题。

相反，应当使用Celery的 ``@shared_task`` 装饰器。这将创建访问任意“当
前应用”的任务对象，这是一个类似于 Flask 的蓝图和应用情境的概念。这就
是为什么我们在上面调用 ``celery_app.set_default()`` 的原因。

下面是一个将两个数字相加并返回结果的任务实例。

.. code-block:: python

    from celery import shared_task

    @shared_task(ignore_result=False)
    def add_together(a: int, b: int) -> int:
        return a + b

早些时候，我们将 Celery 配置为默认忽略任务结果。现在由于我们想知道这
个任务的返回值，于是设置 ``ignore_result=False`` 。另一方面，如果一个
任务不需要结果，例如发送电子邮件，就不需要这样设置。


调用任务
-------------

被装饰函数会成为一个任务对象，具有在后台调用它的方法。最简单的方式是
使用 ``delay(*args, **kwargs)`` 方法。更多方法参见 Celery 的文档。

必须有一个 Celery 工作者正在运行才能运行任务。如何启动一个工作者在前
面的章节已描述。

.. code-block:: python

    from flask import request

    @app.post("/add")
    def start_add() -> dict[str, object]:
        a = request.form.get("a", type=int)
        b = request.form.get("b", type=int)
        result = add_together.delay(a, b)
        return {"result_id": result.id}

路由并没有立即得到任务的结果。否则将阻断响应，无法达到我们的目的。
相反，我们应当返回正在运行的任务的结果 ID ，用 ID 来获取结果。


获取结果
---------------

为了获取我们上面启动的任务的结果，我们将添加另一个路由，该路由接收之
前返回的结果 ID ，返回任务是否已经完成（准备好），是否成功完成，如果
完成，那么返回值（或错误）是什么。

.. code-block:: python

    from celery.result import AsyncResult

    @app.get("/result/<id>")
    def task_result(id: str) -> dict[str, object]:
        result = AsyncResult(id)
        return {
            "ready": result.ready(),
            "successful": result.successful(),
            "value": result.result if result.ready() else None,
        }

现在你可以使用第一个路由启动任务，然后使用第二个路由轮询结果。这使得
Flask 的请求工作者不会因为等待任务的完成而被阻塞。

Flask 仓库包含一个
`例子 <https://github.com/pallets/flask/tree/main/examples/celery>`_
，该例子使用 JavaScript 来提交任务并轮询进度和结果。


传递数据给任务
---------------------

上面的“ add ”任务需要两个整数作为参数。为了向任务传递参数， Celery
必须把它们序列化为可以传递给其他进程的格式。因此不建议传递复杂的对象。
例如，不可能传递一个 SQLAlchemy 模型对象，因为该对象基本是不可序列化
的，并且还与查询它的会话相绑定。

请在任务中传递必须的最小数据量，然后通过这些数据获取或重新其他复杂数
据。假设有这样一个任务，当已登录的用户要求对他们的数据进行归档时，该
任务将运行。 Flask 请求知道已登录的用户，并从数据库中查询到用户对象。
它是通过查询数据库中的一个给定 id 得到的，所以任务可以做同样的事情。
因此，传递用户的 id 优于传递用户对象。

.. code-block:: python

    @shared_task
    def generate_user_archive(user_id: str) -> None:
        user = db.session.get(User, user_id)
        ...

    generate_user_archive.delay(current_user.id)
