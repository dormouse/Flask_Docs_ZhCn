如何为 Flask 做出贡献
==========================

感谢您为 Flask 做出贡献！


问答支持
--------

问题跟踪器的用途是记录 Flask 本身相关的问题和功能需求的，因此请不要使
用问题跟踪器来提问。如果有关于 Flask 使用方面或者你自己代码的方面的问
题，请使用下列途径之一提问：

-   Discord chat 上的 ``#questions`` 频道： https://discord.gg/pallets
-   在 `Stack Overflow`_ 上提问。提问前请先使用以下方法在 Google 上搜
    索：
    ``site:stackoverflow.com flask {search term, exception message, etc.}``
-   长期或者大型问题讨论，请在我们的 `GitHub 讨论`_ 上提问。

.. _Stack Overflow: https://stackoverflow.com/questions/tagged/flask?tab=Frequent
.. _GitHub 讨论: https://github.com/pallets/flask/discussion

报告问题
----------------

请在报告中包含以下内容：

-   描述你希望发生的事情。
-   如果可能，提供一个 `最小的可重现的示例`_ 以帮助我们找到问题。这也
    有助于鉴别问题是否也你自己的代码有关。
-   描述实际发生了什么。如果有异常，则应当包含完整的回溯。
-   列出你的 Python 、 Flask 和 Werkzeug 版本。如果可能，检查是否这个
    问题已在存储库中修复。

.. _最小的可重现的示例: https://stackoverflow.com/help/minimal-reproducible-example


提交补丁
------------------

在提交一个 PR 之前，如果没有相关的开放议题，那么建议打开一个新的相关
议题讨论一下。如果你对某个议题感兴趣，而这个议题没有相关联的 PR 也没
有指定维护人，那么你就直接上手吧，不需要征得同意。

提交补丁应当做好以下工作：

-   使用 `Black`_ 格式化你的代码。如果按照下面的介绍，安装好了
    `pre-commit`_ ，那么这个工具及其他的工具都可以自动运行。
-   如果补丁增加或者改动了代码，那么应当包含测试，并确保如果没有补丁，
    测试就会失败。
-   更新所有的相关文档页面和 docstring 。文档页面和 docstring 应当在
    第 72 个字符处换行。
-   在 ``CHANGES.rst`` 中增加一个条目，条目的样式与其他条目相同。同时，
    在相关的 docstring 中包含 ``.. versionchanged::`` 行内变更记录。

.. _Black: https://black.readthedocs.io
.. _pre-commit: https://pre-commit.com


首次使用 GitHub Codespaces 的设置
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`GitHub Codespaces`_ 创建了一个已经设置好的项目开发环境。默认情况下，
它是在 Visual Studio Code for the Web 中打开的，但可以通过修改 GitHub
配置文件，改为使用本地计算机上的 Visual Studio Code 或 JetBrains
PyCharm 打开。

-   确保你有一个 `GitHub 账户`_ 。
-   在项目的资源库页面，点击绿色的“代码”按钮，然后点击 “在主界面创
    建”。
-   代码空间将被设置，然后会打开 Visual Studio Code 。但是，因为需要
    安装 Python 扩展，所以你需要多等一会儿。当底部的终端显示
    virtualenv 被激活时，就准备好了。
-   检出一个分支，然后 `start coding`_ 。

.. _GitHub Codespaces: https://docs.github.com/en/codespaces
.. _devcontainer: https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers


首次设置本地环境
~~~~~~~~~~~~~~~~

-   确保你有一个 `GitHub 账户`_ 。
-   下载并安装 `最新版的 git`_ 。
-   配置使用 git 的 `username`_ 和 `email`_ 。

    .. code-block:: text

        $ git config --global user.name 'your name'
        $ git config --global user.email 'your email'

-   点击 `Fork`_ 按钮将 Flask fork 到你的 GitHub 账户。
-   在本地 `Clone`_ 你的 fork ，用你的用户名替换下面命令中的
    ``your-username`` 。

    .. code-block:: text

        $ git clone https://github.com/your-username/flask
        $ cd flask

-   使用最新版的 Python ，创建一个 virtualenv 。

    - Linux/macOS

      .. code-block:: text

         $ python3 -m venv .venv
         $ . .venv/bin/activate

    - Windows

      .. code-block:: text

         > py -3 -m venv .venv
         > .venv\Scripts\activate

-   安装开发依赖，然后在可编辑模式下安装 Flask 。

    .. code-block:: text

        $ python -m pip install -U pip setuptools wheel
        $ pip install -r requirements/dev.txt && pip install -e .

-   安装 pre-commit 钩子。

    .. code-block:: text

        $ pre-commit install --install-hooks

.. _GitHub 账号: https://github.com/join
.. _最新版的 git: https://git-scm.com/downloads
.. _username: https://docs.github.com/en/github/using-git/setting-your-username-in-git
.. _email: https://docs.github.com/en/github/setting-up-and-managing-your-github-user-account/setting-your-commit-email-address
.. _Fork: https://github.com/pallets/flask/fork
.. _Clone: https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#step-2-create-a-local-clone-of-your-fork

.. _start coding:

开始写代码
~~~~~~~~~~~~

-   创建一个分支来表明你想要处理的议题。如果要提交一个缺陷修复或者文
    档修正，请从最后的“ .x ”分支来创建分支。

    .. code-block:: text

        $ git fetch origin
        $ git checkout -b your-branch-name origin/2.0.x

    如果要提交的是增加功能或者改变功能，请从“ main ”分支来创建分支。

    .. code-block:: text

        $ git fetch origin
        $ git checkout -b your-branch-name origin/main

-   使用你最喜欢的编辑器，修改代码， `随时提交`_ 。
-   如果你处于一个 codespace 中，那么第一次提交时会提示
    `创建一个 fork`_ 。输入 ``Y`` 继续。
-   应当包含覆盖你所做的全部修改的测试，并且确保没有补丁则测试失败。
    运行下文提到的测试。
-   把你的提交推送到 GitHub 上你的 fork 中，并 `创建一个拉取请求`_ 。
    在拉取请求的描述中链接类似 ``fixes #123`` 的议题。

    .. code-block:: text

        $ git push --set-upstream origin your-branch-name

.. _随时提交: https://afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
.. _创建一个 fork: https://docs.github.com/en/codespaces/developing-in-codespaces/using-source-control-in-your-codespace#about-automatic-forking
.. _创建一个拉取请求: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request

.. _Running the tests:

运行测试
~~~~~~~~~~~~~~~~~

用 pytest 运行基本的测试套件。

.. code-block:: text

    $ pytest

上述测试是针对当前环境的，通常是有效的。当你提交拉取请求时， CI 会运
行全部测试。如果不想浪费时间，那么可以用 tox 运行所有测试。

.. code-block:: text

    $ tox


运行测试覆盖
~~~~~~~~~~~~~~~~~~~~~

生成一个报告，确定哪些代码未被测试覆盖，以指明工作的方向。使用
``coverage`` 运行 ``pytest`` 并生成一份报告。

如果你正在使用 GitHub Codespaces ，那么 ``coverage`` 已经安装好了，可
以跳过安装命令。

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

请阅读更多关于 `Sphinx <https://www.sphinx-doc.org/en/stable/>`__ 的
内容。
