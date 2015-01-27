.. _tutorial-schema:

步骤 1 ：数据库模式
=======================

首先我们要创建数据库模式。本应用只需要使用一张表，并且由于我们使用 SQLite ，
所以这一步非常简单。把以下内容保存为 `schema.sql` 文件并放在我们上一步创建的
`flaskr` 文件夹中就行了：

.. sourcecode:: sql

    drop table if exists entries;
    create table entries (
      id integer primary key autoincrement,
      title text not null,
      text text not null
    );

这个模式只有一张名为 `entries` 的表，表中的字段为 `id` 、 `title` 和 `text` 。
`id` 是主键，是自增整数型字段，另外两个字段是非空的字符串型字段。

下面请阅读 :ref:`tutorial-setup` 。
