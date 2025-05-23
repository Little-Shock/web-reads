# Web Reads - Markdown到HTML转换指南

这个仓库包含了一系列文章的Markdown源文件和转换后的HTML页面，提供移动友好的阅读体验。

## Markdown语法指南

在编写文章时，请使用以下Markdown语法和特殊标记：

### 基本语法

- **标题**: 使用`#`表示一级标题，`##`表示二级标题，以此类推
  ```markdown
  # 文章主标题
  ## 第一节标题
  ### 小节标题
  ```

- **段落**: 使用空行分隔段落
  ```markdown
  第一段内容...

  第二段内容...
  ```

- **强调**: 使用`**文本**`表示重点强调（将在HTML中转换为红色高亮）
  ```markdown
  这是普通文本，这里是**重点强调**的内容。
  ```

- **引用**: 使用`>`开始引用块
  ```markdown
  > 这是一段引用文本，将会有特殊的样式。
  ```

- **列表**: 使用`-`或`*`表示无序列表，使用数字加`.`表示有序列表
  ```markdown
  - 第一项
  - 第二项

  1. 第一步
  2. 第二步
  ```

### 特殊标记

- **图片描述**: 使用`**图：**`开头的段落表示图片描述
  ```markdown
  **图：**这里是图片的描述文本，会有特殊样式。
  ```

- **日期标记**: 重要日期会自动添加特殊样式
  ```markdown
  2020年8月13日，Epic Games执行了Project Liberty计划。
  ```

### 文章结构

每篇文章应包含以下部分：

1. **标题**: 使用一级标题(`#`)
2. **引言**: 文章开头的简短介绍
3. **正文章节**: 使用二级标题(`##`)组织
4. **结语**: 通常是最后一个章节
5. **参考来源**: 在文章末尾使用以下格式
   ```markdown
   **（本文作者根据公开资料整理，参考了 [来源1]、[来源2] 等媒体的报道和资料，特此致谢。）**
   ```

## 转换脚本使用指南

本仓库提供了一个Python脚本，用于将Markdown文件自动转换为HTML页面，保留所有特殊格式和样式。

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用方法

```bash
python md2html.py <markdown文件路径>
```

例如：

```bash
python md2html.py "Epic 大战 Apple/epic 大战 apple.md"
```

脚本将在同一目录下生成`index.html`文件，包含完整的HTML页面，带有响应式设计、暗黑模式切换、目录导航等功能。

### 自定义选项

脚本支持以下自定义选项：

- `--title`: 自定义页面标题（默认使用Markdown的一级标题）
- `--output`: 指定输出文件路径（默认为同目录下的index.html）

例如：

```bash
python md2html.py "文章.md" --title "自定义标题" --output "custom/path/index.html"
```

## 维护指南

1. 所有内容编辑都应在Markdown文件中进行
2. 使用转换脚本生成HTML文件
3. 不要直接编辑生成的HTML文件
4. 如需修改样式或功能，请编辑`md2html.py`中的模板部分

## 目录结构

```
web-reads/
├── index.html                # 主页
├── README.md                 # 本指南
├── md2html.py                # 转换脚本
├── requirements.txt          # 依赖配置
└── [文章目录]/
    ├── [文章名].md           # Markdown源文件
    └── index.html            # 生成的HTML页面
```