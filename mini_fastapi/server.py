# -*- coding: utf-8 -*-
"""mini_fastapi.server —— socket 五步法 + 请求解析 + 路由分发 + 响应对象。

第 1 周：socket 五步法，收发原始字节
第 3 周：手写路由表
第 5 周：parse_request() 返回 Request 对象
第 9 周：处理函数返回 Response 对象，to_bytes() 统一发出去
"""
import socket

from .request import parse_request
from .response import error
from .router import RouteTable


def read_request(conn):
    """从连接上读一条完整请求。

    比课堂的 conn.recv(4096) 稳一点：先读到 \\r\\n\\r\\n 拿到头，
    再按 Content-Length 把请求体补齐，避免 POST 大 body 被截断。
    """
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = conn.recv(4096)
        if not chunk:
            break
        buf += chunk

    head, sep, body = buf.partition(b"\r\n\r\n")
    if not sep:
        return buf

    length = 0
    for line in head.split(b"\r\n")[1:]:
        key, _, value = line.partition(b":")
        if key.strip().lower() == b"content-length":
            try:
                length = int(value.strip())
            except ValueError:
                length = 0

    while len(body) < length:
        chunk = conn.recv(4096)
        if not chunk:
            break
        body += chunk

    return head + sep + body


class Server:
    """一个极简的同步 HTTP 服务器（仅标准库）。"""

    def __init__(self, host="127.0.0.1", port=8000, routes=None):
        self.host = host
        self.port = port
        self.routes = RouteTable(routes or {})

    def add_route(self, path, handler):
        self.routes.add(path, handler)
        return handler

    def handle(self, request):
        """一次请求 -> 一个 Response 对象。异常统一兜底成 400 / 500。"""
        return self.routes.dispatch(request)

    def handle_raw(self, raw):
        """原始字节 -> 响应字节，方便在不启动 socket 的情况下做测试。"""
        request = parse_request(raw)
        print(request, flush=True)          # 第 5 周要求：控制台打印 Request 对象
        return self.handle(request).to_bytes()

    def handle_connection(self, conn):
        raw = read_request(conn)
        if not raw.strip():
            return                           # 浏览器探活，不该进解析流程
        try:
            conn.sendall(self.handle_raw(raw))
        except ValueError as exc:
            conn.sendall(error(400, "请求报文格式错误: %s" % exc).to_bytes())
        except Exception as exc:
            conn.sendall(error(500, "服务器内部错误: %s" % exc).to_bytes())

    def serve_forever(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        print("mini-fastapi 已启动: http://%s:%d  (Ctrl+C 停止)" % (self.host, self.port), flush=True)
        try:
            while True:
                conn, _ = server.accept()
                with conn:
                    conn.settimeout(10)
                    self.handle_connection(conn)
        except KeyboardInterrupt:
            print("\n服务器已停止", flush=True)
        finally:
            server.close()


def run(host="127.0.0.1", port=8000, routes=None):
    """建一个服务器并立刻启动，供示例脚本调用。"""
    Server(host, port, routes).serve_forever()
    return None
