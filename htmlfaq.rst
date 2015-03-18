HTML/XHTML 常见问答
===================

Flask 的文档和示例应用使用 HTML5 。你可能会注意到，在许多情况下，当结束标记
是可选的时候，并不使用它们，这样 HTML 会更简洁且加载更迅速。因为在开发者中，
有许多关于 HTML 和 XHTML 的混淆，本文档尝试回答一些主要的疑问。


XHTML 的历史
------------

有一段时间， XHTML 横空出世，大有取代 HTML 之势。然而时至今日，鲜有真正使用
XHTML （根据 XML 规则处理的 HTML ）的网站。出现这种情况的原因很多。其一是
Internet Explorer 对 XHTML 支持不完善。 根据规范要求 XHTML 必须使用
`application/xhtml+xml` MIME 类型，但是 Internet Explorer 却拒绝读取这个
MIME 类型的文件。

虽然通过配置 Web 服务器来为 XHTML 提供正确的服务相对简单，但是却很少有人这么
做。这可能是因为正确地使用 XHTML 是一件很痛苦的事情。

痛中之通是 XML 苛刻的（严厉且无情）错误处理。当 XML 处理中遭遇错误时，浏览器
会把一个丑陋的错误消息显示给用户，而不是尝试从错误中恢并显示出能显示的部分。
web 上大多数的 (X)HTML 是基于非 XML 的模板引擎（比如 Flask 所使用的 Jinja）
生成的。而这些模板引擎并不会阻止你偶然创建无效的 XHTML 。也有基于 XML 的模板
引擎，诸如 Kid 和流行的 Genshi ，但是它们通常具有更大的运行时开销， 并且用
起来很不爽，因为它们必须遵守 XML 规则。

大多数用户，不管怎样，假设他们正确地使用了 XHTML 。他们在文档的顶部写下一个
XHTML doctype ，并且闭合了所有必要闭合的标签（ 在 XHTML 中 ``<br>`` 要写作
``<br />`` 或 ``<br></br>`` ）。即使文档可以正确地通过 XHTML 验证，然而真正
决定浏览器中 XHTML/HTML 处理的是前面提到的，经常不被正确设置的 MIME 类型。
一旦类型错误，有效的 XHTML 会被视作无效的 HTML 处理。

XHTML 也改变了使用 JavaScript 的方式。要在 XHTML 下正确地工作，程序员不得不
使用带有 XHTML 名称空间的 DOM 接口来查询 HTML 元素。


History of HTML5
----------------

Development of the HTML5 specification was started in 2004 under the name
"Web Applications 1.0" by the Web Hypertext Application Technology Working
Group, or WHATWG (which was formed by the major browser vendors Apple,
Mozilla, and Opera) with the goal of writing a new and improved HTML
specification, based on existing browser behavior instead of unrealistic
and backwards-incompatible specifications.

For example, in HTML4 ``<title/Hello/`` theoretically parses exactly the
same as ``<title>Hello</title>``.  However, since people were using
XHTML-like tags along the lines of ``<link />``, browser vendors implemented
the XHTML syntax over the syntax defined by the specification.

In 2007, the specification was adopted as the basis of a new HTML
specification under the umbrella of the W3C, known as HTML5.  Currently,
it appears that XHTML is losing traction, as the XHTML 2 working group has
been disbanded and HTML5 is being implemented by all major browser vendors.

HTML versus XHTML
-----------------

The following table gives you a quick overview of features available in
HTML 4.01, XHTML 1.1 and HTML5. (XHTML 1.0 is not included, as it was
superseded by XHTML 1.1 and the barely-used XHTML5.)

.. tabularcolumns:: |p{9cm}|p{2cm}|p{2cm}|p{2cm}|

+-----------------------------------------+----------+----------+----------+
|                                         | HTML4.01 | XHTML1.1 | HTML5    |
+=========================================+==========+==========+==========+
| ``<tag/value/`` == ``<tag>value</tag>`` | |Y| [1]_ | |N|      | |N|      |
+-----------------------------------------+----------+----------+----------+
| ``<br/>`` supported                     | |N|      | |Y|      | |Y| [2]_ |
+-----------------------------------------+----------+----------+----------+
| ``<script/>`` supported                 | |N|      | |Y|      | |N|      |
+-----------------------------------------+----------+----------+----------+
| should be served as `text/html`         | |Y|      | |N| [3]_ | |Y|      |
+-----------------------------------------+----------+----------+----------+
| should be served as                     | |N|      | |Y|      | |N|      |
| `application/xhtml+xml`                 |          |          |          |
+-----------------------------------------+----------+----------+----------+
| strict error handling                   | |N|      | |Y|      | |N|      |
+-----------------------------------------+----------+----------+----------+
| inline SVG                              | |N|      | |Y|      | |Y|      |
+-----------------------------------------+----------+----------+----------+
| inline MathML                           | |N|      | |Y|      | |Y|      |
+-----------------------------------------+----------+----------+----------+
| ``<video>`` tag                         | |N|      | |N|      | |Y|      |
+-----------------------------------------+----------+----------+----------+
| ``<audio>`` tag                         | |N|      | |N|      | |Y|      |
+-----------------------------------------+----------+----------+----------+
| New semantic tags like ``<article>``    | |N|      | |N|      | |Y|      |
+-----------------------------------------+----------+----------+----------+

.. [1] This is an obscure feature inherited from SGML. It is usually not
       supported by browsers, for reasons detailed above.
.. [2] This is for compatibility with server code that generates XHTML for
       tags such as ``<br>``.  It should not be used in new code.
.. [3] XHTML 1.0 is the last XHTML standard that allows to be served
       as `text/html` for backwards compatibility reasons.

.. |Y| image:: _static/yes.png
       :alt: Yes
.. |N| image:: _static/no.png
       :alt: No

What does "strict" mean?
------------------------

HTML5 has strictly defined parsing rules, but it also specifies exactly
how a browser should react to parsing errors - unlike XHTML, which simply
states parsing should abort. Some people are confused by apparently
invalid syntax that still generates the expected results (for example,
missing end tags or unquoted attribute values).

Some of these work because of the lenient error handling most browsers use
when they encounter a markup error, others are actually specified.  The
following constructs are optional in HTML5 by standard, but have to be
supported by browsers:

-   Wrapping the document in an ``<html>`` tag
-   Wrapping header elements in ``<head>`` or the body elements in
    ``<body>``
-   Closing the ``<p>``, ``<li>``, ``<dt>``, ``<dd>``, ``<tr>``,
    ``<td>``, ``<th>``, ``<tbody>``, ``<thead>``, or ``<tfoot>`` tags.
-   Quoting attributes, so long as they contain no whitespace or
    special characters (like ``<``, ``>``, ``'``, or ``"``).
-   Requiring boolean attributes to have a value.

This means the following page in HTML5 is perfectly valid:

.. sourcecode:: html

    <!doctype html>
    <title>Hello HTML5</title>
    <div class=header>
      <h1>Hello HTML5</h1>
      <p class=tagline>HTML5 is awesome
    </div>
    <ul class=nav>
      <li><a href=/index>Index</a>
      <li><a href=/downloads>Downloads</a>
      <li><a href=/about>About</a>
    </ul>
    <div class=body>
      <h2>HTML5 is probably the future</h2>
      <p>
        There might be some other things around but in terms of
        browser vendor support, HTML5 is hard to beat.
      <dl>
        <dt>Key 1
        <dd>Value 1
        <dt>Key 2
        <dd>Value 2
      </dl>
    </div>


New technologies in HTML5
-------------------------

HTML5 adds many new features that make Web applications easier to write
and to use.

-   The ``<audio>`` and ``<video>`` tags provide a way to embed audio and
    video without complicated add-ons like QuickTime or Flash.
-   Semantic elements like ``<article>``, ``<header>``, ``<nav>``, and
    ``<time>`` that make content easier to understand.
-   The ``<canvas>`` tag, which supports a powerful drawing API, reducing
    the need for server-generated images to present data graphically.
-   New form control types like ``<input type="date">`` that allow user
    agents to make entering and validating values easier.
-   Advanced JavaScript APIs like Web Storage, Web Workers, Web Sockets,
    geolocation, and offline applications.

Many other features have been added, as well. A good guide to new features
in HTML5 is Mark Pilgrim's soon-to-be-published book, `Dive Into HTML5`_.
Not all of them are supported in browsers yet, however, so use caution.

.. _Dive Into HTML5: http://www.diveintohtml5.org/

What should be used?
--------------------

Currently, the answer is HTML5.  There are very few reasons to use XHTML
considering the latest developments in Web browsers.  To summarize the
reasons given above:

-   Internet Explorer (which, sadly, currently leads in market share)
    has poor support for XHTML.
-   Many JavaScript libraries also do not support XHTML, due to the more
    complicated namespacing API it requires.
-   HTML5 adds several new features, including semantic tags and the
    long-awaited ``<audio>`` and ``<video>`` tags.
-   It has the support of most browser vendors behind it.
-   It is much easier to write, and more compact.

For most applications, it is undoubtedly better to use HTML5 than XHTML.
