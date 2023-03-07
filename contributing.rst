如何为 Flask 做出贡献
==========================

感谢您为 Flask 做出贡献！


问答支持
--------

问题跟踪器的用途是记录 Flask 本身相关的问题和功能需求的，因此请不要使用问题
跟踪器来提问。如果有关于 Flask 使用方面或者你自己代码的方面的问题，请使用下
列途径之一提问：

-   Discord chat 上的 ``#questions`` 频道：
    https://discord.gg/pallets
-   在 `Stack Overflow`_ 上提问。提问前请先使用以下方法在 Google 上搜索：
    ``site:stackoverflow.com flask {search term, exception message, etc.}``
-   长期或者大型问题讨论，请在我们的 `GitHub 讨论`_ 上提问。

.. _Stack Overflow: https://stackoverflow.com/questions/tagged/flask?tab=Frequent
.. _GitHub 讨论: https://github.com/pallets/flask/discussion

报告问题
----------------

请在报告中包含以下内容：

-   描述你希望发生的事情。
-   如果可能，提供一个 `最小的可重现的示例`_ 以帮助我们找到问题。
    这也有助于鉴别问题是否也你自己的代码有关。
-   描述实际发生了什么。如果有异常，则应当包含完整的回溯。
-   列出你的 Python 、 Flask 和 Werkzeug 版本。如果可能，检查是否这个问题已
    在存储库中修复。

.. _最小的可重现的示例: https://stackoverflow.com/help/minimal-reproducible-example


提交补丁
------------------

在提交一个 PR 之前，如果没有相关的开放议题，那么建议打开一个新的相关议题讨论
一下。如果你对某个议题感兴趣，而这个议题没有相关联的 PR 也没有指定维护人，那么
你就直接上手吧，不需要征得同意。

提交补丁应当做好以下工作：

-   使用 `Black`_ 格式化你的代码。如果按照下面的介绍，安装好了
    `pre-commit`_ ，那么这个工具及其他的工具都可以自动运行。
-   如果补丁增加或者改动了代码，那么应当包含测试，并确保如果没有补丁，测试就会
    失败。
-   更新所有的相关文档页面和 docstring 。文档页面和 docstring 应当在第 72 个字符
    处换行。
-   在 ``CHANGES.rst`` 中增加一个条目，条目的样式与其他条目相同。同时，在相关的
    docstring 中包含 ``.. versionchanged::`` 行内变更记录。

.. _Black: https://black.readthedocs.io
.. _pre-commit: https://pre-commit.com


首次设置
~~~~~~~~~~~~~~~~

-   下载并安装 `最新版的 git`_ 。
-   配置使用 git 的 `username`_ 和 `email`_ 。

    .. code-block:: text

        $ git config --global user.name 'your name'
        $ git config --global user.email 'your email'

-   确保你有一个 `GitHub 账号`_ 。
-   点击 `Fork`_ 按钮将 Flask fork 到你的 GitHub 账户。
-   把主仓库 `Clone`_ 到本地。

    .. code-block:: text

        $ git clone https://github.com/pallets/flask
        $ cd flask

-   把你的工作作为一个远程分支，用你的用户名替换 ``{username}`` ，这样对远程
    分支进行了命名，缺省的 Pallets 远程分支名为 "origin" 。

    .. code-block:: text

        $ git remote add fork https://github.com/{username}/flask

-   创建一个 virtualenv 。

    - Linux/macOS

      .. code-block:: text

         $ python3 -m venv env
         $ . env/bin/activate

    - Windows

      .. code-block:: text

         > py -3 -m venv env
         > env\Scripts\activate

-   升级 pip 和 setuptools 。

    .. code-block:: text

        $ python -m pip install --upgrade pip setuptools

-   安装开发依赖，然后在可编辑模式下安装 Flask 。

    .. code-block:: text

        $ pip install -r requirements/dev.txt && pip install -e .

-   安装 pre-commit 钩子。

    .. code-block:: text

        $ pre-commit install


.. _最新版的 git: https://git-scm.com/downloads
.. _username: https://docs.github.com/en/github/using-git/setting-your-username-in-git
.. _email: https://docs.github.com/en/github/setting-up-and-managing-your-github-user-account/setting-your-commit-email-address
.. _GitHub 账号: https://github.com/join
.. _Fork: https://github.com/pallets/flask/fork
.. _Clone: https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#step-2-create-a-local-clone-of-your-fork


开始写代码
~~~~~~~~~~~~

-    创建一个分支来表明你想要处理的议题。如果要提交一个缺陷修复或者文档修正，
     请从最后的“ .x ”分支来创建分支。

    .. code-block:: text

        $ git fetch origin
        $ git checkout -b your-branch-name origin/2.0.x

     如果要提交的是增加功能或者改变功能，请从“ main ”分支来创建分支。

    .. code-block:: text

        $ git fetch origin
        $ git checkout -b your-branch-name origin/main

-   使用你最喜欢的编辑器，修改代码， `随时提交`_ 。
-   应当包含覆盖你所做的全部修改的测试，并且确保没有补丁则测试失败。详细内容见
    下一节。
-   把你的提交推送到 GitHub 上你的分支中，并 `创建一个拉取请求`_ 。在拉取请求中
    链接类似 ``fixes #123`` 的议题。

    .. code-block:: text

        $ git push --set-upstream fork your-branch-name

.. _随时提交: https://afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
.. _创建一个拉取请求: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request


运行测试
~~~~~~~~~~~~~~~~~

用 pytest 运行基本的测试套件。

.. code-block:: text

    $ pytest

上述测试是针对当前环境的，通常是有效的。当你提交拉取请求时， CI 会运行全部测试。
如果不想浪费时间，那么可以用 tox 运行所有测试。

.. code-block:: text

    $ tox


运行测试覆盖
~~~~~~~~~~~~~~~~~~~~~

生成一个报告，确定哪些代码未被测试覆盖，以指明工作的方向。
使用 ``coverage`` 运行 ``pytest`` 并生成一份报告。

.. code-block:: text

    $ pip install coverage
    $ coverage run -m pytest
    $ coverage html

在浏览器中打开 ``htmlcov/index.html`` 并研读报告。

请阅读更多关于 `coverage <https://coverage.readthedocs.io>`__ 的文档。


构建文档
~~~~~~~~~~~~~~~~~

使用 Sphinx 构建 ``docs`` 文件夹中的文档。

.. code-block:: text

    $ cd docs
    $ make html


在浏览器中打开 ``_build/html/index.html`` 以查看文档。

请阅读更多关于 `Sphinx <https://www.sphinx-doc.org/en/stable/>`__ 的内容。
