# 후기-상품 연결 상품 단위 선호 페르소나 조사 v0.1

- 작성: 장기훈 파트 조사 자료 (팀 내부 리뷰용 초안)
- 일자: 2026-11-11
- 범위: 공개 후기 → 워커힐 상품(객실·패키지·venue) 연결 → 상품 단위 선호를 갖춘 페르소나 구축
- 관련 문서: `proposal-methodology-v0.7.md` (§5.5 케이스 베이스 시드, §8.2 확산 재검토 조건), `experiment-design-v1.md`, `annex-1/2/5`
- 데이터 근거: `sku-catalog-snapshot-v0.1.md` (동일 일자 스냅샷)
- 문서 구성: §0-§2는 한 페이지 요약, §3 이하는 근거·상세. 문헌 번호는 부록 A를 가리킨다.

<!-- anchors: 스크래핑은 전면 배제 | 이 연결과 가격 민감도 설계가 본 프로젝트의 기여 축이다 | 라벨이 못 붙어도 선호는 잡힌다 | 가격 민감도는 ABSA만으로 표현할 수 없다 | 벡터 산출은 코드가 한다 | 리뷰어 이름·아바타·정확한 투숙일·사진은 저장하지 않는다 | 스크래퍼는 어떤 플랫폼에도 제작하지 않는다 | Phase 0는 외부 계약 없이 진행 가능하며 팀 제안서 병합 일정과 무관하게 선개시를 권한다 -->

---

## 0. 한 페이지 요약

**목표 한 줄**: 공개 후기에서 상품 단위 선호를 추출해, 페르소나 파이프라인 II단계(코드 샘플링)에 들어갈 `product_affinity`를 채운다.

**핵심 결론 4가지**

1. **연결 앵커는 이미 확보됐다.** 공식 카탈로그 스냅샷(`sku-catalog-snapshot-v0.1.md`)으로 객실 34종·패키지 14건·venue 30+를 확보했다. 리뷰 연결에 필요한 목적 집합은 전부 공개 카탈로그에서 나오며, 판매 실적 연계용 1차 데이터(POS·멤버십)만 MOU 후보이다.
2. **후기 소스는 라이선스 경로만 취한다.** P0: 워커힐 1차 데이터(MOU) + Expedia Rapid Guest Reviews API. P1: Google Places(콜당 최대 5건 샘플)·TripAdvisor API(객실·다이닝 탭 분리). P2: 국내 OTA는 라이선스 협의 전까지 미사용. 스크래핑은 전면 배제 — 각사 이용약관이 robots·스크래핑·AI 어시스턴트를 명시하고, 대법원 2022 야놀자 v 여기어때 판례(부록 A [C1])가 국내 DB 무단 수집의 위험을 확정했다.
3. **방법론은 성숙 문헌의 조합이지만 목표가 신규다.** 엔티티 연결(규칙→임베딩→cross-encoder→LLM 매처)과 ABSA(SemEval-2016 호텔 택소노미)는 검증된 기법이다. 단 "호텔 리뷰→룸타입/패키지 SKU 연결" 선행연구가 존재하지 않아(부록 A [P1] 결론), 이 연결과 가격 민감도 설계가 본 프로젝트의 기여 축이다.
4. **검증은 단순 분포 매칭으로 불충분하다.** 페어와이즈 선택 일치(conjoint 감사 설계 [P14]), 프롬프트·시드 안정성, 상품 선호 유무 ablation이 필요하다. Baig et al.의 알고리즘 감사가 시뮬레이션 검증 템플릿이 된다(재현 주장 아님 — v0.7 §5.13 원칙).

**핵심 표 — 후기 소스 × 상품 입도 × 접근 경로 (2026-11-11 검증)**

| 소스 | 리뷰량 | 상품 입도 | 접근 경로 · 우선순위 |
|---|---|---|---|
| 워커힐 1차 (GEI·리워즈·CS·POS) | 미공개 | venue·패키지·멤버십 | MOU (marketing@walkerhill.com + 제휴 폼) · P0 |
| Expedia Rapid Guest Reviews API | 1,002 | property + 여행 사유·동행·투숙월 | 공식 API 키 · P0 |
| Google Places API (New) | ~3,849 | property 집계 + ≤5건 샘플 | 공식 API (캐시 금지) · P1 |
| TripAdvisor | 1,129 (객실 탭 412·다이닝 탭 130) | property + 객실/다이닝 탭 | 공식 Content/Terra API · P1 |
| Agoda | ~9,279 | property 집계만 | Partner Content API (텍스트 없음) · P2 |
| 여기어때 | 657 | 패키지·객실 헤더 라벨 | 라이선스 협의 · P2 |
| 야놀자 | 658 | — | 라이선스 협의 · P2 |
| Trip.com | ~378 | 객실 타입별 버킷 | 라이선스 협의 · P2 |
| Naver (더뷔페 등 개별 venue) | 5,685 (더뷔페) | venue·메뉴 단위 | 리뷰 API 부재 — 협의 필요 · P2 |

**다음 액션 3가지**: ① 크로스워크 스키마 + 링크 검증셋(500-1,000쌍) 구축(무예산, §12 Phase 0) ② 워커힐 MOU 문의 + Expedia API 키 발급(§12 Phase 1) ③ 한국어 ABSA 콜드스타트 스키마 확정(§6).

---

## 1. 과제 정의와 팀 인터페이스

### 1.1 파트 범위

- 입력: 공개 후기(라이선스 경로로 수집) + 공식 SKU 마스터(스냅샷 v0.1)
- 처리: (a) 후기 텍스트 → 상품 연결, (b) 연결된 후기 → 속성별 감성(ABSA), (c) 감성·평점·가격 → 상품 단위 선호 벡터
- 출력: 페르소나의 `product_affinity`(상품 선호) — 페르소나 파이프라인 II단계(코드 샘플링)의 입력 확장

### 1.2 팀 핸드오프 인터페이스

| 팀원 | 파트 | 본 조사와의 인터페이스 |
|---|---|---|
| 박희지 | 재현성·일관성 평가 체계 + 기준 수치 | 링커·ABSA는 결정론적으로 실행하고 버전 고정. 크로스워크 매핑 테이블 버저닝(`raw_label`+`product_id`)과 링크 검증셋 ground truth가 재현성 평가의 대상이 된다 |
| 조영근 | 미선택 이유 분석 + 신상품 잠식 효과 | `link_type = none/unresolved` 비율 분포가 미선택 리뷰 집단 분류의 기초. 신규 venue(잠식 시나리오)는 `attribute_family` 슬롯으로 페르소나에 매핑 |
| 김시온 | 페르소나→손님 생성기, 고객 집단 규모 확장 | 손님 생성기 입력 스키마: `persona(attribute_vector, product_affinity JSONB, n_supporting_reviews, cell_k)` — `cell_k ≥ 10` 게이트만 발행(§7) |
| 하청 (커먼컴퓨터) | WISE 운용 | 링크 테이블·선호 벡터는 WISE 배치 구조에 얹히는 확장. 배치 호출 주기·스키마는 annex-2 구조 준수 |

### 1.3 성공 기준

1. 링크 정확도: 검증셋(500-1,000쌍) 기준 precision/recall 보고
2. 커버리지: 후기 중 `attribute_family` 이상 연결 비율(정확 SKU 못 붙여도 속성군 유지)
3. 발행 게이트: `cell_k ≥ 10` 통과 페르소나·상품 조합 수
4. 효용: 상품 선호 유무 ablation에서 시뮬레이션 결정 차이가 관측되는지(§8)

---

## 2. 왜 상품 단위 선호인가 (가치 주장)

1. **기존 설계의 두 한계를 채운다.** annex-1이 명시한 한계 — "상황별 소비 반응도: 부분 + 객실 한정", "외부 요인 연계: 객실 내 이동만" — 은 상품 단위 선호 데이터가 확보되면 객실 밖 상품(다이닝·스파·액티비티)까지 확장할 근거가 된다.
2. **케이스 베이스 시드를 보강한다.** v0.7 §5.5의 케이스 베이스 시드는 실적 N건이다. 리뷰 기반 상품 선호는 시드의 보강 후보이며, 1차 실적 데이터가 MOU로 들어오면 그때 대체 가능하다.
3. **페르소나가 상품을 구분하게 만든다.** Baig et al. [P14]의 알고리즘 감사에 따르면 LLM의 페르소나 조건 호텔 선택은 평점(+31.6%p)과 가격(−30.0%p) 같은 몇 개의 조잡한 신호가 지배하며, 목록 위치 같은 내용 없는 인자만으로도 ~$12/및 차이를 만든다. 상품 수준 선호를 명시 주입하지 않으면 시뮬레이션 손님이 객실 타입·패키지·venue를 구분하지 못한다는 뜻이고, 이것이 본 파트의 존재 이유다.
4. **확산 재검토 조건의 데이터 기반을 제공한다.** v0.7 §8.2는 "입소문·리뷰 확산이 요구사항에 들어오는 경우에만" 확산 모델(MiroFish 계열) 재검토를 조건으로 건다. 본 파트의 후기·선호 데이터가 그 조건이 실제로 들어왔을 때의 재료가 된다.

---

## 3. 후기 소스 인벤토리 (2026-11-11 검증)

### 3.1 플랫폼별 상세

| 소스 (리뷰량) | 상품 입도 | 접근 경로 | 법적 상태 · 우선순위 |
|---|---|---|---|
| 워커힐 1차 — GEI·리워즈·CS '고객의 소리'·멤버십·다이닝 POS·패키지 판매 (미공개) | spa·이벤트·패키지·다이닝·멤버십 — 유일한 진짜 상품 단위 | 협의 MOU — `marketing@walkerhill.com` + walkerhill.com 제휴 폼 (사이트 확인 완료) | 계약 기반 · P0 |
| Expedia Rapid Guest Reviews API (1,002) | property + 여행 사유 + 동행자 + 투숙월 | 공식 Rapid/EAN 키 | 라이선스 · P0 |
| Google Places API (New) (~3,849) | property 집계 + 콜당 최대 5건 샘플 | 공식 API | 라이선스 — 샘플링 전용, 캐시 금지 · P1 |
| TripAdvisor Content/Terra API (1,129: Room & Suite 412 · Dining 130) | Traveler / 객실 / 다이닝 탭 + Sleep Quality | 공식 API — legacy→Terra 전환일은 계약 전 docs.terra.tripadvisor.com에서 재확인 | 라이선스 — 24시간 캐시·표시 규칙 · P1 |
| Agoda Partner Content API (~9,279) | `numberOfReviews` + `ratingAverage` — property 집계만, 리뷰 텍스트 없음 | 공식 API | 라이선스 — 집계 전용 · P2 |
| 여기어때 (657) | 패키지·객실 헤더 라벨 | 호텔 계정 경로 또는 직접 라이선스 협의 | 법률 검토 필요 · P2 |
| 야놀자 (658) | 미확인 | 동상 | 법률 검토 필요 · P2 |
| Trip.com (~378) | 객실 타입별 리뷰 버킷 | 동상 | 법률 검토 필요 · P2 |
| Naver Place — 더뷔페·금룡·피자힐·수영장·리버파크·스카이야드 등 개별 venue (더뷔페 5,685) | venue·메뉴 항목 단위 | 자사 venue면 SmartPlace, 아니면 라이선스 요청 | 리뷰 API 부재 · P2 |
| Naver 블로그·유튜브 (—) | 서사적 상품 경험 | 경계 있는 수동 코퍼스, 건별 라이선스 확인 | "영리적 사용 불가" · P3 |

### 3.2 전제 교정 (조사 과정에서 확정)

1. 더글라스 하우스는 **서울 광진구** 본 부지의 성인 전용 동이다(영암 신설 리조트와 혼동 금지). walkerhill.com 맵·TripAdvisor d15019381로 확인.
2. 크루즈 예약 플랫폼은 워커힐 인벤토리를 취급하지 않는다 — 소싱 대상에서 제외.

### 3.3 워커힐 자산 (MOU 협상 근거)

- GEI(고객경험지수) 공개 수치: 더뷔페 만족도 93.8 / 직원서비스 95.7, 3년 누적 105만 방문
- AI '와인 도슨트' 추천 운영 실적: 3개월 12,139명 — **호텔이 이미 F&B 개인화 AI를 운영 중**이므로 본 프로젝트는 신규 실험이 아니라 기존 역량의 시뮬레이션 확장으로 제안할 수 있다.
- 워커힐 스스로 공식 카탈로그를 완비해 둔 상태(스냅샷 §2-§4) — 상품 마스터 협업의 진입 장벽이 낮다.

---

## 4. 연결 앵커: SKU 마스터

연결 작업의 목적 집합(target set)은 `sku-catalog-snapshot-v0.1.md` v1로 고정한다. 규율:

1. 모든 OTA 상품 라벨은 두 번 저장한다 — `raw_label`(감사용 원문) + `product_id`(분석용). 매핑 테이블 자체를 버전 관리한다.
2. OTA 라벨 변형 실측 예: `스탠다드 트윈룸 (낮은 층, 전망 없음)` vs `스탠다드 트윈룸 전망없음(3층&5층)` — 동일 official 스탠다드의 다른 표기.
3. 전망(RIVER/MOUNTAIN)은 OTA가 만든 축이므로 official 스키마와 분리·별도 모델링.
4. 링크 검증셋(ground truth 500-1,000쌍)은 스냅샷에서 생성한다. WDC Products [T8]에 호스피탈리티 슬라이스가 없어 기존 벤치마크 대체가 불가능하며, 미등장 엔티티 일반화는 매처의 알려진 약점이라(엔티티 매칭 문헌 공통) 자체 검증셋이 필수다.

---

## 5. 연결 방법론: 후기 텍스트 → product_id

### 5.1 파이프라인 (S2a-S2f)

| 단계 | 기법 | 근거 | 산출 |
|---|---|---|---|
| S2a | 규칙·어휘 정규화 (한국어 형태소 분석, 라벨 클린업) | 전통 ER 전처리 관행 | 정규화된 라벨·텍스트 |
| S2b | 임베딩 검색으로 후보 생성 | BLINK [T15], GENRE [T14] 계열 | top-k 후보 SKU |
| S2c | cross-encoder 재순위 | Ditto [T9] | 후보 정렬 + 점수 |
| S2d | LLM 매처 — **SELECT 전략** (모델에 후보 중 선택만 시킴) | Wang et al., "Match, Compare, or Select?" [T6] — SELECT가 최고 성능 | 최종 매칭 + 근거 |
| S2e | 온톨로지 기반 RAG 폴백 | FoodOntoRAG [T12] — 온톨로지 드리프트 내성 | 스키마 변화 내성 |
| S2f | 감사·평가셋 | WDC Products [T8] 벤치마크 방식, 자체 500-1,000쌍 | precision/recall 보고 |

설계 결정: S2d에서 LLM에게 자유 생성(compare) 대신 **후보 중 선택(select)**만 시킨다. 이는 결정론·감사 가능성·재현성(박희지 파트 요구)에 유리하다.

### 5.2 연결 결과의 4값 분류

| link_type | 의미 | 후속 처리 |
|---|---|---|
| `exact_product` | 구체 SKU 확정 (예: 클럽 스위트, Begin Vegan 패키지) | 상품 단위 선호 집계 |
| `attribute_family` | 속성군만 확정 (예: "수영장 좋았어요" → IndoorPool, "스위트" → 스위트군) | 속성군 단위 선호 집계 — **라벨이 못 붙어도 선호는 잡힌다** |
| `unresolved` | 상품 관련이나 매칭 실패 | 조영근 파트의 미선택·불만족 분석 코퍼스로 이관 |
| `none` | 상품 무관 후기 | 제외 |

핵심 설계 결정: `attribute_family`를 버리지 않고 유지한다. 국내 OTA 라벨 변형(§4)과 후기 서술의 모호성을 감안하면 exact_product만 추구하면 커버리지가 무너진다.

### 5.3 산출 스키마

연결 결과는 `product_id + link_type + confidence + evidence_span`(원문 근거 구간)으로 기록한다. evidence_span은 감사·분쟁 대응·ABSA 입력의 공통 자산이다.

---

## 6. 선호 추출: ABSA → 상품 단위 선호 벡터

### 6.1 감성 택소노미 (SemEval-2016 Task 5 호텔 도메인 [T27])

| 축 | 라벨 |
|---|---|
| entity (무엇에 대해) | HOTEL · ROOMS · ROOM-AMENITIES · FACILITIES · SERVICE · LOCATION · FOOD&DRINKS |
| attribute (무엇을 평가) | general · price · comfort · cleanliness · quality · style_options · design_features · miscellaneous |

LLM 시대 실행은 3단계 계층으로 간다: Tier 1 프롬프트 기반 지시 튜닝(InstructABSA [T35]), Tier 2 핵심 문단 요약(PAKPA [T36]), Tier 4중 속성-감성-타깃 사중 추출(quads [T39]·OATS [T42]). 2024-2025 평가 문헌([T37]·[T28]·[T29])은 LLM 기반 ABSA가 호텔 도메인에서 fine-tuning 대비 경쟁적 이상임을 반복 보고한다.

### 6.2 한국어 콜드스타트

- 스키마: SemEval 택소노미의 번역 이식이 viable한 콜드스타트라는 근거가 있다 — KPC-cF [T23]은 번역 기반 pseudo-label + 이중 필터링으로 한국어 ABSA가 영어 대비 ~3%p F1 격차에 도달함을 보고했다.
- 한국어 자원: CARBD-Ko [T45], KR3 [T48], Korean-ABSA-Dataset [T47], AI-Hub 생성형AI 관광 특화 말뭉치 [T87], 문화빅데이터마켓 '숙박시설 리뷰 감성분석' 데이터 [T86].
- 평가 문제점: 정답 라벨과 평점의 불일치(SentimentLens [T40]의 dual-modality 문제) — 평점만으로 감성을 대신하지 않는다.

### 6.3 선호 벡터 레시피 (코드 산출 — 페르소나 II단계 "반드시 코드가 수행한다" 원칙 준수)

```text
페르소나 Π, 후기 r ∈ Reviews(Π) (기존 아키타입·여행 속성 배정에서 파생된 후기 집합)
w(r) = 최신성 감쇠(IRA [P13]) × 플랫폼 보정(§6.4)

pref[Π][sku]    = Σ_r w(r) · [polarity × intensity, aspect, price_band]   # exact_product
pref[Π][family] = normalize(속성군 내 집계)                               # attribute_family
price_sensitivity[Π][family] = cov(rating | price_band)                   # price_band 부착 필요
```

- `price_band`는 SKU 마스터(스냅샷 §3 가격)에서 부착한다. **가격 민감도는 ABSA만으로 표현할 수 없다** — 감성은 속성별 극성만 준다. 가격대를 SKU에 붙이고 조건부 선호를 계산하는 것이 워커힐 특화 설계이며, 선행연구에서 직접 찾을 수 없어 스스로 설계해야 하는 부분이다(부록 A 결론 3).
- 발화자 필터 [P12]: 리뷰어가 **직접 경험한 의견**만 채택한다. 전달·추천 의견("친구 말로는…")은 페르소나 선호로 쓰면 안 된다.

### 6.4 편향 보정 4종

| 편향 | 보정 | 근거 |
|---|---|---|
| 표본 선택 (후기 작성자 ≠ 이용자 전체) | 성향 점수 재가중 | Han & Mikhailova [P11] |
| 플랫폼 간 측정·선택 편향 | 플랫폼 보정 계수 | Han & Anderson [P10] |
| 시간 drift + 안정 코어 | 최신성 감쇠 + stable-core 항 | IRA [P13], VRS-DWMoE [P16] |
| 극단 평점·상호성 | 극단 편향 완화 참고 | Karaman [P9], Smironva [P8], Fradkin [P15] |

---

## 7. 페르소나 부여: 기존 파이프라인과의 결합

### 7.1 결합 설계 (7단계)

```text
1. Reviews(Π)     ← 기존 아키타입·여행 속성 배정에서 파생
2. ABSA(Π)        ← §6.1 출력 (리뷰어 보유 의견만)
3. Link(Π)        ← §5 출력 (product_id + confidence + attribute_family 폴백)
4. 상품 선호      ← §6.3 레시피 (코드 산출)
5. LLM 합성 (제한적) ← Exp3rt 스타일 teacher-distilled [P2]:
       prompt = (아키타입 텍스트, 여행 속성, 상위 N개 상품 선호 + 근거 스팬)
       output = 페르소나 서사(narrative) + 기계 판독형 product_preferences[]
6. 가드레일       ← §6.4 보정 4종
7. 검증           ← §8
```

원칙 정합성:

- **벡터 산출은 코드가 한다.** 선호 벡터·가격 민감도는 결정론적 집계(§6.3)이고, LLM은 서사와 근거 요약만 담당한다 — 기존 파이프라인의 "II단계 반드시 코드" 원칙을 그대로 유지한다.
- **개인 식별자 없음(annex-2 I1).** `review_uid = HMAC-SHA256(회전 salt, platform:review_id)` — 리뷰어 이름·아바타·정확한 투숙일·사진은 저장하지 않는다.

### 7.2 페르소나·후기 스키마

```sql
review(review_uid, product_id, platform, platform_review_id_hash,
       rating, aspect_scores JSONB, review_text_redacted,
       stay_month, trip_reason, traveller_type, party_size, ingested_at)
-- NO reviewer name, NO avatar, NO exact stay date, NO photos

persona(persona_id, attribute_vector, product_affinity JSONB,
        n_supporting_reviews, cell_k, derived_at)
-- product_affinity: {sku: {score, family, evidence[]}} 형태
-- 발행은 cell_k >= 10인 조합만
```

### 7.3 시뮬레이션 호출 경계

annex-2 원칙 유지: 고객 시뮬레이션 호출에는 합성 페르소나만 통과한다. 후기 원문·리뷰어 힌트는 시뮬레이션 프롬프트에 들어가지 않고, 코드가 만든 선호 벡터만 들어간다.

---

## 8. 검증 설계

1. **분포 매칭은 불충분.** Nakajima [P13]는 주변 분포 일치가 저렴하고 불충분한 검증 기준임을 보였다 — 문구·위치 효과가 결과를 뒤집을 수 있다.
2. **페어와이즈 선택 일치(conjoint).** Baig et al. [P14]의 사전 지정 알고리즘 감사 설계 — 페르소나·프롬프트 템플릿·12개 모델에 걸친 무작위 선택 기반 conjoint로 AMCE 추정. 우리 시뮬레이션의 검증 템플릿으로 채택한다(재현 주장 아님).
3. **안정성.** 프롬프트 템플릿·시드 교차로 선호 벡터의 안정성 측정 — 박희지 파트의 일관성 평가와 동일 축.
4. **Ablation.** 상품 선호 없는 페르소나(CUP [P4]·GPTM [P17] 베이스라인) 대비 결정 차이 측정 — "상품 단위 선호가 시뮬레이션을 바꾸는가"의 직접 답.
5. **링커 평가.** 검증셋 precision/recall + 미등장 SKU 일반화(알려진 약점, 별도 리포트).

---

## 9. 컴플라이언스

### 9.1 플랫폼 이용약관 (2026-11 기준 검증)

| 플랫폼 | 조항·제약 | 시사점 |
|---|---|---|
| Booking.com | A15.2: 스크래핑·로봇·AI 어시스턴트 명시 금지 | 스크래퍼 제작 금지. Property Scores API 존재하나 객실 단위 노출 미확인 |
| Agoda | v6.3 (2026-07-10 개정) 동일 금지 | Partner Content API로 집계만 |
| Google | Places 리뷰 필드 최대 5건·캐싱 금지 (공식 문서 확인) | 샘플링 소스 전용 |
| Naver | Open API 이용약관 §2.3: AI 학습·활용 금지 (2026-10-07 개정) | 리뷰 API 자체가 부재 — venue별 협의 경로만 |
| Naver 블로그·유튜브 | "영리적 사용 불가" | P3 수동 코퍼스만, 건별 확인 |
| TripAdvisor | 24시간 캐시·표시 규칙 | Terra 전환일 재확인 후 계약 |
| Expedia | Rapid Guest Reviews API 공식 제공 | 리뷰 텍스트를 라이선스로 얻는 유일한 검증 경로 |

### 9.2 국내 판례

대법원 2022 야놀자 v 여기어때 [C1]: DB 제작자 권리를 3단계(원자료 공짜 여부 → 상당 투자 → 일부·전부 이용)로 판단. 리뷰 DB의 무단 대량 수집은 국내에서도 손해배상 사안이 된다 — **국내 OTA 스크래핑 회피의 결정적 근거**.

### 9.3 개인정보 (PIPA)

- 리뷰어 식별자(작성자명·프로필)는 개인정보다. 수집 시 비식별 처리가 기본이며, §20조 출처 고지 의무를 계약 경로에서 처리한다.
- 데이터 3법 체계의 가명·익명정보 경로가 법적 근거이며, 워커힐 1차 데이터(MOU)는 계약으로 출처 고지를 해결한다.
- 본 파트 스키마(§7.2)는 설계 단계부터 식별자 미수집 — I1 원칙의 이행.

### 9.4 결론

수집 경로는 **라이선스 API + 1차 MOU + 자사 공개 카탈로그**만. 스크래퍼는 어떤 플랫폼에도 제작하지 않는다.

---

## 10. 선행연구와 차별화

### 10.1 국내 학술 (호스피탈리티 리뷰 분석)

| 연구 | 소스·방법 | 본 파트와의 관계 |
|---|---|---|
| 최지유 외 2018, 관광경영학회 22 | 국내 호텔 리뷰 마이닝 | 방법론적으로 가장 가까운 형제 연구 |
| 곽민정 외 2019, 관광경영연구 | 속성별 감성 분석 | 속성-선호 행렬 — 페르소나 선호와 가장 근접 |
| 임영희 2019, 세종대 박사 | 11,240건 TripAdvisor, 15개 국내 호텔, 감성사전 | 외래관광객 × 국내호텔 × 감성의 직접 선례 |
| 박영욱·정규엽 2021 | DMR 토픽모델링, 5성급 외국인 리뷰 | 토픽↔평점 연계 |
| 임영희 2023, 호텔경영학연구 | TF-IDF + CONCOR 네트워크, 한옥호텔 | 속성-선호 구조 |
| 이영주·김홍범 2018, 관광학연구 | Word2Vec + 리뷰ID 조인 | 동일 조인키 아키텍처 선례 |
| 최지유 외 2017, 관광학연구 | 7,220건 UCINET 선택속성 (객실·청결·직원·위치·조식 상위) | 속성 중심성 |
| 강주영 외 2025, JIIS | Google Maps 리뷰 BERTopic + SHAP-DNN + IPA, 백화점 | 가장 최신 국내 선례 — 워커힐 다이닝 페르소나로 이식 가능 |

### 10.2 산업 선례

- 여기어때 → 망고플레이트 인수(20만 맛집·70만 리뷰) + AI 리뷰 대응 — 플랫폼 측 AI 리뷰 분석 선례
- 트립토파즈: Expedia + Trip.com API 통합으로 320만 호텔 상품 유통 — **라이선스 기반 멀티 OTA 통합의 국내 작동 사례**, 잠재 협업 파트너
- 워커힐 자체: GEI 공개 + 와인 도슨트(§3.3)

### 10.3 차별화 포인트

1. **"호텔 리뷰 → 룸타입/패키지 SKU 연결" 선행연구 부재** — 가장 가까운 것은 일반 상품 연결([T1]·[T5]·[T12])과 호텔 ABSA(상품 연결 없음)의 조합. 이 조합이 본 프로젝트의 기여 축.
2. **가격 민감도의 신규 설계** — ABSA는 극성만 주고 가격 민감도를 주지 않는다(§6.3). price_band 부착은 스스로 설계하는 부분이며 조영근 파트의 가격-잠식 분석과 연결된다.
3. **페르소나·상품 단위 축** — 국내 선행연구는 속성 중심 분석이지 페르소나 부여가 아니다. persona/product-unit이 차별화 축이다.

---

## 11. 위험·한계

| 위험 | 내용 | 대응 |
|---|---|---|
| 가격 데이터 결핍 | price_sensitivity 계산에는 price_band가 SKU에 붙어야 한다. 공개 카탈로그는 최저가만 고지 | 스냅샷 §3 가격 + 상품권 가격(공식 근거)으로 대역 구축; 1차 데이터 확보 시 정밀화 |
| 한국어 ABSA 성능 천정 | 영어 대비 ~3%p F1 격차가 현실적 상한 [T23] | 격차를 감안한 커버리지 목표 설정 + 근거 스팬 사람 검수 |
| OTA 라벨 변형 | 라벨이 상시 변한다(§4 실측) | 크로스워크 버저닝 + S2e 온톨로지 폴백 |
| 검증셋 구축 비용 | 기존 벤치마크 대체 불가, 500-1,000쌍 자체 구축 | Phase 0 무예산 작업으로 우선 배치 |
| 문헌 인용 함정 | "Horton (1999) *Listeners' Character*"은 검증 불가 — 인용 금지. Horton & Wohl (1956) [P1] 사용 | 인용 전 개별 검증 규칙 |
| 일부 문헌 모델 라인업 이상 | TAIL 계열 보고의 모델 비교는 주의 해석 | 선택 모델로 자체 재실험 |
| 리뷰량 소스 편향 | Agoda 9,279 vs Booking 271처럼 소스 간 격차가 크다 | §6.4 플랫폼 보정 + 소스별 가중치 공개 |

---

## 12. 실행 계획

| Phase | 내용 | 산출물 | 의존성 · 예산 |
|---|---|---|---|
| 0 (즉시) | 크로스워크 스키마 설계 + 링크 검증셋(500-1,000쌍) 구축 + 한국어 ABSA 스키마 확정 | 검증셋 v1, 스키마 문서 | 없음 (스냅샷 v0.1 완료) · 무 |
| 1 (계약) | 워커힐 1차 MOU 문의 + Expedia Rapid API 키 + TripAdvisor Terra 확인 | 데이터 계약 | 팀장·의뢰 업체 경로 · API 이용료 |
| 2 (구축) | 링커 S2a-S2d 구현 + ABSA 파이프라인 + 선호 벡터 코드 모듈 | 링크 테이블·선호 벡터 v1 | Phase 0-1 · 개발 공수 |
| 3 (검증) | conjoint 감사 + ablation + 안정성 측정 | 검증 리포트 | Phase 2 · 개발 공수 |

Phase 0는 외부 계약 없이 진행 가능하며 팀 제안서 병합 일정과 무관하게 선개시를 권한다.

---

## 부록 A. 참고 문헌 (선별)

**연결·엔티티 매칭**
- [T1] XU et al., "Towards the Effective Linking of Social Media Contents to Products in E-Commerce Catalogs", CIKM 2016
- [T6] Wang et al., "Match, Compare, or Select? An Investigation of LLM-Based Entity Matching", COLING 2025 — SELECT 전략 근거
- [T8] Peeters & Bizer, "WDC Products: A Multi-Dimensional Entity Matching Benchmark", EDBT 2024
- [T9] Li et al., "Ditto: Deep Entity Matching with Pre-Trained Language Models", VLDB 2021
- [T12] Drole et al., "Beyond Fine-Tuning: Robust Food Entity Linking under Ontology Drift with FoodOntoRAG", arXiv 2603.09758
- [T14] De Cao et al., "Autoregressive Entity Retrieval (GENRE)", ICLR 2021
- [T15] Laskar et al., "BLINK with Elasticsearch…", NAACL 2022

**ABSA**
- [T23] Nam, "Korean ABSA via Implicit-Feature Alignment with Corpus Filtering (KPC-cF)", arXiv 2407.00342
- [T27] Pontiki et al., "SemEval-2016 Task 5: Aspect Based Sentiment Analysis"
- [T28] Jeong & Lee, "An Aspect-Based Review Analysis Using ChatGPT…Hotel Service Failures", Sustainability 16(4), 2024
- [T35] Scaria et al., "InstructABSA", NAACL 2024
- [T36] Tang et al., "Prompted Aspect Key Point Analysis (PAKPA)", ACL 2024
- [T37] Zhou, "A Comprehensive Evaluation of LLMs on ABSA", arXiv 2412.02279
- [T40] Jayakody et al., "SentimentLens: Reconciling Sentiment and Ratings…", arXiv 2606.00084
- [T42] Chebolu et al., "OATS: Opinion Aspect Target Sentiment Quadruple Extraction", COLING/LREC 2024
- [T45] Jang et al., "CARBD-Ko", arXiv 2402.15046
- [T86] 문화빅데이터마켓, 히어로웍스 숙박시설 리뷰 감성분석 데이터
- [T87] AI-Hub, 생성형AI 관광 특화 말뭉치

**페르소나·편향·검증**
- [P1] Horton & Wohl, "Mass Communication and Para-Social Interaction", Participations 3(1), 1956 — 페르소나 개념의 검증된 원전
- [P2] Kim et al., "Review-driven Personalized Preference Reasoning with LLMs (Exp3rt)", SIGIR 2025
- [P3] Bang & Song, "PURE: LLM-based User Profile Management…", arXiv 2502.14541
- [P4] "Recommendations by Concise User Profiles from Review Text (CUP)", arXiv 2311.01314
- [P8] Smironva et al., "Self-selection and non-response biases in customers' hotel ratings", Current Issues in Tourism 2019
- [P9] Karaman, "Online Review Solicitations Reduce Extremity Bias…", Management Science 2020
- [P10] Han & Anderson, "The Platform Matters: Selection and Measurement Bias in Online Reviews", 2025
- [P11] Han & Mikhailova, "Reducing the Bias in Online Reviews Using Propensity Score Adjustment", 2024
- [P12] Deng & Wiebe, "Recognizing Opinion Sources…", IJCAI 2016 — 발화자 필터
- [P13] Lee et al., "IRA: Adaptive Interest-aware Representation…", SIGIR 2025 Industry · Nakajima, "Passing Coarse Marginal Checks Can Be Cheap", arXiv 2608.00979
- [P14] Baig, Gillani & Ali, "Whose hotel does the AI recommend? An algorithm audit…", arXiv 2606.16344
- [P15] Fradkin et al., "Bias and Reciprocity in Online Reviews: Evidence From Airbnb", NBER 2015
- [P16] Zhao et al., "Double-Wing Mixture of Experts for Streaming Recommendations (VRS-DWMoE)", WISE 2020
- [P17] Wang et al., "Mining User Preferences…Genre-aware Personalized Neural Topic Model (GPTM)", 2025

**국내 판례·법령**
- [C1] 대법원 2022, 야놀자 v 여기어때 DB 제작자 권리 사건 — law.go.kr 판례 (precSeq 226943, 234437) 확인
- [C2] 개인정보보호법 §20조 출처 고지, 데이터 3법 가명·익명정보 체계 — PIPC 가이드라인 확인

---

## 부록 B. 검증 로그 요약

| 주장 | 검증 방법 | 상태 |
|---|---|---|
| 플랫폼별 리뷰량·입도 | 8개 플랫폼 라이브 페이지 | 확인 2026-11-11 |
| Booking/Agoda/TripAdvisor/Naver 스크래핑·AI 조항 | 각사 공식 약관 원문 | 확인 (원문 인용 보관) |
| Google Places 최대 5건·캐시 금지 | Google 공식 문서 | 확인 (원문 인용 보관) |
| Expedia Rapid Guest Reviews API 스키마 | developers.expediagroup.com | 확인 |
| 대법원 2022 판례 3단계 구조 | law.go.kr + 법률신문 | 확인 |
| PIPA·데이터 3법 경로 | PIPC 가이드라인 + 법령정보센터 | 확인 |
| SKU 마스터 전 항목 | walkerhill.com 공식 카탈로그 | `sku-catalog-snapshot-v0.1.md` §7 참조 |
| 더글라스 하우스 소재·성인 전용 | walkerhill.com 맵 + TripAdvisor | 확인 |
| 국내 선행연구 12편 | RISS·KoreaScience·KCI | 확인 |
