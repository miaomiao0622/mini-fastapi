# -*- coding: utf-8 -*-
"""mini_fastapi.demo —— 示例应用：把 Request 和 Response 一起用起来。

这些处理函数就是第 9 周作业「本次作业要交（request + response）」的验收样例：
每个函数收一个 Request，返回一个 Response 子类对象。
"""
import html as html_module
from datetime import datetime

from .response import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    json_response,
)
from .server import Server


def index(request):
    return HTMLResponse(
        "<h1>mini-fastapi</h1>"
        "<p>第 9 周：Request + Response 已就位</p>"
        "<ul>"
        "<li><a href='/hello?name=Tom'>/hello?name=Tom</a></li>"
        "<li><a href='/info?a=1&a=2'>/info</a> （把这次请求全部信息列成表格）</li>"
        "<li><a href='/api/time'>/api/time</a></li>"
        "<li><a href='/nope'>/nope</a> （看看 404 长什么样）</li>"
        "</ul>"
    )


def hello(request):
    name = request.get_query("name", "world")        # Request 的行为
    return HTMLResponse("<h1>Hello, %s</h1>" % html_module.escape(name))


def echo(request):
    """POST 一个 JSON 到 /echo，原样回显。"""
    data = request.json() or {}                      # 空 body 返回 None
    return json_response({"ok": True, "echo": data})


def info(request):
    """第 5 周课后作业：用 HTML 表格展示本次请求的全部信息。"""
    rows = [
        ("方法 method", request.method),
        ("路径 path", request.path),
        ("协议版本 version", request.version),
        ("查询参数 query", repr(request.query)),
        ("是否 JSON 请求", "是" if request.is_json() else "否"),
        ("请求体 body", request.text() or "（空）"),
        ("Cookies", repr(request.cookies())),
        ("get_header('content-TYPE')", repr(request.get_header("content-TYPE"))),
    ]
    for key, value in request.raw_headers.items():
        rows.append(("Header: " + key, value))
    body = ["<h1>请求信息 /info</h1>", "<table border='1' cellpadding='6'>",
            "<tr><th>项目</th><th>值</th></tr>"]
    for key, value in rows:
        body.append("<tr><td>%s</td><td>%s</td></tr>" % (
            html_module.escape(str(key)), html_module.escape(str(value))))
    body.append("</table>")
    return HTMLResponse("".join(body))


def api_time(request):
    return JSONResponse({"now": datetime.now().isoformat(timespec="seconds"),
                         "path": request.path})


def about(request):
    return PlainTextResponse("mini-fastapi 0.9.0 - 课程实验：手写一个迷你 FastAPI")


def go_home(request):
    return RedirectResponse("/")


def create_app(host="127.0.0.1", port=8000):
    """手工填路由表（第 11 周才会用 @app.get 替换这一步）。"""
    app = Server(host, port)
    app.add_route("/", index)
    app.add_route("/hello", hello)
    app.add_route("/echo", echo)
    app.add_route("/info", info)
    app.add_route("/api/time", api_time)
    app.add_route("/about", about)
    app.add_route("/go", go_home)
    return app


def main():
    create_app().serve_forever()
