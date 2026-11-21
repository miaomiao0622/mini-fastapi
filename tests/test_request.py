# -*- coding: utf-8 -*-
"""Request / parse_request 的单元测试（标准库 unittest，零第三方依赖）。"""
import unittest

from mini_fastapi import Message, Request, parse_request

BODY_POST = '{"name": "小明", "week": 9}'
RAW_POST = (
    "POST /api/echo?src=lab HTTP/1.1\r\n"
    "Host: 127.0.0.1:8000\r\n"
    "Content-Type: application/json\r\n"
    "Cookie: sid=abc123; theme=dark\r\n"
    "Content-Length: " + str(len(BODY_POST.encode("utf-8"))) + "\r\n"
    "\r\n" + BODY_POST
)


class TestRequest(unittest.TestCase):

    def test_parse_basic(self):
        req = parse_request(RAW_POST.encode("utf-8"))
        self.assertIsInstance(req, Request)
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.path, "/api/echo")     # query 不参与路径
        self.assertEqual(req.version, "HTTP/1.1")
        self.assertEqual(req.get_query("src"), "lab")

    def test_header_case_insensitive(self):
        req = parse_request(RAW_POST.encode("utf-8"))
        self.assertEqual(req.get_header("CONTENT-TYPE"), "application/json")
        self.assertEqual(req.get_header("content-type"), "application/json")
        self.assertEqual(req.get_header("Host"), "127.0.0.1:8000")
        self.assertEqual(req.get_header("missing", "默认值"), "默认值")
        self.assertIn("Cookie", req.raw_headers)     # 原始大小写仍保留

    def test_query_single_and_list(self):
        req = Request("GET", "/search", {"tag": ["python", "web"], "page": ["2"]},
                      "HTTP/1.1", {}, "")
        self.assertEqual(req.get_query("tag"), "python")
        self.assertEqual(req.get_query_list("tag"), ["python", "web"])
        self.assertEqual(req.get_query("missing"), None)
        self.assertEqual(req.get_query("missing", 1), 1)
        self.assertEqual(req.get_query_list("missing"), [])

    def test_json_and_text(self):
        req = parse_request(RAW_POST.encode("utf-8"))
        self.assertEqual(req.json(), {"name": "小明", "week": 9})
        self.assertIn("小明", req.text())
        empty = Request("GET", "/", {}, "HTTP/1.1", {}, "")
        self.assertIsNone(empty.json())              # 空 body 不报错
        self.assertFalse(empty.is_json())
        self.assertTrue(req.is_json())

    def test_cookies(self):
        req = parse_request(RAW_POST.encode("utf-8"))
        self.assertEqual(req.cookies(), {"sid": "abc123", "theme": "dark"})
        self.assertEqual(req.get_cookie("theme"), "dark")
        self.assertIsNone(req.get_cookie("nope"))

    def test_repr(self):
        req = parse_request(b"GET /hello?name=tom HTTP/1.1\r\nHost: x\r\n\r\n")
        self.assertEqual(repr(req), "<Request GET /hello?name=tom>")

    def test_malformed_request_raises(self):
        for raw in (b"GET\r\n\r\n", b"hello world\r\n\r\n", b"GET / HTTP/1.1\r\nBadHeader\r\n\r\n"):
            with self.assertRaises(ValueError):
                parse_request(raw)

    def test_inheritance_contract(self):
        """第 6 周要求：Request 继承 Message，且接口一行不变。"""
        req = Request("GET", "/", {}, "HTTP/1.1", {"X-A": "1"}, "")
        self.assertIsInstance(req, Message)
        self.assertNotIn("get_header", Request.__dict__)   # 来自基类，没有重写
        self.assertEqual(req.get_header("x-a"), "1")


if __name__ == "__main__":
    unittest.main()
