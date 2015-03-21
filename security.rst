安全注意事项
=======================

Web 应用常常会面对各种各样的安全问题，因此要把所有问题都解决是很难的。 Flask
尝试为你解决许多安全问题，但是更多的还是只能靠你自己。

.. _xss:

跨站脚本攻击（XSS）
-------------------

跨站脚本攻击是指在一个网站的环境中注入恶任意的 HTML （包括附带的 JavaScript
）。要防防御这种攻击，开发者需要正确地转义文本，使其不能包含恶意的 HTML 标记。
更多的相关信息请参维基百科上在文章： `Cross-Site Scripting
<http://en.wikipedia.org/wiki/Cross-site_scripting>`_ 。

在 Flask 中，除非显式指明不转义， Jinja2 会自动转义所有值。这样可以排除所有
模板导致的 XSS 问题，但是其它地方仍需小心：

-   不使用 Jinja2 生成 HTML 。
-   在用户提交的数据上调用了 :class:`~flask.Markup` 。
-   发送上传的 HTML ，永远不要这么做，使用 `Content-Disposition: attachment`
    标头来避免这个问题。
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

当用户鼠标停放在这个链接上时，会在警告窗口里显示 cookie 信息。一个精明的攻击者
可能还会执行其它的 JavaScript 代码，而不是把 cookie 显示给用户。结合 CSS 注入，
攻击者甚至可以把元素填满整个页面，这样用户把鼠标停放在页面上的任何地方都会触发
攻击。


Cross-Site Request Forgery (CSRF)
---------------------------------

Another big problem is CSRF.  This is a very complex topic and I won't
outline it here in detail just mention what it is and how to theoretically
prevent it.

If your authentication information is stored in cookies, you have implicit
state management.  The state of "being logged in" is controlled by a
cookie, and that cookie is sent with each request to a page.
Unfortunately that includes requests triggered by 3rd party sites.  If you
don't keep that in mind, some people might be able to trick your
application's users with social engineering to do stupid things without
them knowing.

Say you have a specific URL that, when you sent `POST` requests to will
delete a user's profile (say `http://example.com/user/delete`).  If an
attacker now creates a page that sends a post request to that page with
some JavaScript they just has to trick some users to load that page and
their profiles will end up being deleted.

Imagine you were to run Facebook with millions of concurrent users and
someone would send out links to images of little kittens.  When users
would go to that page, their profiles would get deleted while they are
looking at images of fluffy cats.

How can you prevent that?  Basically for each request that modifies
content on the server you would have to either use a one-time token and
store that in the cookie **and** also transmit it with the form data.
After receiving the data on the server again, you would then have to
compare the two tokens and ensure they are equal.

Why does Flask not do that for you?  The ideal place for this to happen is
the form validation framework, which does not exist in Flask.

.. _json-security:

JSON Security
-------------

.. admonition:: ECMAScript 5 Changes

   Starting with ECMAScript 5 the behavior of literals changed.  Now they
   are not constructed with the constructor of ``Array`` and others, but
   with the builtin constructor of ``Array`` which closes this particular
   attack vector.

JSON itself is a high-level serialization format, so there is barely
anything that could cause security problems, right?  You can't declare
recursive structures that could cause problems and the only thing that
could possibly break are very large responses that can cause some kind of
denial of service at the receiver's side.

However there is a catch.  Due to how browsers work the CSRF issue comes
up with JSON unfortunately.  Fortunately there is also a weird part of the
JavaScript specification that can be used to solve that problem easily and
Flask is kinda doing that for you by preventing you from doing dangerous
stuff.  Unfortunately that protection is only there for
:func:`~flask.jsonify` so you are still at risk when using other ways to
generate JSON.

So what is the issue and how to avoid it?  The problem are arrays at
top-level in JSON.  Imagine you send the following data out in a JSON
request.  Say that's exporting the names and email addresses of all your
friends for a part of the user interface that is written in JavaScript.
Not very uncommon:

.. sourcecode:: javascript

    [
        {"username": "admin",
         "email": "admin@localhost"}
    ]

And it is doing that of course only as long as you are logged in and only
for you.  And it is doing that for all `GET` requests to a certain URL,
say the URL for that request is
``http://example.com/api/get_friends.json``.

So now what happens if a clever hacker is embedding this to his website
and social engineers a victim to visiting his site:

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

If you know a bit of JavaScript internals you might know that it's
possible to patch constructors and register callbacks for setters.  An
attacker can use this (like above) to get all the data you exported in
your JSON file.  The browser will totally ignore the ``application/json``
mimetype if ``text/javascript`` is defined as content type in the script
tag and evaluate that as JavaScript.  Because top-level array elements are
allowed (albeit useless) and we hooked in our own constructor, after that
page loaded the data from the JSON response is in the `captured` array.

Because it is a syntax error in JavaScript to have an object literal
(``{...}``) toplevel an attacker could not just do a request to an
external URL with the script tag to load up the data.  So what Flask does
is to only allow objects as toplevel elements when using
:func:`~flask.jsonify`.  Make sure to do the same when using an ordinary
JSON generate function.
