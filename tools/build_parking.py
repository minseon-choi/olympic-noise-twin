"""올림픽공원 주차장 입출차 CSV → parking.js

사용법 (저장소 루트에서):
    python tools/build_parking.py

data/parking/ 안의 CSV를 모두 읽습니다. 컬럼은 입차일시, 출차일시가 있으면 됩니다
(한국체육산업개발 입출차 정보 파일. 2024.7 파일과 2025년 연간 파일 모두 같은 형식).

parking.js 내용
    days[날짜]       그 날의 시간대별 입차(in)·출차(out) 대수 (실측)
    profile[weekday|weekend]  가진 데이터 전체의 시간대별 평균 (날짜가 없을 때 대신 씀)
"""
import csv, glob, json, os
from collections import defaultdict
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "parking")
OUT = os.path.join(ROOT, "parking.js")


def rows(path):
    for enc in ("utf-8-sig", "cp949"):
        try:
            with open(path, encoding=enc, newline="") as f:
                data = list(csv.DictReader(f))
            return data
        except UnicodeDecodeError:
            continue
    raise ValueError(f"인코딩을 알 수 없음: {path}")


def parse(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y%m%d%H%M%S", "%Y/%m/%d %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def main():
    files = sorted(glob.glob(os.path.join(SRC, "*.csv")))
    if not files:
        raise SystemExit(f"CSV가 없습니다: {SRC}")
    days = defaultdict(lambda: {"in": [0] * 24, "out": [0] * 24})
    n = 0
    for p in files:
        for r in rows(p):
            t_in, t_out = parse(r.get("입차일시")), parse(r.get("출차일시"))
            if t_in:
                days[t_in.strftime("%Y-%m-%d")]["in"][t_in.hour] += 1
                n += 1
            if t_out:
                days[t_out.strftime("%Y-%m-%d")]["out"][t_out.hour] += 1
        print(f"읽음: {os.path.basename(p)}")

    # 파일 경계에 걸친 날(입차 기록 없이 출차만 있는 날)은 빼기
    days = {d: v for d, v in days.items() if sum(v["in"]) > 0}

    prof = {}
    for kind, want in (("weekday", False), ("weekend", True)):
        ds = [d for d in days if (datetime.strptime(d, "%Y-%m-%d").weekday() >= 5) == want]
        if ds:
            prof[kind] = {
                k: [round(sum(days[d][k][h] for d in ds) / len(ds)) for h in range(24)]
                for k in ("in", "out")
            }
            prof[kind]["n"] = len(ds)

    span = f"{min(days)} ~ {max(days)}"
    out = {"span": span, "days": dict(sorted(days.items())), "profile": prof}
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("// tools/build_parking.py로 만든 파일입니다. 직접 고치지 마세요.\n")
        f.write(f"// 출처: 한국체육산업개발(주) 올림픽공원 주차장 입출차 정보 ({span}, 입차 {n:,}건)\n")
        f.write("window.PARKING = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"저장: {OUT} ({len(days)}일, {span})")


if __name__ == "__main__":
    main()
