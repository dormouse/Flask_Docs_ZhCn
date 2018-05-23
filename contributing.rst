如何为 Flask 做出贡献
==========================

感谢您考虑为 Flask 做出贡献！

支持问题
-----------------

请不要使用问题跟踪器来提问。有关你自己代码的问题请使用下列途径之一提问：

* 在 FreeNode 上的 IRC ``#pocoo`` 频道。
* 更普通的问题请使用 FreeNode 上的 IRC ``#python`` 频道。
* 邮件列表 flask@python.org 用于长期或者大型问题讨论。
* 在 `Stack Overflow`_ 上提问。首先使用以下方法在 Google 上搜索：
  ``site:stackoverflow.com flask {search term, exception message, etc.}``

.. _Stack Overflow: https://stackoverflow.com/questions/tagged/flask?sort=linked

报告问题
----------------

- 描述你希望发生的事情。
- 如果可能，提供一个 `最小的、完整的和可验证的示例`_ 以帮助我们找到问题。
  这也有助于鉴别问题是否也你自己的代码有关。
- 描述实际发生了什么。如果有异常，则应当包含完整的回溯。
- 列出你的 Python 、 Flask 和 Werkzeug 版本。如果可能，检查是否这个问题已
  在存储库中修复。

.. _最小的、完整的和可验证的示例: https://stackoverflow.com/help/mcve

提交补丁
------------------

- 如果补丁是用于解决错误的，那么应当包含一个测试，并明确说明错误发生于何种
  情况之下。确保如果没有补丁，测试就会失败。
- 尝试遵循 `PEP8`_ ，但是如果代码行长度限制使用代码更丑陋的话，则可以忽略
  这条规则。

首次设置
~~~~~~~~~~~~~~~~

- 下载并安装 `最新版的 git`_.
- 配置使用 git 的 `username`_ 和 `email`_::

        git config --global user.name 'your name'
        git config --global user.email 'your email'

- 确保你有一个 `GitHub 账号`_.
- 点击 `Fork`_ 按钮将 Flask fork 到你的 GitHub 账户。
- 把你的 GitHub fork `Clone`_ 到本地::

        git clone https://github.com/{username}/flask
        cd flask

- 添加一个主存储库作为远程库，稍后更新::

        git remote add pallets https://github.com/pallets/flask
        git fetch pallets

- 创建一个 virtualenv::

        python3 -m venv env
        . env/bin/activate
        # or "env\Scripts\activate" on Windows

- 用开发依赖在编辑模式下安装 Flask::

        pip install -e ".[dev]"

.. _GitHub 账号: https://github.com/join
.. _最新版的 git: https://git-scm.com/downloads
.. _username: https://help.github.com/articles/setting-your-username-in-git/
.. _email: https://help.github.com/articles/setting-your-email-in-git/
.. _Fork: https://github.com/pallets/flask/fork
.. _Clone: https://help.github.com/articles/fork-a-repo/#step-2-create-a-local-clone-of-your-fork

开始写代码
~~~~~~~~~~~~

- 创建一个分支来鉴别你想要处理的问题（例如 ``2287-dry-test-suite`` ）。
- 使用你最喜欢的编辑器，修改代码， `随时提交`_ 。
- 尝试遵循 `PEP8`_ ，但是如果代码行长度限制使用代码更丑陋的话，则可以忽略
  这条规则。
- 应当包含覆盖你所做的全部修改的测试。确保没有补丁则测试失败。
  `运行测试 <contributing-testsuite_>`_ 。
- 将你的提交推送到 GitHub 并 `创建一个 pull request`_ 。
- 庆祝成功 🎉

.. _随时提交: http://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
.. _PEP8: https://pep8.org/
.. _创建一个 pull request: https://help.github.com/articles/creating-a-pull-request/

.. _contributing-testsuite:

运行测试
~~~~~~~~~~~~~~~~~

用以下命令运行基础测试::

    pytest

这只在当前环境下运行测试。这是否相关取决于你在处理 Flask 的哪个部分。
当你提交 pull request 时， Travis-CI 会运行全部测试。

完整的测试套件运行时间会很长，因为它会在多种 Python 及其依赖的环境下运行。
在所有环境下运行测试需要有 Python 2.7 、 3.4 、 3.5 、 3.6 和 PyPy 2.7 。
然后运行::

    tox

运行测试覆盖
~~~~~~~~~~~~~~~~~~~~~

生成一个哪些代码未被测试覆盖的报告可以指明从哪里开始贡献。使用
``coverage`` 运行 ``pytest`` 并在终端生成一个报告和一份交互 HTML 文档::

    coverage run -m pytest
    coverage report
    coverage html
    # then open htmlcov/index.html

请阅读更多关于 `coverage <https://coverage.readthedocs.io>`_ 的文档。

用 ``tox`` 运行完整测试套件会组合所有运行测试的覆盖报告。


构建文档
~~~~~~~~~~~~~~~~~

使用 Sphinx 构建 ``docs`` 文件夹中的文档::

    cd docs
    make html

在浏览器中打开 ``_build/html/index.html`` 以查看文档。

请阅读更多关于 `Sphinx <http://www.sphinx-doc.org>`_ 的内容。


make 目标
~~~~~~~~~~~~

Flask 提供一个 ``Makefile`` ，包含各种捷径。它们可以保证安装好所有依赖。

- ``make test`` 用 ``pytest`` 运行基础测试套件
- ``make cov``  用 ``coverage`` 运行基础测试套件
- ``make test-all`` 用 ``tox`` 运行完整测试套件
- ``make docs`` 构建 HTML 文档

注意：零填充文件模式
-------------------------------

本存储库包含多个零填充文件模式，当提交存储库到 GitHub 之外的 git 主机时可
能会引发问题。修复这个问题会破坏提交历史记录，因此我们建议忽略这个问题。
如果推送失败并且你使用的是如 GitLab 这样的自托管 git 服务，那么在管理面板
中关闭存储库检查。

这些文件还会在克隆时引发问题。如果你在 git 配置文件中有以下设置::

    [fetch]
    fsckobjects = true

或者 ::

    [receive]
    fsckObjects = true

那么克隆时会失败。唯一的解决方法是在克隆时把上面的设置项目设置为 false ，
并在克隆完成后恢复。
