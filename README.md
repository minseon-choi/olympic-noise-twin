# 🎶 올림픽공원 공연 소음 확산 트윈
(한국체육산업개발(주) 공공데이터 활용 경진대회)

공연 일정·관람객·날씨 데이터로 공연날 주변 주거지 소음을 예측하고, 서울시 S-DoT 실측값으로 검증해 3D 지도에 보여주는 웹 서비스

## 🛠 기술 스택 (Tech Stack)

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Three.js](https://img.shields.io/badge/Three.js-000000?style=for-the-badge&logo=threedotjs&logoColor=white)
![WebGL](https://img.shields.io/badge/WebGL-990000?style=for-the-badge&logo=webgl&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=for-the-badge&logo=openstreetmap&logoColor=white)

## ✨ 주요 기능 (Key Features)

- 🎬 **과거 공연 리플레이**
  - 2025년 올림픽공원 야외 페스티벌 5개를 날짜·시간대별로 재생
  - 55dB 이상 구역을 히트맵과 5dB 간격 등음선으로 3D 지도에 표시
- 🏢 **주거단지별 소음 판정**
  - 기준에 가까워지거나 넘는 아파트 동만 색으로 강조하고, 관련 없는 건물은 어둡게 처리
  - 단지 4곳의 기준 초과 동 수와 최대 소음을 소음·진동관리법 생활소음 기준(주간 65dB, 야간 60dB)과 비교
- 💬 **한 줄 요약**
  - 그 시각에 어느 단지가 왜 기준을 넘는지 문장으로 안내
- 📡 **실측 검증**
  - 공원 주변 S-DoT 센서 8개의 실제 소음과 모델 예측을 그래프로 비교
  - 같은 요일 공연 없는 주말 대비 소음 상승폭 표시

## 📊 사용 데이터

| 데이터 | 출처 | 상태 |
|---|---|---|
| 공연·시간별 관람객 수 (2025) | 문화공공데이터광장 | ✅ 실제 |
| 센서 위치·소음·기온 (2025) | 서울시 S-DoT | ✅ 실제 |
| 건물·도로·호수·공원 | OpenStreetMap | ✅ 실제 |
| 주차장 시간별 입출차 | 한국체육산업개발(주) | ✅ 실제 (2024.7 요일 유형 평균, 2025년 파일로 교체 예정) |
| 풍향·풍속 | 축제별 대표값 | ⚠️ 가정 |

## 📁 폴더 구조

```
├── index.html          화면 · 소음 모델 · 3D 지도 (Three.js)
├── osm.json            OpenStreetMap 지도 데이터
├── sdot.js             S-DoT 실측 데이터 (자동 생성)
├── parking.js          주차장 입출차 데이터 (자동 생성)
├── tools/
│   ├── build_sdot.py      S-DoT 원본 CSV → sdot.js
│   └── build_parking.py   주차장 입출차 CSV(data/parking/) → parking.js
└── data/               원본 데이터 (깃 제외)
```

> 지도 토큰이 필요 없습니다. `index.html`이 `osm.json`을 불러오므로 Live Server나 GitHub Pages처럼 웹 서버로 열어야 합니다.

<details>
<summary>🔊 소음 모델</summary>

공연 사운드(거리 감쇠, 공기 흡음, 지면 효과, 풍향 보정, 스피커 지향성, 야간 기온역전) + 입·퇴장 인파 + 도로 교통 소음(주차장 시간별 입출차 대수 반영)을 에너지 합산합니다. 판정 기준은 생활소음 규제기준(주간 65dB, 야간 60dB)입니다.

지도 위 선은 같은 소음 크기를 이은 등음선(5dB 간격)이고, 퍼져 나가는 파동 움직임은 시각 효과입니다.
</details>

## 📚 데이터 출처

문화공공데이터광장 · 서울특별시 S-DoT · © OpenStreetMap contributors · 한국체육산업개발(주)
