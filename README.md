# L线 - 本地数据记录与多折线图分析工具

一个轻量级 Web 应用，帮助你在本地记录和可视化多条数据线的变化趋势。数据存储在本地 SQLite 数据库中，无需联网，安全私密。

## 截图

> 在此处添加应用截图
>
> ![主界面](screenshots/main.png)
> ![数据录入](screenshots/data-entry.png)

## 功能

- **多折线管理** — 自由添加、删除、重命名折线，自定义每条线的颜色
- **数据录入** — 选择折线 → 填入数值 → 选择日期，一键保存
- **交互式图表** — 基于 ECharts，支持滚轮缩放、鼠标拖动平移
- **标签标注** — 每个数据点可添加标签（如"空腹"、"服药后"），标注特殊含义
- **最大/最小值标记** — 图表自动标记每条折线的最大值和最小值
- **多种显示模式** — 悬停查看详情 或 全标签模式，自由切换
- **日期范围筛选** — 快捷键：全部 / 近7天 / 近30天 / 近90天 / 近1年 / 自定义
- **数据点编辑** — 点击图表上的数据点，弹窗修改数值、日期、标签或直接删除
- **数据持久化** — SQLite 本地存储，关闭浏览器数据不丢失
- **标签显示切换** — 可选择显示或隐藏标签、最大/最小值标记
- **首次引导** — 首次打开为空，引导用户添加第一条折线
- **桌面快捷方式** — 运行 `create-shortcut.bat` 一键在桌面创建带图标的快捷方式

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 (Composition API) + ECharts 5 + Axios |
| 后端 | Python Flask |
| 数据库 | SQLite |
| 构建工具 | Vite |

## 快速开始

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 构建前端

```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. 启动应用

```bash
python app.py
```

打开浏览器访问 `http://localhost:5000`

> **Windows 用户**：
> - 双击 `start.bat` 一键启动应用
> - 双击 `create-shortcut.bat` 可在桌面创建带图标的快捷方式（只需运行一次）

### 开发模式

```bash
# 终端 1：启动 Flask 后端
python app.py

# 终端 2：启动 Vite 开发服务器（支持热更新）
cd frontend
npm run dev
# 访问 http://localhost:5173
```

## 数据存储

所有数据保存在 `data/data.db`（SQLite），包含两张表：

- `lines` — 折线信息（名称、颜色、可见性）
- `data_points` — 数据点（数值、日期、标签，外键关联折线）

## 项目结构

```
├── app.py                  # Flask 应用入口
├── config.py               # 配置
├── database.py             # 数据库初始化与连接
├── requirements.txt        # Python 依赖
├── L.png                   # 应用图标（可替换为你的图标）
├── start.bat               # Windows 一键启动
├── create-shortcut.bat     # 创建桌面快捷方式
├── create_shortcut.py      # 快捷方式生成脚本
├── launch.vbs              # 静默启动（无控制台窗口）
├── routes/
│   ├── __init__.py
│   ├── lines.py            # 折线 CRUD API
│   └── data_points.py      # 数据点 CRUD API
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   │   └── L.png           # 网页图标
│   └── src/
│       ├── main.js
│       ├── App.vue          # 根组件
│       ├── api.js           # API 客户端
│       ├── styles/main.css
│       └── components/
│           ├── LineManager.vue          # 折线管理
│           ├── DataEntry.vue           # 数据录入
│           ├── ChartView.vue           # 图表渲染
│           ├── DateRangeFilter.vue     # 日期筛选
│           ├── DataPointEditDialog.vue # 数据点编辑
│           └── ConfirmDialog.vue       # 确认对话框
└── data/
    └── .gitkeep             # 数据库目录占位
```

## License

MIT
