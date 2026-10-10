#!/usr/bin/env python3
"""Refresh the coding-profile block in README.md.

Pulls live numbers from LeetCode, Codeforces and CodeChef. If a platform
is unreachable, the last known values in data/stats.json are kept.
Usage:  python scripts/update_stats.py [--render-only]
"""
import datetime
import json
import pathlib
import re
import sys
import urllib.request
from urllib.parse import quote

USER = "vivekboyina"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "stats.json"
README = ROOT / "README.md"
UA = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}


def http(url, data=None, headers=None, timeout=25):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def leetcode():
    q = {
        "query": "query($u:String!){matchedUser(username:$u){submitStatsGlobal{acSubmissionNum{difficulty count}}}}",
        "variables": {"u": USER},
    }
    out = json.loads(http(
        "https://leetcode.com/graphql",
        json.dumps(q).encode(),
        {"Content-Type": "application/json", "Referer": "https://leetcode.com"},
    ))
    rows = out["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
    d = {r["difficulty"]: r["count"] for r in rows}
    return {"solved": d["All"], "easy": d["Easy"], "medium": d["Medium"], "hard": d["Hard"]}


def codeforces():
    info = json.loads(http(f"https://codeforces.com/api/user.info?handles={USER}"))["result"][0]
    subs = json.loads(http(f"https://codeforces.com/api/user.status?handle={USER}"))["result"]
    solved = {(s["problem"].get("contestId"), s["problem"]["index"]) for s in subs if s.get("verdict") == "OK"}
    return {"solved": len(solved), "rating": info.get("rating"), "rank": info.get("rank")}


def codechef():
    html = http(f"https://www.codechef.com/users/{USER}")
    rating = re.search(r'rating-number[^>]*>\s*(\d+)', html)
    stars = re.search(r'(\d)\s*★', html)
    if not rating:
        raise ValueError("CodeChef rating not found")
    return {"rating": int(rating.group(1)), "stars": int(stars.group(1)) if stars else None}


FETCHERS = {"leetcode": leetcode, "codeforces": codeforces, "codechef": codechef}


def badge(label, msg, color, logo, logo_color, link):
    def esc(s):
        return quote(str(s).replace("-", "--").replace("_", "__"), safe="")
    url = (f"https://img.shields.io/badge/{esc(label)}-{esc(msg)}-{color}"
           f"?style=for-the-badge&logo={logo}&logoColor={logo_color}&labelColor=0d1117")
    return f'<a href="{link}"><img src="{url}" alt="{label}"/></a>'


def render(s, stamp):
    lc, cf, cc = s["leetcode"], s["codeforces"], s["codechef"]
    cf_msg = (f'{cf["rating"]} rating' if cf.get("rating") else
              (f'{cf["solved"]} solved' if cf.get("solved") else "Profile"))
    cc_msg = f'{cc["rating"]} rating' if cc.get("rating") else "Profile"
    if cc.get("stars") and cc.get("rating"):
        cc_msg = f'{cc["stars"]}★ {cc["rating"]}'

    badges = [
        badge("LeetCode", f'{lc["solved"]} solved', "FFA116", "leetcode", "FFA116", f"https://leetcode.com/u/{USER}"),
        badge("CodeChef", cc_msg, "5B4638", "codechef", "white", f"https://www.codechef.com/users/{USER}"),
        badge("Codeforces", cf_msg, "1F8ACB", "codeforces", "1F8ACB", f"https://codeforces.com/profile/{USER}"),
        badge("HackerRank", "C++ 5★ · SQL 5★", "00EA64", "hackerrank", "00EA64", f"https://www.hackerrank.com/profile/{USER}"),
        badge("GeeksforGeeks", "Profile", "2F8D46", "geeksforgeeks", "2F8D46", f"https://www.geeksforgeeks.org/user/{USER}/"),
    ]
    lines = ["<br/>", "<p>", "  " + "\n  ".join(badges[:3]), "  <br/>", "  " + "\n  ".join(badges[3:]), "</p>"]
    if lc.get("easy") is not None and (lc["easy"] + lc["medium"] + lc["hard"]) > 0:
        lines.append(f'<sub>🟢 Easy {lc["easy"]} &nbsp;·&nbsp; 🟡 Medium {lc["medium"]} &nbsp;·&nbsp; 🔴 Hard {lc["hard"]}</sub><br/>')
    lines.append(f"<sub>Auto-updated {stamp}</sub>")
    return "\n".join(lines)


def main():
    render_only = "--render-only" in sys.argv
    old = json.loads(DATA.read_text())
    new = json.loads(json.dumps(old))

    if not render_only:
        for name, fn in FETCHERS.items():
            try:
                new[name].update(fn())
            except Exception as e:  # keep last known values
                print(f"[warn] {name}: {e}", file=sys.stderr)

    changed = new != {k: v for k, v in old.items()} or render_only
    text = README.read_text(encoding="utf-8")
    has_block = re.search(r"<!--CODING_START-->(.*?)<!--CODING_END-->", text, re.S)
    if not changed and has_block and has_block.group(1).strip():
        print("No changes.")
        return

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    block = f"<!--CODING_START-->\n{render(new, stamp)}\n<!--CODING_END-->"
    text = re.sub(r"<!--CODING_START-->.*?<!--CODING_END-->", lambda _m: block, text, flags=re.S)
    README.write_text(text, encoding="utf-8")
    DATA.write_text(json.dumps(new, indent=2) + "\n")
    print("README updated.")


if __name__ == "__main__":
    main()
