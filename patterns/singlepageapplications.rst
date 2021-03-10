单页应用
========================

Flask 可以用为单页应用（ SPA ）提供服务，实现方式是把前端框架生成的静态文件
放在项目的子文件夹中。你还需要创建一个全包端点把所有请求指向你的 SPA 。

下面的演示如何用一个 API 为 SPA 提供服务::

    from flask import Flask, jsonify

    app = Flask(__name__, static_folder='app', static_url_path="/app")


    @app.route("/heartbeat")
    def heartbeat():
        return jsonify({"status": "healthy"})


    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return app.send_static_file("index.html")
