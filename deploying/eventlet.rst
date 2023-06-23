eventlet
========

与其使用带 eventlet worker 的 :doc:`gunicorn` ，不如直接使用
`eventlet`_ 。 Gunicorn 提供了一个更加可配置并且经过生产测试的服务器。

`eventlet`_ 允许编写异步的，基于协程代码。这些代码看上去就像标准的
Python 协程代码一样。它使用 `greenlet`_ 来实现任务切换，不用写
``async/await`` 或者使用 ``asyncio`` 。

:doc:`gevent` 是另一个功能相同的库。使用两者中的哪一个，取决于某些依赖
性或者其他的因素。

eventlet 提供一个 WSGI 服务器，这个服务器可以同进处理多个连接，而不是
每个工作进行处理一个连接。你必须在自己的代码中使用 eventlet 才能看到使
用该服务器的好处。

.. _eventlet: https://eventlet.net/
.. _greenlet: https://greenlet.readthedocs.io/en/latest/


安装
----------

使用 eventlet ， greenlet 必须大于等于 1.0 ，否则本地情境如
``request`` 将无法正常工作。当使用 PyPy 时， PyPy 必须大于等于
7.3.7 。

创建一个，安装你的应用，然后安装 ``eventlet`` 。

.. code-block:: text

    $ cd hello-app
    $ python -m venv .venv
    $ . .venv/bin/activate
    $ pip install .  # install your application
    $ pip install eventlet


运行
-------

如果要使用 eventlet 服务器，那么要在代码中导入它的 ``wsgi.server`` 。
可以在应用中导入，也可以在应用工厂中导入。

.. code-block:: python
    :caption: ``wsgi.py``

    import eventlet
    from eventlet import wsgi
    from hello import create_app

    app = create_app()
    wsgi.server(eventlet.listen(("127.0.0.1", 8000)), app)

.. code-block:: text

    $ python wsgi.py
    (x) wsgi starting up on http://127.0.0.1:8000


外部绑定
------------------

eventlet 如果作为 root 来运行，那么会导致应用也作为 root 来运行，这样
做是不安全的。然而，如果不以 root 运行，那么就不能绑定 80 或者 443
端口。所以在 eventlet 前应当设置一个反向代理，如 :doc:`nginx` 或者
:doc:`apache-httpd` 。

你可以通过前述的在服务器参数中使用 ``0.0.0.0`` 来把所有外部 IP 绑定到
一个非特权端口。但是当使用反向代理设置时，请不要这么做，否则可以会绕过
代理。

``0.0.0.0`` 不是一个有效的导航地址，你应该在浏览器中使用一个特定的 IP
地址。
