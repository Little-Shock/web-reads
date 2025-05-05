#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown到HTML转换脚本
用于将Markdown文件转换为带有样式和功能的HTML页面

使用方法: python md2html.py <markdown文件路径> [--title "自定义标题"] [--output "输出路径"]
"""

import os
import re
import sys
import argparse
import html as html_module
from pathlib import Path # 引入 Path

# --- 配置 ---
# 扫描时的基础目录
ARTICLES_DIR = "."
# 扫描时排除的目录名
EXCLUDED_DIRS = [".git", "__pycache__", "node_modules", "开发过程"]
# Markdown 文件后缀
MD_SUFFIX = ".md"
# 输出的 HTML 文件名
OUTPUT_HTML = "index.html"
# --- End 配置 ---

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='将Markdown文件转换为HTML页面。省略文件路径则扫描所有目录。')
    # 修改为可选参数
    parser.add_argument('markdown_file', nargs='?', default=None, help=f'Markdown文件路径 (可选，省略则扫描 {ARTICLES_DIR} 下的所有文章目录)')
    parser.add_argument('--title', help='自定义页面标题')
    parser.add_argument('--output', help='输出文件路径 (仅在指定单个 markdown_file 时有效)')
    return parser.parse_args()

def extract_title(md_content):
    """从Markdown内容中提取标题"""
    title_match = re.search(r'^# (.+)$', md_content, re.MULTILINE)
    if title_match:
        return title_match.group(1)
    return None

def extract_toc_items(html_content):
    """从生成的HTML中提取目录项"""
    toc_items = []
    # 查找所有h2标题
    h2_pattern = re.compile(r'<h2 id="section(\d+)">(.+?)</h2>')
    for match in h2_pattern.finditer(html_content):
        section_num = match.group(1)
        toc_text = match.group(2)
        toc_items.append({'id': f'section{section_num}', 'text': toc_text})
    return toc_items

def generate_toc_html(toc_items):
    """生成目录HTML"""
    if not toc_items:
        return ''

    toc_html = '<div class="toc">\n'
    toc_html += '    <div class="toc-title">目录</div>\n'
    toc_html += '    <ul class="toc-list">\n'

    for item in toc_items:
        toc_html += f'        <li><a href="#{item["id"]}">{item["text"]}</a></li>\n'

    toc_html += '    </ul>\n'
    toc_html += '</div>\n'
    return toc_html

# 日期标记已经在行处理时完成，不需要额外的处理函数

def scan_for_md_files(base_dir, excluded_dirs, md_suffix):
    """扫描指定目录下（排除特定子目录）的所有 Markdown 文件"""
    md_files = []
    for root, dirs, files in os.walk(base_dir, topdown=True):
        # 修改 dirs 列表以排除特定目录
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]

        # 只处理子目录中的文件，不处理 base_dir 根目录下的文件
        if root == base_dir:
            continue

        for file in files:
            if file.lower().endswith(md_suffix):
                md_files.append(os.path.join(root, file))
    return md_files

def convert_markdown_to_html(md_content):
    """将Markdown转换为HTML"""
    # 提取标题，避免重复
    title_match = re.search(r'^# (.+)$', md_content, re.MULTILINE)
    if title_match:
        # 移除原始标题，避免重复
        md_content = re.sub(r'^# .+$', '', md_content, 1, re.MULTILINE)

    # 替换二级标题的ID
    section_counter = 1

    def replace_heading(match):
        nonlocal section_counter
        heading_text = match.group(1)
        current_section = section_counter
        section_counter += 1
        return f'## {heading_text} {{#section{current_section}}}'

    # 替换所有二级标题，添加自定义ID
    md_content = re.sub(r'^## (.+)$', replace_heading, md_content, flags=re.MULTILINE)

    # 已经导入了html模块

    # 手动处理Markdown
    lines = md_content.split('\n')
    html_lines = []
    in_paragraph = False
    in_blockquote = False

    for line in lines:
        line = line.strip()

        # 跳过空行
        if not line:
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            if in_blockquote:
                html_lines.append('</blockquote>')
                in_blockquote = False
            continue

        # 处理二级标题
        h2_match = re.match(r'## (.+) {#section(\d+)}', line)
        if h2_match:
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            heading_text = h2_match.group(1)
            section_id = h2_match.group(2)
            html_lines.append(f'<h2 id="section{section_id}">{heading_text}</h2>')
            continue

        # 处理引用
        if line.startswith('>'):
            quote_text = line[1:].strip()
            if not in_blockquote:
                html_lines.append('<blockquote>')
                in_blockquote = True
            html_lines.append(f'<p>{html_module.escape(quote_text)}</p>')
            continue
        elif in_blockquote:
            html_lines.append('</blockquote>')
            in_blockquote = False

        # 检查是否为列表项
        if line.startswith('•'):
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False

            # 提取列表项内容
            list_content = line[1:].strip()

            # 处理列表项中的强调
            list_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', list_content)

            # 添加列表项
            html_lines.append(f'<div class="list-item" style="margin-bottom: 1rem; padding-left: 1.5rem; text-indent: -1rem;">• {html_module.escape(list_content)}</div>')
            continue

        # 处理普通段落
        if not in_paragraph:
            html_lines.append('<p>')
            in_paragraph = True

        # 处理强调
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)

        # 处理日期标记 - 在HTML转义前处理
        # 使用一个简单的方法：只匹配一次最长的日期格式
        if "年" in line and "月" in line:
            # 尝试匹配完整日期 (2023年5月1日)
            match = re.search(r'\d{4}年\d{1,2}月\d{1,2}日', line)
            if match:
                date_text = match.group(0)
                line = line.replace(date_text, f'<span class="date-marker">{date_text}</span>')
            else:
                # 尝试匹配年月 (2023年5月)
                match = re.search(r'\d{4}年\d{1,2}月', line)
                if match:
                    date_text = match.group(0)
                    line = line.replace(date_text, f'<span class="date-marker">{date_text}</span>')
        elif "月" in line and "日" in line:
            # 尝试匹配月日 (5月1日)
            match = re.search(r'\d{1,2}月\d{1,2}日', line)
            if match:
                date_text = match.group(0)
                line = line.replace(date_text, f'<span class="date-marker">{date_text}</span>')

        # 处理图片描述
        if '**图：**' in line:
            if in_paragraph:
                html_lines[-1] = '<p class="image-description">'
            line = line.replace('**图：**', '<strong>图：</strong>')
            html_lines.append(line)
            continue

        # 保留HTML标签，不进行转义
        if '<span class="date-marker">' in line:
            html_lines.append(line)
        else:
            # 只转义非HTML内容
            html_lines.append(html_module.escape(line).replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>'))

    # 关闭最后一个段落
    if in_paragraph:
        html_lines.append('</p>')
    if in_blockquote:
        html_lines.append('</blockquote>')

    html = '\n'.join(html_lines)

    # 处理参考文献
    ref_pattern = r'<p>\s*<strong>（本文作者根据公开资料整理，(.+?)）</strong>\s*</p>'
    ref_replacement = r'<div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid var(--border-color); font-size: 0.9rem; color: var(--secondary-color);"><p><strong>（本文作者根据公开资料整理，\1）</strong></p></div>'
    html = re.sub(ref_pattern, ref_replacement, html)

    return html

def convert_single_file(md_file_path, custom_title=None, output_path_arg=None):
    """转换单个Markdown文件为HTML"""
    try:
        # 检查文件是否存在
        if not os.path.exists(md_file_path):
            print(f"错误: 文件 '{md_file_path}' 不存在")
            return False # 返回失败

        # 读取Markdown文件
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 提取标题
        title = custom_title or extract_title(md_content) or Path(md_file_path).stem # 使用 stem 获取无后缀的文件名

        # 转换Markdown为HTML
        html_content = convert_markdown_to_html(md_content)

        # 提取目录项
        toc_items = extract_toc_items(html_content)

        # 生成目录HTML
        toc_html = generate_toc_html(toc_items)

        # 确定输出路径
        if output_path_arg:
            # 如果命令行指定了输出路径 (仅在单文件模式下有效)
            output_path = output_path_arg
            os.makedirs(os.path.dirname(output_path), exist_ok=True) # 确保目录存在
        else:
            # 默认输出到 Markdown 文件所在的目录，文件名为 index.html
            dir_name = os.path.dirname(md_file_path)
            output_path = os.path.join(dir_name, OUTPUT_HTML)

        # 获取简短标题（用于导航栏）
        short_title = title.split('：')[0] if '：' in title else title

        # HTML模板 (保持不变, 但确保变量名如 {title}, {short_title}, {toc_html}, {html_content} 存在)
        # 注意: f-string 需要双花括号来转义CSS中的花括号 {{ ... }}
        html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
            --header-bg: #f8f9fa;
            --container-width: 800px;
            --container-padding: 20px;
            --font-size: 16px;
            --line-height: 1.7;
            --paragraph-spacing: 1.4rem;
            --font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --serif-font: 'Noto Serif SC', serif;
        }}

        [data-theme="dark"] {{
            --text-color: #eee;
            --bg-color: #121212;
            --highlight-color: #ff7597;
            --secondary-color: #adb5bd;
            --border-color: #2d2d2d;
            --link-color: #58a6ff;
            --header-bg: #1e1e1e;
        }}

        [data-theme="sepia"] {{
            --text-color: #5F4B32;
            --bg-color: #F9F5E9;
            --highlight-color: #d23669;
            --secondary-color: #7D6E5B;
            --border-color: #E8E0D0;
            --link-color: #9C6644;
            --header-bg: #F2ECD9;
        }}

        * {{
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
            font-size: var(--font-size);
        }}

        body {{
            font-family: var(--font-family);
            line-height: var(--line-height);
            color: var(--text-color);
            background-color: var(--bg-color);
            max-width: 100%;
            margin: 0;
            padding: 0;
            transition: background-color 0.3s ease, color 0.3s ease;
        }}

        .container {{
            padding-left: var(--container-padding);
            padding-right: var(--container-padding);
            padding-top: 10px;
            padding-bottom: 10px;
            max-width: var(--container-width);
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
            max-width: var(--container-width);
            margin: 0 auto;
            /* 在批量模式下，CSS 中的相对路径需要调整 */
            /* padding: var(--container-padding); */ /* 这行似乎不适合header */
             padding-left: var(--container-padding);
             padding-right: var(--container-padding);
        }}

        .title-small {{
            font-size: 1.1rem;
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
            font-family: var(--serif-font);
            font-size: 1.8rem;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
            line-height: 1.3;
        }}

        h2 {{
            font-family: var(--serif-font);
            font-size: 1.4rem;
            margin-top: 2.5rem;
            margin-bottom: 1.2rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
            scroll-margin-top: 70px;
        }}

        p {{
            margin-bottom: var(--paragraph-spacing);
            font-size: 1.05rem;
            text-align: justify;
        }}

        strong {{
            color: var(--highlight-color);
            font-weight: 700;
        }}

        .dropcap {{
            float: left;
            font-size: 3.5em;
            line-height: 0.9;
            font-weight: 700;
            margin-right: 0.1em;
            margin-top: 0.1em;
            font-family: var(--serif-font);
            color: var(--highlight-color);
        }}

        blockquote {{
            margin: 1.5em 0;
            padding: 1em 1.5em;
            border-left: 4px solid var(--highlight-color);
            background-color: rgba(0,0,0,0.03);
            font-style: italic;
            border-radius: 0 8px 8px 0;
        }}

        [data-theme="dark"] blockquote {{
            background-color: rgba(255,255,255,0.05);
        }}

        .date-marker {{
            font-weight: 700;
            text-decoration: underline;
            text-decoration-color: var(--highlight-color);
            text-decoration-thickness: 2px;
            text-underline-offset: 4px;
        }}

        .toc {{
            background-color: rgba(0,0,0,0.03);
            border-radius: 8px;
            padding: 15px 20px;
            margin: 20px 0 30px;
        }}

        [data-theme="dark"] .toc {{
            background-color: rgba(255,255,255,0.05);
        }}

        .toc-title {{
            font-weight: 700;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }}

        .toc-list {{
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }}

        .toc-list li {{
            margin-bottom: 8px;
            line-height: 1.4;
        }}

        .toc-list a {{
            color: var(--link-color);
            text-decoration: none;
            display: block;
            padding: 5px 0;
            font-size: 0.95rem;
        }}

        .toc-list a:hover {{
            text-decoration: underline;
        }}

        .image-description {{
            font-size: 0.95rem;
            color: var(--secondary-color);
            font-style: italic;
            margin-top: -0.5rem;
        }}

        .list-item {{
            margin-bottom: 1rem;
            padding-left: 2rem;
            text-indent: -1rem;
            line-height: 1.6;
        }}

        .progress-container {{
            width: 100%;
            height: 4px;
            background: transparent;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1001;
        }}

        .progress-bar {{
            height: 4px;
            background: var(--highlight-color);
            width: 0%;
            transition: width 0.1s ease;
        }}

        .back-to-top {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--highlight-color);
            color: white;
            text-align: center;
            line-height: 40px;
            font-size: 20px;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1000;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}

        .back-to-top.visible {{
            opacity: 1;
        }}

        /* 特殊的CSS类，用于在移动端应用我们的设置 */
        .reader-settings-applied {{
            font-size: var(--font-size) !important;
        }}

        .reader-settings-applied p {{
            margin-bottom: var(--paragraph-spacing) !important;
        }}

        .reader-settings-applied .container {{
            /* 在 reader-settings 中应用 padding，这里保持默认 */
            /* padding: var(--container-padding) !important; */
             padding-left: var(--container-padding) !important;
             padding-right: var(--container-padding) !important;
             padding-top: 10px !important;
             padding-bottom: 10px !important;
            max-width: var(--container-width) !important;
        }}

        /* 响应式调整 - 注意 f-string 的花括号转义 {{ ... }} */
        @media (max-width: 600px) {{
            html:not(.reader-settings-applied) {{
                font-size: var(--font-size);
            }}

            .container:not(.reader-settings-applied) {{
                padding-left: var(--container-padding);
                padding-right: var(--container-padding);
                padding-top: 10px;
                padding-bottom: 10px;
                max-width: 100%;
            }}

            h1 {{
                font-size: 1.6rem;
            }}

            h2 {{
                font-size: 1.3rem;
            }}

            .dropcap {{
                font-size: 3em;
            }}

            html:not(.reader-settings-applied) p {{
                text-align: left;
                margin-bottom: var(--paragraph-spacing);
            }}

            /* 改善列表项在移动端的显示 */
            .list-item {{
                padding-left: 1rem !important;
                text-indent: -0.7rem !important;
                font-size: 1rem;
                line-height: 1.5;
            }}
        }}
    </style>
</head>
<body>
    <div class="progress-container">
        <div class="progress-bar" id="progress-bar"></div>
    </div>

    <div class="back-to-top" id="back-to-top">↑</div>

    <header>
        <div class="header-content">
            <div style="display: flex; align-items: center;">
                 <!-- 返回主页链接需要是相对根目录的 -->
                <a href="../{OUTPUT_HTML}" style="display: flex; align-items: center; color: var(--text-color); text-decoration: none; margin-right: 15px;">
                    <span style="font-size: 1.2rem; margin-right: 5px;">←</span>
                    <span style="font-size: 0.9rem;">返回主页</span>
                </a>
                <h3 class="title-small">{short_title}</h3>
            </div>
            <div style="display: flex; align-items: center;">
                <!-- 设置按钮由reader-settings.js动态创建 -->
                <button class="theme-toggle" id="theme-toggle">🌙</button>
            </div>
        </div>
    </header>

    <div class="container">
        <h1>{title}</h1>

        {toc_html}

        {html_content}
    </div>

    <!-- 阅读设置面板由reader-settings.js动态创建 -->

    <script>
        // 基本功能脚本
        const themeToggle = document.getElementById('theme-toggle');
        const backToTopButton = document.getElementById('back-to-top');

        // 检查本地存储中的主题设置
        // 注意 JS 中的花括号也需要转义 {{ ... }}
        if (localStorage.getItem('theme') === 'dark') {{
            document.documentElement.setAttribute('data-theme', 'dark');
            themeToggle.textContent = '☀️';
        }}

        // 切换主题（基本功能，详细设置由reader-settings.js处理）
        themeToggle.addEventListener('click', () => {{
            const currentTheme = document.documentElement.getAttribute('data-theme');
            if (currentTheme === 'dark') {{
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                themeToggle.textContent = '🌙';
            }} else {{
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                themeToggle.textContent = '☀️';
            }}
        }});

        // 阅读进度指示器和回到顶部按钮
        window.onscroll = function() {{
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            // 需要检查元素是否存在
            const progressBar = document.getElementById("progress-bar");
            if (progressBar) {{
                 progressBar.style.width = scrolled + "%";
            }}


            // 显示或隐藏回到顶部按钮
            if (backToTopButton) {{ // 检查按钮是否存在
                 if (winScroll > 300) {{
                    backToTopButton.classList.add("visible");
                }} else {{
                    backToTopButton.classList.remove("visible");
                }}
            }}
        }};

        // 回到顶部功能
        if (backToTopButton) {{ // 检查按钮是否存在
             backToTopButton.addEventListener("click", function() {{
                window.scrollTo({{
                    top: 0,
                    behavior: "smooth"
                }});
            }});
        }}
    </script>

    <!-- 引入阅读设置脚本 - 路径相对于根目录 -->
    <script src="../reader-settings.js"></script>
</body>
</html>''' # 结束 f-string

        # 写入HTML文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)

        print(f"成功将 '{md_file_path}' 转换为 '{output_path}'")
        return True # 返回成功

    except Exception as e:
        print(f"处理文件 '{md_file_path}' 时出错: {e}")
        import traceback
        traceback.print_exc() # 打印详细错误信息
        return False # 返回失败

def main():
    """主函数"""
    args = parse_args()

    if args.markdown_file:
        # --- 单文件转换模式 ---
        print(f"开始转换单个文件: {args.markdown_file}")
        convert_single_file(args.markdown_file, args.title, args.output)
    else:
        # --- 批量扫描转换模式 ---
        print(f"开始扫描目录 '{ARTICLES_DIR}' (排除: {EXCLUDED_DIRS}) 下的 {MD_SUFFIX} 文件...")
        md_files_to_convert = scan_for_md_files(ARTICLES_DIR, EXCLUDED_DIRS, MD_SUFFIX)

        if not md_files_to_convert:
            print("未找到任何 Markdown 文件进行转换。")
            sys.exit(0)

        print(f"找到以下 {len(md_files_to_convert)} 个 Markdown 文件将被转换:")
        for md_file in md_files_to_convert:
            print(f"- {md_file}")

        # 请求确认
        try:
             confirm = input("是否继续转换所有文件? (y/n): ").lower().strip()
        except EOFError: # 处理管道输入或无交互环境
             print("非交互模式，跳过确认。")
             confirm = 'y' # 或者可以设置为 'n' 以默认取消

        if confirm == 'y' or confirm == 'yes':
            print("开始批量转换...")
            success_count = 0
            fail_count = 0
            for md_file in md_files_to_convert:
                if convert_single_file(md_file): # 使用默认标题和输出路径
                    success_count += 1
                else:
                    fail_count += 1
            print("-" * 20)
            print(f"批量转换完成。成功: {success_count}, 失败: {fail_count}")
        else:
            print("操作已取消。")
            sys.exit(0)

if __name__ == '__main__':
    main()
