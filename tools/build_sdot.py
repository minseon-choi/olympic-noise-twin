"""S-DoT 원본 CSV에서 공원 주변 센서의 공연일·평소 주말 소음과 날씨를 뽑아 sdot.js를 만든다.

사용법 (저장소 폴더에서):
    python3 tools/build_sdot.py "<S-DoT_NATURE_2025 압축 푼 폴더>" sdot.js

data/sdot_2025 폴더에 있는 파일도 함께 찾는다.
"""
import csv, glob, json, math, os, re, sys, statistics as st
from collections import defaultdict

SRC = sys.argv[1] if len(sys.argv) > 1 else 'data/sdot_2025'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'sdot.js'
EXTRA = [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sdot_2025')]

# 지도 원점 (index.html의 LAT0, LON0와 같아야 함)
LAT0, LON0 = 37.5206, 127.1215
KX, KY = 111320 * math.cos(math.radians(LAT0)), 110540

# 공원 주변 실제 S-DoT 센서 (설치위치정보 2026.3.11 기준)
SENSORS = [
    ('OC3CL200017', '성내동 강동대로 199 (대로변)', 37.52406575, 127.1285088),
    ('OC3CL210115', '성내동 435-12 (주거)', 37.525641, 127.129665),
    ('OC3CL200123', '성내동 강동대로 245 (도로·공원)', 37.52168425, 127.133751),
    # 제외: V02Q1940417 성내동 강동대로53길 (주거)
    #   낮 시간 소음이 측정 하한 35dB에 고정(한 시간 최대 36·최소 35)되고 밤에는 49~51dB로 바뀌는 패턴이
    #   공연 없는 날에도 반복되어 센서 이상으로 판단. 2025 축제일 9~23시 값의 81%가 정확히 35dB.
    ('OC3CL210107', '성내동 422 (주거)', 37.528351, 127.130989),
    ('OC3CL200070', '성내동 강동대로 143-22 (도로·공원)', 37.5271227, 127.121652),
    ('V02Q1940764', '오륜동 양재대로 1232 (주거)', 37.515327061, 127.134113236),
    ('V02Q1940832', '방이1동 양재대로71길 (주거)', 37.511768309, 127.124209484),
]
IDS = {s[0] for s in SENSORS}

# 공연일 → 같은 요일의 공연 없는 주말(앞뒤 1주)
EVENT_BASE = {
    '2025-05-30': ['2025-05-23', '2025-06-06'],
    '2025-05-31': ['2025-05-24', '2025-06-07'],
    '2025-06-01': ['2025-05-25', '2025-06-08'],
    '2025-06-14': ['2025-06-07', '2025-06-21'],
    '2025-06-15': ['2025-06-08', '2025-06-22'],
    '2025-06-28': ['2025-06-21', '2025-07-05'],
    '2025-06-29': ['2025-06-22', '2025-07-06'],
    '2025-09-13': ['2025-09-06', '2025-09-27'],
    '2025-09-14': ['2025-09-07', '2025-09-28'],
    '2025-09-20': ['2025-09-06', '2025-09-27'],
    '2025-09-21': ['2025-09-07', '2025-09-28'],
    '2025-10-18': ['2025-10-11', '2025-10-25'],
    '2025-10-19': ['2025-10-12', '2025-10-26'],
}
DATES = sorted(set(EVENT_BASE) | {d for v in EVENT_BASE.values() for d in v})


def find_file(date):
    y, m, d = date.split('-')
    ymd = y + m + d
    for root in [SRC] + EXTRA:
        hits = glob.glob(os.path.join(root, '**', f'*PUBDATA_{ymd}.csv'), recursive=True)
        if hits:
            return hits[0]
    for root in [SRC] + EXTRA:
        for f in glob.glob(os.path.join(root, '**', 'S-DoT_NATURE_*.csv'), recursive=True):
            mt = re.search(r'(\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})', os.path.basename(f))
            if not mt:
                continue
            a = f'{mt[1]}-{mt[2]}-{mt[3]}'
            ey = int(mt[1]) + (1 if mt[4] < mt[2] else 0)
            b = f'{ey}-{mt[4]}-{mt[5]}'
            if a <= date <= b:
                return f
    return None


def open_csv(path):
    for enc in ('utf-8-sig', 'cp949'):
        try:
            fh = open(path, encoding=enc)
            if '시리얼' in fh.readline():
                fh.seek(0)
                return fh
            fh.close()
        except UnicodeDecodeError:
            pass
    raise RuntimeError(f'인코딩을 알 수 없음: {path}')


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


noise = defaultdict(list)   # (serial, date, hour) -> [소음 평균]
wx = defaultdict(lambda: {'t': [], 'ws': [], 'wd': []})  # (date, hour)

files = defaultdict(set)
for d in DATES:
    f = find_file(d)
    if f:
        files[f].add(d)
    else:
        print('파일 없음:', d)

for f, want in files.items():
    print('읽는 중:', os.path.basename(f))
    for r in csv.DictReader(open_csv(f)):
        s = r.get('시리얼')
        if s not in IDS:
            continue
        t = r.get('측정시간', '')
        day, hh = t[:10], t[11:13]
        if day not in want or not hh.isdigit():
            continue
        h = int(hh)
        v = num(r.get('소음 평균(dB)'))
        if v is not None and 20 < v < 120:
            noise[(s, day, h)].append(v)
        w = wx[(day, h)]
        for key, col in (('t', '온도 평균(℃)'), ('ws', '풍속 평균(m/s)'), ('wd', '풍향 평균(m/s)')):
            x = num(r.get(col))
            if x is not None:
                w[key].append(x)


def hourly(s, day):
    return [round(st.mean(noise[(s, day, h)]), 1) if noise.get((s, day, h)) else None for h in range(24)]


def energy_mean(vals):
    vals = [v for v in vals if v is not None]
    return round(10 * math.log10(sum(10 ** (v / 10) for v in vals) / len(vals)), 1) if vals else None


out = {'sensors': [], 'days': {}, 'wx': {}}
for s, n, la, lo in SENSORS:
    out['sensors'].append({'id': s, 'n': n, 'x': round((lo - LON0) * KX), 'y': round((la - LAT0) * KY)})

for day, bases in EVENT_BASE.items():
    rec = {}
    for s, *_ in SENSORS:
        meas = hourly(s, day)
        base_rows = [hourly(s, b) for b in bases]
        base = [energy_mean([r[h] for r in base_rows]) for h in range(24)]
        rec[s] = {'meas': meas, 'base': base}
    out['days'][day] = rec
    t, ws_, wd = [], [], []
    for h in range(24):
        w = wx.get((day, h), {'t': [], 'ws': [], 'wd': []})
        t.append(round(st.median(w['t']), 1) if w['t'] else None)
        ws_.append(round(st.median(w['ws']), 1) if w['ws'] else None)
        if w['wd']:
            sx = sum(math.sin(math.radians(a)) for a in w['wd'])
            cx = sum(math.cos(math.radians(a)) for a in w['wd'])
            wd.append(round(math.degrees(math.atan2(sx, cx)) % 360))
        else:
            wd.append(None)
    out['wx'][day] = {'t': t, 'ws': ws_, 'wd': wd}

with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write('// tools/build_sdot.py로 만든 파일입니다. 직접 고치지 마세요.\n')
    fh.write('// 출처: 서울시 S-DoT 환경정보(2025), 시간대별 소음 평균(dB). base = 같은 요일 공연 없는 주말 2일의 에너지 평균.\n')
    fh.write('window.SDOT = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')

filled = sum(1 for d in out['days'].values() for s in d.values() for v in s['meas'] if v is not None)
wxn = sum(1 for d in out['wx'].values() for v in d['t'] if v is not None)
wdn = sum(1 for d in out['wx'].values() for v in d['wd'] if v is not None)
print(f'완료: {OUT} ({os.path.getsize(OUT)//1024} KB), 소음 {filled}칸, 기온 {wxn}칸, 풍향 {wdn}칸')
