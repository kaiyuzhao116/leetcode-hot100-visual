#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描题解目录 -> 生成 README.md 与 index.html。

用法:
    python tools/build.py

约定:
    - 每题一个目录，目录名形如 `1.两数之和` / `146.LRU缓存`
    - 目录下的 *.html 即为该题的图解（可多篇）
    - `_backup/` 为草稿目录，不参与发布
"""
import os
import re
import sys
import html
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = "kaiyuzhao116"
REPO = "leetcode-hot100-visual"
SITE = "https://%s.github.io/%s/" % (OWNER, REPO)
REPO_URL = "https://github.com/%s/%s" % (OWNER, REPO)

# ---------------------------------------------------------------- 官方题单
# (题号, 题目名, 难度)
CATEGORIES = [
    ("哈希", [(1, "两数之和", "简单"), (49, "字母异位词分组", "中等"), (128, "最长连续序列", "中等")]),
    ("双指针", [(283, "移动零", "简单"), (11, "盛最多水的容器", "中等"), (15, "三数之和", "中等"), (42, "接雨水", "困难")]),
    ("滑动窗口", [(3, "无重复字符的最长子串", "中等"), (438, "找到字符串中所有字母异位词", "中等")]),
    ("子串", [(560, "和为 K 的子数组", "中等"), (239, "滑动窗口最大值", "困难"), (76, "最小覆盖子串", "困难")]),
    ("普通数组", [(53, "最大子数组和", "中等"), (56, "合并区间", "中等"), (189, "轮转数组", "中等"),
                (238, "除自身以外数组的乘积", "中等"), (41, "缺失的第一个正数", "困难")]),
    ("矩阵", [(73, "矩阵置零", "中等"), (54, "螺旋矩阵", "中等"), (48, "旋转图像", "中等"), (240, "搜索二维矩阵 II", "中等")]),
    ("链表", [(160, "相交链表", "简单"), (206, "反转链表", "简单"), (234, "回文链表", "简单"),
              (141, "环形链表", "简单"), (142, "环形链表 II", "中等"), (21, "合并两个有序链表", "简单"),
              (2, "两数相加", "中等"), (19, "删除链表的倒数第 N 个结点", "中等"), (24, "两两交换链表中的节点", "中等"),
              (25, "K 个一组翻转链表", "困难"), (138, "随机链表的复制", "中等"), (148, "排序链表", "中等"),
              (23, "合并 K 个升序链表", "困难"), (146, "LRU 缓存", "中等")]),
    ("二叉树", [(94, "二叉树的中序遍历", "简单"), (104, "二叉树的最大深度", "简单"), (226, "翻转二叉树", "简单"),
                (101, "对称二叉树", "简单"), (543, "二叉树的直径", "简单"), (102, "二叉树的层序遍历", "中等"),
                (108, "将有序数组转换为二叉搜索树", "简单"), (98, "验证二叉搜索树", "中等"),
                (230, "二叉搜索树中第 K 小的元素", "中等"), (199, "二叉树的右视图", "中等"),
                (114, "二叉树展开为链表", "中等"), (105, "从前序与中序遍历序列构造二叉树", "中等"),
                (437, "路径总和 III", "中等"), (236, "二叉树的最近公共祖先", "中等"),
                (124, "二叉树中的最大路径和", "困难")]),
    ("图论", [(200, "岛屿数量", "中等"), (994, "腐烂的橘子", "中等"), (207, "课程表", "中等"), (208, "实现 Trie (前缀树)", "中等")]),
    ("回溯", [(46, "全排列", "中等"), (78, "子集", "中等"), (17, "电话号码的字母组合", "中等"),
              (39, "组合总和", "中等"), (22, "括号生成", "中等"), (79, "单词搜索", "中等"),
              (131, "分割回文串", "中等"), (51, "N 皇后", "困难")]),
    ("二分查找", [(35, "搜索插入位置", "简单"), (74, "搜索二维矩阵", "中等"),
                 (34, "在排序数组中查找元素的第一个和最后一个位置", "中等"), (33, "搜索旋转排序数组", "中等"),
                 (153, "寻找旋转排序数组中的最小值", "中等"), (4, "寻找两个正序数组的中位数", "困难")]),
    ("栈", [(20, "有效的括号", "简单"), (155, "最小栈", "中等"), (394, "字符串解码", "中等"),
             (739, "每日温度", "中等"), (84, "柱状图中最大的矩形", "困难")]),
    ("堆", [(215, "数组中的第 K 个最大元素", "中等"), (347, "前 K 个高频元素", "中等"), (295, "数据流的中位数", "困难")]),
    ("贪心算法", [(121, "买卖股票的最佳时机", "简单"), (55, "跳跃游戏", "中等"),
                 (45, "跳跃游戏 II", "中等"), (763, "划分字母区间", "中等")]),
    ("动态规划", [(70, "爬楼梯", "简单"), (118, "杨辉三角", "简单"), (198, "打家劫舍", "中等"),
                 (279, "完全平方数", "中等"), (322, "零钱兑换", "中等"), (139, "单词拆分", "中等"),
                 (300, "最长递增子序列", "中等"), (152, "乘积最大子数组", "中等"),
                 (416, "分割等和子集", "中等"), (32, "最长有效括号", "困难")]),
    ("多维动态规划", [(62, "不同路径", "中等"), (64, "最小路径和", "中等"), (5, "最长回文子串", "中等"),
                     (1143, "最长公共子序列", "中等"), (72, "编辑距离", "中等")]),
    ("技巧", [(136, "只出现一次的数字", "简单"), (169, "多数元素", "简单"),
             (75, "颜色分类", "中等"), (31, "下一个排列", "中等"), (287, "寻找重复数", "中等")]),
]

DIFF_ICON = {"简单": "🟢", "中等": "🟡", "困难": "🔴"}
DIFF_CLASS = {"简单": "easy", "中等": "medium", "困难": "hard"}

# ---------------------------------------------------------------- 扫描目录


def scan():
    """返回 {题号: {"dir": .., "files": [相对路径..]}}"""
    found = {}
    for name in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, name)
        if not os.path.isdir(path) or name.startswith(".") or name.startswith("_"):
            continue
        m = re.match(r"^(\d+)\.(.+)$", name)
        if not m:
            continue
        num = int(m.group(1))
        files = []
        for cur, dirs, fs in os.walk(path):
            dirs[:] = [d for d in dirs if d != "_backup" and not d.startswith(".")]
            for f in sorted(fs):
                if f.lower().endswith(".html") and not f.startswith("."):
                    rel = os.path.relpath(os.path.join(cur, f), ROOT).replace(os.sep, "/")
                    files.append(rel)
        if files:
            found[num] = {"dir": name, "files": sorted(files, key=primary_key)}
    return found


def primary_key(path):
    """让「可视化 / 图解」排在「API 速查」前面，决定卡片与 README 的默认入口。"""
    name = os.path.basename(path)
    score = 0
    if "可视化" in name:
        score += 3
    if "图解" in name:
        score += 2
    if "速查" in name:
        score -= 3
    return (-score, len(name), name)


def label(path, dir_name):
    """由文件名生成短标题: '131.分割回文串/分割回文串-双指针回溯图解.html' -> '双指针回溯图解'"""
    base = os.path.splitext(os.path.basename(path))[0]
    cn = re.sub(r"^\d+\.", "", dir_name)
    if base.startswith(cn):
        base = base[len(cn):].lstrip("-—_ ")
    m = re.match(r"^\d+\.", base)
    if m:
        base = base[m.end():].strip()
    return base or "图解"


def quote(path):
    return urllib.parse.quote(path, safe="/")


def build_data():
    found = scan()
    groups = []
    done_nums, total_files = [], 0
    for cat, items in CATEGORIES:
        rows = []
        for num, title, diff in items:
            hit = found.get(num)
            entries = []
            if hit:
                done_nums.append(num)
                for f in hit["files"]:
                    entries.append({"path": f, "url": quote(f), "label": label(f, hit["dir"])})
                total_files += len(entries)
            rows.append({"num": num, "title": title, "diff": diff, "entries": entries,
                         "done": bool(entries), "dir": hit["dir"] if hit else ""})
        groups.append({"cat": cat, "rows": rows,
                       "done": sum(1 for r in rows if r["done"]), "total": len(rows)})
    extras = []
    for num, hit in sorted(found.items()):
        if any(r["num"] == num for g in groups for r in g["rows"]):
            continue
        entries = [{"path": f, "url": quote(f), "label": label(f, hit["dir"])} for f in hit["files"]]
        extras.append({"num": num, "title": re.sub(r"^\d+\.", "", hit["dir"]),
                       "diff": "", "dir": hit["dir"], "entries": entries,
                       "done": True, "cat": "扩展"})
        total_files += len(entries)
    data = {
        "groups": groups,
        "extras": extras,
        "done": len(set(done_nums)),
        "total": sum(g["total"] for g in groups),
        "files": total_files,
        "missing": [r["num"] for g in groups for r in g["rows"] if not r["done"]],
    }
    return data


# ---------------------------------------------------------------- README


def readme(data):
    done, total, files = data["done"], data["total"], data["files"]
    pct = int(round(done * 100 / total))

    # 专题进度表
    tbl = ["| 专题 | 题数 | 已完成 | 进度 |", "|:--|--:|--:|:--|"]
    for g in data["groups"]:
        p = int(round(g["done"] * 100 / g["total"]))
        mark = "✅" if p == 100 else ("⬜" if p == 0 else "🟡")
        tbl.append("| **%s** | %d | %d | %s %d%% |" % (g["cat"], g["total"], g["done"], mark, p))

    # 题目清单
    blocks = []
    for i, g in enumerate(data["groups"]):
        lines = ["<details%s>" % (" open" if i == 0 else ""),
                 "<summary><b>%s</b> &nbsp;·&nbsp; %d/%d</summary>" % (g["cat"], g["done"], g["total"]),
                 "",
                 "| # | 题目 | 难度 | 图解 |",
                 "|:--|:--|:--|:--|"]
        for r in g["rows"]:
            if r["done"]:
                first = r["entries"][0]
                cnt = len(r["entries"])
                link = "[%s](%s/blob/main/%s)" % (
                    "查看 %d 篇" % cnt if cnt > 1 else "查看图解", REPO_URL, first["url"])
            else:
                link = "—"
            lines.append("| %d | %s | %s %s | %s |" % (
                r["num"], r["title"], DIFF_ICON.get(r["diff"], ""), r["diff"], link))
        lines.append("")
        lines.append("</details>")
        blocks.append("\n".join(lines))

    # 扩展题
    extra_tbl = ""
    if data["extras"]:
        rows = ["| # | 题目 | 图解 |", "|:--|:--|:--|"]
        for e in data["extras"]:
            first = e["entries"][0]
            rows.append("| %d | %s | [%s](%s/blob/main/%s) |" % (
                e["num"], e["title"],
                "查看 %d 篇" % len(e["entries"]) if len(e["entries"]) > 1 else "查看图解", REPO_URL, first["url"]))
        extra_tbl = "\n".join(rows)

    missing_txt = "、".join(str(n) for n in data["missing"]) or "无"

    readme_tpl = """<div align="center">

# LeetCode 热题 100 · 可视化题解

**把抽象算法「看着跑」起来 —— 每题一篇可交互 HTML 图解，看见每一步，而不是背下每一行**

[![Stars](https://img.shields.io/github/stars/@@OWNER@@/@@REPO@@?style=for-the-badge&logo=github&label=%E2%AD%90%20Star&color=f5c542)](https://github.com/@@OWNER@@/@@REPO@@/stargazers)
[![Forks](https://img.shields.io/github/forks/@@OWNER@@/@@REPO@@?style=for-the-badge&logo=git&color=58a6ff)](https://github.com/@@OWNER@@/@@REPO@@/forks)
[![Last Commit](https://img.shields.io/github/last-commit/@@OWNER@@/@@REPO@@?style=for-the-badge&color=3fb950)](https://github.com/@@OWNER@@/@@REPO@@/commits/main)
[![Progress](https://img.shields.io/badge/%E8%BF%9B%E5%BA%A6-@@DONE@@%2F@@TOTAL@@-3fb950?style=for-the-badge)](@@REPO_URL@@)
[![License](https://img.shields.io/badge/License-MIT-bc8cff?style=for-the-badge)](https://github.com/@@OWNER@@/@@REPO@@/blob/main/LICENSE)

[🌐 在线刷题](@@SITE@@) &nbsp;·&nbsp; [📘 题目清单](#题目清单) &nbsp;·&nbsp; [🧩 进度看板](#进度看板) &nbsp;·&nbsp; [🚀 每日更新](#每天怎么更新)

</div>

---

## 这是什么

LeetCode「热题 100」是中文社区公认的算法入门主线，但大多数题解只有静态代码 + 几行注释：
**看完觉得懂了，合上就忘，面试一写就卡。**

这个仓库做的是另一件事 —— 把每道题的**执行过程**做成一篇可以自己操控的网页：

- 🎬 **每一步都看得见**：数组、哈希表、双指针、递归调用栈、BFS 队列、回溯搜索树……都在页面上真实动起来，支持暂停 / 单步 / 调速 / 拖进度条。
- 📦 **单文件、零依赖**：每篇题解就是一个 HTML 文件，不加载任何外部 CDN，双击即开，飞机上也能看。
- 🧭 **先讲为什么，再讲怎么写**：每页都有一节「为什么这么做 / 为什么不能那么做」，用反例把边界条件讲透。
- 🧱 **按专题推进，进度实时更新**：17 个专题逐个攻克，当前 **@@DONE@@ / @@TOTAL@@**，未完成的题目按计划补齐。

> 不是把答案抄一遍，而是把「为什么这么想」拆成一步一动画出来。

---

## 先看一眼

<table>
<tr>
<td width="50%"><img src="https://raw.githubusercontent.com/@@OWNER@@/@@REPO@@/main/screenshots/n-queens.png" alt="51. N 皇后：DFS 回溯与剪枝，冲突格标红、代码行同步高亮"></td>
<td width="50%"><img src="https://raw.githubusercontent.com/@@OWNER@@/@@REPO@@/main/screenshots/rain-water.png" alt="42. 接雨水：双指针，水位随左右边界收缩上涨"></td>
</tr>
<tr>
<td><img src="https://raw.githubusercontent.com/@@OWNER@@/@@REPO@@/main/screenshots/two-sum.png" alt="1. 两数之和：HashMap 建表与查补数逐步演示"></td>
<td><img src="https://raw.githubusercontent.com/@@OWNER@@/@@REPO@@/main/screenshots/home.png" alt="在线首页：按专题筛选、搜索、进度统计"></td>
</tr>
</table>

---

## 进度看板

**@@DONE@@ / @@TOTAL@@ 已完成** &nbsp;·&nbsp; **@@FILES@@ 篇可视化图解** &nbsp;·&nbsp; 剩余待补：@@MISSING@@

@@PROGRESS_TABLE@@

<details>
<summary>进度是怎么统计的</summary>

每个题号对应一个目录，目录下的 HTML 数量就是该题的图解篇数；有些题会保留「双指针版 / 单调栈版」等多篇对照。数据由 `tools/build.py` 扫描目录自动生成，不手工维护。

</details>

---

## 题目清单

@@PROBLEMS@@

@@EXTRAS_BLOCK@@

---

## 每篇题解长什么样

打开任意一篇，结构基本一致：

| 区块 | 内容 |
|:--|:--|
| 算法卡片 | 一句话概括思路 + 时间/空间复杂度 |
| 为什么 | 用反例说明为什么必须这么写（最容易写错的地方） |
| 可视化 | 逐步播放的动画，配当前步骤的讲解文字与变量状态 |
| 代码 | 与动画同步高亮的代码，播放到哪行亮哪行 |
| 控制条 | 单步 / 自动播放 / 速度 / 进度条 / 用例切换 |

---

## 目录结构

```
@@REPO@@/
├── index.html              # 导航首页（在线版同款）
├── README.md
├── tools/build.py          # 扫描目录，重新生成 README 与首页
├── 1.两数之和/
│   ├── 两数之和-哈希表可视化.html
│   └── HashMap-API速查.html
├── 146.LRU缓存/
│   └── ...
└── ...
```

命名规则：`题号.题目名/题目名-解法要点.html`，一个题号下可以有多篇。

---

## 怎么看

**在线看（推荐）**：@@SITE@@

**本地看**：把仓库下载下来，直接双击任意 `.html` 文件即可，无需启动服务、无需联网。

```bash
git clone https://github.com/@@OWNER@@/@@REPO@@.git
```

---

## 每天怎么更新

写完新题后，在仓库根目录执行：

```bash
python tools/build.py        # 重新扫描目录，刷新 README 与首页
git add -A
git commit -m "新增 34. 在排序数组中查找元素的第一个和最后一个位置"
git push
```

`build.py` 会自动更新进度数字、专题完成度、题目清单里的「查看图解」链接，以及首页的卡片和筛选器 —— 不需要手工改任何一处计数。

Windows 上也可以直接运行 `tools/publish.ps1`，它等于「重建 + 提交 + 推送」三连：

```powershell
powershell -ExecutionPolicy Bypass -File tools/publish.ps1 "新增 34. 在排序数组中查找元素的第一个和最后一个位置"
```

---

## 一起把它补完

- 发现某篇图解讲错了、动画卡住了、边界条件漏了？欢迎提 [Issue](https://github.com/@@OWNER@@/@@REPO@@/issues)。
- 有更清晰的画法或更优的解法？欢迎提 PR，格式照着现有题解来就行。
- 如果这个仓库帮你少卡了一次，**点个 ⭐ Star** 就是最实在的支持 —— 它会让我知道这条路值得继续画下去。

<div align="center">

### ⭐ Star 趋势

[![Star History Chart](https://api.star-history.com/svg?repos=@@OWNER@@/@@REPO@@&type=Date)](https://star-history.com/#@@OWNER@@/@@REPO@@&Date)

</div>

---

## 说明

- 题目描述与版权归 [LeetCode](https://leetcode.cn/) 所有，本仓库仅作学习交流。
- 代码与图解均为原创整理，采用 [MIT License](https://github.com/@@OWNER@@/@@REPO@@/blob/main/LICENSE)，转载请保留出处。

<div align="center"><sub>如果它对你有用，请点亮右上角的 ⭐ Star，让更多正在刷 Hot 100 的人看到它。</sub></div>
"""

    readme_tpl = (readme_tpl
                  .replace("@@OWNER@@", OWNER)
                  .replace("@@REPO@@", REPO)
                  .replace("@@SITE@@", SITE)
                  .replace("@@REPO_URL@@", REPO_URL)
                  .replace("@@DONE@@", str(done))
                  .replace("@@TOTAL@@", str(total))
                  .replace("@@FILES@@", str(files))
                  .replace("@@MISSING@@", missing_txt)
                  .replace("@@PROGRESS_TABLE@@", "\n".join(tbl))
                  .replace("@@PROBLEMS@@", "\n\n".join(blocks)))

    extras_block = ""
    if extra_tbl:
        extras_block = ("## 扩展题解（不在 Hot 100 内）\n\n"
                        "刷题时顺手整理的同类题，作为对照阅读：\n\n%s" % extra_tbl)
    readme_tpl = readme_tpl.replace("@@EXTRAS_BLOCK@@", extras_block)

    # 去掉空占位（无扩展题时不留空行）
    if not extras_block:
        readme_tpl = readme_tpl.replace("\n\n\n---\n\n## 每篇题解长什么样", "\n\n---\n\n## 每篇题解长什么样")
    return readme_tpl


# ---------------------------------------------------------------- 首页

PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LeetCode 热题 100 · 可视化题解</title>
<meta name="description" content="LeetCode 热题 100 可视化题解：每题一篇可交互 HTML 图解，单步演示哈希表、双指针、递归栈、BFS、回溯的真实执行过程。当前进度 @@DONE@@/@@TOTAL@@，持续更新。">
<meta property="og:title" content="LeetCode 热题 100 · 可视化题解">
<meta property="og:description" content="把抽象算法「看着跑」起来。@@DONE@@/@@TOTAL@@ 已完成，持续更新。">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='78' font-size='80'>🔥</text></svg>">
<style>
  :root{
    --bg:#0d1117;--panel:#161b22;--panel2:#1c2128;--border:#30363d;
    --text:#e6edf3;--muted:#8b949e;--blue:#58a6ff;--green:#3fb950;
    --purple:#bc8cff;--orange:#e3b341;--red:#f85149;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
    --mono:"Cascadia Code",Consolas,"SF Mono",Menlo,monospace;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.6;
    background-image:radial-gradient(900px 500px at 15% -5%,rgba(88,166,255,.16),transparent 60%),
                      radial-gradient(700px 420px at 88% 0%,rgba(188,140,255,.13),transparent 60%);
    background-repeat:no-repeat}
  .wrap{max-width:1180px;margin:0 auto;padding:0 20px}
  a{color:inherit;text-decoration:none}

  header{position:sticky;top:0;z-index:50;backdrop-filter:blur(10px);
    background:rgba(13,17,23,.82);border-bottom:1px solid var(--border)}
  .nav{display:flex;align-items:center;gap:14px;height:60px}
  .brand{display:flex;align-items:center;gap:9px;font-weight:700;letter-spacing:.2px}
  .brand .logo{width:26px;height:26px;border-radius:7px;display:grid;place-items:center;
    background:linear-gradient(135deg,#58a6ff,#bc8cff);font-size:14px;color:#0d1117;font-weight:800}
  .nav .spacer{flex:1}
  .nav a.link{color:var(--muted);font-size:13px;padding:6px 2px}
  .nav a.link:hover{color:var(--text)}
  .ghbtn{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--border);
    background:var(--panel);border-radius:8px;padding:7px 13px;font-size:13px;font-weight:600}
  .ghbtn:hover{border-color:var(--blue);color:var(--blue)}

  .hero{padding:64px 0 34px;display:grid;grid-template-columns:1.25fr .75fr;gap:38px;align-items:center}
  .kicker{display:inline-flex;align-items:center;gap:8px;font-size:12px;color:var(--green);
    border:1px solid rgba(63,185,80,.4);background:rgba(63,185,80,.08);border-radius:999px;padding:5px 12px;margin-bottom:18px}
  .hero h1{font-size:44px;line-height:1.22;letter-spacing:-.5px;margin-bottom:14px}
  .hero h1 em{font-style:normal;background:linear-gradient(100deg,#58a6ff,#bc8cff 55%,#3fb950);
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
  .hero p.lead{color:var(--muted);font-size:15px;max-width:560px}
  .cta{display:flex;gap:10px;margin-top:26px;flex-wrap:wrap}
  .btn{display:inline-flex;align-items:center;gap:8px;border-radius:9px;padding:11px 20px;font-size:14px;font-weight:600;border:1px solid var(--border)}
  .btn.main{background:var(--blue);border-color:var(--blue);color:#0d1117}
  .btn.main:hover{filter:brightness(1.1)}
  .btn.ghost{background:var(--panel);color:var(--text)}
  .btn.ghost:hover{border-color:var(--blue);color:var(--blue)}

  .ringcard{background:var(--panel);border:1px solid var(--border);border-radius:16px;padding:22px;text-align:center}
  .ring{position:relative;width:150px;height:150px;margin:4px auto 14px}
  .ring svg{width:100%;height:100%}
  .ring .inner{position:absolute;inset:0;display:grid;place-items:center;line-height:1.1}
  .ring b{font-size:36px;font-family:var(--mono)}
  .ring span{display:block;font-size:12px;color:var(--muted)}
  .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px}
  .stat{background:var(--panel2);border-radius:9px;padding:9px 6px}
  .stat b{display:block;font-family:var(--mono);font-size:17px}
  .stat span{font-size:11px;color:var(--muted)}

  .toolbar{padding:8px 0 0}
  .searchrow{display:flex;gap:10px;align-items:center;margin-bottom:14px}
  .search{flex:1;display:flex;align-items:center;gap:9px;background:var(--panel);border:1px solid var(--border);
    border-radius:10px;padding:10px 14px}
  .search:focus-within{border-color:var(--blue);box-shadow:0 0 0 3px rgba(88,166,255,.12)}
  .search input{flex:1;background:none;border:none;outline:none;color:var(--text);font-size:14px;font-family:var(--sans)}
  .search input::placeholder{color:var(--muted)}
  .search kbd{font-family:var(--mono);font-size:11px;color:var(--muted);border:1px solid var(--border);
    border-radius:5px;padding:1px 6px}
  .chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
  .chip{font-size:12.5px;color:var(--muted);background:var(--panel);border:1px solid var(--border);
    border-radius:999px;padding:5px 13px;cursor:pointer;transition:.15s;user-select:none}
  .chip:hover{color:var(--text);border-color:#484f58}
  .chip.on{color:var(--blue);border-color:var(--blue);background:rgba(88,166,255,.12)}
  .chip .n{color:var(--muted);font-family:var(--mono);font-size:11px;margin-left:5px}
  .chip.on .n{color:var(--blue)}
  .difrow{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:12px;color:var(--muted)}
  .switch{margin-left:auto;display:flex;align-items:center;gap:7px;cursor:pointer;user-select:none}
  .switch input{appearance:none;width:34px;height:19px;background:#30363d;border-radius:999px;position:relative;cursor:pointer;transition:.15s}
  .switch input:checked{background:rgba(63,185,80,.75)}
  .switch input::after{content:"";position:absolute;top:2.5px;left:3px;width:14px;height:14px;border-radius:50%;background:#e6edf3;transition:.15s}
  .switch input:checked::after{left:17px}

  .listhead{display:flex;align-items:baseline;gap:12px;margin:26px 0 16px}
  .listhead h2{font-size:18px}
  .listhead .hint{font-size:12px;color:var(--muted)}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:14px;padding-bottom:10px}
  .card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:15px 16px;
    display:flex;flex-direction:column;gap:9px;position:relative;transition:transform .16s,border-color .16s,box-shadow .16s}
  .card:hover{transform:translateY(-2px);border-color:#484f58;box-shadow:0 10px 26px rgba(0,0,0,.35)}
  .card.todo{opacity:.5;border-style:dashed;background:transparent}
  .card.todo:hover{transform:none;box-shadow:none;border-color:var(--border)}
  .ctop{display:flex;align-items:center;gap:8px}
  .num{font-family:var(--mono);font-size:12px;color:var(--muted)}
  .diff{font-size:11px;border:1px solid;border-radius:5px;padding:1px 7px;line-height:1.5}
  .d-easy{color:var(--green);border-color:rgba(63,185,80,.5);background:rgba(63,185,80,.08)}
  .d-medium{color:var(--orange);border-color:rgba(227,179,65,.5);background:rgba(227,179,65,.08)}
  .d-hard{color:var(--red);border-color:rgba(248,81,73,.5);background:rgba(248,81,73,.08)}
  .cnt{margin-left:auto;font-size:11px;color:var(--muted);font-family:var(--mono)}
  .ttl{font-size:16px;font-weight:650;line-height:1.35}
  .card:not(.todo) .ttl:hover{color:var(--blue)}
  .tags{display:flex;gap:6px;flex-wrap:wrap}
  .tag{font-size:11px;color:var(--muted);background:var(--panel2);border:1px solid var(--border);border-radius:6px;padding:2px 8px}
  .files{display:flex;gap:6px;flex-wrap:wrap;margin-top:2px}
  .files a{font-size:11.5px;color:var(--muted);border-bottom:1px dashed #3d444d;padding-bottom:1px}
  .files a:hover{color:var(--blue);border-color:var(--blue)}
  .card .go{font-size:11.5px;color:var(--blue);margin-top:auto;padding-top:4px}
  .card.todo .go{color:var(--muted)}

  .empty{display:none;text-align:center;color:var(--muted);font-size:14px;padding:50px 0}
  .empty.show{display:block}

  footer{margin-top:46px;border-top:1px solid var(--border);padding:26px 0 40px;color:var(--muted);font-size:12.5px}
  footer .row{display:flex;gap:16px;flex-wrap:wrap;align-items:center}
  footer a{border-bottom:1px solid transparent}
  footer a:hover{color:var(--blue);border-color:var(--blue)}

  @media(max-width:860px){
    .hero{grid-template-columns:1fr;padding:40px 0 22px;gap:24px}
    .hero h1{font-size:32px}
    .ringcard{max-width:420px}
    .nav a.link{display:none}
  }
</style>
</head>
<body>
<header>
  <div class="wrap nav">
    <a class="brand" href="./"><span class="logo">🔥</span><span>LeetCode Hot 100 · 可视化</span></a>
    <span class="spacer"></span>
    <a class="link" href="#list">题目清单</a>
    <a class="link" href="#progress">进度</a>
    <a class="link" href="@@REPO_URL@@" target="_blank" rel="noopener">GitHub</a>
    <a class="ghbtn" href="@@REPO_URL@@" target="_blank" rel="noopener">⭐ Star</a>
  </div>
</header>

<main class="wrap">
  <section class="hero">
    <div>
      <span class="kicker">● 正在更新 &nbsp;·&nbsp; @@DONE@@ / @@TOTAL@@</span>
      <h1>把抽象算法<em>看着跑</em>起来<br>Hot 100 的每一步都看得见</h1>
      <p class="lead">哈希表怎么建、双指针什么时候动、递归栈压了几层、回溯在哪一步剪枝 ——
      静态题解讲不清的地方，这里用可单步播放的动画一步步演给你看。单文件、零依赖、双击即开。</p>
      <div class="cta">
        <a class="btn main" href="#list">开始刷题 →</a>
        <a class="btn ghost" href="@@REPO_URL@@" target="_blank" rel="noopener">⭐ 去 GitHub 点 Star</a>
      </div>
    </div>
    <div class="ringcard">
      <div class="ring">
        <svg viewBox="0 0 100 100" aria-hidden="true">
          <circle cx="50" cy="50" r="44" fill="none" stroke="#21262d" stroke-width="6"></circle>
          <circle cx="50" cy="50" r="44" fill="none" stroke="url(#g)" stroke-width="6" stroke-linecap="round"
            stroke-dasharray="@@DASH@@" transform="rotate(-90 50 50)"></circle>
          <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#58a6ff"></stop>
            <stop offset="100%" stop-color="#3fb950"></stop></linearGradient></defs>
        </svg>
        <div class="inner"><div><b>@@DONE@@</b><span>/ @@TOTAL@@ 题</span></div></div>
      </div>
      <div class="stats">
        <div class="stat"><b>@@FILES@@</b><span>篇图解</span></div>
        <div class="stat"><b>17</b><span>个专题</span></div>
        <div class="stat"><b>@@PCT@@%</b><span>完成度</span></div>
      </div>
    </div>
  </section>

  <section id="list">
    <div class="searchrow">
      <div class="search">
        <span>🔍</span>
        <input id="q" type="search" placeholder="搜题号或题名，例如 15 / 接雨水 / 回溯" autocomplete="off">
        <kbd>/</kbd>
      </div>
    </div>
    <div class="chips" id="cats">@@CATCHIPS@@</div>
    <div class="difrow">
      <span id="diffs">
        <span class="chip on" data-diff="全部">全部难度</span>
        <span class="chip" data-diff="简单">🟢 简单</span>
        <span class="chip" data-diff="中等">🟡 中等</span>
        <span class="chip" data-diff="困难">🔴 困难</span>
      </span>
      <label class="switch"><input type="checkbox" id="onlyTodo"><span>只看未完成</span></label>
    </div>
    <div class="listhead">
      <h2>题目清单</h2>
      <span class="hint" id="countHint"></span>
    </div>
    <div class="grid" id="grid">@@CARDS@@</div>
    <div class="empty" id="empty">没有匹配的题目，换个关键词试试。</div>
  </section>

  @@EXTRAS@@

  <section id="progress" style="margin-top:40px">
    <div class="listhead"><h2>专题进度</h2><span class="hint">每天补几道，进度自动刷新</span></div>
    <div style="background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:6px 18px">
      @@PROGROWS@@
    </div>
  </section>
</main>

<footer>
  <div class="wrap row">
    <span>题目与题面版权归 <a href="https://leetcode.cn/" target="_blank" rel="noopener">LeetCode</a> 所有，本仓库仅作学习交流。</span>
    <span>代码与图解采用 <a href="LICENSE">MIT License</a>。</span>
    <span class="spacer" style="flex:1"></span>
    <a href="@@REPO_URL@@" target="_blank" rel="noopener">GitHub</a>
    <a href="@@REPO_URL@@/issues" target="_blank" rel="noopener">反馈问题</a>
    <a href="@@REPO_URL@@/stargazers" target="_blank" rel="noopener">⭐ Star</a>
  </div>
</footer>

<script>
(function () {
  var grid = document.getElementById('grid');
  var cards = [].slice.call(grid.querySelectorAll('.card'));
  var q = document.getElementById('q');
  var cats = document.getElementById('cats');
  var diffs = document.getElementById('diffs');
  var onlyTodo = document.getElementById('onlyTodo');
  var empty = document.getElementById('empty');
  var hint = document.getElementById('countHint');
  var cat = '全部', diff = '全部';

  function apply() {
    var kw = (q.value || '').trim().toLowerCase();
    var shown = 0, done = 0;
    cards.forEach(function (c) {
      var ok = true;
      if (cat !== '全部' && c.dataset.cat !== cat) ok = false;
      if (diff !== '全部' && c.dataset.diff !== diff) ok = false;
      if (onlyTodo.checked && c.dataset.done === '1') ok = false;
      if (kw) {
        var hay = (c.dataset.t + ' ' + c.dataset.num + ' ' + c.dataset.cat).toLowerCase();
        if (hay.indexOf(kw) === -1) ok = false;
      }
      c.style.display = ok ? '' : 'none';
      if (ok) { shown++; if (c.dataset.done === '1') done++; }
    });
    empty.classList.toggle('show', shown === 0);
    hint.textContent = '显示 ' + shown + ' 道 · 已完成 ' + done + ' 道';
  }

  cats.addEventListener('click', function (e) {
    var el = e.target.closest('.chip');
    if (!el) return;
    [].forEach.call(cats.querySelectorAll('.chip'), function (c) { c.classList.remove('on'); });
    el.classList.add('on');
    cat = el.dataset.cat;
    apply();
  });

  diffs.addEventListener('click', function (e) {
    var el = e.target.closest('.chip');
    if (!el) return;
    [].forEach.call(diffs.querySelectorAll('.chip'), function (c) { c.classList.remove('on'); });
    el.classList.add('on');
    diff = el.dataset.diff;
    apply();
  });

  q.addEventListener('input', apply);
  onlyTodo.addEventListener('change', apply);
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== q) { e.preventDefault(); q.focus(); }
  });
  apply();
})();
</script>
</body>
</html>
"""


def page(data):
    done, total, files = data["done"], data["total"], data["files"]
    pct = int(round(done * 100 / total))
    circ = 2 * 3.1415926 * 44
    arc = circ * pct / 100

    chips = ['<span class="chip on" data-cat="全部">全部<span class="n">%d</span></span>' % total]
    for g in data["groups"]:
        chips.append('<span class="chip" data-cat="%s">%s<span class="n">%d/%d</span></span>' % (
            html.escape(g["cat"]), html.escape(g["cat"]), g["done"], g["total"]))
    if data["extras"]:
        chips.append('<span class="chip" data-cat="扩展">扩展<span class="n">%d</span></span>' % len(data["extras"]))

    def card_html(item, cat):
        cls = "card" if item["done"] else "card todo"
        diff_cls = DIFF_CLASS.get(item["diff"], "")
        pill = '<span class="diff d-%s">%s</span>' % (diff_cls, item["diff"]) if diff_cls else ""
        cnt = '<span class="cnt">%d 篇</span>' % len(item["entries"]) if item["entries"] else '<span class="cnt">待更新</span>'
        ttl = html.escape(item["title"])
        head = ('<div class="ctop"><span class="num">#%d</span>%s%s</div>'
                % (item["num"], pill, cnt))
        if item["done"]:
            first = item["entries"][0]
            title_html = '<a class="ttl" href="%s">%s</a>' % (first["url"], ttl)
            tags = '<div class="tags"><span class="tag">%s</span></div>' % html.escape(cat)
            extra_files = ""
            if len(item["entries"]) > 1:
                extra_files = '<div class="files">' + "".join(
                    '<a href="%s">%s</a>' % (e["url"], html.escape(e["label"])) for e in item["entries"]) + "</div>"
            go = '<span class="go">查看图解 →</span>'
        else:
            title_html = '<span class="ttl">%s</span>' % ttl
            tags = '<div class="tags"><span class="tag">%s</span><span class="tag">施工中</span></div>' % html.escape(cat)
            extra_files = ""
            go = '<span class="go">还没写，催更去 GitHub →</span>'

        return ('<article class="%s" data-num="%d" data-cat="%s" data-diff="%s" data-done="%d" data-t="%s">%s%s%s%s%s</article>'
                % (cls, item["num"], html.escape(cat), item["diff"], 1 if item["done"] else 0,
                   html.escape(item["title"]), head, title_html, tags, extra_files, go))

    cards = []
    for g in data["groups"]:
        for r in g["rows"]:
            cards.append(card_html(r, g["cat"]))

    extras_html = ""
    if data["extras"]:
        cards_e = [card_html(e, "扩展") for e in data["extras"]]
        extras_html = ('<section id="extras" style="margin-top:34px">'
                       '<div class="listhead"><h2>扩展题解</h2>'
                       '<span class="hint">不在 Hot 100 内，刷题时顺手整理的同类题</span></div>'
                       '<div class="grid">%s</div></section>' % "".join(cards_e))

    prog = []
    for g in data["groups"]:
        p = int(round(g["done"] * 100 / g["total"]))
        prog.append(
            '<div style="display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid #21262d">'
            '<span style="width:96px;font-size:13px">%s</span>'
            '<div style="flex:1;height:6px;background:#21262d;border-radius:99px;overflow:hidden">'
            '<div style="width:%d%%;height:100%%;background:linear-gradient(90deg,#58a6ff,#3fb950)"></div></div>'
            '<span style="width:52px;text-align:right;font-family:var(--mono);font-size:12px;color:#8b949e">%d/%d</span>'
            '</div>' % (html.escape(g["cat"]), p, g["done"], g["total"]))
    # 去掉最后一行的边框
    if prog:
        prog[-1] = prog[-1].replace("border-bottom:1px solid #21262d", "border-bottom:none")

    out = (PAGE
           .replace("@@DONE@@", str(done))
           .replace("@@TOTAL@@", str(total))
           .replace("@@FILES@@", str(files))
           .replace("@@PCT@@", str(pct))
           .replace("@@DASH@@", "%.1f %.1f" % (arc, circ - arc))
           .replace("@@CATCHIPS@@", "".join(chips))
           .replace("@@CARDS@@", "\n      ".join(cards))
           .replace("@@EXTRAS@@", extras_html)
           .replace("@@PROGROWS@@", "".join(prog))
           .replace("@@REPO_URL@@", REPO_URL)
           .replace("@@SITE@@", SITE))
    return out


def main():
    data = build_data()
    readme_path = os.path.join(ROOT, "README.md")
    index_path = os.path.join(ROOT, "index.html")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme(data))
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(page(data))

    print("完成 %d/%d，共 %d 篇图解，%d 道待补" % (
        data["done"], data["total"], data["files"], len(data["missing"])))
    print("未完成题号:", " ".join(str(n) for n in data["missing"]))
    if data["extras"]:
        print("扩展题:", " ".join("%d.%s" % (e["num"], e["title"]) for e in data["extras"]))
    print("已生成 README.md 与 index.html")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()