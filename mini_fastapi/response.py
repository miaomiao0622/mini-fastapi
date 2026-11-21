# -*- coding: utf-8 -*-
"""mini_fastapi.response —— 第 9 周要交付的 response 功能。

参考 FastAPI / Starlette 最基础的那部分：
    Response(content, status_code, headers, media_type)
      ├── render(content)          → 把内容变成正文文本
      ├── init_headers()           → Content-Type / Content-Length
      ├── HTMLResponse / PlainTextResponse / JSONResponse / RedirectResponse
      └── to_bytes()               → 可以直接 sendall 的完整报文字节串

与课程第 6 周的继承主线对齐：Response 继承 Message，
和 Request 共用同一份 get_header / set_header / header_lines。
★ 全程不使用装饰器（@ 是第 11 周的内容），一律普通方法。
"""
import json

from .message import Message

REASON_PHRASES = {
    200: "OK",
    201: "Created",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    304: "Not Modified",
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    418: "I'm a Teapot",
    500: "Internal Server Error",
    501: "Not Implemented",
    503: "Service Unavailable",
}

DEFAULT_MEDIA_TYPE = "text/plain; charset=utf-8"


class Response(Message):
    """一次 HTTP 响应。"""

    media_type = None          # 子类给出自己的默认值
    charset = "utf-8"

    def __init__(self, content="", status_code=200, headers=None, media_type=None):
        super().__init__(headers)
        self.status_code = int(status_code)
        self.content = content
        self.media_type = media_type or self.media_type or DEFAULT_MEDIA_TYPE
        self.body = self.render(content)
        self.init_headers()

    def render(self, content):
        """把内容渲染成正文字符串；子类可以覆盖（JSONResponse 就覆盖了它）。"""
        return "" if content is None else str(content)

    def init_headers(self):
        """参考 FastAPI 的 init_headers：补 Content-Type 与 Content-Length。"""
        self.set_header("Content-Type", self.media_type)
        # ★ 第 1 周的老坑：Content-Length 必须是 UTF-8 字节数，不是字符数
        self.set_header("Content-Length", str(len(self.body.encode(self.charset))))

    def reason(self):
        return REASON_PHRASES.get(self.status_code, "Unknown")

    def set_body(self, body):
        """改正文后长度必须跟着重算，否则浏览器会一直转圈。"""
        self.body = self.render(body)
        self.set_header("Content-Length", str(len(self.body.encode(self.charset))))
        return self

    def to_bytes(self):
        """拼出完整 HTTP/1.1 响应报文，可直接交给 socket.sendall()。"""
        status_line = "HTTP/1.1 %d %s\r\n" % (self.status_code, self.reason())
        head = status_line + self.header_lines() + "\r\n"
        return head.encode(self.charset) + self.body.encode(self.charset)

    def __repr__(self):
        return "<Response %d %s content-type=%s bytes=%d>" % (
            self.status_code, self.reason(), self.media_type,
            len(self.body.encode(self.charset)),
        )


class HTMLResponse(Response):
    media_type = "text/html; charset=utf-8"


class PlainTextResponse(Response):
    media_type = "text/plain; charset=utf-8"


class JSONResponse(Response):
    media_type = "application/json; charset=utf-8"

    def render(self, content):
        return json.dumps(content, ensure_ascii=False)


class RedirectResponse(Response):
    media_type = "text/plain; charset=utf-8"

    def __init__(self, url, status_code=307, headers=None):
        super().__init__("", status_code=status_code, headers=headers)
        self.set_header("Location", url)


# ── 便捷工厂函数（普通函数，不是装饰器）──────────────────────────────
def html(body, status_code=200, headers=None):
    return HTMLResponse(body, status_code, headers=headers)


def plain_text(body, status_code=200, headers=None):
    return PlainTextResponse(body, status_code, headers=headers)


def json_response(data, status_code=200, headers=None):
    return JSONResponse(data, status_code, headers=headers)


def not_found(message="404 Not Found"):
    return HTMLResponse("<h1>%s</h1>" % message, status_code=404)


def error(status_code, message):
    return JSONResponse({"error": message}, status_code=status_code)


def build_response(status=200, content_type="text/html; charset=utf-8", body=""):
    """第 3~5 周的自由函数接口，保留兼容。

    以前它返回字符串，现在返回一个 Response 对象 —— 这正是第 7 周
    「响应工厂」与第 9 周「重构为对象」要看到的变化。
    """
    return Response(body, status_code=status, media_type=content_type)
