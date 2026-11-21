# -*- coding: utf-8 -*-
"""把本仓库推到 Gitee 的小助手（第 8 周 git 入门的实践）。

用法：在仓库根目录执行 `python push_to_gitee.py`，按提示粘贴仓库地址。
它只做三件事：关联远程 origin、确保分支叫 main、push -u 建立追踪关系。
需要你先在 gitee.com 上手工创建好空仓库（这一步涉及账号登录，脚本不代劳）。
"""
import subprocess
import sys


def git(*args, check=True):
    cmd = ["git"] + list(args)
    print("  > " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=check)


def main():
    url = input("请粘贴 Gitee 仓库的 HTTPS 地址（例如 https://gitee.com/用户名/mini-fastapi.git）: ").strip()
    if not url.startswith(("https://", "git@")):
        print("地址看起来不对，应该以 https:// 或 git@ 开头。已退出，没有改动仓库。")
        return 1

    print("\n[1/4] 检查已有远程...")
    result = subprocess.run(["git", "remote"], capture_output=True, text=True)
    if "origin" in result.stdout.split():
        git("remote", "remove", "origin")

    print("[2/4] 关联远程仓库 origin ...")
    git("remote", "add", "origin", url)

    print("[3/4] 主分支统一命名为 main ...")
    git("branch", "-M", "main")

    print("[4/4] 推送并建立 upstream 追踪关系 ...")
    try:
        git("push", "-u", "origin", "main")
    except subprocess.CalledProcessError:
        print("\n推送失败：请确认仓库地址正确、Gitee 账号/密码（或私人令牌）已配置，")
        print("以及仓库是空的（创建时不要勾选初始化 README / .gitignore）。")
        return 1

    print("\n完成！去 Gitee 刷新页面就能看到代码了。以后改动只需：")
    print("    git add . && git commit -m \"说明\" && git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
