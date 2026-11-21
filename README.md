# mini-fastapi · 第 9 周实验作业

> 课程：面向对象分析与设计（24 级软工）
> 第 9 周主题：**python 工程化 + 完成 response 功能 + 交付 request + response + git 远程仓库**
> 版本：0.9.0 ｜ 运行环境：Python ≥ 3.12 ｜ 依赖：**零第三方库，全程标准库**

---

## 一、作业要求 → 本仓库的对应位置

| 作业要求（第 9 周实验作业） | 交付内容 | 位置 |
|---|---|---|
| 结合 git 知识，在 gitee 创建仓库，并实现远程仓库 | 本地仓库已初始化，含 `.gitignore`、规范提交历史、功能分支合并记录；Gitee 创建与推送步骤见第七节 | 仓库根目录 / `push_to_gitee.py` |
| 继续推进 python mini-fastapi 项目 · **python 工程化** | 内外两层同名目录、`pyproject.toml`、`requirements*.txt`、虚拟环境说明、`tests/` 独立测试、README | 整个仓库 |
| 完成 **response 功能**（参考 fastapi 框架，最基础部分） | `Response` 基类 + `render()` / `init_headers()` / `to_bytes()`，以及 `HTMLResponse` / `PlainTextResponse` / `JSONResponse` / `RedirectResponse` | `mini_fastapi/response.py` |
| 本次作业要交 **request + response** | `Request` 对象 + `parse_request()` 已并入工程化项目，与 `Response` 在示例应用里成对使用 | `mini_fastapi/request.py`、`mini_fastapi/demo.py` |

---

## 二、这门课的项目走到哪一步了

课程用「从零手写一个迷你 FastAPI」串起整个学期的面向对象知识点：

| 周次 | 课堂内容 | 在本项目里的落点 |
|---|---|---|
| 第 1 周 | socket 五步法、原生 HTTP 处理、Content-Length 用字节数 | `server.py`、`Response.init_headers()` |
| 第 3 周 | 请求解析成 dict、手写路由表 | `parse_request()`、`RouteTable` |
| 第 5 周 | 封装：`dict` → `Request` 对象；模块与包；工程化骨架 | `Request`、`__init__.py` 门面、项目目录 |
| 第 6 周 | 单继承：抽出 `Message` 基类；提前给出 `Response` 形状 | `message.py`、`Request(Message)` / `Response(Message)` |
| 第 7 周 | 响应工厂：`build_response()` → `Response` 对象 | `response.py`（含兼容函数 `build_response`） |
| 第 8 周 | git 入门：init / add / commit / .gitignore / 分支 / remote / push | 本仓库的提交历史与第七节 |
| **第 9 周** | **重构为对象、工程化、Response 落地** | **本仓库** |

★ 课程规定：**第 11 周才学装饰器**，因此本项目没有 `@app.get()`、`@property` 等任何装饰器，路由是手工填进字典的。

---

## 三、目录结构

```
mini-fastapi/                  ← 仓库根目录（外层），git 就建在这里
├── mini_fastapi/              ← 真正的包（内层，import 时用的是这一层）
│   ├── __init__.py            ← 门面：对外导出名单 __all__
│   ├── message.py             ← Message 基类（头部能力，Request/Response 共用）
│   ├── request.py             ← Request + parse_request
│   ├── response.py            ← ★ 本周重点：Response 体系
│   ├── router.py              ← RouteTable(dict) + 分发
│   ├── server.py              ← socket 五步法 + 主循环
│   ├── demo.py                ← 示例应用，7 个路由
│   └── __main__.py            ← 支持 python -m mini_fastapi
├── examples/app.py            ← 另一个启动方式（演示 sys.path 处理）
├── tests/                     ← 28 个单元测试，不和源码混在一起
│   ├── test_request.py
│   ├── test_response.py
│   ├── test_router.py
│   └── test_server.py
├── pyproject.toml             ← 项目元数据、构建配置、可执行入口
├── requirements.txt           ← 运行时依赖：空（课程要求零第三方依赖）
├── requirements-dev.txt       ← 可选：pytest / ruff
├── .gitignore                 ← 忽略 __pycache__、.venv、构建产物等
├── push_to_gitee.py           ← 推送到 Gitee 的小助手
└── README.md                  ← 本文件
```

---

## 四、快速开始（Windows）

```bash
cd mini-fastapi

# 1) 建虚拟环境（第 5 周工程化：依赖不装到全局）
python -m venv .venv
.venv\Scripts\activate

# 2) 启动服务器
python -m mini_fastapi
# 或：python examples/app.py

# 3) 浏览器打开
#    http://127.0.0.1:8000/
#    http://127.0.0.1:8000/hello?name=Tom
#    http://127.0.0.1:8000/info?a=1&a=2     ← HTML 表格展示本次请求全部信息
#    http://127.0.0.1:8000/api/time
#    http://127.0.0.1:8000/nope             ← 404

# 4) 跑测试（不需要装 pytest，标准库 unittest 即可）
python -m unittest discover -s tests -v
```

POST 一个 JSON 到 `/echo`（PowerShell 或 cmd 里用 curl）：

```bash
curl -X POST http://127.0.0.1:8000/echo -H "Content-Type: application/json" -d "{\"name\":\"小明\",\"week\":9}"
# 返回： {"ok": true, "echo": {"name": "小明", "week": 9}}
```

---

## 五、核心设计说明

### 1. `Message`：共同底座（第 6 周继承）

`Request` 和 `Response` 都要「按大小写不敏感取头部」「把头拼成报文行」，
所以把这些能力上移到 `Message`，子类只写自己不一样的部分：

```python
class Message:
    def __init__(self, headers=None):
        self.raw_headers = dict(headers or {})        # 保留原始写法
        self._lower = {k.lower(): v for k, v in self.raw_headers.items()}  # 内部副本
    def get_header(self, name, default=None): ...
    def set_header(self, name, value): ...
    def header_lines(self): ...
```

`_lower` 的单下画线前缀 = 「内部实现，别从外面碰」（第 5 周访问控制约定）。

### 2. `Request`：数据与行为装进同一个盒子

六个属性 `method / path / query / version / headers / body`，加上
`get_header()`（继承）、`get_query()`、`get_query_list()`、`text()`、`json()`、
`cookies()`、`is_json()`、`__repr__()`。

解析与构造分开：`parse_request(raw) -> Request`，畸形报文抛 `ValueError`，
由服务器主循环统一回 400 —— 这一层不自作主张（第 5 周 P18/P19）。

### 3. `Response`：参考 FastAPI 最基础的部分

对照 Starlette/FastAPI 的 `Response(content, status_code, headers, media_type)`：

| FastAPI | 本项目 | 说明 |
|---|---|---|
| `Response.render(content)` | `render()` | 把内容变成正文；`JSONResponse` 覆盖它做 `json.dumps` |
| `Response.init_headers(headers)` | `init_headers()` | 自动补 `Content-Type` 与 `Content-Length` |
| `JSONResponse` / `HTMLResponse` / `PlainTextResponse` | 同名子类 | 只改 `media_type` / `render` |
| `RedirectResponse` | `RedirectResponse` | 额外设置 `Location` 头 |
| `response.body` / `status_code` | 同名字段 | 便于对照真实框架 |

`to_bytes()` 拼出完整报文，可直接交给 `socket.sendall()`：

```
HTTP/1.1 200 OK\r\n
Content-Type: text/html; charset=utf-8\r\n
Content-Length: 19\r\n        ← 字节数，不是字符数（第 1 周强调过）
\r\n
<h1>你好，世界</h1>
```

同时保留第 3~5 周的自由函数 `build_response(status, content_type, body)`，
但现在它**返回 Response 对象**，正是「重构为对象」这一步的证据。

### 4. 路由与服务器

`RouteTable(dict)` 继承内置容器（第 6 周「只加不改」）：`add()` 手工注册、
`match()` 精确优先再前缀、`dispatch()` 分发。做了一处小改进：根路径 `/`
不参与前缀匹配，否则它是一切路径的前缀，404 永远不出现。

处理函数统一返回 `Response` 对象；`to_response()` 也兼容字符串和旧版
`(status, content_type, body)` 三元组，前几周的代码可以直接搬过来。

`read_request()` 比课堂的 `recv(4096)` 稳一点：先读到 `\r\n\r\n`，
再按 `Content-Length` 把请求体补齐，避免 POST 大 body 被截断。

---

## 六、验收清单

- [ ] `python -m unittest discover -s tests -v` → 28 个测试全部通过
- [ ] 浏览器访问 `/` 能看到首页
- [ ] 访问 `/hello?name=Tom` 显示 `Hello, Tom`
- [ ] POST JSON 到 `/echo`，原样回显；中文不乱码
- [ ] 访问 `/info` 用 HTML 表格列出方法、路径、查询参数、全部请求头、是否 JSON 请求
- [ ] 访问不存在的路径返回 `404 Not Found`
- [ ] 服务器控制台打印的是 `<Request GET /hello?...>` 对象，不是字典
- [ ] `git log --oneline --graph --all` 能看到初始化、功能分支、合并、测试的提交历史
- [ ] Gitee 上能看到推送上去的代码（第七节）

---

## 七、git / Gitee：从本地仓库到远程仓库

本仓库已经按第 8 周讲义做完了本地部分：`git init` → `.gitignore` →
多次 `git add` / `git commit` → 在 `feature/request-response` 功能分支上开发 →
合并回 `main`。常用查看命令：

```bash
git status
git log --oneline --graph --all       # 看提交与分支图
git branch -a                         # 看本地 + 远程分支
git remote -v                         # 看远程关联
```

**远程仓库需要你本人完成（涉及 Gitee 账号登录）**，三步：

1. 打开 <https://gitee.com>，登录（没有账号先注册），点右上角「+」→「新建仓库」。
   - 仓库名建议 `mini-fastapi`，**不要勾选**「初始化仓库 / 添加 .gitignore / 添加开源许可证」，保持空仓库。
2. 复制仓库的 HTTPS 地址，形如 `https://gitee.com/你的用户名/mini-fastapi.git`。
3. 在仓库根目录执行下面任意一种：

```bash
# 方式 A：小助手，按提示粘贴地址即可
python push_to_gitee.py

# 方式 B：手写命令
git remote add origin https://gitee.com/你的用户名/mini-fastapi.git
git branch -M main
git push -u origin main          # -u 建立追踪关系，以后直接 git push
```

第一次推送会要求输入 Gitee 用户名与密码（或私人令牌）。
以后改代码就走 `git add .` → `git commit -m "说明"` → `git push`。

> 若 `git commit` 提示身份未配置，在仓库内执行（只影响本仓库，不改全局）：
> `git config user.name "你的姓名"` / `git config user.email "你的邮箱"`

---

## 八、常见问题

**Q：要不要 pip install？**
A：不用。项目零第三方依赖，`requirements.txt` 为空是正常的；`requirements-dev.txt` 里的 pytest/ruff 只是可选工具。

**Q：为什么不能用 `@app.get("/")`？**
A：装饰器属于第 11 周，本学期要求「先手工做，再学工具替你做」，所以路由是手写字典。

**Q：中文页面乱码 / 浏览器一直转圈？**
A：检查 `Content-Length` 是否用了 `len(body.encode("utf-8"))`。中文一个字符占 3 字节，用字符数会算少，浏览器会一直等。

**Q：`python examples/app.py` 报找不到 mini_fastapi？**
A：直接运行子目录里的脚本时，仓库根不在模块搜索路径上；`examples/app.py` 顶部已经用 `sys.path` 处理。更推荐 `python -m mini_fastapi`。

---

## 九、说明

本项目为课程实验代码，仅使用 Python 标准库，未引入 FastAPI / Starlette 源码；
`Response` 的命名与分层参考其公开设计思路，实现为课堂要求的最基础版本。
