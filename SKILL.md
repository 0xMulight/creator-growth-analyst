---
name: creator-growth-analyst
description: Analyze a creator's own X, YouTube or TikTok CSV data locally, compare posts within each platform, identify hook/retention/save-rate patterns where those metrics exist, and output an evidence-linked improvement plan. Never request passwords or fabricate metrics.
license: MIT
metadata:
  author: 0xMulight
  version: "1.0.0"
---

# Creator Growth Analyst — 内容增长复盘 Skill

## 什么时候用
用户希望复盘X、YouTube、TikTok、Instagram等平台的作品表现，比较选题、前三秒钩子、收藏、分享、完播或留存，并制定下一条内容实验。不能将分析建议伪装成增长保证。

## 所需输入
- 用户自愿提供的 **CSV** 内容数据。参考 `examples/sample-posts.csv` 或空白模板。
- 最少需要 `platform,title,views` 三列；其余 `likes,comments,shares,saves,retention_3s,completion_rate,topic,hook` 等为可选；缺失数据不视为0。
- 不需要账号密码、Cookie、access token、平台API Key。没有用户数据时先给空白模板，不要虚构浏览量或回报。
- 可以由用户手动从各平台后台导出并统一成模板，本仓库不宣称能自动连接X/YouTube/TikTok接口，也不读取他人私人数据。

## 执行工作流
1. 先明确用户关注的目标：播放、完播、收藏、互动、转化；如果已有数据可直接开始，不要反复问。
2. 检查列名、空值、指标含义与各平台时间区间，运行 `python -m creator_growth_analyst validate CSV路径`。数据异常就先停止。
3. 经允许，在能运行Python的环境里执行 `python -m creator_growth_analyst analyze CSV路径 --out reports`。
4. 阅读 `reports/report.md` 和 `reports/action_plan.json`，优先引用 **同一平台内的**高收藏率、有效互动率、留存/完播相关证据；若样本<3或指标缺失，标注“不足以判断”。
5. 输出 3 条以内的具体可执行实验：例如保持其他变量一致，测试两个钩子写法；给出具体下一条脚本建议，不要保证效果。
6. 只在用户明确请求、并且对应app/账号授权就绪的前提下安排发布；默认不自动发帖，不修改任何第三方数据。

## 一句话提示词
“请用 Creator Growth Analyst 复盘我这30条X/YouTube数据。先检查数据完整性，按平台分别找出收藏和留存表现最好的选题，并给我3个下一周能测试的改进方法。没有的数据写缺失，不要猜。”

## 解释口径
- `engagement_per_view` 是已提供的点赞+回复+转发+收藏除以播放量；部分字段缺失则属于“不完整互动率”。
- 所有平台都允许缺失3秒留存/完播率；**不能将观看量、曝光量、播放完成量混为一谈**。
- 少量数据只提示观察，不称统计显著；工具不做黑箱增长预测。
- Grok Bot是否能运行本机脚本，取决于用户是否授权执行；不能因为Skill存储在GitHub就声称自动接通平台。
