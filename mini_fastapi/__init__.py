# -*- coding: utf-8 -*-
"""mini_fastapi —— 课程实验：从零手写一个迷你 FastAPI。

门面（第 5 周 P20）：外部只写 `from mini_fastapi import Request, JSONResponse`，
不需要知道它们分别放在哪个文件里。
"""
from .message import Message
from .request import Request, parse_request
from .response import (
    DEFAULT_MEDIA_TYPE,
    REASON_PHRASES,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
    build_response,
    error,
    html,
    json_response,
    not_found,
    plain_text,
)
from .router import RouteTable, to_response
from .server import Server, read_request, run

__version__ = "0.9.0"        # 第 9 周：重构为对象 + 工程化 + Response 落地

__all__ = [
    "Message",
    "Request", "parse_request",
    "Response", "HTMLResponse", "PlainTextResponse", "JSONResponse", "RedirectResponse",
    "html", "plain_text", "json_response", "not_found", "error", "build_response",
    "REASON_PHRASES", "DEFAULT_MEDIA_TYPE",
    "RouteTable", "to_response",
    "Server", "run", "read_request",
    "__version__",
]
