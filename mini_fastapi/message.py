# -*- coding: utf-8 -*-
"""mini_fastapi.message —— HTTP 消息的共同底座。

第 6 周单继承机制的产物：Request 和 Response 都是「一种 HTTP 消息」，
把两边都要用的头部能力上移到 Message，子类只写自己不一样的部分。

课程约定：
  * raw_headers 保留浏览器/服务器写下的原始大小写，展示与转发时用；
  * _lower 是内部实现（单下画线前缀 = 别从外面碰），用于大小写不敏感查询；
  * RFC 9110 § 5.1：字段名大小写不敏感，字段值大小写敏感。
"""


class Message:
    """只管头部，只管怎么把头部变成报文文本。"""

    def __init__(self, headers=None):
        self.raw_headers = dict(headers or {})
        self._lower = {k.lower(): v for k, v in self.raw_headers.items()}

    def get_header(self, name, default=None):
        """忽略大小写地取一个头部。"""
        return self._lower.get(name.lower(), default)

    def set_header(self, name, value):
        """新增 / 覆盖一个头部；同名但大小写不同，也视为同一个头。"""
        value = str(value)
        for existing in list(self.raw_headers):
            if existing.lower() == name.lower() and existing != name:
                del self.raw_headers[existing]
        self.raw_headers[name] = value
        self._lower[name.lower()] = value

    def header_lines(self):
        """把头拼成 HTTP 报文格式，每行自带 CRLF。"""
        return "".join("%s: %s\r\n" % item for item in self.raw_headers.items())

    def __repr__(self):
        return "<%s headers=%d>" % (type(self).__name__, len(self.raw_headers))
