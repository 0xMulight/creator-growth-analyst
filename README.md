# 📈 Creator Growth Analyst

**Creator Tools 05 / 0xMulight**｜独立内容复盘 Skill + 真正能跑的本地 CSV 分析程序。

每条视频/帖子发完，看完数据就忘了？这个项目帮你**从真实数据找到下一条应该测试什么**。完全本地运行、无需账号登录。

## 能做什么
- 接受 **X、YouTube、TikTok** 或其他平台的手动汇总CSV，按平台拆开做比较。
- 计算播放量、已知互动/播放、收藏/播放、分享/播放；如果你提供3秒留存、完播率、平均观看时间，还能分析这些指标。
- 输出一个中文 `report.md`、一份 `metrics.csv`、一份供Bot阅读的 `action_plan.json`。
- 根据可用数据建议下一轮AB测试。缺数据写“缺失”，样本少时提醒，不编造热门结论。

## Windows 10 快速开始（不用终端）
1. 安装 [Python 3.10+](https://www.python.org/downloads/)，勾选 **Add Python to PATH**。
2. 下载本仓库ZIP并解压，双击 **`启动数据复盘.bat`**。
3. 先选 **1** 分析示例 `examples/sample-posts.csv`，看 `reports/report.md`。
4. 打开 `examples/blank-template.csv`，按同样列名粘贴你自己每篇内容的数据（用Excel保存为CSV UTF-8也可以）。
5. 选 **2** 输入你自己的CSV文件路径，生成独立报告。

## 命令行（可选）
```powershell
python -m creator_growth_analyst validate examples/sample-posts.csv
python -m creator_growth_analyst analyze examples/sample-posts.csv --out reports
```

## 数据列（最低只需前3项）
| 列名 | 意思 | 说明 |
|---|---|---|
| `platform` | 平台 | x / youtube / tiktok 等 |
| `title` | 作品标题 | 必填 |
| `views` | 播放/观看量 | 必填；请核实你所在平台口径 |
| `post_id,date,url` | 作品ID、日期、链接 | 可选 |
| `topic,hook` | 选题、前三秒/开头钩子 | 可选，方便复盘选题 |
| `likes,comments,shares,saves` | 点赞、评论、转发、收藏 | 可选，缺失绝不假装0 |
| `retention_3s,completion_rate` | 3秒留存率、完播率 | 可填 `0.64` 或 `64%`；有的平台不提供 |
| `avg_watch_seconds,video_seconds` | 平均观看秒数、视频时长 | 可选；不是自动识别 |
| `impressions,clicks,followers_gained` | 曝光、点击、涨粉 | 可选 |

**注意：** 各平台的观看、曝光、完播指标定义可能不同，报告**不合并成跨平台表现排行榜**。只记录你真实获取的指标，某列不支持就留空。分享和保存数值如 `1.2k` 也能识别。

## 用在Grok Bot里
> 根据我提供的内容数据，先校验字段，按平台分别看哪类选题最容易被收藏、哪些开头在前三秒流失严重，最后给我3个下周能执行的改进实验。没有留存数据就说没有，不能编。

参见 [SKILL.md](SKILL.md)。Grok Bot可以保存你教给它的工作流为Skill，但要运行本仓库Python程序，需要给Bot一个可访问代码与数据的执行环境或在自己的电脑上运行。**GitHub仓库本身不等于一键安装**。[官方Skill文档](https://docs.x.ai/grok-bot/skills-routines-and-automations)。

## 安全、隐私和边界
- 默认离线分析，不上传CSV，不索取Cookie/密码/令牌，不自动发帖。
- 不接入平台官方API，不自动下载X收藏或YouTube Studio的隐私数据；需要用户自行导出或手动填表。
- 只能发现数据相关性和指标异常，不能保证播放量提升。
- 样本量不足或字段不全时明确提示，不得伪造留存率或声称平台认可。

详细示例：[docs/workflow.md](docs/workflow.md)。MIT License。
