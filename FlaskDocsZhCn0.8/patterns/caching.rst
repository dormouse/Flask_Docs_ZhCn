.. _caching-pattern:

缓存
=======

当你的应用变慢的时候，可以考虑加入缓存。至少这是最简单的加速方法。缓存有什么用？
假设有一个函数耗时较长，但是这个函数在五分钟前返回的结果还是正确的。那么我们就
可以考虑把这个函数的结果在缓存中存放一段时间。

Flask 本身不提供缓存，但是它的基础库之一 Werkzeug 有一些非常基本的缓存支持。它
支持多种缓存后端，通常你需要使用的是 memcached 服务器。

设置一个缓存
------------------

与创建 :class:`~flask.Flask` 对象类似，你需要创建一个缓存对象并保持它。如果你
正在使用开发服务器，那么你可以创建一个
:class:`~werkzeug.contrib.cache.SimpleCache` 对象。这个对象提供简单的缓存，它把
缓存项目保存在 Python 解释器的内存中::

    from werkzeug.contrib.cache import SimpleCache
    cache = SimpleCache()

如果你要使用 memcached ，那么请确保有 memcache 模块支持（你可以从
`PyPI <http://pypi.python.org/>`_ 获得模块）和一个正在运行的 memcached 服务器。
连接 memcached 服务器示例::

    from werkzeug.contrib.cache import MemcachedCache
    cache = MemcachedCache(['127.0.0.1:11211'])

如果你正在使用 App Engine ，那么你可以方便地连接到 App Engine memcache 服务器::

    from werkzeug.contrib.cache import GAEMemcachedCache
    cache = GAEMemcachedCache()

使用缓存
-------------

现在的问题是如何使用缓存呢？有两个非常重要的操作：
:meth:`~werkzeug.contrib.cache.BaseCache.get` 和
:meth:`~werkzeug.contrib.cache.BaseCache.set` 。下面展示如何使用它们：

:meth:`~werkzeug.contrib.cache.BaseCache.get` 用于从缓存中获得项目，调用时使用
一个字符串作为键名。如果项目存在，那么就会返回这个项目，否则返回 `None`::

    rv = cache.get('my-item')

:meth:`~werkzeug.contrib.cache.BaseCache.set` 用于把项目添加到缓存中。第一个参数
是键名，第二个参数是键值。还可以提供一个超时参数，当超过时间后项目会自动删除。

下面是一个完整的例子::

    def get_my_item():
        rv = cache.get('my-item')
        if rv is None:
            rv = calculate_value()
            cache.set('my-item', rv, timeout=5 * 60)
        return rv
