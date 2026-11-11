# SKU 카탈로그 스냅샷 v0.1 — 워커힐 공식 카탈로그

- 스냅샷 일자: **2026-11-11**
- 원천: walkerhill.com 공식 카탈로그 (허브 `/en/Stay`, `/about/Map` · 그랜드 한국어 `/grandwalkerhillseoul/room`, `/grandwalkerhillseoul/Package`)
- 수집 방법: 공개 카탈로그 직접 열람·수동 컴파일. OTA 스크래핑 없음(자사 공개 페이지만).
- 용도: `review-persona-survey-v0.1.md` §4의 연결 앵커. 리뷰→상품 연결의 목적 집합(target set)이며, `product` 테이블 `official_*` 필드는 **본 스냅샷 v1만을 원천**으로 한다.
- 갱신 규율: 패키지는 시즌 회전이 있으므로 갱신 시 새 버전 파일(v0.2)을 만들고 기존 버전은 폐기하지 않는다(크로스워크 감사용). 객실은 구조적 변화(신설·리모델링)가 있을 때만 갱신.

<!-- anchors: OTA 스크래핑 없음(자사 공개 페이지만) | 기존 버전은 폐기하지 않는다(크로스워크 감사용) | 본 스냅샷 v1만을 원천으로 한다 | 동일한 official 스탠다드에 서로 다른 표기 | 객실 SKU 합계: 그랜드 17 + 더글라스 3 + 비스타 14 = 34종 | 매핑 테이블 자체를 버전 관리한다 | 미등장 SKU 일반화가 매처의 약점이라 | 성인 전용(Adults-Only) -->

---

## 1. 부동산(portfolio) 구조

| 키 | 명칭 · 위치 | 객실 수 | 비고 |
|---|---|---|---|
| GRAND | 그랜드 워커힐 서울 · 서울 광진구 워커힐로 177 | 557실 | 본관. 조사 단계 공식 페이지 기준 검증값(2026-11-11) |
| VISTA | 비스타 워커힐 서울 · 동일 부지 | 미확보 | B1·로비 통로로 그랜드와 연결 |
| DOUGLAS | 더글라스 하우스 · 동일 부지 | 50실 | 성인 전용(Adults-Only) |
| ASTON | 애스톤 하우스 · 동일 부지 | 미확보 | 가이드맵 숙박 목록에 확인, 상세 미수집 |
| DARAKHYU | 다락휴 · 인천공항 T1·T2, 여수 엑스포 | 미확보 | 스마트 호텔(시간제, 최소 3시간) |
| TRANSIT | 인천공항 환승호텔 · 인천공항 T1·T2 | 미확보 | 시간제(최소 6시간, 20시 이후 OVERNIGHT) |
| MATINA | 마티나 라운지 · 인천공항 환승호텔 | — | 라운지(Matina GOLD 별도 운영) |

운영 법인: SK네트웍스(주) (사업자등록번호 124-81-00718, 통신판매 신고 제2015-서울광진-0710호) — 각 페이지 footer 확인.

---

## 2. 객실 SKU

### 2.1 그랜드 워커힐 서울 (한국어 객실종합안내 기준, 사이트 분류 체계 그대로)

| 분류 | sku_ko / sku_en | 위치·실수(공식 고지) | URL slug |
|---|---|---|---|
| GRAND DELUXE | 스탠다드 / Standard | 본관 3층·5층, 실수 미고지 | `room/Standard` |
| GRAND DELUXE | 딜럭스 / Deluxe | 본관, 실수 미고지 | `room/Deluxe` |
| GRAND DELUXE | 딜럭스 스위트 / Deluxe Suite | 본관 14층, 실수 미고지 | `room/DeluxeSuite` |
| GRAND DELUXE | 키즈 딜럭스 스위트 / Kids Deluxe Suite | 본관 14층, 실수 미고지 | `room/KidsDeluxeSuite` |
| GRAND DELUXE | 패밀리 딜럭스 스위트 / Family Deluxe Suite | 호텔 8층 (17실) | `room/FamilyDeluxeSuite` |
| GRAND DELUXE | 비건 스위트 / Grand Vegan Suite | 호텔 8층 (3실) | `room/GrandVeganSuite` |
| GRAND CLUB | 클럽 딜럭스 / Club Deluxe | 호텔 8~15층 (21실) | `room/Club-Deluxe` |
| GRAND CLUB | 클럽 스위트 / Club Suite | 9·10층 (34실) + 15·16층 (22실) | `room/Club-Suite` |
| GRAND CLUB | 바비 스위트 / Club Barbie Suite | 호텔 16층 (2실) — 'Forever Barbie'/'New Dreams' 2콘셉트 | `room/Club-Barbie-Suite` |
| GRAND CLUB | 클럽 트레디셔널 스위트 / Club Traditional Suite | 호텔 9·10층 (6실) — 온돌 모티브 | `room/Club-Traditional-Suite` |
| GRAND CLUB | 허니문 스위트 / Club Honeymoon Suite | 호텔 8층 (3실) | `room/Club-Honeymoon-Suite` |
| GRAND CLUB | 그랜드 스위트 / Grand Suite | 호텔 17층 (4실) — 한실/양실 2타입 | `room/Grand-Suite` |
| GRAND CLUB | 그랜드 패밀리 스위트 / Grand Family Suite | 호텔 15·16층 (6실) | `room/Grand-Family-Suite` |
| GRAND CLUB | 로열 스위트 / Royal Suite | 호텔 17층 (1실) | `room/Royal-Suite` |
| GRAND CLUB | 프리미어 스위트 / Premier Suite | 호텔 17층 (1실) | `room/Premier-Suite` |
| GRAND CLUB | 프레지덴셜 스위트 / Presidential Suite | 호텔 17층 (1실) — 국빈급 VIP 전용 | `room/Presidential-Suite` |
| VILLA | 빌라 / Villa | 워커힐 야외(숲 속 별장), 실수 미고지 | `room/villa` |

비고: GRAND CLUB 권역에는 객실 외 혜택 시설로 **클럽라운지**(`room/GrandClub-by-Walkerhill`)가 있음 — 리뷰에서 "클럽라운지" 언급은 클럽 권역 객실의 부속 속성으로 취급.

### 2.2 더글라스 하우스 (성인 전용)

| sku_ko | sku_en | URL slug |
|---|---|---|
| 딜럭스 | Douglas Deluxe (Adults-Only) | `douglas/room/DouglasDeluxe` |
| 트레디셔널 스위트 | Traditional Suite (Adults-Only) | `douglas/room/TraditionalSuite` |
| 스위트 | Douglas Suite (Adults-Only) | `douglas/room/DouglasSuite` |

### 2.3 비스타 워커힐 서울 (영어 페이지 기준 — 한국어 상세 페이지는 §6 미수집)

| sku_en | URL slug |
|---|---|
| Vista Deluxe | `room/VistaDeluxe` |
| Vista Deluxe Balcony | `room/VistaDeluxeBalcony` |
| Spa Deluxe | `room/SpaDeluxe` |
| Signature Deluxe | `room/SignatureDeluxe` |
| Signature Deluxe Balcony | `room/SignatureDeluxeBalcony` |
| Signature Spa Deluxe | `room/SignatureSpaDeluxe` |
| Junior Corner Suite | `room/JuniorCornerSuite` |
| Junior Spa Suite | `room/JuniorSpaSuite` |
| Studio Suite | `room/StudioSuite` |
| Corner Suite | `room/CornerSuite` |
| Spa Suite | `room/SpaSuite` |
| Ambassador Suite | `room/AmbassadorSuite` |
| Super Spa Suite | `room/SuperSpaSuite` |
| Presidential Suite | `room/PresidentialSuite` |

객실 SKU 합계: **그랜드 17 + 더글라스 3 + 비스타 14 = 34종**.

---

## 3. 패키지 SKU (2026-11-11 기준, 사이트 고지 "총 14건")

`pkg_id`는 공식 페이지 URL 식별자(`/grandwalkerhillseoul/Package/{id}`). 가격은 "세금 및 봉사료 포함" 최저가 표기.

| pkg_id | property | 패키지명 · 키워드 | 판매 기간 · 가격(KRW~) |
|---|---|---|---|
| 8859 | GRAND | Hyvää Joulua 휘바 욜루아 — 2026 산타 키즈 빌리지 입장 | 2026.12.18~12.25 · 549,000 |
| 8865 | GRAND | Santa Night Village — 2026 산타 나이트 빌리지 입장 | 2026.12.18~12.25 · 457,000 |
| 8829 | GRAND | [가을] 캠크닉 인더 포레스트 — 캠크닉·불멍·포레스트 카라반·소파 라운지·포레스트 파크 | 2026.08.24~11.30 · 247,000 |
| 8871 | DOUGLAS | Santa Night Village — 2026 산타 나이트 빌리지 입장 | 2026.12.18~12.25 · 529,000 |
| 8831 | DOUGLAS | [가을] 체크인 불멍 — 캠크닉·불멍·포레스트 카라반 | 2026.08.24~11.30 · 319,000 |
| 8770 | DOUGLAS | [1인] 나홀로 쉼 — 1인 전용·더글라스 라운지·웰컴 리추얼 기프트 | 2026.03.30~12.31 · 259,000 |
| 8797 | GRAND | 두근두근 성수 Ver.2 — 성수 패키지·웰니스 사우나·향수 공방 클래스·1박 or 2박 | 2026.05.18~12.31 · 290,000 |
| 5181 | GRAND | [빌라] One Stay, Only Yours — 프라이빗 빌라·룸서비스·웰컴 플래터 (사이트 예약 버튼 비노출) | 2025.03.24~2026.12.31 · 899,000 |
| 8625 | GRAND | The Triple Stay — 3인 패키지·클럽 라운지·주중 한정 | 2025.03.10~2026.12.31 · 659,000 |
| 8588 | GRAND | Barbie Suite — 바비 스위트 연계 | 2024.02.29~2026.12.31 · 689,000 |
| 3262 | DOUGLAS | Rest Together — 2~3인·더글라스 라운지·콰트로 피자 | 2024.01.01~2026.12.31 · 387,000 |
| 8587 | GRAND | Memorable Familycation — 패밀리·키즈 스위트룸·인룸 키즈 텐트·콤비네이션 피자 | 2024.01.01~2026.12.31 · 457,000 |
| 6141 | GRAND | [특가] Early Bird Sale — 홈페이지 사전 예약 최대 할인 | 2024.01.01~2026.12.31 · 미고지 |
| 8388 | GRAND | Begin Vegan — 국내 최초 비건룸·비건 미니바·더뷔페 조식 | 2024.01.01~2026.12.31 · 459,000 |

### 3.1 프로모션 (객실 패키지 외, 동일 페이지 고지)

| id | 명칭 | 기간 · 금액 | 유형 |
|---|---|---|---|
| 8856 | 싱가포르 항공 '크리스플라이어' 더블 마일리지 | 2026.10.01~11.30 · 금액 미고지 | 항공 제휴 |
| 8862 | [온달] 겨울바다 낙지정찬 | 2026.11.02~11.30 · 85,000 | 다이닝 (venue: Ondal) |
| 8861 | [금룡] 설향진미 (雪香珍味) | 2026.11.02~12.31 · 150,000 | 다이닝 (venue: Geumryong) |
| 8824 | 워커힐을 담다: 시그니처 리큐어 | 2026.07.01~11.30 · 45,000 | 다이닝·기념품 |

---

## 4. 다이닝·시설 venue 마스터

### 4.1 다이닝 (영어 네비게이션 URL로 property 귀속 확인)

| venue_key | 명칭 (유형) | property | 비고 |
|---|---|---|---|
| Ondal | 온달 (한식당) | GRAND | |
| Geumryong | 금룡 (중식당) | GRAND | |
| LePassage | 르 파사쥬 (고메스토어) | GRAND | |
| ThePavilion | 더파빌리온 (로비 라운지) | GRAND | |
| LuxBar | LUX BAR (클럽 라운지 바) | GRAND | |
| TheBuffet | 더뷔페 (파인 다이닝 뷔페) | VISTA | 그랜드 한국어 네비에도 링크 존재하나 Map·영어 네비 기준 VISTA 귀속 |
| Moegi | 모에기(MOEGI, 일식) | VISTA | |
| Myongwolgwan | 명월관 | VISTA | |
| PizzaHill | 피자힐 | VISTA | 산책로 A 코스상 명월관→피자힐 인접 |
| Geumryong31 | 31금룡 | 별도 사이트 | `www.31geumryong.com` 외부 도메인 운영 |
| Matina | 마티나 라운지 (라운지) | TRANSIT | Matina GOLD 별도 |

### 4.2 시설·액티비티·웰니스 (가이드맵 분류 그대로)

| category | venue_key | 명칭 | 비고 |
|---|---|---|---|
| 즐길거리 | WalkerhillLibrary | 워커힐 라이브러리 | |
| 즐길거리 | DouglasLibrary | 더글라스 라이브러리 | |
| 즐길거리 | Casino | 카지노 | 외국인 전용 |
| 즐길거리 | ForestPark | 포레스트 파크 | |
| 즐길거리 | LightTheater | 빛의 시어터 | |
| 액티비티 | RiverPark | 리버파크 | |
| 액티비티 | TenesseePark | 테네즈 파크 | |
| 액티비티 | Fitness | 피트니스 센터 | |
| 액티비티 | IndoorPool | 실내 수영장 | |
| 액티비티 | GolfClub | 워커힐 골프클럽 | 예약 경로 별도(`/GolfClub`) |
| 웰니스 | SKYARD | 스카이야드 | 시그니처 보타닉 가든 (VISTA) |
| 웰니스 | VSPA | V SPA | 프리미엄 코스메틱 (VISTA) |
| 웰니스 | WellnessClub | 웰니스 클럽 | VISTA |
| 웰니스 | DouglasGarden | 더글라스 가든 | |
| 웰니스 | HealingForest | 힐링 포레스트 | |
| 라운지 | ClubLounge | 클럽라운지 | GRAND — 클럽 객실 부속 혜택 |
| 라운지 | DouglasLounge | 더글라스 라운지 | DOUGLAS — 패키지 8770·3262 연계 |
| 편의시설 | ParkingEV | 주차타워 전기차 충전 | |
| 편의시설 | CU | CU 편의점 | |
| 편의시설 | Blooming | 블루밍 (플라워샵) | |
| 옥외 | WalkTrailA~D | 산책로 A~D | 명월관·피자힐·더글라스 가든 경유 코스 |
| 옥외 | JoggingCourse | 조깅코스 | 2km / 15분 |

### 4.3 웨딩 & 미팅 (수용인원 공식 고지)

| venue_key | 명칭 | 위치 | 수용인원 |
|---|---|---|---|
| VistaHall | 비스타홀 | 비스타 B2 | 400~800명 |
| WalkerHall | 워커홀 | 컨벤션 센터 1F | 300~400명 |
| GrandHall | 그랜드홀 | 비스타 B1 | 대연회장 250~550명 / 소연회장 20~140명 |
| ArtHall | 아트홀 | 컨벤션 센터 4F | 60~150명 |
| Pine | 파인 | 컨벤션 센터 4F | 30~40명 |
| Oak | 오크 | 컨벤션 센터 4F | 30~40명 |

### 4.4 기타 판매 채널 (venue 마스터 외 참고)

- 멤버십: 워커힐 리워즈 / 워커힐 프레스티지 클럽(WPC) / STAR VIP — `rate_plan_class`의 MEMBER·B2B 축과 연결.
- 상품권: 워커힐 상품권 50,000·100,000원, 뷔페 상품권 198,000원(저녁 성인 1인) — 더뷔페 가격대의 공식 근거.
- 워커힐 스토어: `store.walkerhill.com` (온라인 상점, 상세 미수집).

---

## 5. 데이터모델 매핑 규칙

본 스냅샷은 `product` 테이블의 원천이 된다:

```sql
product(product_id, official_room_type, official_package_name, view_type,
        rate_plan_class, venue_key, valid_from, valid_to)
-- official_room_type      <- §2 sku_ko / sku_en
-- official_package_name   <- §3 패키지명 (pkg_id 보존)
-- venue_key               <- §4 venue_key
-- view_type ∈ {RIVER, MOUNTAIN, NONE, NA}  -- OTA가 만든 축: official 스키마와 분리·별도 관리
-- rate_plan_class ∈ {PUBLIC, MEMBER, B2B, PACKAGE}
-- valid_from/valid_to     <- §3 판매 기간; 객실은 스냅샷 버전 기준
```

크로스워크 규율:

1. 모든 OTA 상품 라벨은 두 번 저장한다 — `raw_label`(감사용 원문) + `product_id`(분석용). 매핑 테이블 자체를 버전 관리한다.
2. OTA 라벨은 변형이 잦다. 실측 예: `스탠다드 트윈룸 (낮은 층, 전망 없음)`과 `스탠다드 트윈룸 전망없음(3층&5층)`은 동일한 official 스탠다드에 서로 다른 표기.
3. 링크 검증셋(ground truth 500~1,000쌍)은 본 스냅샷 §2·§3에서 생성한다. WDC Products 등 기존 매칭 벤치마크에 호스피탈리티 슬라이스가 없어 자체 구축이 필수이며, 미등장 SKU 일반화가 매처의 약점이라는 점(엔티티 매칭 문헌 공통)을 감안한다.

---

## 6. 미수집 항목 (다음 스냅샷 또는 1차 데이터 확보 시)

| 항목 | 필요성 |
|---|---|
| 비스타 한국어 객실 상세 페이지 (`/vistawalkerhillseoul/room/`) | 한국어 OTA 라벨 매칭 타깃 — 영어 sku_en만으로는 국내 OTA 크로스워크 불가 |
| 애스톤 하우스 상세 | 가이드맵에만 확인, SKU·객실 수 미확보 |
| 다락휴·환승호텔 룸타입 | 시간제 상품(3시간/6시간 단위) — 리뷰 입도 자체가 다름, 별도 처리 |
| 더뷔페 시간대·메뉴 가격 상세 | 네이버 더뷔페 리뷰 5,685건의 메뉴 단위 매칭 타깃 (상품권 198,000원만 확인됨) |
| 멤버십 등급별 요율 구조 | 리워즈/WPC/STAR VIP → `rate_plan_class` MEMBER 축 채우기 |
| 워커힐 스토어 상품 | 리테일 SKU — 범위 논의 후 결정 |

---

## 7. 검증 로그

| 항목 | 방법 | 상태 |
|---|---|---|
| 부동산 구조·운영 법인 | 허브 footer, brand 사이트맵 | 확인 2026-11-11 |
| 그랜드 객실 17종·층수·실수 | `/grandwalkerhillseoul/room` 본문 | 확인 2026-11-11 |
| 더글라스 객실 3종 (성인 전용) | 네비 + `/en/Stay` | 확인 2026-11-11 |
| 비스타 객실 14종 (영어) | `/en/Stay` ROOM TYPE | 확인 2026-11-11 |
| 패키지 14건·프로모션 4건·가격·기간 | `/grandwalkerhillseoul/Package` | 확인 2026-11-11 |
| 다이닝 10·시설 30+·연회장 수용인원 | `/about/Map` + 영어 네비 URL 귀속 | 확인 2026-11-11 |
| 멤버십 3등급·상품권·스토어 | 사이트맵·상품권 팝업 | 확인 2026-11-11 |
