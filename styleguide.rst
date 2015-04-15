Pocoo 风格指南
==============

所有 Pocoo 项目都遵循 Pocoo 风格指南， Flask 项目也不例外。 Flask 补丁必须
遵循这个指南，同时也推荐 Flask 扩展遵循这个指南。

一般而言， Pocoo 风格指南遵循 :pep:`8` ，有一些小差异和扩充。

总体布局
--------

缩进：
  4个空格。不使用制表符，没有例外。

最大行长：
  软限制为 79 个字符，不超过 84 个字符。尝试合理放置 `break` 、 `continue`
  和 `return` 声明来避免代码过度嵌套。

续行:
  可以使用反斜杠来续行，续行应对齐最后一个点号或等于号，或者缩进四个空格::

    this_is_a_very_long(function_call, 'with many parameters') \
        .that_returns_an_object_with_an_attribute

    MyModel.query.filter(MyModel.scalar > 120) \
                 .order_by(MyModel.name.desc()) \
                 .limit(10)

  如果你在括号内的换行，那么续行应对齐括号::

    this_is_a_very_long(function_call, 'with many parameters',
                        23, 42, 'and even more')

  对于有许多元素的元组或列表，在起始括号后立即换行::
  
    items = [
        'this is the first', 'set of items', 'with more items',
        'to come in this line', 'like this'
    ]

空行：
  顶层函数和类由两个空行分隔，其它一个空行。不要使用过多空行来分隔代码
  逻辑段。例如::

    def hello(name):
        print 'Hello %s!' % name


    def goodbye(name):
        print 'See you %s.' % name


    class MyClass(object):
        """This is a simple docstring"""

        def __init__(self, name):
            self.name = name

        def get_annoying_name(self):
            return self.name.upper() + '!!!!111'

表达式和语句
------------

常规空格规则：
  - 不是单词的一元运算符不使用空格（例如： ``-`` 、 ``~`` 等等），在圆括号
    也是这样。
  - 用空格包围二元运算符。

  对::

    exp = -1.05
    value = (item_value / item_count) * offset / exp
    value = my_list[index]
    value = my_dict['key']

  错::

    exp = - 1.05
    value = ( item_value / item_count ) * offset / exp
    value = (item_value/item_count)*offset/exp
    value=( item_value/item_count ) * offset/exp
    value = my_list[ index ]
    value = my_dict ['key']

禁止 Yoda 语句：
  永远不要用变量来比较常量，而是用常量来比较变量：

  对::

    if method == 'md5':
        pass

  错::

    if 'md5' == method:
        pass

比较：
  - 针对任意类型使用 ``==`` 和 ``!=``
  - 针对单一类型使用 ``is`` 和 ``is not`` （例如： ``foo is not None`` ）
  - 永远不要与 `True` 或 `False` 作比较（例如永远不要写 ``foo == False`` ，
    而应当写 ``not foo`` ）

排除检验：
  使用 ``foo not in bar`` 而不是 ``not foo in bar``

实例检验：
  使用 ``isinstance(a, C)`` 而不是 ``type(A) is C`` ，但是通常应当避免检验
  实例，而应当检验特性。


命名约定
--------

- 类名： ``CamelCase`` ，缩写词大写（ ``HTTPWriter`` 而不是
  ``HttpWriter`` ）
- 变量名： ``lowercase_with_underscores``
- 方法和函数名： ``lowercase_with_underscores``
- 常量： ``UPPERCASE_WITH_UNDERSCORES``
- 预编译正则表达式： ``name_re``

被保护的成员以单个下划线作为前缀，混合类则使用双下划线。

如果使用关键字作为类的名称，那么在名称末尾添加下划线。与内置构件冲突是允许
的，请 **一定不要** 用在变量名后添加下划线的方式解决冲突。如果函数需要访问
一个隐蔽的内置构件，请重新绑定内置构件到一个不同的名字。

函数和方法参数:
  - 类方法: ``cls`` 作为第一个参数
  - 实例方法: ``self`` 作为第一个参数
  - 用于属性的 lambda 表达式应该把第一个参数替换为 ``x`` ，
    像 ``display_name = property(lambda x: x.real_name or x.username)``
    中一样


文档字符串
----------

文档字符串约定:
  所有的文档字符串为 Sphinx 可理解的 reStructuredText 格式。它们的形态
  因行数不同而不同。如果只有一行，三引号闭合在同一行，否则开头的三引号
  与文本在同一行，结尾的三引号独立一行::  

    def foo():
        """This is a simple docstring"""


    def bar():
        """This is a longer docstring with so much information in there
        that it spans three lines.  In this case the closing triple quote
        is on its own line.
        """

模块头:
  模块头包含一个 utf-8 编码声明（即使没有使用非 ASCII 字符，也始终推
  荐这么做）和一个标准的文档字符串::

    # -*- coding: utf-8 -*-
    """
        package.module
        ~~~~~~~~~~~~~~

        A brief description goes here.

        :copyright: (c) YEAR by AUTHOR.
        :license: LICENSE_NAME, see LICENSE_FILE for more details.
    """

  谨记使用合适的版权和许可证文件以利于通过 Flask 扩展审核。


注释
----

注释的规则与文档字符串类似。两者都使用 reStructuredText 格式。如果一个
注释被用于一个说明类属性，在起始的井号（ ``#`` ）后加一个冒号::

    class User(object):
        #: the name of the user as unicode string
        name = Column(String)
        #: the sha1 hash of the password + inline salt
        pw_hash = Column(String)
