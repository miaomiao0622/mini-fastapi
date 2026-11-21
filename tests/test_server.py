# -*- coding: utf-8 -*-
"""端到端测试：原始报文进 -> 完整 HTTP 响应字节出，再走一次真实 socket。"""
import json
import socket
import threading
import unittest

from mini_fastapi import read_request
from mini_fastapi.demo import create_app


class TestServer(unittest.TestCase):

    def setUp(self):
        self.app = create_app()

    def test_handle_raw_get(self):
        raw = b"GET /hello?name=Tom HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        out = self.app.handle_raw(raw).decode("utf-8")
        self.assertTrue(out.startswith("HTTP/1.1 200 OK"))
        self.assertIn("Hello, Tom", out)

    def test_handle_raw_post_json(self):
        body = json.dumps({"name": "小明", "week": 9}, ensure_ascii=False)
        raw = ("POST /echo HTTP/1.1\r\nHost: 127.0.0.1\r\n"
               "Content-Type: application/json\r\n"
               "Content-Length: %d\r\n\r\n%s"
               % (len(body.encode("utf-8")), body)).encode("utf-8")
        out = self.app.handle_raw(raw).decode("utf-8")
        self.assertIn("application/json", out)
        self.assertIn('"echo"', out)
        self.assertIn("小明", out)

    def test_404_and_info(self):
        out = self.app.handle_raw(
            b"GET /nope HTTP/1.1\r\nHost: x\r\n\r\n").decode("utf-8")
        self.assertTrue(out.startswith("HTTP/1.1 404 Not Found"))

        info = self.app.handle_raw(
            b"GET /info?a=1&a=2 HTTP/1.1\r\nHost: x\r\nCookie: sid=abc\r\n\r\n"
        ).decode("utf-8")
        self.assertIn("<table", info)
        self.assertIn("sid", info)

    def test_bad_request_is_400(self):
        # handle_raw 里的解析异常由 handle_connection 兜底，这里直接验证兜底响应
        from mini_fastapi import error
        self.assertTrue(error(400, "bad").to_bytes().startswith(b"HTTP/1.1 400 Bad Request"))

    def test_real_socket_with_split_body(self):
        """头与体分两次发，验证 read_request 会按 Content-Length 把体补齐。"""
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]

        def worker():
            conn, _ = listener.accept()
            with conn:
                conn.settimeout(5)
                raw = read_request(conn)
                conn.sendall(self.app.handle_raw(raw))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        body = json.dumps({"msg": "分两次发送"}, ensure_ascii=False)
        head = ("POST /echo HTTP/1.1\r\nHost: 127.0.0.1\r\n"
                "Content-Type: application/json\r\n"
                "Content-Length: %d\r\n\r\n" % len(body.encode("utf-8")))
        client = socket.create_connection(("127.0.0.1", port), timeout=5)
        client.sendall(head.encode("utf-8"))
        client.sendall(body.encode("utf-8"))
        chunks = []
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        client.close()
        thread.join(timeout=5)
        listener.close()

        out = b"".join(chunks).decode("utf-8")
        self.assertTrue(out.startswith("HTTP/1.1 200 OK"))
        self.assertIn("分两次发送", out)


if __name__ == "__main__":
    unittest.main()
