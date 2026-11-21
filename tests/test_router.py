# -*- coding: utf-8 -*-
"""路由表与分发：路径匹配、404、三种历史返回值的兼容。"""
import unittest

from mini_fastapi import HTMLResponse, Request, Response, RouteTable, to_response


def index(request):
    return HTMLResponse("home")


def hello(request):
    return HTMLResponse("hello")


class TestRouter(unittest.TestCase):

    def setUp(self):
        self.routes = RouteTable({"/": index, "/hello": hello, "/api": index})

    def test_exact_match_first(self):
        handler, how = self.routes.match("/hello")
        self.assertIs(handler, hello)
        self.assertEqual(how, "精确")

    def test_prefix_match(self):
        handler, how = self.routes.match("/api/v1/items")
        self.assertIs(handler, index)
        self.assertTrue(how.startswith("前缀"))

    def test_root_does_not_swallow_404(self):
        """第 6 周 RouteTable 的小改进：根路径不参与前缀匹配，否则 404 永不出现。"""
        handler, _ = self.routes.match("/nope")
        self.assertIsNone(handler)

    def test_paths_and_add(self):
        self.assertEqual(self.routes.paths(), ["/", "/api", "/hello"])
        self.routes.add("/about", index)
        self.assertIn("/about", self.routes.paths())
        with self.assertRaises(TypeError):
            self.routes.add("/bad", "not callable")

    def test_to_response_three_forms(self):
        self.assertIsInstance(to_response(HTMLResponse("x")), Response)
        self.assertIsInstance(to_response("x"), HTMLResponse)
        legacy = to_response((404, "text/html; charset=utf-8", "<h1>404</h1>"))
        self.assertEqual(legacy.status_code, 404)
        with self.assertRaises(TypeError):
            to_response(123)

    def test_dispatch_404_is_response(self):
        req = Request("GET", "/nope", {}, "HTTP/1.1", {}, "")
        resp = self.routes.dispatch(req)
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
