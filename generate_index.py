#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自动生成Web Reads主页的脚本
功能：
1. 扫描目录，识别所有文章
2. 提取文章标题和简介
3. 为每篇文章生成随机设计元素
4. 生成主页HTML
"""

import os
import re
import random
import json
from datetime import datetime
from pathlib import Path
import colorsys

# 配置
ARTICLES_DIR = "."  # 文章所在的根目录
INDEX_FILE = "index.html"  # 主页文件名
EXCLUDED_DIRS = [".git", "__pycache__", "node_modules"]  # 排除的目录
ARTICLE_FILE = "index.html"  # 文章HTML文件名
ARTICLE_MD_PATTERN = r".*\.md$"  # Markdown文件模式
CONFIG_FILE = "articles_config.json"  # 文章配置文件

# 颜色配置
HIGHLIGHT_COLORS = [
    "#d23669",  # 原始红色
    "#2e86de",  # 蓝色
    "#10ac84",  # 绿色
    "#8854d0",  # 紫色
    "#f0932b",  # 橙色
    "#eb4d4b",  # 红色
    "#6ab04c",  # 绿色
    "#22a6b3",  # 青色
]

# 生成随机颜色
def generate_random_colors(count=5):
    """生成一组随机颜色，确保颜色之间有足够的差异"""
    colors = []
    for i in range(count):
        # 使用HSV色彩空间生成均匀分布的颜色
        h = random.random()  # 随机色相
        s = 0.6 + random.random() * 0.4  # 饱和度在0.6-1.0之间
        v = 0.7 + random.random() * 0.3  # 亮度在0.7-1.0之间

        # 转换为RGB，然后转为十六进制
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        color = "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))
        colors.append(color)

    return colors

# 扫描目录，查找所有文章
def scan_articles():
    """扫描目录，查找所有文章"""
    articles = []

    # 加载现有配置（如果存在）
    existing_config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        except Exception as e:
            print(f"警告: 无法加载配置文件: {e}")

    # 遍历目录
    for item in os.listdir(ARTICLES_DIR):
        # 排除特定目录和文件
        if item in EXCLUDED_DIRS or item.startswith('.') or item == INDEX_FILE or not os.path.isdir(item):
            continue

        article_dir = os.path.join(ARTICLES_DIR, item)
        article_html = os.path.join(article_dir, ARTICLE_FILE)

        # 检查是否存在index.html文件
        if not os.path.exists(article_html):
            continue

        # 查找目录中的Markdown文件
        md_files = []
        for file in os.listdir(article_dir):
            if re.match(ARTICLE_MD_PATTERN, file):
                md_files.append(os.path.join(article_dir, file))

        # 提取文章信息
        article_info = extract_article_info(article_html, md_files)
        if article_info:
            # 检查是否已有配置
            if item in existing_config:
                # 保留现有的颜色和描述
                article_info['color'] = existing_config[item].get('color', article_info['color'])
                if 'description' in existing_config[item] and existing_config[item]['description']:
                    article_info['description'] = existing_config[item]['description']

            articles.append({
                'dir': item,
                'path': os.path.join(item, ARTICLE_FILE),
                'title': article_info['title'],
                'description': article_info['description'],
                'color': article_info['color'],
                'date': article_info['date']
            })

    # 按日期排序（最新的在前面）
    articles.sort(key=lambda x: x['date'], reverse=True)

    return articles

# 从HTML文件中提取文章信息
def extract_article_info(html_file, md_files):
    """从HTML文件中提取文章信息"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取标题
        title_match = re.search(r'<title>(.*?)</title>', content)
        title = title_match.group(1) if title_match else "未知标题"

        # 尝试从h1标签提取更准确的标题
        h1_match = re.search(r'<h1>(.*?)</h1>', content)
        if h1_match:
            title = h1_match.group(1)

        # 提取描述（尝试从第一段获取）
        description = ""
        p_match = re.search(r'<p>(.*?)</p>', content)
        if p_match:
            # 清除HTML标签
            description = re.sub(r'<[^>]+>', '', p_match.group(1))
            # 截断描述
            if len(description) > 150:
                description = description[:147] + "..."

        # 如果没有找到描述，尝试从Markdown文件中提取
        if not description and md_files:
            for md_file in md_files:
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        md_content = f.read()

                    # 跳过标题，查找第一段
                    lines = md_content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith('#'):
                            description = line.strip()
                            if len(description) > 150:
                                description = description[:147] + "..."
                            break

                    if description:
                        break
                except Exception:
                    continue

        # 生成随机颜色
        color = random.choice(HIGHLIGHT_COLORS)

        # 获取文件修改时间作为日期
        date = datetime.fromtimestamp(os.path.getmtime(html_file))

        return {
            'title': title,
            'description': description,
            'color': color,
            'date': date
        }

    except Exception as e:
        print(f"提取文章信息时出错: {e}")
        return None

# 保存文章配置
def save_articles_config(articles):
    """保存文章配置到JSON文件"""
    config = {}
    for article in articles:
        config[article['dir']] = {
            'title': article['title'],
            'description': article['description'],
            'color': article['color'],
            'date': article['date'].isoformat()
        }

    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存配置文件时出错: {e}")

# 生成主页HTML
def generate_index_html(articles):
    """生成主页HTML"""
    # 使用三重引号和大括号转义
    html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Reads | powered by Little Shock</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --text-color: #333;
            --bg-color: #fff;
            --highlight-color: #d23669;
            --secondary-color: #6c757d;
            --border-color: #eee;
            --link-color: #0366d6;
            --card-bg: #f8f9fa;
            --header-bg: #f8f9fa;
        }}

        [data-theme="dark"] {{
            --text-color: #eee;
            --bg-color: #121212;
            --highlight-color: #ff7597;
            --secondary-color: #adb5bd;
            --border-color: #2d2d2d;
            --link-color: #58a6ff;
            --card-bg: #1e1e1e;
            --header-bg: #1e1e1e;
        }}

        * {{
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
            font-size: 16px;
        }}

        body {{
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.7;
            color: var(--text-color);
            background-color: var(--bg-color);
            max-width: 100%;
            margin: 0;
            padding: 0;
            transition: background-color 0.3s ease, color 0.3s ease;
        }}

        .container {{
            padding: 20px;
            max-width: 1000px;
            margin: 0 auto;
        }}

        header {{
            position: sticky;
            top: 0;
            background-color: var(--header-bg);
            padding: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 1000;
        }}

        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1000px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        .title-small {{
            font-size: 1.2rem;
            font-weight: 700;
            margin: 0;
        }}

        .theme-toggle {{
            background: none;
            border: none;
            color: var(--text-color);
            cursor: pointer;
            font-size: 1.5rem;
            padding: 5px;
        }}

        h1 {{
            font-family: 'Noto Serif SC', serif;
            font-size: 2rem;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
            line-height: 1.3;
            text-align: center;
        }}

        .subtitle {{
            text-align: center;
            color: var(--secondary-color);
            margin-bottom: 2rem;
        }}

        .little-shock-link {{
            text-align: center;
            margin-bottom: 2rem;
            font-size: 0.95rem;
        }}

        .little-shock-link a {{
            color: var(--link-color);
            text-decoration: none;
            border-bottom: 1px dashed var(--secondary-color);
            padding-bottom: 2px;
            transition: color 0.2s ease, border-color 0.2s ease;
        }}

        .little-shock-link a:hover {{
            color: var(--highlight-color);
            border-color: var(--highlight-color);
        }}

        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}

        .article-card {{
            background-color: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            position: relative;
        }}

        .article-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }}

        .card-content {{
            padding: 20px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }}

        .card-title {{
            font-size: 1.2rem;
            font-weight: 700;
            margin-top: 0;
            margin-bottom: 10px;
            color: var(--text-color);
        }}

        .card-description {{
            color: var(--secondary-color);
            font-size: 0.95rem;
            margin-bottom: 15px;
            flex-grow: 1;
        }}

        .read-button {{
            display: inline-block;
            background-color: var(--highlight-color);
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 500;
            text-align: center;
            transition: background-color 0.2s ease;
        }}

        .read-button:hover {{
            background-color: var(--highlight-color);
            opacity: 0.9;
        }}

        .card-accent {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            margin-top: 50px;
            color: var(--secondary-color);
            font-size: 0.9rem;
            border-top: 1px solid var(--border-color);
        }}

        .last-updated {{
            text-align: center;
            color: var(--secondary-color);
            font-size: 0.9rem;
            margin-top: 30px;
        }}

        @media (max-width: 768px) {{
            .articles-grid {{
                grid-template-columns: 1fr;
            }}

            h1 {{
                font-size: 1.8rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h3 class="title-small">Web Reads</h3>
            <button class="theme-toggle" id="theme-toggle">🌙</button>
        </div>
    </header>

    <div class="container">
        <h1>Web Reads</h1>
        <p class="subtitle">移动友好的阅读体验</p>

        <div class="little-shock-link">
            <a href="https://waytoagi.feishu.cn/wiki/UaxewECiHiVBmykypR0c48FhnFd" target="_blank">Little Shock 专区 @ WaytoAGI</a>
        </div>

        <div class="articles-grid">
            {article_cards}
        </div>

        <p class="last-updated">最后更新: {last_updated}</p>
    </div>

    <footer>
        <p>© Little Shock</p>
    </footer>

    <script>
        // 暗黑模式切换功能
        const themeToggle = document.getElementById('theme-toggle');

        // 检查本地存储中的主题设置
        if (localStorage.getItem('theme') === 'dark') {{
            document.documentElement.setAttribute('data-theme', 'dark');
            themeToggle.textContent = '☀️';
        }}

        // 切换主题
        themeToggle.addEventListener('click', () => {{
            if (document.documentElement.getAttribute('data-theme') === 'dark') {{
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                themeToggle.textContent = '🌙';
            }} else {{
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                themeToggle.textContent = '☀️';
            }}
        }});
    </script>
</body>
</html>
'''

    # 生成文章卡片
    article_cards = ""
    for article in articles:
        card_template = f"""
            <div class="article-card">
                <div class="card-accent" style="background-color: {article['color']};"></div>
                <div class="card-content">
                    <h3 class="card-title">{article['title']}</h3>
                    <p class="card-description">{article['description']}</p>
                    <a href="{article['path']}" class="read-button" style="background-color: {article['color']};">阅读文章</a>
                </div>
            </div>
        """
        article_cards += card_template

    # 获取当前时间
    last_updated = datetime.now().strftime("%Y年%m月%d日 %H:%M")

    # 替换模板中的占位符
    html_content = html_template.format(
        article_cards=article_cards,
        last_updated=last_updated
    )

    # 写入文件
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"已生成主页: {INDEX_FILE}")

# 主函数
def main():
    """主函数"""
    print("开始扫描文章...")
    articles = scan_articles()
    print(f"找到 {len(articles)} 篇文章")

    # 保存文章配置
    save_articles_config(articles)

    # 生成主页
    generate_index_html(articles)

    print("完成!")

if __name__ == "__main__":
    main()
