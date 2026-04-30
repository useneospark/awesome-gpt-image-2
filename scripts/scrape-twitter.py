#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter/X 提示词抓取脚本

从 Twitter/X 搜索和抓取与 gpt-image-2 相关的提示词内容，
用于更新 awesome-gpt-image-2 仓库。

使用方法:
    python scripts/scrape-twitter.py --search "gpt-image-2 prompt"
    python scripts/scrape-twitter.py --user awesome_prompts --max 20
    python scripts/scrape-twitter.py --batch-users user1,user2,user3

注意: 此脚本使用 xcancel.com (Nitter 替代) 抓取公开推文
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# 添加技能目录到路径
SKILL_PATH = Path.home() / ".claude" / "skills" / "twitter-scraper" / "scripts"
if SKILL_PATH.exists():
    sys.path.insert(0, str(SKILL_PATH.parent.parent))
    try:
        from skills.twitter_scraper.scripts.scraper import (
            parse_tweets_from_html,
            format_tweets_for_report,
            save_tweets
        )
        SCRAPER_AVAILABLE = True
    except ImportError:
        SCRAPER_AVAILABLE = False
else:
    SCRAPER_AVAILABLE = False


# 默认关注的 Twitter 账号列表（AI/设计相关）
DEFAULT_USERS = [
    "sama",                # Sam Altman (OpenAI CEO)
    "gdb",                 # Greg Brockman (OpenAI Co-founder)
    "OpenAI",              # OpenAI Official
    "youmind_ai",          # YouMind (参考项目的团队)
    "LinusEkenstam",       # AI Design
    "javilopen",           # AI Prompts
    "nickfloats",          # AI Creator
    "dr_cintas",           # AI Art
    "hasanssh",            # AI & Design
    "jamesbridle",         # Art & AI
]

# 搜索关键词列表
SEARCH_KEYWORDS = [
    "gpt-image-2",
    "gpt image 2 prompt",
    "gpt-4o image",
    "chatgpt image generation",
    "AI image prompt",
]


def clean_html_text(text: str) -> str:
    """清理 HTML 文本"""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&#39;', "'")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_prompts_from_tweets(tweets: List[Dict]) -> List[Dict]:
    """从推文中提取提示词"""
    prompts = []

    for tweet in tweets:
        text = tweet.get('text', '')
        if not text:
            continue

        # 查找提示词模式（通常以引号或 > 开头）
        prompt_patterns = [
            r'["\']([^"\']{50,800})["\']',  # 引号中的长文本
            r'>([^<\n]{50,800})',           # > 开头的文本
            r'Prompt[:\s]*([^\n]{50,800})', # "Prompt:" 后面的文本
        ]

        for pattern in prompt_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) > 50:  # 提示词通常较长
                    prompts.append({
                        'source': tweet.get('username', 'unknown'),
                        'source_url': tweet.get('url', ''),
                        'date': tweet.get('date', ''),
                        'likes': tweet.get('likes', 0),
                        'text': clean_html_text(match),
                        'full_tweet': clean_html_text(text),
                        'extracted_at': datetime.now().isoformat()
                    })

    return prompts


def generate_markdown_from_prompts(prompts: List[Dict], output_file: str):
    """将提取的提示词生成为 Markdown 文件"""
    lines = [
        "# Twitter 抓取的新提示词",
        "",
        f"> 自动生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 共抓取 {len(prompts)} 条提示词",
        "",
        "---",
        ""
    ]

    for i, prompt in enumerate(prompts, 1):
        lines.extend([
            f"### Prompt {i}",
            "",
            f"**来源:** @{prompt['source']}",
            f"**日期:** {prompt['date']}",
            f"**点赞:** {prompt['likes']}",
            "",
            f"> {prompt['text']}",
            "",
            f"[查看原始推文]({prompt['source_url']})",
            "",
            "---",
            ""
        ])

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"已生成 Markdown 文件: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='从 Twitter/X 抓取 gpt-image-2 相关提示词'
    )
    parser.add_argument(
        '--user', '-u', type=str,
        help='抓取单个用户的推文'
    )
    parser.add_argument(
        '--users', type=str,
        help='批量抓取，逗号分隔用户名'
    )
    parser.add_argument(
        '--max', '-m', type=int, default=10,
        help='每个账号最大抓取数量 (默认: 10)'
    )
    parser.add_argument(
        '--output', '-o', type=str,
        help='输出 JSON 文件路径'
    )
    parser.add_argument(
        '--markdown', type=str,
        help='输出 Markdown 文件路径'
    )
    parser.add_argument(
        '--batch-users', action='store_true',
        help='抓取默认批量用户列表'
    )

    args = parser.parse_args()

    if not SCRAPER_AVAILABLE:
        print("警告: twitter-scraper 模块不可用")
        print("请确保在正确的环境中运行此脚本")
        print("")
        print("使用说明:")
        print("1. 此脚本需要在 OpenClaw/Claude Code 环境中运行")
        print("2. 使用 browser 工具访问 xcancel.com 获取页面内容")
        print("3. 然后使用 scraper.py 解析 HTML")
        print("")
        print("手动步骤:")
        for user in DEFAULT_USERS[:3]:
            print(f"   browser open 'https://xcancel.com/{user}'")
            print(f"   browser act wait 3000")
            print(f"   browser snapshot")
            print(f"   # 然后解析 HTML 提取推文")
        return

    # 确定要抓取的用户列表
    if args.batch_users:
        users = DEFAULT_USERS
    elif args.users:
        users = [u.strip() for u in args.users.split(',')]
    elif args.user:
        users = [args.user]
    else:
        users = DEFAULT_USERS[:3]  # 默认抓取前3个

    print("=" * 60)
    print("Twitter/X GPT Image 2 提示词抓取工具")
    print("=" * 60)
    print(f"目标账号: {', '.join(users)}")
    print(f"抓取数量: {args.max} 条/账号")
    print("=" * 60)
    print("")
    print("注意: 实际抓取需要使用 browser 工具")
    print("请按照以下步骤手动执行:")
    print("")

    all_tweets = []
    for username in users:
        print(f"\n@{username}:")
        print(f"  1. browser open 'https://xcancel.com/{username}'")
        print(f"  2. browser act wait 3000")
        print(f"  3. browser snapshot")
        print(f"  4. 提取 HTML 并用 parse_tweets_from_html() 解析")

    # 如果有实际数据，处理并保存
    if all_tweets:
        prompts = extract_prompts_from_tweets(all_tweets)

        print(f"\n提取到 {len(prompts)} 条提示词")

        # 保存 JSON
        if args.output:
            save_tweets(prompts, args.output)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_tweets(prompts, f"prompts/prompts_{timestamp}.json")

        # 生成 Markdown
        if args.markdown:
            generate_markdown_from_prompts(prompts, args.markdown)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            generate_markdown_from_prompts(
                prompts,
                f"prompts/twitter_prompts_{timestamp}.md"
            )
    else:
        print("\n未获取到推文数据。请使用 browser 工具手动抓取。")


if __name__ == "__main__":
    main()
