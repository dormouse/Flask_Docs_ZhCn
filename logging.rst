日志
=======

Flask 使用标准 Python :mod:`logging` 。所有与 Flask 相关的消息都用
:meth:`app.logger <flask.Flask.logger>` 来记录，其名称与
:attr:`app.name <flask.Flask.name>` 相同。这个日志记录器也可用于你自己
的日志记录。

.. code-block:: python

    @app.route('/login', methods=['POST'])
    def login():
        user = get_user(request.form['username'])

        if user.check_password(request.form['password']):
            login_user(user)
            app.logger.info('%s logged in successfully', user.username)
            return redirect(url_for('index'))
        else:
            app.logger.info('%s failed to log in', user.username)
            abort(401)

如果您没有配置日志， Python 的默认日志级别一般是“ warning ”。低于配
置的日志级别的日志是不可见的。


基本配置
-------------------

当想要为项目配置日志时，应当在程序启动时尽早进行配置。如果晚了，那么
:meth:`app.logger <flask.Flask.logger>` 就会成为缺省记录器。如果有可能
的话，应当在创建应用对象之前配置日志。

这个例子使用 :func:`~logging.config.dictConfig` 来创建一个类似于 Flask
缺省配置的日志记录配置::

    from logging.config import dictConfig

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    app = Flask(__name__)


缺省配置
````````

如果没有自己配置日志， Flask 会自动添加一个
:class:`~logging.StreamHandler` 到
:meth:`app.logger <flask.Flask.logger>` 。
在请求过程中，它会写到由 WSGI 服务器指定的，保存在
``environ['wsgi.errors']`` 变量中的日志流（通常是 :data:`sys.stderr` ）
中。在请求之外，则会记录到 :data:`sys.stderr` 。


移除缺省配置
````````````

如果在操作 :meth:`app.logger <flask.Flask.logger>` 之后配置日志，并且
需要移除缺省的日志记录器，可以导入并移除它::

    from flask.logging import default_handler

    app.logger.removeHandler(default_handler)


把出错信息通过电子邮件发送给管理者
--------------------------------------------

当产品运行在一个远程服务器上时，可能不会经常查看日志信息。 WSGI 服务器
可能会在一个文件中记录日志消息，而你只会在当用户告诉你出错的时候才会查
看日志文件。

为了主动发现并修复错误，可以配置一个
:class:`logging.handlers.SMTPHandler` ，用于在一般错误或者更高级别错误
发生时发送一封电子邮件::

    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(
        mailhost='127.0.0.1',
        fromaddr='server-error@example.com',
        toaddrs=['admin@example.com'],
        subject='Application Error'
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    if not app.debug:
        app.logger.addHandler(mail_handler)

这需要在同一台服务器上拥有一个 SMTP 服务器。关于配置日志的更多内容请参
阅 Python 文档。


注入请求信息
-----------------------------

看到更多请求信息，如 IP 地址，有助调试某些错误。可以继承
:class:`logging.Formatter` 来注入自己的内容，以显示在日志消息中。然后，
可以修改 Flask 缺省的日志记录器、上文所述的电子邮件日志记录器或者其他
日志记录器的格式器。::

    from flask import has_request_context, request
    from flask.logging import default_handler

    class RequestFormatter(logging.Formatter):
        def format(self, record):
            if has_request_context():
                record.url = request.url
                record.remote_addr = request.remote_addr
            else:
                record.url = None
                record.remote_addr = None

            return super().format(record)

    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )
    default_handler.setFormatter(formatter)
    mail_handler.setFormatter(formatter)


其他库
---------------

其他库可能也会产生大量日志，而你也正好需要查看这些日志。最简单的方法是
向根记录器中添加记录器。::

    from flask.logging import default_handler

    root = logging.getLogger()
    root.addHandler(default_handler)
    root.addHandler(mail_handler)

单独配置每个记录器更好还是只配置一个根记录器更好，取决你的项目。::

    for logger in (
        logging.getLogger(app.name),
        logging.getLogger('sqlalchemy'),
        logging.getLogger('other_package'),
    ):
        logger.addHandler(default_handler)
        logger.addHandler(mail_handler)


Werkzeug
````````

Werkzeug 记录基本的请求/响应信息到 ``'werkzeug'`` 日志记录器。如果根记
录器没有配置，那么 Werkzeug 会向记录器添加一个
:class:`~logging.StreamHandler` 。 

Flask 扩展
````````````````

根据情况不同，一个扩展可能会选择记录到
:meth:`app.logger <flask.Flask.logger>` 或者其自己的日志记录器。具体请
查阅扩展的文档。
