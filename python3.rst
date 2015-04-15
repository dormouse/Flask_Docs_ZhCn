.. _python3_support:

Python 3 支持
=============

Flask 及其所有依赖包都支持 Python 3 ，因此理论上来说你能够在 Python 3
使用。然而在 Python 3 环境下开始你的下一个项目之前你需要留心一些事情。

要求
----

如果你要在 Python 3 环境下使用 Flask ，那么必须使用 Python 3.3 或者更高
版本。3.2 以及更早的版本是 *不* 支持的。

除此之外你还必须使用最新的 `itsdangerous`, `Jinja2` and `Werkzeug` 版本。

API 稳定性
----------

Python 3 的 unicode 和字节使用方式使编写底层代码变得困难。主要影响了 WSGI
中间件以及与 WSGI 提供的信息进行交互。 Werkzeug 已经用高级帮助器封装了所有
信息，但是其中一些是专门为支持 Python 3 添加的，还比较新。

许多关于 WSGI 细节的文档编写于 WSGI 支持 Python 3 之前。尽管 Werkzeug 和
Flask 在 Python 2.x 版本的 API 在支持 Python 3 时基本不用改动，但是不作
保证。

用户少
------

根据 PyPI 下载统计， Python 3 用户不到 Python 2 用户的 1％ 。因此，如果你
遇到 Python3 的特定问题，那么恐怕很难在互联网上搜索到答案。

小生态系统
----------

大多数 Flask 扩、所有的文档和绝大多数 PyPI 提供的库都还不支持 Python 3 。
即使你现在清楚地知道 Python 3 支持你的项目以及项目所需要的一切，但是谁能
预料半年以后的事呢？如果你富于冒险精神，那么可以自己移植库，但最好乞求一颗
勇敢的心。

建议
----

除非你已经很熟悉版本的差异，否则在生态系统成熟之前，建议仍然使用当前版本的
Python 。

升级之痛苦大部分针对低级别的库，例如 Flask 和 Werkzeug ，而不是较高级别的
应用程序。例如， Flask 仓库中的所有示例都同时支持 Python 2 和 Python 3 ，
不需要改动一行代码。

