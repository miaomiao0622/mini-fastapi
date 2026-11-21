# -*- coding: utf-8 -*-
"""Response 体系的单元测试：状态行、头部、Content-Length 字节数、子类渲染。"""
import unittest

from mini_fastapi import (
    HTMLResponse, JSONResponse, Message, PlainTextResponse,
    RedirectResponse, Response, build_response,
)


class TestResponse(unittest.TestCase):

    def test_status_line_and_headers(self):
        raw = Response("<h1>hi</h1>", 200, media_type="text/html; charset=utf-8").to_bytes()
        text = raw.decode("utf-8")
        head, _, body = text.partition("\r\n\r\n")
        self.assertTrue(head.startswith("HTTP/1.1 200 OK\r\n"))
        self.assertIn("Content-Type: text/html; charset=utf-8\r\n", text)
        self.assertIn("Content-Length: %d\r\n" % len("<h1>hi</h1>".encode("utf-8")), text)
        self.assertEqual(body, "<h1>hi</h1>")
        self.assertTrue(text.endswith("\r\n\r\n<h1>hi</h1>"))

    def test_content_length_uses_bytes_not_characters(self):
        """第 1 周的老坑：中文正文，字符数 != UTF-8 字节数。"""
        body = "<h1>你好，世界</h1>"
        resp = HTMLResponse(body)
        self.assertNotEqual(len(body), len(body.encode("utf-8")))
        self.assertEqual(resp.get_header("content-length"),
                         str(len(body.encode("utf-8"))))
        self.assertEqual(len(resp.to_bytes().split(b"\r\n\r\n", 1)[1]),
                         len(body.encode("utf-8")))

    def test_set_body_updates_length(self):
        resp = PlainTextResponse("abc")
        self.assertEqual(resp.get_header("Content-Length"), "3")
        resp.set_body("abcdef")
        self.assertEqual(resp.get_header("Content-Length"), "6")

    def test_set_header_same_name_different_case(self):
        resp = Response("x", headers={"Content-Type": "text/plain"})
        resp.set_header("content-type", "text/html")
        self.assertEqual(len(resp.raw_headers), 2)   # Content-Type + Content-Length
        self.assertEqual(resp.get_header("CONTENT-TYPE"), "text/html")

    def test_json_response_keeps_chinese(self):
        resp = JSONResponse({"msg": "你好", "week": 9})
        self.assertEqual(resp.body, '{"msg": "你好", "week": 9}')
        self.assertIn("application/json", resp.get_header("content-type"))
        self.assertIn("你好", resp.to_bytes().decode("utf-8"))

    def test_subclasses(self):
        self.assertIn("text/html", HTMLResponse("x").media_type)
        self.assertIn("text/plain", PlainTextResponse("x").media_type)
        redirect = RedirectResponse("/hello", status_code=302)
        self.assertTrue(redirect.to_bytes().startswith(b"HTTP/1.1 302 Found\r\n"))
        self.assertEqual(redirect.get_header("location"), "/hello")

    def test_status_codes(self):
        self.assertTrue(Response("x", 404).to_bytes().startswith(b"HTTP/1.1 404 Not Found"))
        self.assertTrue(Response("x", 500).to_bytes().startswith(
            b"HTTP/1.1 500 Internal Server Error"))
        self.assertTrue(Response("x", 599).to_bytes().startswith(b"HTTP/1.1 599 Unknown"))

    def test_legacy_build_response_returns_object(self):
        resp = build_response(404, "text/html; charset=utf-8", "<h1>404</h1>")
        self.assertIsInstance(resp, Response)
        self.assertEqual(resp.status_code, 404)

    def test_inheritance_contract(self):
        resp = Response("x")
        self.assertIsInstance(resp, Message)
        self.assertNotIn("get_header", Response.__dict__)


if __name__ == "__main__":
    unittest.main()
