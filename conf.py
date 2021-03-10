import packaging.version
# from collections import namedtuple
from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

#ProjectLink = namedtuple("ProjectLink", ("title", "url"))

# Project --------------------------------------------------------------

project = "Flask"
copyright = "2010 Pallets"
author = "Pallets"
release = "1.1.2"
version = "1.1.2"

# General --------------------------------------------------------------
language = 'zh_CN'

master_doc = "index"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.log_cabinet",
    "pallets_sphinx_themes",
    "sphinx_issues",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "werkzeug": ("https://werkzeug.palletsprojects.com/", None),
    "click": ("https://click.palletsprojects.com/", None),
    "jinja": ("http://jinja.pocoo.org/docs/", None),
    "itsdangerous": ("https://itsdangerous.palletsprojects.com/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/", None),
    "wtforms": ("https://wtforms.readthedocs.io/en/stable/", None),
    "blinker": ("https://pythonhosted.org/blinker/", None),
}
issues_github_path = "pallets/flask"

# HTML -----------------------------------------------------------------
html_theme = 'pallets_sphinx_themes'
html_theme_path = ["."]

# html_theme = "flask"
html_theme_options = {"index_sidebar_logo": False}
html_context = {
    "project_links": [
        ProjectLink("赞助 Pallets", "https://palletsprojects.com/donate"),
        ProjectLink("Flask 官网", "https://palletsprojects.com/p/flask/"),
        ProjectLink("PyPI 发行", "https://pypi.org/project/Flask/"),
        ProjectLink("源代码", "https://github.com/pallets/flask/"),
        ProjectLink("问题追踪", "https://github.com/pallets/flask/issues/"),
        ProjectLink("中文翻译", "https://github.com/dormouse/Flask_Docs_ZhCn"),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}
html_static_path = ["_static"]
html_favicon = "_static/flask-icon.png"
html_logo = "_static/flask-icon.png"
html_title = "Flask 中文文档（ 1.1.2 ）"
html_show_sourcelink = False

# LaTeX ----------------------------------------------------------------

latex_documents = [
    (master_doc, "Flask-{}.tex".format(version), html_title, author, "manual")
]

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
        url = "{0}master/{1}".format(base_url, text)
    else:
        url = "{0}{1}/{2}".format(base_url, release, text)

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
