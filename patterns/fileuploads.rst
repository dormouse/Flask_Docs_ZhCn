.. _uploading-files:

上传文件
===============

是的，这里要谈的是一个老问题：文件上传。文件上传的基本原理实际上很简单，基本上
是：

1. 一个带有 ``enctype=multipart/form-data`` 的 ``<form>`` 标记，标记中含有
   一个 ``<input type=file>`` 。
2. 应用通过请求对象的 :attr:`~flask.request.files` 字典来访问文件。
3. 使用文件的 :meth:`~werkzeug.datastructures.FileStorage.save` 方法把文件永久
   地保存在文件系统中。

简介
---------------------

让我们从一个基本的应用开始，这个应用上传文件到一个指定目录，并把文件显示给用户。
以下是应用的引导代码::

    import os
    from flask import Flask, request, redirect, url_for
    from werkzeug import secure_filename

    UPLOAD_FOLDER = '/path/to/the/uploads'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

首先我们导入了一堆东西，大多数是浅显易懂的。:func:`werkzeug.secure_filename` 会
在稍后解释。`UPLOAD_FOLDER` 是上传文件要储存的目录，`ALLOWED_EXTENSIONS` 是允许
上传的文件扩展名的集合。接着我们给应用手动添加了一个 URL 规则。一般现在不会做
这个，但是为什么这么做了呢？原因是我们需要服务器（或我们的开发服务器）为我们提供
服务。因此我们只生成这些文件的 URL 的规则。

为什么要限制文件件的扩展名呢？如果直接向客户端发送数据，那么你可能不会想让用户
上传任意文件。否则，你必须确保用户不能上传 HTML 文件，因为 HTML 可能引起 XSS
问题（参见 :ref:`xss` ）。如果服务器可以执行 PHP 文件，那么还必须确保不允许上传
`.php` 文件。但是谁又会在服务器上安装 PHP 呢，对不？  :)

下一个函数检查扩展名是否合法，上传文件，把用户重定向到已上传文件的 URL::

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('uploaded_file',
                                        filename=filename))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''

那么 :func:`~werkzeug.utils.secure_filename` 函数到底是有什么用？有一条原则是“
永远不要信任用户输入”。这条原则同样适用于已上传文件的文件名。所有提交的表单数据
可能是伪造的，文件名也可以是危险的。此时要谨记：在把文件保存到文件系统之前总是要
使用这个函数对文件名进行安检。

.. admonition:: 进一步说明

   你可以会好奇 :func:`~werkzeug.utils.secure_filename` 做了哪些工作，如果不使用
   它会有什么后果。假设有人把下面的信息作为 `filename` 传递给你的应用::

      filename = "../../../../home/username/.bashrc"

   假设 ``../`` 的个数是正确的，你会把它和 `UPLOAD_FOLDER` 结合在一起，那么用户
   就可能有能力修改一个服务器上的文件，这个文件本来是用户无权修改的。这需要了解
   应用是如何运行的，但是请相信我，黑客都是病态的 :)

   现在来看看函数是如何工作的：

   >>> secure_filename('../../../../home/username/.bashrc')
   'home_username_.bashrc'

现在还剩下一件事：为已上传的文件提供服务。 Flask 0.5 版本开始我们可以使用一个
函数来完成这个任务::

    from flask import send_from_directory

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename)

另外，可以把 `uploaded_file` 注册为 `build_only` 规则，并使用
:class:`~werkzeug.wsgi.SharedDataMiddleware` 。这种方式可以在 Flask 老版本中
使用::

    from werkzeug import SharedDataMiddleware
    app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                     build_only=True)
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/uploads':  app.config['UPLOAD_FOLDER']
    })

如果你现在运行应用，那么应该一切都应该按预期正常工作。


改进上传
-----------------

.. versionadded:: 0.6

Flask 到底是如何处理文件上传的呢？如果上传的文件很小，那么会把它们储存在内存中。
否则就会把它们保存到一个临时的位置（通过 :func:`tempfile.gettempdir` 可以得到
这个位置）。但是，如何限制上传文件的尺寸呢？缺省情况下， Flask 是不限制上传文件
的尺寸的。可以通过设置配置的 ``MAX_CONTENT_LENGTH`` 来限制文件尺寸::

    from flask import Flask, Request

    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

上面的代码会把尺寸限制为 16 M 。如果上传了大于这个尺寸的文件， Flask 会抛出一个
:exc:`~werkzeug.exceptions.RequestEntityTooLarge` 异常。

Flask 0.6 版本中添加了这个功能。但是通过继承请求对象，在较老的版本中也可以实现
这个功能。更多信息请参阅 Werkzeug 关于文件处理的文档。


上传进度条
--------------------

在不久以前，许多开发者是这样实现上传进度条的：分块读取上传的文件，在数据库中储存
上传的进度，然后在客户端通过 JavaScript 获取进度。简而言之，客户端每 5 秒钟向
服务器询问一次上传进度。觉得讽刺吗？客户端在明知故问。

现在有了更好的解决方案，更快且更可靠。网络发生了很大变化，你可以在客户端使用
HTML5 、 JAVA 、 Silverlight 或 Flash 获得更好的上传体验。请查看以下库，学习
一些优秀的上传的示例：

-   `Plupload <http://www.plupload.com/>`_ - HTML5, Java, Flash
-   `SWFUpload <http://www.swfupload.org/>`_ - Flash
-   `JumpLoader <http://jumploader.com/>`_ - Java


一个更简便的方案
------------------

因为所有应用中上传文件的方案基本相同，因此可以使用 `Flask-Uploads`_ 扩展来实现
文件上传。这个扩展实现了完整的上传机制，还具有白名单功能、黑名单功能以及其他
功能。

.. _Flask-Uploads: http://packages.python.org/Flask-Uploads/
