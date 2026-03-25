# MyCalendar

一个用于生成中国黄历 iCalendar 文件的小工具，并附带一个可直接部署到 GitHub Pages 的静态下载页。

## 文件说明

- `generate_ics.py`：生成黄历 `.ics` 文件
- `chinese_almanac.ics`：当前生成好的日历文件
- `index.html`：GitHub Pages 首页，提供下载入口

## 本地生成黄历文件

```bash
python3 generate_ics.py --start 2026 --end 2028 --output chinese_almanac.ics
```

## 发布到 GitHub Pages

1. 把仓库 push 到 GitHub
2. 打开仓库的 `Settings > Pages`
3. `Source` 选择 `Deploy from a branch`
4. 分支选择 `main`
5. 目录选择 `/(root)`
6. 等待 GitHub 部署完成后访问：`https://qilpmgl.github.io/MyCalendar`

## 页面用途

GitHub Pages 首页会提供：

- `.ics` 文件直接下载入口
- GitHub 仓库入口
- 针对手机和桌面端都可访问的静态展示页
