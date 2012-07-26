.. _distribute-deployment:

使用 Distribute 部署
=========================

`distribute`_ 的前身是 setuptools ，它是一个扩展库，通常用于分发 Python 库和
扩展。它的英文名称的就是“分发”的意思。它扩展了 Python 自带的一个基础模块安装
系统 distutils ，支持多种更复杂的结构，方便了大型应用的分发部署。它的主要特色：

- **支持依赖** ：一个库或者应用可以声明其所依赖的其他库的列表。依赖库将被自动
  安装。
- **包注册** ：可以在安装过程中注册包，这样就可以通过一个包查询其他包的信息。
  这套系统最有名的功能是“切入点”，即一个包可以定义一个入口，以便于其他包挂接，
  用以扩展包。
- **安装管理** ： distribute 中的 `easy_install` 可以为你安装其他库。你也可以
  使用早晚会替代 `easy_install` 的 `pip`_ ，它除了安装包还可以做更多的事。

Flask 本身，以及其他所有在 cheeseshop 中可以找到的库要么是用 distribute 分发的，
要么是用老的 setuptools 或 distutils 分发的。

在这里我们假设你的应用名称是 `yourapplication.py` ，且没有使用模块，而是一个
:ref:`包 <larger-applications>` 。 `distribute`_ 不支持分发标准模块，因此我们不
讨论模块的问题。关于如何把模块转换为包的信息参见 :ref:`larger-applications`
方案。

使用 distribute 将使发布更复杂，也更加自动化。如果你想要完全自动化处理，请同时
阅读 :ref:`fabric-deployment` 一节。

基础设置脚本
------------------

因为你已经安装了 Flask ，所以你应当已经安装了 setuptools 或 distribute 。如果
没有安装，不用怕，有一个 `distribute_setup.py`_ 脚本可以帮助你安装。只要下载这个
脚本，并在你的 Python 解释器中运行就可以了。

标准声明: :ref:`最好使用 virtualenv <virtualenv>` 。

你的设置代码应用放在 `setup.py` 文件中，这个文件应当位于应用旁边。这个文件名只是
一个约定，但是最好不要改变，因为大家都会去找这个文件。

是的，即使你使用 `distribute` ，你导入的包也是 `setuptools` 。 `distribute` 完全
向后兼容于 `setuptools` ，因此它使用相同的导入名称。

Flask 应用的基础 `setup.py` 文件示例如下::

    from setuptools import setup

    setup(
        name='Your Application',
        version='1.0',
        long_description=__doc__,
        packages=['yourapplication'],
        include_package_data=True,
        zip_safe=False,
        install_requires=['Flask']
    )

请记住，你必须显式的列出子包。如果你要 distribute 自动为你搜索包，你可以使用
`find_packages` 函数::

    from setuptools import setup, find_packages

    setup(
        ...
        packages=find_packages()
    )

大多数 `setup` 的参数可以望文生义，但是 `include_package_data` 和 `zip_safe`
可以不容易理解。 `include_package_data` 告诉 distribute 要搜索一个
`MANIFEST.in` 文件，把文件内容所匹配的所有条目作为包数据安装。可以通过使用这个
参数分发 Python 模块的静态文件和模板（参见 :ref:`distributing-resources` ）。
`zip_safe` 标志可用于强制或防止创建 zip 压缩包。通常你不会想要把包安装为 zip
压缩文件，因为一些工具不支持压缩文件，而且压缩文件比较难以调试。


.. _distributing-resources:

分发资源
----------------------

如果你尝试安装上文创建的包，你会发现诸如 `static` 或 `templates` 之类的文件夹
没有被安装。原因是 distribute 不知道要为你添加哪些文件。你要做的是：在你的
`setup.py` 文件旁边创建一个 `MANIFEST.in` 文件。这个文件列出了所有应当添加到
tar 压缩包的文件::

    recursive-include yourapplication/templates *
    recursive-include yourapplication/static *

不要忘了把 `setup` 函数的 `include_package_data` 参数设置为 `True` ！否则即使把
内容在 `MANIFEST.in` 文件中全部列出来也没有用。


声明依赖
----------------------

依赖是在 `install_requires` 参数中声明的，这个参数是一个列表。列表中的每一项都是
一个需要在安装时从 PyPI 获得的包。缺省情况下，总是会获得最新版本的包，但你可以
指定最高版本和最低版本。示例::

    install_requires=[
        'Flask>=0.2',
        'SQLAlchemy>=0.6',
        'BrokenPackage>=0.7,<=1.0'
    ]

我前面提到，依赖包都从 PyPI 获得的。但是如果要从别的地方获得包怎么办呢？你只要
还是按照上述方法写，然后提供一个可选地址列表就行了::

    dependency_links=['http://example.com/yourfiles']

请确保页面上有一个目录列表，且页面上的链接指向正确的 tar 压缩包。这样
distribute 就会找到文件了。如果你的包在公司内部网络上，请提供指向服务器的 URL 。


安装 / 开发
-----------------------

要安装你的应用（理想情况下是安装到一个 virtualenv ），只要运行带 `install` 参数
的 `setup.py` 脚本就可以了。它会将你的应用安装到 virtualenv 的 site-packages
文件夹下，同时下载并安装依赖::

    $ python setup.py install

如果你正开发这个包，同时也希望相关依赖被安装，那么可以使用 `develop` 来代替::

    $ python setup.py develop

这样做的好处是只安装一个指向 site-packages 的连接，而不是把数据复制到那里。这样
在开发过程中就不必每次修改以后再运行 `install` 了。


.. _distribute: http://pypi.python.org/pypi/distribute
.. _pip: http://pypi.python.org/pypi/pip
.. _distribute_setup.py: http://python-distribute.org/distribute_setup.py
