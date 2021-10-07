通过 jQuery 使用 AJAX
=====================

`jQuery`_ 是一个小型的 JavaScript 库，通常用于简化 DOM 和 JavaScript 的使
用。它是一个非常好的工具，可以通过在服务端和客户端交换 JSON 来使网络应用更
具有动态性。

JSON 是一种非常轻巧的传输格式，非常类似于 Python 原语（数字、字符串、字典
和列表）。 JSON 被广泛支持，易于解析。 JSON 在几年之前开始流行，在网络应用
中迅速取代了 XML 。

.. _jQuery: https://jquery.com/

载入 jQuery
--------------

为了使用 jQuery ，你必须先把它下载下来，放在应用的静态目录中，并确保它被载
入。理想情况下你有一个用于所有页面的布局模板。在这个模板的 ``<body>`` 的底
部添加一个 script 语句来载入 jQuery ：

.. sourcecode:: html

   <script src="{{ url_for('static', filename='jquery.js') }}"></script>

另一个方法是使用 Google 的 `AJAX 库 API
<https://developers.google.com/speed/libraries/>`_ 来载入 jQuery：

.. sourcecode:: html

    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script>window.jQuery || document.write('<script src="{{
      url_for('static', filename='jquery.js') }}">\x3C/script>')</script>

在这种方式中，应用会先尝试从 Google 下载 jQuery ，如果失败则会调用静态目录
中的备用 jQuery 。这样做的好处是如果用户已经去过使用与 Google 相同版本的
jQuery 的网站后，访问你的网站时，页面可能会更快地载入，因为浏览器已经缓存
了 jQuery 。

我的网站在哪里？
-----------------

我的网站在哪里？如果你的应用还在开发中，那么答案很简单：它在本机的某个端口
上，且在服务器的根路径下。但是如果以后要把应用移到其他位置（例如
``http://example.com/myapp`` ）上呢？在服务端，这个问题不成为问题，可以使
用 :func:`~flask.url_for` 函数来得到答案。但是如果我们使用 jQuery ，那么就
不能硬码应用的路径，只能使用动态路径。怎么办？

一个简单的方法是在页面中添加一个 script 标记，设置一个全局变量来表示应用的
根路径。示例：

.. sourcecode:: html+jinja

   <script>
     $SCRIPT_ROOT = {{ request.script_root|tojson }};
   </script>


JSON 视图函数
-------------------

现在让我们来创建一个服务端函数，这个函数接收两个 URL 参数（两个需要相加的
数字），然后向应用返回一个 JSON 对象。下面这个例子是非常不实用的，因为一般
会在客户端完成类似工作，但这个例子可以简单明了地展示如何使用 jQuery 和 Flask::

    from flask import Flask, jsonify, render_template, request
    app = Flask(__name__)

    @app.route('/_add_numbers')
    def add_numbers():
        a = request.args.get('a', 0, type=int)
        b = request.args.get('b', 0, type=int)
        return jsonify(result=a + b)

    @app.route('/')
    def index():
        return render_template('index.html')

正如你所见，我还添加了一个 `index` 方法来渲染模板。这个模板会按前文所述载
入 jQuery 。模板中有一个用于两个数字相加的表单和一个触发服务端函数的链接。

注意，这里我们使用了 :meth:`~werkzeug.datastructures.MultiDict.get` 方法。
它不会调用失败。如果字典的键不存在，就会返回一个缺省值（这里是 ``0`` ）。
更进一步它还会把值转换为指定的格式（这里是 `int` ）。在脚本（ API 、
JavaScript 等）触发的代码中使用它特别方便，因为在这种情况下不需要特殊的错
误报告。

HTML
--------

你的 index.html 模板要么继承一个已经载入 jQuery 和设置好 `$SCRIPT_ROOT` 变
量的 :file:`layout.html` 模板，要么在模板开头就做好那两件事。下面就是应用
的 HTML 示例（ :file:`index.html` ）。注意，我们把脚本直接放入了 HTML 中。
通常更好的方式是放在独立的脚本文件中：

.. sourcecode:: html

    <script>
      $(function() {
        $('a#calculate').bind('click', function() {
          $.getJSON($SCRIPT_ROOT + '/_add_numbers', {
            a: $('input[name="a"]').val(),
            b: $('input[name="b"]').val()
          }, function(data) {
            $("#result").text(data.result);
          });
          return false;
        });
      });
    </script>
    <h1>jQuery Example</h1>
    <p><input type=text size=5 name=a> +
       <input type=text size=5 name=b> =
       <span id=result>?</span>
    <p><a href=# id=calculate>calculate server side</a>

这里不讲述 jQuery 运行详细情况，仅对上例作一个简单说明：

1. ``$(function() { ... })`` 定义浏览器在页面的基本部分载入完成后立即执行
   的代码。
2. ``$('selector')`` 选择一个元素供你操作。
3. ``element.bind('event', func)`` 定义一个用户点击元素时运行的函数。如果
   函数返回 `false` ，那么缺省行为就不会起作用（本例为转向 `#` URL ）。
4. ``$.getJSON(url, data, func)`` 向 `url` 发送一个 ``GET`` 请求，并把
   `data` 对象的内容作为查询参数。一旦有数据返回，它将调用指定的函数，并把
   返回值作为函数的参数。注意，我们可以在这里使用先前定义的 `$SCRIPT_ROOT`
   变量。

本页的完整代码可以在 :gh:`示例源代码 <examples/javascript>` 下载。
使用 ``XMLHttpRequest`` 和 ``fetch`` 同样。

