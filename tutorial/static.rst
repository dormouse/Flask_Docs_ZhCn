静态文件
============

验证视图和模板已经可用了，但是看上去很朴素。可以使用一些 `CSS`_ 给 HTML
添加点样式。样式不会改变，所以应当使用 *静态文件* ，而不是模板。

Flask 自动添加一个 ``static`` 视图，视图使用相对于 ``flaskr/static``
的相对路径。 ``base.html`` 模板已经使用了一个 ``style.css`` 文件连接：

.. code-block:: html+jinja

    {{ url_for('static', filename='style.css') }}

除了 CSS ，其他类型的静态文件可以是 JavaScript 函数文件或者 logo 图片。它们
都放置于 ``flaskr/static`` 文件夹中，并使用
``url_for('static', filename='...')`` 引用。

本教程不专注于如何写 CSS ，所以你只要复制以下内容到
``flaskr/static/style.css`` 文件：

.. code-block:: css
    :caption: ``flaskr/static/style.css``

    html { font-family: sans-serif; background: #eee; padding: 1rem; }
    body { max-width: 960px; margin: 0 auto; background: white; }
    h1 { font-family: serif; color: #377ba8; margin: 1rem 0; }
    a { color: #377ba8; }
    hr { border: none; border-top: 1px solid lightgray; }
    nav { background: lightgray; display: flex; align-items: center; padding: 0 0.5rem; }
    nav h1 { flex: auto; margin: 0; }
    nav h1 a { text-decoration: none; padding: 0.25rem 0.5rem; }
    nav ul  { display: flex; list-style: none; margin: 0; padding: 0; }
    nav ul li a, nav ul li span, header .action { display: block; padding: 0.5rem; }
    .content { padding: 0 1rem 1rem; }
    .content > header { border-bottom: 1px solid lightgray; display: flex; align-items: flex-end; }
    .content > header h1 { flex: auto; margin: 1rem 0 0.25rem 0; }
    .flash { margin: 1em 0; padding: 1em; background: #cae6f6; border: 1px solid #377ba8; }
    .post > header { display: flex; align-items: flex-end; font-size: 0.85em; }
    .post > header > div:first-of-type { flex: auto; }
    .post > header h1 { font-size: 1.5em; margin-bottom: 0; }
    .post .about { color: slategray; font-style: italic; }
    .post .body { white-space: pre-line; }
    .content:last-child { margin-bottom: 0; }
    .content form { margin: 1em 0; display: flex; flex-direction: column; }
    .content label { font-weight: bold; margin-bottom: 0.5em; }
    .content input, .content textarea { margin-bottom: 1em; }
    .content textarea { min-height: 12em; resize: vertical; }
    input.danger { color: #cc2f2e; }
    input[type=submit] { align-self: start; min-width: 10em; }

你可以在
:gh:`示例代码 <examples/tutorial/flaskr/static/style.css>` 找到一个排版不
紧凑的 ``style.css`` 。

访问 http://127.0.0.1/auth/login ，页面如下所示。

.. image:: flaskr_login.png
    :align: center
    :class: screenshot
    :alt: screenshot of login page

关于 CSS 的更多内容参见 `Mozilla 的文档 <CSS_>`_ 。改动静态文件后需要刷新
页面。如果刷新没有作用，请清除浏览器的缓存。

.. _CSS: https://developer.mozilla.org/docs/Web/CSS

下面请阅读 :doc:`blog` 。
