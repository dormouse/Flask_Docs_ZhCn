缓存
=======

当你的应用变慢的时候，可以考虑加入缓存。至少这是最简单的加速方法。缓存有什
么用？假设有一个函数耗时较长，但是这个函数在五分钟前返回的结果还是正确的。
那么我们就可以考虑把这个函数的结果在缓存中存放一段时间。

Flask 本身不提供缓存，但是 `Flask-Caching`_ 扩展可以。
Flask-Caching 支持多种后端，甚至可以支持你自己开发的后端。

.. _Flask-Caching: https://flask-caching.readthedocs.io/en/latest/

