# 🎶 올림픽공원 공연 소음 확산 트윈
(한국체육산업개발(주) 공공데이터 활용 경진대회)

공연 일정·관람객·날씨 데이터로 공연날 주변 주거지 소음을 예측하고, 서울시 S-DoT 실측값으로 검증해 3D 지도에 보여주는 웹 서비스

## 🛠 기술 스택 (Tech Stack)

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![CesiumJS](https://img.shields.io/badge/CesiumJS-6CADDF?style=for-the-badge&logo=cesium&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=for-the-badge&logo=openstreetmap&logoColor=white)

## ✨ 주요 기능 (Key Features)

- 🎬 **과거 공연 리플레이**
  - 2025년 올림픽공원 야외 페스티벌 5개를 시간대별로 재생
  - 무대에서 퍼지는 소음을 무지개색 히트맵과 파동으로 3D 지도에 표시
- 🔮 **재개장 대비 예측**
  - 무대·음향 출력·스피커 방향·풍향·관객 수를 바꿔보는 시나리오 모드
  - 생활소음 기준을 넘는 주거단지와 대응 방안을 바로 제안
- 📡 **실측 검증**
  - 공원 주변 S-DoT 센서 8개의 실제 소음과 모델 예측 비교
  - 같은 요일 공연 없는 주말 대비 소음 상승폭 표시
- 🏢 **주거단지별 소음 판정**
  - 공연·인파·교통 소음을 나눠 단지별로 표시
  - 소음·진동관리법 생활소음 규제기준 대비 초과 여부 판정

## 📊 사용 데이터

| 데이터 | 출처 | 상태 |
|---|---|---|
| 공연·시간별 관람객 수 (2025) | 문화공공데이터광장 | ✅ 실제 |
| 센서 위치·소음·기온 (2025) | 서울시 S-DoT | ✅ 실제 |
| 건물·도로·호수·공원 | OpenStreetMap | ✅ 실제 |
| 풍향·풍속 | 계절 평균 | ⚠️ 가정 |
| 시간당 입차 | 한국체육산업개발 연계 데이터 (연결 예정) | ⚠️ 샘플 |

## 📁 폴더 구조

```
├── index.html          화면 · 소음 모델 · 3D 지도
├── config.js           Cesium ion 토큰
├── osm.json            OpenStreetMap 지도 데이터
├── sdot.js             S-DoT 실측 데이터 (자동 생성)
├── tools/build_sdot.py S-DoT 원본 CSV → sdot.js 변환
└── data/               원본 데이터 (깃 제외)
```

<details>
<summary>🔊 소음 모델</summary>

공연 사운드(거리 감쇠, 공기 흡음, 풍향 보정, 스피커 지향성, 야간 기온역전, 건물 차폐) + 입·퇴장 인파 + 도로 교통 소음을 에너지 합산합니다. 판정 기준은 생활소음 규제기준(주간 65dB, 야간 60dB)입니다.
</details>

## 📚 데이터 출처

문화공공데이터광장 · 서울특별시 S-DoT · © OpenStreetMap contributors · 한국체육산업개발(주)
