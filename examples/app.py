# -*- coding: utf-8 -*-
"""示例应用入口：python examples/app.py

也可以直接 `python -m mini_fastapi`（推荐，不需要下面这段路径处理）。
这段 sys.path 是第 5 周「模块搜索路径」的实际应用：
直接运行 examples/app.py 时，解释器只把 examples/ 放进 sys.path，
得手动把仓库根目录加进去，才 import 得到内层的 mini_fastapi 包。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mini_fastapi.demo import create_app  # noqa: E402

if __name__ == "__main__":
    create_app().serve_forever()
