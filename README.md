# Website Build System

## 如何更新网站内容

1. 编辑 `content/` 目录下对应的 JSON 文件
2. 运行 `python3 build.py` 重新生成 index.html
3. 把 PDF 文件放到 `pdfs/` 目录，在 `content/publications.json` 中填写 pdf 文件名
4. 运行 `git add -A && git commit -m "..." && git push` 发布
