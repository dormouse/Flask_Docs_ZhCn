import packaging.version
# from collections import namedtuple
from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

#ProjectLink = namedtuple("ProjectLink", ("title", "url"))

# Project --------------------------------------------------------------

project = "Flask"
copyright = "2010 Pallets"
author = "Pallets"
# release = "2.1.2"
# version = "2.1.2"
release, version = get_version("Flask")

# General --------------------------------------------------------------
language = 'zh_CN'

default_role = "code"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.log_cabinet",
    "sphinx_tabs.tabs",
    "pallets_sphinx_themes",
]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_preserve_defaults = True
extlinks = {
    "issue": ("https://github.com/pallets/flask/issues/%s", "#%s"),
    "pr": ("https://github.com/pallets/flask/pull/%s", "#%s"),
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "werkzeug": ("https://werkzeug.palletsprojects.com/", None),
    "click": ("https://click.palletsprojects.com/", None),
    "jinja": ("https://jinja.palletsprojects.com/", None),
    "itsdangerous": ("https://itsdangerous.palletsprojects.com/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/", None),
    "wtforms": ("https://wtforms.readthedocs.io/", None),
    "blinker": ("https://blinker.readthedocs.io/", None),
}
# HTML -----------------------------------------------------------------
# html_theme = 'flask'
# html_theme_path = ["./pallets_sphinx_themes"]

html_theme = "flask"
html_theme_options = {"index_sidebar_logo": False}
html_context = {
    "project_links": [
        ProjectLink("赞助", "https://palletsprojects.com/donate"),
        ProjectLink("PyPI 发行", "https://pypi.org/project/Flask/"),
        ProjectLink("源代码", "https://github.com/pallets/flask/"),
        ProjectLink("问题追踪", "https://github.com/pallets/flask/issues/"),
        ProjectLink("聊天", "https://discord.gg/pallets"),
        ProjectLink("翻译源代码", "https://github.com/dormouse/Flask_Docs_ZhCn"),
        ProjectLink("翻译问题反馈", "https://github.com/dormouse/Flask_Docs_ZhCn/issues"),
        ProjectLink("联系翻译作者", "dormouse.young@gmail.com"),
        ProjectLink("翻译版权声明：CC BY-NC-SA 4.0", "https://creativecommons.org/licenses/by-nc-sa/4.0/"),
    ],
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html", "ethicalads.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html", "ethicalads.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html", "ethicalads.html"]}
html_static_path = ["_static"]
html_favicon = "_static/shortcut-icon.png"
html_logo = "_static/flask-vertical.png"
html_title = f"Flask中文文档({version})"
html_show_sourcelink = False

# Local Extensions -----------------------------------------------------


def github_link(name, rawtext, text, lineno, inliner, options=None, content=None):
    app = inliner.document.settings.env.app
    release = app.config.release
    base_url = "https://github.com/pallets/flask/tree/"

    if text.endswith(">"):
        words, text = text[:-1].rsplit("<", 1)
        words = words.strip()
    else:
        words = None
    if packaging.version.parse(release).is_devrelease:
        url = f"{base_url}main/{text}"
    else:
        url = f"{base_url}{release}/{text}"

    if words is None:
        words = url

    from docutils.nodes import reference
    from docutils.parsers.rst.roles import set_classes

    options = options or {}
    set_classes(options)
    node = reference(rawtext, words, refuri=url, **options)
    return [node], []


def setup(app):
    app.add_role("gh", github_link)
