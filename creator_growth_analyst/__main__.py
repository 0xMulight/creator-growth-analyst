"""Analyze manually exported post metrics with transparent formulas and missing-data handling."""
import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

REQUIRED={'platform','title','views'}
COUNTS=('views','impressions','likes','comments','shares','saves','clicks','followers_gained')
OPTIONAL_RATES=('retention_3s','completion_rate')
NUMERIC=('video_seconds','avg_watch_seconds')


def number(raw, col, line):
    if raw is None or str(raw).strip() == '':return None
    val=str(raw).strip().replace(',','').replace(' ','').replace('，','')
    multiplier=1
    if col in COUNTS and val[-1:].lower() in ('k','m'):
        multiplier=1000 if val[-1].lower()=='k' else 1000000
        val=val[:-1]
    try:f=float(val)*multiplier
    except (ValueError, OverflowError):raise ValueError(f'第{line}行 {col} 不是数字：{raw}')
    if not math.isfinite(f) or f < 0:
        raise ValueError(f'第{line}行 {col} 不允许负数或无穷大')
    if col in COUNTS and not f.is_integer():
        raise ValueError(f'第{line}行 {col} 必须是整数')
    return int(f) if col in COUNTS else f


def rate(raw, col, line):
    if raw is None or str(raw).strip()=='':return None
    s=str(raw).strip().replace(' ','')
    is_pct=s.endswith('%')
    if is_pct:s=s[:-1]
    x=number(s,col,line)
    if x is None:return None
    if is_pct or x > 1:x/=100
    if not 0 <= x <= 1:raise ValueError(f'第{line}行 {col} 必须在0%到100%之间')
    return x


def load_rows(path):
    path=Path(path)
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames:raise ValueError('CSV没有标题行')
        fields={x.strip() for x in reader.fieldnames if x}
        missing=REQUIRED-fields
        if missing:raise ValueError('CSV缺少必需列：'+', '.join(sorted(missing)))
        records=[]
        for lineno,raw in enumerate(reader,2):
            d={k.strip():str(v or '').strip() for k,v in raw.items() if k is not None}
            if not any(d.values()):continue
            if not d.get('platform') or not d.get('title'):
                raise ValueError(f'第{lineno}行需要platform和title')
            obj={k:d.get(k,'') for k in ('platform','post_id','title','topic','hook','date','url')}
            for k in COUNTS:obj[k]=number(d.get(k),k,lineno)
            for k in OPTIONAL_RATES:obj[k]=rate(d.get(k),k,lineno)
            for k in NUMERIC:obj[k]=number(d.get(k),k,lineno)
            if obj['views'] is None:
                raise ValueError(f'第{lineno}行缺少views')
            if obj['video_seconds'] is not None and obj['video_seconds']<=0:
                raise ValueError(f'第{lineno}行video_seconds必须大于0')
            views=obj['views']
            known={k:obj[k] for k in ('likes','comments','shares','saves') if obj[k] is not None}
            obj['observed_interactions']=sum(known.values()) if known else None
            obj['engagement_per_view']=(obj['observed_interactions']/views) if (known and views) else None
            obj['save_per_view']=(obj['saves']/views) if (obj['saves'] is not None and views) else None
            obj['share_per_view']=(obj['shares']/views) if (obj['shares'] is not None and views) else None
            obj['avg_watch_ratio']=((obj['avg_watch_seconds']/obj['video_seconds']) if (obj['avg_watch_seconds'] is not None and obj['video_seconds'] is not None) else None)
            obj['present_interaction_columns']=','.join(known)
            records.append(obj)
    if not records:raise ValueError('CSV没有有效数据')
    return records,fields


def pct(x):return '缺失' if x is None else f'{x*100:.2f}%'


def median(values):
    vs=[v for v in values if v is not None]
    return statistics.median(vs) if vs else None


def analyze(records, fields, min_views=100):
    groups=defaultdict(list)
    for r in records:groups[r['platform'].lower()].append(r)
    lines=['# Creator Growth Analyst｜内容数据复盘','','> 数据来自用户提供的CSV；只做本地统计，不抓取账号数据。不同平台的播放/互动口径不可直接横比。','','## 数据概况',f'- 内容数：{len(records)}；涉及平台：{len(groups)}。','- 互动率 = (已提供的点赞+评论+分享+收藏)/播放量。未提供的字段**不按0处理**，互动率有可能只是部分指标。',f'- 小样本阈值：播放量至少{min_views}才进入榜单，样本不足时标注。','','## 平台内对比']
    result={'meta':{'posts':len(records),'platforms':len(groups),'min_views':min_views,'note':'Missing counts are null, not zero; per-view metrics may be partial.'},'platforms':{},'recommendations':[],'warnings':[]}
    for platform,subset in sorted(groups.items()):
        eligible=[r for r in subset if r['views']>=min_views]
        lines += ['',f'### {platform.upper()} · {len(subset)}条',f'- 播放中位数：{median([r["views"] for r in subset]):,.0f}；有效样本：{len(eligible)}条。']
        complete=[r for r in eligible if all(r[k] is not None for k in ('likes','comments','shares','saves'))]
        med=median([r['engagement_per_view'] for r in eligible if r['engagement_per_view'] is not None])
        lines.append(f'- 已知互动/播放中位数：{pct(med)}；完整4项互动字段：{len(complete)}/{len(eligible)}。')
        ranked=sorted([r for r in eligible if r['engagement_per_view'] is not None],key=lambda r:r['engagement_per_view'],reverse=True)
        if ranked:
            lines += ['','| 代表作品 | 播放 | 已知互动/播放 | 收藏/播放 | 分享/播放 |','|---|---:|---:|---:|---:|']
            for r in ranked[:5]:
                title=r['title'].replace('|','/').replace('\n',' ')
                lines.append(f'| {title[:45]} | {r["views"]:,} | {pct(r["engagement_per_view"])} | {pct(r["save_per_view"])} | {pct(r["share_per_view"])} |')
        else:lines.append('- 没有满足最小播放量且带互动字段的帖子，暂不排名。')
        ret=[r['retention_3s'] for r in subset if r['retention_3s'] is not None]
        complete_rate=[r['completion_rate'] for r in subset if r['completion_rate'] is not None]
        if ret or complete_rate:
            lines.append(f'- 3秒留存中位数：{pct(median(ret))}；完播率中位数：{pct(median(complete_rate))}。')
        result['platforms'][platform]={'posts':len(subset),'eligible_posts':len(eligible),'median_views':median([r['views'] for r in subset]),'median_observed_engagement_per_view':med,'complete_interaction_posts':len(complete),'median_retention_3s':median(ret),'median_completion_rate':median(complete_rate),'top_posts':[{'title':r['title'],'views':r['views'],'engagement_per_view':r['engagement_per_view']} for r in ranked[:5]]}
        if len(subset)<3:
            msg=f'{platform.upper()}只有{len(subset)}条，不能据此断定某种内容表现更好。';lines.append('- ⚠️ '+msg);result['warnings'].append(msg)
        topic_groups=defaultdict(list)
        for r in eligible:
            if r['topic']:topic_groups[r['topic']].append(r)
        topic_rank=[(topic,vals,median([x['save_per_view'] for x in vals]),median([x['engagement_per_view'] for x in vals])) for topic,vals in topic_groups.items() if len(vals)>=2]
        topic_rank.sort(key=lambda r:(r[2] is not None,r[2] if r[2] is not None else -1),reverse=True)
        if topic_rank:
            lines+=['','**同平台多条选题观察**（每组至少2条）：']
            for topic,vals,save,eng in topic_rank[:3]:lines.append(f'- {topic}：{len(vals)}条，收藏/播放中位数 {pct(save)}，已知互动/播放中位数 {pct(eng)}。')
        # Suggest only where data exists; never invent retention data
        if ret and median(ret)<0.5:
            result['recommendations'].append({'platform':platform,'reason':f'3秒留存中位数{pct(median(ret))}','action':'优先测试前3秒直接给结果的开头；下一轮保留其他变量一致','priority':'high'})
        if complete_rate and median(complete_rate)<0.25:
            result['recommendations'].append({'platform':platform,'reason':f'完播率中位数{pct(median(complete_rate))}','action':'压缩铺垫与重复镜头，先做一组时长AB测试','priority':'high'})
        save_med=median([r['save_per_view'] for r in eligible])
        if save_med is not None and save_med>=0.01:
            result['recommendations'].append({'platform':platform,'reason':f'收藏/播放中位数{pct(save_med)}','action':'复用有收藏价值的模板、步骤和清单，同时观察样本是否持续','priority':'medium'})
        if not eligible:
            result['recommendations'].append({'platform':platform,'reason':'没有达到阈值的样本','action':f'先累计播放≥{min_views}的作品，再做选题结论','priority':'low'})
    if not result['recommendations']:
        result['recommendations'].append({'platform':'all','reason':'没有满足预设规则的显著模式','action':'继续按平台积累播放量、收藏和3秒留存数据，暂不强行下结论','priority':'low'})
    lines+=['','## 下一轮实验（建议，不是因果结论）']
    for x in result['recommendations']:
        lines.append(f'- **{x["platform"]}**：{x["action"]}。依据：{x["reason"]}。')
    absent=[x for x in ('saves','shares','retention_3s','completion_rate') if x not in fields]
    if absent:
        warning='原始CSV缺少这些整列指标：'+', '.join(absent)+'；不应写成0。'
        result['warnings'].append(warning)
    lines+=['','## 数据边界与下一步']
    for x in result['warnings']:lines.append('- ⚠️ '+x)
    lines+=['- X、YouTube、TikTok的观看次数、留存口径可能不同：**不要合并成跨平台总排名**。','- 同一平台的不同内容长度、发布时间和流量来源会影响结果，建议做同主题A/B测试。','- 建议下一轮记录：内容主题、开头、发布时间、播放量、点赞、评论、转发、收藏、3秒留存和完播率（如果平台提供）。','- 这是描述性统计与经验规则，不证明改动必然提升播放量；未经用户批准不发布内容或修改账号。','']
    return '\n'.join(lines),result


def write_metrics(rows,out):
    fieldnames=['platform','post_id','title','topic','hook','date','url','views','impressions','likes','comments','shares','saves','clicks','followers_gained','retention_3s','completion_rate','avg_watch_seconds','video_seconds','observed_interactions','present_interaction_columns','engagement_per_view','save_per_view','share_per_view','avg_watch_ratio']
    with (out/'metrics.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fieldnames);w.writeheader()
        for r in rows:w.writerow({k:'' if r.get(k) is None else r.get(k,'') for k in fieldnames})


def main(argv=None):
    p=argparse.ArgumentParser(description='Creator Growth Analyst：本地CSV复盘，缺失数据不编造')
    subs=p.add_subparsers(dest='command',required=True)
    for c in ('validate','analyze'):
        s=subs.add_parser(c);s.add_argument('csv')
        if c=='analyze':s.add_argument('--out',default='reports');s.add_argument('--min-views',type=int,default=100)
    args=p.parse_args(argv)
    try:
        records,fields=load_rows(args.csv)
        print(f'数据校验成功：{len(records)}条、{len(set(r["platform"].lower() for r in records))}个平台')
        if args.command=='analyze':
            if args.min_views<1:raise ValueError('--min-views 必须≥1')
            out=Path(args.out).expanduser().resolve();out.mkdir(parents=True,exist_ok=True)
            md,insights=analyze(records,fields,args.min_views)
            (out/'report.md').write_text(md,encoding='utf-8')
            (out/'action_plan.json').write_text(json.dumps(insights,ensure_ascii=False,indent=2),encoding='utf-8')
            write_metrics(records,out)
            print('已生成：'+str(out/'report.md')+'、metrics.csv、action_plan.json')
        return 0
    except (OSError,ValueError,csv.Error) as exc:
        print('错误：'+str(exc),file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
