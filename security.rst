安全注意事项
=======================

Web 应用常常会面对各种各样的安全问题，因此要把所有问题都解决是很难的。 Flask
尝试为你解决许多安全问题，但是更多的还是只能靠你自己。

.. _xss:

跨站脚本攻击（XSS）
-------------------

跨站脚本攻击是指在一个网站的环境中注入恶任意的 HTML （包括附带的 JavaScript
）。要防防御这种攻击，开发者需要正确地转义文本，使其不能包含恶意的 HTML
标记。更多的相关信息请参维基百科上在文章： `Cross-Site Scripting
<http://en.wikipedia.org/wiki/Cross-site_scripting>`_ 。

在 Flask 中，除非显式指明不转义， Jinja2 会自动转义所有值。这样可以排除所有
模板导致的 XSS 问题，但是其它地方仍需小心：

-   不使用 Jinja2 生成 HTML 。
-   在用户提交的数据上调用了 :class:`~flask.Markup` 。
-   发送上传的 HTML ，永远不要这么做，使用
    `Content-Disposition: attachment` 标头来避免这个问题。
-   发送上传的文本文件。一些浏览器基于文件开头几个字节来猜测文件的
    content-type ，用户可以利用这个漏洞来欺骗浏览器，通过伪装文本文件来执行
    HTML 。

另一件非常重要的漏洞是不用引号包裹的属性值。虽然 Jinja2 可以通过转义 HTML
来保护你免受 XSS 问题，但是仍无法避免一种情况：属性注入的 XSS 。为了免受这种
攻击，必须确保在属性中使用 Jinja 表达式时，始终用单引号或双引号包裹:

.. sourcecode:: html+jinja

   <a href="{{ href }}">the text</a>

为什么必须这么做？因为如果不这么做，攻击者可以轻易地注入自制的 JavaScript
处理器。例如一个攻击者可以注入以下 HTML+JavaScript 代码：

.. sourcecode:: html

   onmouseover=alert(document.cookie)

当用户鼠标停放在这个链接上时，会在警告窗口里显示 cookie 信息。一个精明的
攻击者可能还会执行其它的 JavaScript 代码，而不是把 cookie 显示给用户。结合
CSS 注入，攻击者甚至可以把元素填满整个页面，这样用户把鼠标停放在页面上的
任何地方都会触发攻击。

跨站请求伪造（ CSRF ）
----------------------

另一个大问题是 CSRF 。这个问题非常复杂，因此我不会在此详细展开，只是介绍
CSRF 是什么以及在理论上如何避免这个问题。

如果你的验证信息存储在 cookie 中，那么你就使用了隐式的状态管理。“已登入”
这个状态由一个 cookie 控制，并且这个 cookie 在页面的每个请求中都会发送。
不幸的是，在第三方站点发送的请求中也会发送这个 cookie 。如果你不注意这点，
一些人可能会通过社交引擎来欺骗应用的用户在不知情的状态下做一些蠢事。

假设你有一个特定的 URL ，当你发送 `POST` 请求时会删除一个用户的资料（例如
`http://example.com/user/delete` 。如果一个攻击者现在创造一个页面并通过
页面中的 JavaScript 发送这个 post 请求，只要诱骗用户加载该页面，那么用户的
资料就会被删除。

设象在有数百万的并发用户的 Facebook 上，某人放出一些小猫图片的链接。当用户
访问那个页面欣赏毛茸茸的小猫图片时，他们的资料就被删除了。

那么如何预防这个问题呢？基本思路是：对于每个要求修改服务器内容的请求，应该
使用一次性令牌，并存储在 cookie 里， **并且** 在发送表单数据的同时附上它。
在服务器再次接收数据之后，需要比较两个令牌，并确保它们相等。

为什么 Flask 没有替你做这件事？因为这应该是表单验证框架做的事，而 Flask 不
包括表单验证。

.. _json-security:

JSON 安全
---------

.. admonition:: ECMAScript 5 的变更

   从 ECMAScript 5 开始，常量的行为改变了。现在它们不由 ``Array`` 或其它
   的构造函数构造，而是由 ``Array`` 的内建构造函数构造，关闭了这个特殊的
   攻击媒介。

JSON 本身是一种高级序列化格式，所以它几乎没有什么可以导致安全问题，对吗？
你不能声明导致问题的递归结构，唯一可能导致破坏的就是非常大的响应可能导致
接收端在某种意义上拒绝服务。

然而有一个陷阱。由于浏览器在 CSRF 问题上处理方式， JSON 也不能幸免。幸运
的是， JavaScript 规范中有一个怪异的部分可以轻易地解决这一问题。 Flask
在这方面做了一点工作，为你避免一些风险。不幸的是，只有在
:func:`~flask.jsonify` 中有这样的保护，所以使用其它方法生成 JSON 仍然有
风险。

那么，问题出在哪里？如何避免？问题的根源是数组是 JSON 中的一等公民。设想
有一个 JavaScript 写的用户界面，在界面中导出你所有朋友的姓名和电子邮件
地址，常见的是在 JSON 请求中发送如下数据：

.. sourcecode:: javascript

    [
        {"username": "admin",
         "email": "admin@localhost"}
    ]

当然只能你登入的时候，针对本人才可以这么做。而且，它对一个特定 URL 上的所有
`GET` 请求都这么做。假设请求的 URL 是
``http://example.com/api/get_friends.json`` 

那么如果一个聪明的黑客把这个嵌入到他自己的网站上，并用社交引擎使得受害者访问
他的网站，会发生什么:

.. sourcecode:: html

    <script type=text/javascript>
    var captured = [];
    var oldArray = Array;
    function Array() {
      var obj = this, id = 0, capture = function(value) {
        obj.__defineSetter__(id++, capture);
        if (value)
          captured.push(value);
      };
      capture();
    }
    </script>
    <script type=text/javascript
      src=http://example.com/api/get_friends.json></script>
    <script type=text/javascript>
    Array = oldArray;
    // now we have all the data in the captured array.
    </script>

如果你懂得一些 JavaScript 的内部工作机制，你会知道给构造函数打补丁和为
setter 注册回调是可能的。一个攻击者可以利用这点（像上面一样上）来获取
所有你导出的 JSON 文件中的数据。如果在 script 标签中定义了内容类型是
``text/javascript`` ，浏览器会完全忽略 ``application/json`` 的
mimetype ，而把其作为 JavaScript 来求值。因为顶层数组元素是允许的（虽然
没用）且我们在自己的构造函数中挂钩，在这个页面载入后， JSON 响应中的数据
会出现在 `captured` 数组中。

因为在 JavaScript 中对象文字（ ``{...}`` ）处于顶层是一个语法错误，攻
击者可能不只是用 script 标签加载数据并请求一个外部的 URL 。所以， Flask
所做的只是在使用 :func:`~flask.jsonify` 时允许对象作为顶层元素。应当确保
使用普通的 JSON 生成函数时也这么做。

