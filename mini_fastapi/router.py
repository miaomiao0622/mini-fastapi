# -*- coding: utf-8 -*-
"""mini_fastapi.router —— 路由表与分发。

第 3 周手写 dict 路由表 → 第 6 周扩展内置容器 RouteTable(dict)
→ 第 9 周：处理函数统一返回 Response 对象，同时也兼容旧的三元组写法。
★ 不使用装饰器：@app.get('/') 是第 11 周才解锁的语法。
"""
from .response import HTMLResponse, Response, not_found


class RouteTable(dict):
    """是 dict，也是路由表（第 6 周「只加不改」的例子）。"""

    def add(self, path, handler):
        if not callable(handler):
            raise TypeError("路由 %r 必须绑定一个可调用对象" % path)
        self[path] = handler
        return handler

    def match(self, path):
        """精确优先，再退化为前缀匹配。"""
        if path in self:
            return self[path], "精确"
        for prefix in self:
            # 根路径 '/' 是所有路径的前缀，若参与前缀匹配会让 404 永远不出现
            if prefix == "/":
                continue
            if path.startswith(prefix):
                return self[prefix], "前缀 " + prefix
        return None, None

    def paths(self):
        return sorted(self.keys())

    def dispatch(self, request):
        """路由三问：路径是什么 → 谁处理 → 返回什么。"""
        handler, _ = self.match(request.path)
        if handler is None:
            return not_found()
        return to_response(handler(request))


def to_response(result):
    """把处理函数的返回值统一变成 Response 对象。

    兼容三种历史写法，方便把前几周的代码平滑搬过来：
        Response 对象                     → 原样返回
        "字符串"                          → 当作 HTML
        (status, content_type, body)     → 第 3~5 周的三元组
    """
    if isinstance(result, Response):
        return result
    if isinstance(result, str):
        return HTMLResponse(result)
    if isinstance(result, (tuple, list)) and len(result) == 3:
        status, content_type, body = result
        return Response(body, status_code=status, media_type=content_type)
    raise TypeError("处理函数必须返回 Response / str / (status, content_type, body)")
