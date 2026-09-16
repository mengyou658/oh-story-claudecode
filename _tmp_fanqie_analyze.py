# -*- coding: utf-8 -*-
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(r'e:\oh-story-claudecode\_tmp_fanqie_out.txt')
_f = open(OUT, 'w', encoding='utf-8')
def print(*args, **kwargs):
    kwargs.setdefault('file', _f)
    __builtins__['print'](*args, **kwargs) if not isinstance(__builtins__, dict) else __builtins__['print'](*args, **kwargs)
# safer
import builtins
def print(*args, **kwargs):
    kwargs['file'] = _f
    builtins.print(*args, **kwargs)

def parse(path):
    text = Path(path).read_text(encoding='utf-8')
    genres = re.findall(r'^## (.+?) — (\d+) 本', text, re.M)
    titles_ok = re.search(r'标题解析：成功 (\d+) / 共 (\d+)', text)
    quality = re.search(r'数据质量：\[([^\]]+)\]', text)
    channel = re.search(r'全 (\d+) 题材', text)

    books = []
    current_genre = None
    lines = text.splitlines()
    for line in lines:
        m = re.match(r'^## (.+?) — (\d+) 本', line)
        if m:
            current_genre = m.group(1)
            continue
        m = re.match(r'^### #(\d+) (.+)$', line)
        if m:
            books.append({
                'genre': current_genre,
                'rank': int(m.group(1)),
                'title': m.group(2).strip(),
                'reads': None,
                'tags': [],
                'intro': '',
                'intro_tags': [],
            })
            continue
        if books and books[-1]['reads'] is None:
            m = re.search(r'(\d+(?:\.\d+)?)万 在读', line)
            if m:
                books[-1]['reads'] = float(m.group(1))
        if books and line.startswith('**标签：**'):
            books[-1]['tags'] = [t.strip() for t in line.replace('**标签：**', '').split('、') if t.strip()]

    collecting = False
    for line in lines:
        if line.strip() == '**简介**':
            collecting = True
            continue
        if collecting:
            if line.startswith('###') or line.startswith('##') or line.startswith('---'):
                collecting = False
                continue
            if line.strip():
                for b in reversed(books):
                    if not b.get('intro'):
                        b['intro'] = line.strip()
                        brackets = re.findall(r'【([^】]+)】', line)
                        brackets2 = re.findall(r'［([^］]+)］', line)
                        paren = re.findall(r'[（(]([^）)]+)[）)]', line)
                        tags_raw = []
                        for br in brackets + brackets2:
                            parts = re.split(r'[＋+\、,，/]', br)
                            tags_raw.extend([p.strip() for p in parts if p.strip() and len(p.strip()) < 40])
                        for p in paren:
                            if any(x in p for x in ['+', '＋', '、', '无cp', '无CP', '穿越', '重生', '种田']):
                                parts = re.split(r'[＋+\、,，/]', p)
                                tags_raw.extend([x.strip() for x in parts if x.strip() and len(x.strip()) < 40])
                        b['intro_tags'] = tags_raw
                        break
                collecting = False

    return {
        'genres': genres,
        'titles_ok': titles_ok.groups() if titles_ok else None,
        'quality': quality.group(1) if quality else None,
        'channel_n': channel.group(1) if channel else None,
        'books': books,
    }


def analyze(name, data):
    books = data['books']
    print(f'=== {name} ===')
    print(f'题材数(头): {data["channel_n"]}, 解析: {data["titles_ok"]}, 质量: {data["quality"]}')
    print(f'题材明细: {[(g, n) for g, n in data["genres"]]}')
    print(f'有效本数: {len(books)}, 有在读: {sum(1 for b in books if b["reads"])}')

    print('\n--- 题材头部在读 ---')
    genre_stats = []
    for g, n in data['genres']:
        gb = [b for b in books if b['genre'] == g]
        reads = [b['reads'] for b in gb if b['reads']]
        if not reads:
            continue
        genre_stats.append((
            g,
            reads[0],
            sum(reads[:3]) / min(3, len(reads)),
            sum(reads) / len(reads),
            max(reads),
            len(reads),
        ))
    genre_stats.sort(key=lambda x: -x[1])
    for row in genre_stats:
        print(f'{row[0]}: #1={row[1]}万 top3均={row[2]:.1f} 均值={row[3]:.1f} max={row[4]} n={row[5]}')

    print('\n--- 书名模式 ---')
    titles = [b['title'] for b in books]
    patterns = {
        '冒号结构': sum(1 for t in titles if '：' in t or ':' in t),
        '我/我靠开头感': sum(1 for t in titles if re.search(r'我|我靠|我有|我在|我成', t)),
        '穿/穿越': sum(1 for t in titles if '穿' in t),
        '重生': sum(1 for t in titles if '重生' in t),
        '末世': sum(1 for t in titles if '末世' in t),
        '游戏/副本': sum(1 for t in titles if any(x in t for x in ['游戏', '副本', '通关', '玩家', 'NPC', '主神'])),
        '系统': sum(1 for t in titles if '系统' in t),
        '领主/种田': sum(1 for t in titles if any(x in t for x in ['领主', '种田', '基建'])),
        '苟': sum(1 for t in titles if '苟' in t),
        '她': sum(1 for t in titles if '她' in t),
        '后+被/成了': sum(1 for t in titles if '后' in t and ('被' in t or '成了' in t or '她' in t)),
        '诸天/万界/综': sum(1 for t in titles if any(x in t for x in ['综', '同人', '诸天', '万界'])),
        '诡异/克苏鲁/无限': sum(1 for t in titles if any(x in t for x in ['诡异', '克苏鲁', '怪谈', '无限'])),
        '反派': sum(1 for t in titles if '反派' in t),
        '开局': sum(1 for t in titles if '开局' in t),
        '从X开始': sum(1 for t in titles if '从' in t and '开始' in t),
        '年代': sum(1 for t in titles if '年代' in t),
        '娱乐圈': sum(1 for t in titles if any(x in t for x in ['娱乐', '明星', '顶流', '影后', '影帝'])),
        '婚': sum(1 for t in titles if '婚' in t),
        '千金': sum(1 for t in titles if '千金' in t),
        '兽': sum(1 for t in titles if '兽' in t),
        '星际': sum(1 for t in titles if '星际' in t),
        '丧尸': sum(1 for t in titles if '丧尸' in t),
        '空间': sum(1 for t in titles if '空间' in t),
        '直播': sum(1 for t in titles if '直播' in t),
        '双穿/双重生': sum(1 for t in titles if '双重生' in t or '双穿' in t),
        '巫师': sum(1 for t in titles if '巫师' in t),
        '领主': sum(1 for t in titles if '领主' in t),
        '家族': sum(1 for t in titles if '家族' in t),
        '学院': sum(1 for t in titles if '学院' in t),
        '鉴宝/文物': sum(1 for t in titles if any(x in t for x in ['鉴宝', '文物', '博物馆'])),
        '短剧/漫剧书名': sum(1 for t in titles if '短剧' in t or '漫剧' in t),
        '囤': sum(1 for t in titles if '囤' in t),
        '假死/死遁': sum(1 for t in titles if any(x in t for x in ['假死', '死遁', '装死'])),
        '替嫁/冲喜': sum(1 for t in titles if any(x in t for x in ['替嫁', '冲喜', '换亲'])),
        '疯批': sum(1 for t in titles if '疯批' in t),
        '神明': sum(1 for t in titles if '神' in t),
    }
    for k, v in sorted(patterns.items(), key=lambda x: -x[1]):
        if v >= 3:
            print(f'  {k}: {v}')

    print('\n--- 简介【】热词 top45 (>=2) ---')
    tag_c = Counter()
    for b in books:
        for t in b.get('intro_tags', []):
            t2 = t.lower().replace('ｃｐ', 'cp')
            tag_c[t2] += 1
        for t in b.get('tags', []):
            tag_c[t.lower()] += 1
    for t, c in tag_c.most_common(45):
        if c >= 2:
            print(f'  {t}: {c}')

    print('\n--- 跨题材关键词 ---')
    keywords = [
        '末世', '丧尸', '重生', '穿越', '游戏', '副本', '系统', '苟', '种田', '基建',
        '领主', '诡异', '无限', '诸天', '万界', '反派', '无cp', '无CP', '大女主',
        '甜宠', '替嫁', '闪婚', '娱乐圈', '直播', '星际', '兽世', '空间', '囤货',
        '觉醒', '异能', '卡牌', '巫师', '西幻', '家族', '规则怪谈', '克苏鲁',
        '同人', '综', '悬疑', '推理', '电竞', '漫剧', '影视', '钢铁洪流', '上交国家',
        '买买买', '跟着重生', '装弱', '双洁', '先婚后爱', '年代文', '文娱',
        '第四天灾', '玩家', 'NPC', '主神', '地下城', '学院', '争霸', '万族',
    ]
    kw_genres = defaultdict(set)
    kw_count = Counter()
    for b in books:
        blob = b['title'] + ' ' + b.get('intro', '') + ' ' + ' '.join(b.get('intro_tags', [])) + ' ' + ' '.join(b.get('tags', []))
        blob_l = blob.lower()
        for kw in keywords:
            if kw.lower() in blob_l or kw in blob:
                kw_count[kw] += 1
                kw_genres[kw].add(b['genre'])
    for kw, c in kw_count.most_common(60):
        ng = len(kw_genres[kw])
        if c >= 3 and ng >= 2:
            gs = ','.join(sorted(kw_genres[kw]))
            print(f'  {kw}: {c}本/{ng}题材 [{gs}]')

    print('\n--- 全榜在读TOP15 ---')
    for b in sorted(books, key=lambda x: -(x['reads'] or 0))[:15]:
        print(f"  {b['reads']}万 [{b['genre']}] {b['title']}")

    # sample titles for key patterns
    print('\n--- 模式样例 ---')
    for key, pred in [
        ('末世书名', lambda t: '末世' in t),
        ('游戏相关书名', lambda t: any(x in t for x in ['游戏', '副本', '通关', '玩家', 'NPC'])),
        ('苟', lambda t: '苟' in t),
        ('领主', lambda t: '领主' in t),
        ('巫师', lambda t: '巫师' in t),
        ('从X开始', lambda t: '从' in t and '开始' in t),
        ('无CP简介', lambda b: any('无cp' in x.lower() for x in b.get('intro_tags', []) + b.get('tags', []))),
        ('漫剧/影视', lambda t: any(x in t for x in [])),
    ]:
        if key == '无CP简介':
            samples = [b['title'] for b in books if pred(b)][:8]
        elif key == '漫剧/影视':
            samples = [b['title'] for b in books if '漫剧' in b.get('intro', '') or '影视' in b.get('intro', '') or '漫剧' in ' '.join(b.get('intro_tags', []))][:8]
        else:
            samples = [b['title'] for b in books if pred(b['title'])][:8]
        if samples:
            print(f'  {key}: {samples}')

    return books, kw_count, kw_genres, genre_stats, tag_c


male = parse(r'e:\oh-story-claudecode\扫榜结果\跨平台_全榜_20260916\番茄男频阅读榜_全题材_20260916.md')
female = parse(r'e:\oh-story-claudecode\扫榜结果\跨平台_全榜_20260916\番茄女频阅读榜_全题材_20260916.md')
mb, mkw, mkg, mgs, mtag = analyze('男频', male)
fb, fkw, fkg, fgs, ftag = analyze('女频', female)

print('\n=== 交叉(两边各>=3) ===')
all_kw = set(mkw) | set(fkw)
for kw in sorted(all_kw, key=lambda k: -(mkw.get(k, 0) + fkw.get(k, 0))):
    mc, fc = mkw.get(kw, 0), fkw.get(kw, 0)
    if mc >= 3 and fc >= 3:
        print(f'{kw}: 男{mc}本/{len(mkg[kw])}题材 女{fc}本/{len(fkg[kw])}题材')

print('\n=== 男强女弱 / 女强男弱 ===')
for kw in sorted(all_kw, key=lambda k: -(mkw.get(k, 0) + fkw.get(k, 0))):
    mc, fc = mkw.get(kw, 0), fkw.get(kw, 0)
    if (mc >= 5 and fc <= 1) or (fc >= 5 and mc <= 1):
        side = '偏男' if mc > fc else '偏女'
        print(f'{side} {kw}: 男{mc} 女{fc}')
