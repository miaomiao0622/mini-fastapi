# -*- coding: utf-8 -*-
"""mini_fastapi.request —— 请求对象与请求解析。

第 3 周：parse_request() 返回 dict
第 5 周：dict -> Request 对象（封装 = 数据 + 行为）
第 6 周：Request 改为继承 Message，头部能力交给基类
第 9 周：并入工程化项目，补齐 cookies() / is_json() 等基础能力
"""
import json
from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs

from .message import Message


class Request(Message):
    """一次 HTTP 请求。只保留「请求」特有的部分。"""

    def __init__(self, method, path, query, version, headers, body):
        super().__init__(headers)               # 头部交给基类，接口一行不变
        self.method = method
        self.path = path
        self.query = query or {}
        self.version = version
        self.body = body or ""
        self._cookies = self._parse_cookies()

    def _parse_cookies(self):
        """解析 Cookie 请求头，多个 cookie 用 '; ' 分隔（第 5 周课后作业）。"""
        raw = self.get_header("Cookie", "")
        if not raw:
            return {}
        jar = SimpleCookie()
        try:
            jar.load(raw)
        except Exception:
            return {}
        return {key: morsel.value for key, morsel in jar.items()}

    def cookies(self):
        """返回本次请求的全部 cookie（副本，改它不会影响对象）。"""
        return dict(self._cookies)

    def get_cookie(self, name, default=None):
        return self._cookies.get(name, default)

    def get_query(self, name, default=None):
        """取第一个查询值；没有则返回 default，省掉 [0] 和兜底。"""
        values = self.query.get(name)
        return values[0] if values else default

    def get_query_list(self, name):
        """取全部查询值（同名参数可出现多次），没有则空列表。"""
        return list(self.query.get(name, []))

    def text(self):
        """请求体原始文本。"""
        return self.body

    def json(self):
        """把请求体按 JSON 解析；空 body 返回 None，格式错由 json 模块抛出。"""
        if not self.body or not self.body.strip():
            return None
        return json.loads(self.body)

    def is_json(self):
        """判断是不是 JSON 请求，供 /info 等处理函数使用。"""
        ctype = (self.get_header("Content-Type", "") or "").lower()
        return "application/json" in ctype or ctype.endswith("+json")

    def __repr__(self):
        qs = "&".join("%s=%s" % (k, v[0]) for k, v in self.query.items())
        return "<Request %s %s%s>" % (self.method, self.path, "?" + qs if qs else "")


def parse_request(raw):
    """bytes / str -> Request。

    第 5 周 P18 定下的职责边界：解析协议是「协议层」的活，
    给属性赋值是「对象层」的活，所以写成模块函数而不是 Request(raw)。
    畸形报文不吞异常，交给服务器主循环统一兜底。
    """
    text = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
    head, _, body = text.partition("\r\n\r\n")
    lines = head.split("\r\n")

    parts = lines[0].split()
    if len(parts) != 3:
        raise ValueError("请求行格式错误: %r" % lines[0])
    method, target, version = parts

    parsed = urlparse(target)
    headers = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        key, colon, value = line.partition(":")   # 别用 split(':')，Host 里有冒号
        if not colon:
            raise ValueError("请求头格式错误: %r" % line)
        headers[key.strip()] = value.strip()

    return Request(
        method=method,
        path=parsed.path,
        query=parse_qs(parsed.query),
        version=version,
        headers=headers,
        body=body,
    )
