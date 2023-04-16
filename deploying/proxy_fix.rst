告诉 Flask 它是在一个代理后面
===============================

当使用反向代理，或许多 Python 托管平台时，代理会拦截并转发所有的外部
请求到本地的 WSGI 服务器。

从 WSGI 服务器和 Flask 应用的角度来看，现在，请求是从 HTTP 服务器到本
地地址，而不是从远程地址到外部服务器地址。

HTTP 服务器应该设置 ``X-Forwarded-`` 头信息，以便将真正的值传递给应用。
然后，应用程序可以被告知信任并使用这些值，方法是将其包裹在由 Werkzeug
提供的 :doc:`werkzeug:middleware/proxy_fix` 中间件中。

只有在应用实际处于代理后面的情况才应该使用这个中间件。并且使用时应该
配置其前面链接的代理数量。不是所有的代理都会设置所有的头部。由于传入
的头部可以被伪造，所以你必须设置有多少个代理在设置头部，这样中间件才
知道该相信什么。

.. code-block:: python

    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

记住，只有在一个代理后面时才使用这个中间件，并设置每个头部的代理的正
确数量。如果你把这个配置弄错了，就会造成安全问题。
