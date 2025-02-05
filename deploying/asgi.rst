ASGI
====

如果您想使用 ASGI 服务器，那么将需要利用 WSGI 作为 ASGI 中间件。
推荐使用 asgiref
`WsgiToAsgi <https://github.com/django/asgiref#wsgi-to-asgi-adapter>`_
适配器，因为它与用于 Flask 的 :ref:`async_await` 支持的事件循环相集成。
您可以通过包裹 Flask 应用的方式使用适配器。


.. code-block:: python

    from asgiref.wsgi import WsgiToAsgi
    from flask import Flask

    app = Flask(__name__)

    ...

    asgi_app = WsgiToAsgi(app)

并且用 ASGI 服务器为 ``asgi_app`` 提供服务。例如使用
`Hypercorn <https://github.com/pgjones/hypercorn>`_ 。

.. sourcecode:: text

    $ hypercorn module:asgi_app
