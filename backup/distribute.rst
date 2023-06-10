使用 Setuptools 部署
=========================

`Setuptools`_ 是一个扩展库，通常用于分发 Python 库和扩展。它扩展了 Python
自带的一个基础模块安装系统 distutils ，支持多种更复杂的结构，方便了大型应
用的分发部署。它的主要特色：

- **支持依赖** ：一个库或者应用可以声明其所依赖的其他库的列表。依赖库将被
  自动安装。
- **包注册** ：可以在安装过程中注册包，这样就可以通过一个包查询其他包的信
  息。这套系统最有名的功能是“切入点”，即一个包可以定义一个入口，以便于其
  他包挂接，用以扩展包。
- **安装管理**: :command:`pip` 可以为你安装其他库。

Flask 本身，以及其他所有在 PyPI 中可以找到的库要么是用 setuptools 分发的，
要么是用 distutils 分发的。

在这里我们假设你的应用名称是 :file:`yourapplication.py` ，且没有使用模块，
而是一个包。如果您还没有把应用转换成一个包，那么参阅 :doc:`packages` ，
学习一下如何把模块转换为包。

可用的 setuptools 部署是进行复杂开发的第一步，它将使发布工作更加自动化。如
果你想要完全自动化处理，请同时阅读 :doc:`fabric` 一节。


基础设置脚本
------------------

因为 Flask 依赖 setuptools ，所以安装好了 Flask ，就表示 setuptools 也
已经安装好了。

标准免责声明: :ref:`使用一个 virtualenv <install-create-env>` 。

您的设置代码应用放在 :file:`setup.py` 文件中，这个文件应当位于应用旁
边。这个文件名只是一个约定，但是最好不要改变，因为大家都会去找这个文件。

Flask 应用的基础 :file:`setup.py` 文件示例如下::

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

请记住，你必须显式的列出子包。如果你要 setuptools 自动为你搜索包，你可以使用
``find_packages`` 函数::

    from setuptools import setup, find_packages

    setup(
        ...
        packages=find_packages()
    )

大多数 ``setup`` 的参数可以望文生义，但是 ``include_package_data`` 和
``zip_safe`` 可能不容易理解。 ``include_package_data`` 告诉 setuptools 要
搜索一个 :file:`MANIFEST.in` 文件，把文件内容所匹配的所有条目作为包数据安
装。可以通过使用这个参数分发 Python 模块的静态文件和模板
（参见 :ref:`distributing-resources` ）。 ``zip_safe`` 标志可用于强制或防
止创建 zip 压缩包。通常你不会想要把包安装为 zip 压缩文件，因为一些工具不支
持压缩文件，而且压缩文件比较难以调试。


标记构建版本
--------------

区分发行版本和开发版本是有益的。添加一个 :file:`setup.cfg` 文件来配置这些
选项::

    [egg_info]
    tag_build = .dev
    tag_date = 1

    [aliases]
    release = egg_info -Db ''

运行 ``python setup.py sdist`` 会创建一个带有” .dev “的开发包，并且当前
的数据会添加到 ``flaskr-1.0.dev20160314.tar.gz`` 中。运行
``python setup.py release sdist`` 会一个发行包 ``flaskr-1.0.tar.gz`` 。只
有一个版本。

.. _distributing-resources:

分发资源
----------------------

如果你尝试安装上文创建的包，你会发现诸如 :file:`static` 或
:file:`templates` 之类的文件夹没有被安装。原因是 setuptools 不知道要为你添
加哪些文件。你要做的是：在你的 :file:`setup.py` 文件旁边创建一个
:file:`MANIFEST.in` 文件。这个文件列出了所有应当添加到 tar 压缩包的文件::

    recursive-include yourapplication/templates *
    recursive-include yourapplication/static *

不要忘了把 ``setup`` 函数的 `include_package_data` 参数设置为 ``True`` ！
否则即使把内容在 :file:`MANIFEST.in` 文件中全部列出来也没有用。


声明依赖
----------------------

依赖是在 ``install_requires`` 参数中声明的，这个参数是一个列表。列表中的每
一项都是一个需要在安装时从 PyPI 获得的包。缺省情况下，总是会获得最新版本的
包，但你可以指定最高版本和最低版本。示例::

    install_requires=[
        'Flask>=0.2',
        'SQLAlchemy>=0.6',
        'BrokenPackage>=0.7,<=1.0'
    ]

前面提到，依赖包都从 PyPI 获得的。但是如果要从别的地方获得包怎么办呢？你只
要还是按照上述方法写，然后提供一个可选地址列表就行了::

    dependency_links=['http://example.com/yourfiles']

请确保页面上有一个目录列表，且页面上的链接指向正确的 tar 压缩包。这样
setuptools 就会找到文件了。如果你的包在公司内部网络上，请提供指向服务器的
URL 。


安装 / 开发
-----------------------

要安装你的应用（理想情况下是安装到一个 virtualenv ），只要运行带
``install`` 参数的 :file:`setup.py` 脚本就可以了。它会将你的应用安装到
virtualenv 的 site-packages 文件夹下，同时下载并安装依赖::

    $ python setup.py install

如果你正开发这个包，同时也希望相关依赖被安装，那么可以使用 ``develop`` 来
代替::

    $ python setup.py develop

这样做的好处是只安装一个指向 site-packages 的连接，而不是把数据复制到那里。这样
在开发过程中就不必每次修改以后再运行 ``install`` 了。

.. _pip: https://pypi.org/project/pip/
.. _Setuptools: https://pypi.org/project/setuptools/

