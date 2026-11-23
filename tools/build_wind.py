"""기상청 방재기상관측(AWS) 시간자료 CSV → wind.js

사용법 (저장소 루트에서):
    python tools/build_wind.py

data/wind/ 안의 CSV를 모두 읽습니다 (기상자료개방포털에서 받은 파일 그대로:
지점, 지점명, 일시, 풍향(deg), 풍속(m/s)).
같은 시각에 여러 지점 값이 있으면 PRIORITY 순서로 고릅니다. 송파가 비어 있는 시각은
다른 지점(예: 강동) 파일을 같이 넣어두면 그 값으로 채웁니다.
"""
import csv, glob, json, os
from collections import defaultdict
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "wind")
OUT = os.path.join(ROOT, "wind.js")
PRIORITY = ["송파", "강동", "서울"]  # 올림픽공원에서 가까운 순


def rows(path):
    for enc in ("utf-8-sig", "cp949"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"인코딩을 알 수 없음: {path}")


def rank(name):
    return PRIORITY.index(name) if name in PRIORITY else len(PRIORITY)


def main():
    files = sorted(glob.glob(os.path.join(SRC, "*.csv")))
    if not files:
        raise SystemExit(f"CSV가 없습니다: {SRC}")
    best = {}  # (date, hour) -> (rank, station, wd, ws)
    for p in files:
        for r in rows(p):
            try:
                t = datetime.strptime(r["일시"].strip(), "%Y-%m-%d %H:%M")
                wd, ws = float(r["풍향(deg)"]), float(r["풍속(m/s)"])
            except (KeyError, ValueError):
                continue
            st = r.get("지점명", "").strip()
            key = (t.strftime("%Y-%m-%d"), t.hour)
            if key not in best or rank(st) < best[key][0]:
                best[key] = (rank(st), st, wd, ws)
        print(f"읽음: {os.path.basename(p)}")

    stations = sorted({v[1] for v in best.values()}, key=rank)
    days = defaultdict(lambda: {"wd": [None] * 24, "ws": [None] * 24, "s": [None] * 24})
    for (d, h), (_, st, wd, ws) in best.items():
        days[d]["wd"][h] = round(wd)
        days[d]["ws"][h] = round(ws, 1)
        days[d]["s"][h] = stations.index(st)

    span = f"{min(days)} ~ {max(days)}"
    out = {"span": span, "stations": stations, "days": dict(sorted(days.items()))}
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("// tools/build_wind.py로 만든 파일입니다. 직접 고치지 마세요.\n")
        f.write(f"// 출처: 기상청 방재기상관측(AWS) 시간자료 ({', '.join(stations)}, {span}). s = stations 번호.\n")
        f.write("window.WIND = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"저장: {OUT} ({len(days)}일, 지점 {stations})")


if __name__ == "__main__":
    main()
