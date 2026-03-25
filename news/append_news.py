#!/usr/bin/env python3
"""
新闻简报自动追加脚本
用法: python3 append_news.py '新闻JSON数组字符串'
或者: echo '[{...}]' | python3 append_news.py -
"""
import json
import sys
import os
import subprocess
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def dedupe(data):
    """按 title + date[:10] 去重"""
    seen = set()
    result = []
    for item in data:
        key = (item.get('title', ''), item.get('date', '')[:10])
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

def git_push(message=None):
    if not message:
        message = f"data: 更新新闻数据 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    try:
        subprocess.run(['git', 'add', 'news/data.json'], cwd=os.path.join(REPO_DIR, '..'), check=True)
        subprocess.run(['git', 'commit', '-m', message], cwd=os.path.join(REPO_DIR, '..'), check=True)
        subprocess.run(['git', 'push', 'origin', 'master'], cwd=os.path.join(REPO_DIR, '..'), check=True)
        print(f"✅ 已推送到 GitHub Pages")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git 操作失败: {e}")

def main():
    # 读取新数据
    if len(sys.argv) > 1:
        if sys.argv[1] == '-':
            raw = sys.stdin.read()
        else:
            raw = sys.argv[1]
    else:
        print("用法: python3 append_news.py '[{...}]'")
        sys.exit(1)

    try:
        new_items = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        sys.exit(1)

    if not isinstance(new_items, list):
        new_items = [new_items]

    # 加载现有数据
    existing = load_data()
    print(f"📊 现有 {len(existing)} 条，新增 {len(new_items)} 条")

    # 合并 + 去重
    combined = new_items + existing
    combined = dedupe(combined)
    combined.sort(key=lambda x: x.get('date', ''), reverse=True)

    print(f"📊 去重后共 {len(combined)} 条")

    # 保存
    save_data(combined)
    print(f"✅ 已保存到 {DATA_FILE}")

    # 推送
    if '--push' in sys.argv:
        git_push()

if __name__ == '__main__':
    main()
