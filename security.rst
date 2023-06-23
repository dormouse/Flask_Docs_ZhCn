安全注意事项
=======================

Web 应用常常会面对各种各样的安全问题，因此要把所有问题都解决是很难的。
Flask 尝试为你解决许多安全问题，但是更多的还是只能靠你自己。

.. _security-xss:

跨站脚本攻击（ XSS ）
----------------------

跨站脚本攻击是指在一个网站的环境中注入恶任意的 HTML （包括附带的
JavaScript ）。要防防御这种攻击，开发者需要正确地转义文本，使其不能包
含恶意的 HTML 标记。更多的相关信息请参维基百科上在文章： `跨站脚本
<https://en.wikipedia.org/wiki/Cross-site_scripting>`_ 。

在 Flask 中，除非显式指明不转义， Jinja2 会自动转义所有值。这样可以排
除所有模板导致的 XSS 问题，但是其它地方仍需小心：

-   没有使用 Jinja2 生成 HTML 。
-   在用户提交的数据上调用了 :class:`~markupsafe.Markup` 。
-   发送上传的 HTML ，永远不要这么做，使用
    ``Content-Disposition: attachment`` 头部来避免这个问题。
-   发送上传的文本文件。一些浏览器基于文件开头几个字节来猜测文件的
    content-type ，用户可以利用这个漏洞来欺骗浏览器，通过伪装文本文件
    来执行 HTML 。

另一件非常重要的漏洞是不用引号包裹的属性值。虽然 Jinja2 可以通过转义
HTML 来保护你免受 XSS 问题，但是仍无法避免一种情况：属性注入的 XSS 。
为了免受这种攻击，必须确保在属性中使用 Jinja 表达式时，始终用单引号或
双引号包裹:

.. sourcecode:: html+jinja

   <input value="{{ value }}">

为什么必须这么做？因为如果不这么做，攻击者可以轻易地注入自制的
JavaScript 处理器。例如一个攻击者可以注入以下 HTML+JavaScript 代码：

.. sourcecode:: html

   onmouseover=alert(document.cookie)

当用户鼠标停放在这个输入框上时，会在警告窗口里显示 cookie 信息。一个
精明的攻击者可能还会执行其它的 JavaScript 代码，而不是把 cookie 显示
给用户。结合 CSS 注入，攻击者甚至可以把元素填满整个页面，这样用户把鼠
标停放在页面上的任何地方都会触发攻击。

有一类 XSS 问题 Jinja 的转义无法阻止。 ``a`` 标记的 ``href`` 属性可以
包含一个 `javascript:` URI 。如果没有正确保护，那么当点击它时浏览器将
执行其代码。

.. sourcecode:: html

    <a href="{{ value }}">click here</a>
    <a href="javascript:alert('unsafe');">click here</a>

为了防止发生这种问题，需要设置 :ref:`security-csp` 响应头部。

跨站请求伪造（ CSRF ）
----------------------

另一个大问题是 CSRF 。这个问题非常复杂，因此我不会在此详细展开，只是介绍
CSRF 是什么以及在理论上如何避免这个问题。

如果你的验证信息存储在 cookie 中，那么你就使用了隐式的状态管理。“已登入”
这个状态由一个 cookie 控制，并且这个 cookie 在页面的每个请求中都会发送。不
幸的是，在第三方站点发送的请求中也会发送这个 cookie 。如果你不注意这点，一
些人可能会通过社交引擎来欺骗应用的用户在不知情的状态下做一些蠢事。

假设你有一个特定的 URL ，当你发送 ``POST`` 请求时会删除一个用户的资料（例
如 ``http://example.com/user/delete`` ） 。如果一个攻击者现在创造一个页面
并通过页面中的 JavaScript 发送这个 post 请求，只要诱骗用户加载该页面，那么
用户的资料就会被删除。

设象在有数百万的并发用户的 Facebook 上，某人放出一些小猫图片的链接。当用户
访问那个页面欣赏毛茸茸的小猫图片时，他们的资料就被删除了。

那么如何预防这个问题呢？基本思路是：对于每个要求修改服务器内容的请求，应该
使用一次性令牌，并存储在 cookie 里， **并且** 在发送表单数据的同时附上它。
在服务器再次接收数据之后，需要比较两个令牌，并确保它们相等。

为什么 Flask 没有替你做这件事？因为这应该是表单验证框架做的事，而 Flask 不
包括表单验证。

.. _security-json:

JSON 安全
---------

Flask 0.10 版和更低版本中， :func:`~flask.jsonify` 没序列化顶层数组为
JSON 。这是因为 ECMAScript 4 存在安全漏洞。

ECMAScript 5 关闭了这个漏洞，所以只有非常老的浏览器仍然脆弱，而且还有
`其他更严重的漏洞
<https://github.com/pallets/flask/issues/248#issuecomment-59934857>`_ 。
因此，这个行为被改变了，并且 :func:`~flask.jsonify` 现在支持了序列化数据。

安全头部
----------------

为了控件安全性，浏览器识别多种头部。我们推荐检查应用所使用的以下每种头部。
`Flask-Talisman`_ 扩展可用于管理 HTTPS 和安全头部。

.. _Flask-Talisman: https://github.com/GoogleCloudPlatform/flask-talisman

HTTP Strict Transport Security (HSTS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

告诉浏览器把所有 HTTP 请求转化为 HTTPS ，以防止
man-in-the-middle (MITM) 攻击。 ::

    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security

.. _security-csp:

Content Security Policy (CSP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

告诉浏览器哪里可以加载各种资源。这个头部应当尽可能使用，但是需要为网站定义
正确的政策。一个非常严格的政策是::

    response.headers['Content-Security-Policy'] = "default-src 'self'"

- https://csp.withgoogle.com/docs/index.html
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy

X-Content-Type-Options
~~~~~~~~~~~~~~~~~~~~~~

强制浏览器遵守内容类型而不是尝试检测它，这可以会被滥用，以生成一个跨站脚本
（ XSS ）攻击。 ::

    response.headers['X-Content-Type-Options'] = 'nosniff'

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options

X-Frame-Options
~~~~~~~~~~~~~~~

防止外部网站把你的站点嵌入到 ``iframe`` 中。这样可以防止外部框架点击转化针
对你的页面元素的隐藏点击，也称为“点击支持”。 ::

    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options

.. _security-cookie:

Set-Cookie 选项
~~~~~~~~~~~~~~~~~~

这些选项可以被添加到一个 ``Set-Cookie`` 头部以增强其安全性。 Flask 具有将
其配置于会话 cookie 上的配置选项。它们也可以配置在其他 cookie 上。

- ``Secure`` 限制 cookies 仅用于 HTTPS 流量。
- ``HttpOnly`` 保护 cookies 内容不被 JavaScript 读取。
- ``SameSite`` 限制如何从外部网站通过请求发送 cookie 。可以设置为
  ``'Lax'`` （推荐）或者 ``'Strict'`` 。 ``Lax`` 防止从外部网站通过有 CSRF
  倾向请求（比如一个表单）发送 cookie 。 ``Strict`` 防止通过所有外部请求发
  送 cookie ，包括常规连接。

::

    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )

    response.set_cookie('username', 'flask', secure=True, httponly=True, samesite='Lax')

指定 ``Expires`` 或者 ``Max-Age`` 选项后，将会分别在给定时间后或者当前时间
加上所定义存活期后删除 cookie 。如果两个参数都没有指定，则会在关闭浏览器时
删除。 ::

    # cookie expires after 10 minutes
    response.set_cookie('snakes', '3', max_age=600)

对于会话 cookie 来说，如果
:attr:`session.permanent <flask.session.permanent>` 被设置了，那么
:data:`PERMANENT_SESSION_LIFETIME` 会被用于设置有效期。
Flask 的缺省 cookie 实现会验证加密签名不会超过这个值。降低这个值有助于
缓解重播攻击，可以在稍后发送被拦截的 cookie 。 ::

    app.config.update(
        PERMANENT_SESSION_LIFETIME=600
    )

    @app.route('/login', methods=['POST'])
    def login():
        ...
        session.clear()
        session['user_id'] = user.id
        session.permanent = True
        ...

使用 :class:`itsdangerous.TimedSerializer` 来签名和验证其他 cookie 值（
或者其他任何需要安全签名的值）。

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie

.. _samesite_support: https://caniuse.com/#feat=same-site-cookie-attribute


HTTP Public Key Pinning (HPKP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

告诉浏览器只使用指定的证书密钥进行服务器验证，以防止 MITM 攻击。

.. warning::
   启用后请小心，如果密钥设置或者升级不正确则难以撤消。

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Public_Key_Pinning


复制/粘贴到终端
----------------------

隐藏字符，例如退格字符（ ``\b`` 、 ``^H`` ）可以
导致文本的 HTML 渲染结果与
`粘贴到终端 <https://security.stackexchange.com/q/39118>`__ 的结果不
同。

例如， ``import y\bose\bm\bi\bt\be\b`` 在 HTML 中渲染为
``import yosemite`` ，但是当粘贴到终端时，因为退格字符的作用，会变成
``import os`` 。

如果您预计用户会从您的站点复制和粘贴不受信任的代码，例如从技术博客上的
用户评论中复制代码，那么请考虑增加额外的过滤，例如替换所有 ``\b`` 字符。

.. code-block:: python

    body = body.replace("\b", "")

大多数现代终端会在粘贴时警告并删除隐藏字符，所以这不是绝对必需的。同时
也会存在无法过滤的其他方式的危险命令。根据您网站的用途不同，一般最好显
示关于代码复制的警告。
