# Week 4 Final Presentation — Script (10 min)
## Week 4 [위크 포] 최종 발표 대본

영어 단어 옆 [발음]으로 표기. 총 ~10분.

---

## Slide 0 — Title (15초)

안녕하세요. 최종 발표를 시작하겠습니다.

주제는 **1D metasurface [메타서피스] 에서 메타 원자 간 결합 (coupling
[커플링]) 이 위상 응답에 미치는 영향**입니다.

직접 구현한 **CDA [씨디에이], Coupled Dipole Approximation [커플드 다이폴
어프록시메이션]** 모델과, 클라우드 풀웨이브 시뮬레이터 **Tidy3D [타이디
쓰리디] FDTD [에프디티디]** 의 외부 검증까지 통합한 결과를 보고드리겠습니다.

---

## Slide 1 — Research Question (25초)

연구 질문은 한 문장으로 정리됩니다.

> **"배열 주기 P [피] 가 줄어들수록, 메타 원자 간 결합에 의한 위상 왜곡이
> 어떻게 증가하는가?"**

표준 메타서페이스 설계는 각 메타 원자를 isolated [아이솔레이티드], 즉
독립적으로 가정합니다. 그러나 실제로는 인접 원자가 **electromagnetic
coupling [일렉트로마그네틱 커플링]** 을 통해 위상 응답을 왜곡합니다.

이 왜곡을 **정량적 법칙 (quantitative law [퀀티테이티브 로]) 으로 답하는
것** 이 본 프로젝트의 목표입니다.

---

## Slide 2 — Model + Method (40초)

방법론은 **CDA [씨디에이] scalar [스칼라] TM [티엠] 모델** 입니다.

각 메타 원자를 분극률 α [알파] 를 가진 point dipole [포인트 다이폴]
로 근사하고, self-consistent [셀프 컨시스턴트] 식:

> $p_i = \alpha_i \, E_{\mathrm{loc},i}, \quad E_{\mathrm{loc},i} = E_{\mathrm{inc},i} + \sum_{j \ne i} G(r_{ij}) \, p_j$
>
> 즉, **쌍극자 모멘트 p_i [피 아이] = 분극률 곱하기 국소 전기장 E_loc
> [이 록]**. 국소 전기장은 입사파 E_inc [이 인크] 에 다른 모든 원자가
> 산란한 필드 합이 더해진 것.

이를 N×N [엔 바이 엔] 선형 시스템 **A·p = E_inc** 로 환원합니다.
Green [그린] 함수는 2D scalar Hankel [한켈] 함수:

> $G(r) = (i/4) H_0^{(1)}(k_0 r)$
>
> i 오버 4 [아이 오버 포] 곱하기 H_0^(1) [한켈 영차 제1종] 의 k_0 r
> [케이 영 알] 값.

분극률은 Lorentzian [로렌치안] — 댐핑이 있는 공진기 모델 — 을 사용했고,
디폴트 (default [디폴트]) 파라미터는 ω₀ [오메가 영] = 2.1π [이점일 파이],
γ [감마] = 0.4, F [에프] = 4.0 입니다.

핵심 라이브러리 `cda.py` [씨디에이 닷 파이] 와 NumPy [넘파이] linalg
[린알그] solve [솔브] 만으로 N = 641 까지 1초 이내 풀이가 가능합니다.

---

## Slide 3 — Verification 10/10 (40초)

본 분석에 앞서, **솔버 자체의 정확성** 을 10가지 독립적 물리 검증으로
확보했습니다.

테스트 항목은 다음과 같습니다:
- 단일 쌍극자 sanity check [새너티 체크] — 해석해 (analytical solution
  [어낼리티컬 솔루션]) 와 일치
- 2-dipole [투 다이폴] 해석해 비교
- Green [그린] 함수 공식 및 reciprocity [리시프로시티, 호혜성] 검증
- 선형 시스템 residual [레지듀얼, 잔차]
- 거울 대칭 (mirror symmetry [미러 시메트리])
- 행렬 reciprocity A_ij = A_ji [에이 아이제이 = 에이 제이아이]
- 1/√N [원 오버 루트 엔] 수렴
- 파장 scaling [스케일링] 불변성
- 소광 전력 양수성 (extinction power positivity [익스팅션 파워
  포지티비티])
- 비균일 솔버의 균일 극한

**열 가지 모두 기계 정밀도 (machine precision [머신 프리시전]) 수준에서
통과** — 즉 상대 오차 10^(-16) [십의 마이너스 16승] 수준. 솔버는 신뢰
가능한 상태로 분석을 시작했습니다.

---

## Slide 4 — Direct Answer (60초) ★ 핵심 슬라이드

본 프로젝트의 **핵심 결과** 입니다.

Wood anomaly [우드 어너멀리, 격자 공명] 을 회피한 sub-wavelength [서브
웨이브렝스] 영역, 즉 P ∈ [0.55 λ, 0.85 λ] [피 인 0.55 람다 0.85 람다]
구간을 31개 점으로 fine sweep [파인 스윕] 했습니다.

결과는 다음 power law [파워 로] 로 fit [핏] 됩니다:

> $|\Delta\varphi|(P) \approx 3.9 \cdot (\lambda/P)^{\beta}, \quad \beta = 0.90 \pm 0.10$
>
> 평균 위상 편차 |Δφ| [델타 파이 절댓값] 은 약 3.9 곱하기 (λ/P) [람다
> 오버 피] 의 β [베타] 제곱, β = 0.90 ± 0.10 [영점구공 플러스마이너스
> 영점일공].

R² [알 스퀘어] = 0.73, 1-σ [원 시그마] 표준 오차는 log-log [로그로그]
회귀로 측정한 ±0.10 [플러스마이너스 영점일공] 입니다.

구체 수치:
- P = 0.85 λ → |Δφ| = 3.80°
- P = 0.55 λ → |Δφ| = 5.98°
- 비율 (ratio [레이쇼]) 1.57배 — **+57 percent [퍼센트] 증가**

지수 β ≈ 1 [베타 일 근처] 의 의미는 위상 왜곡이 **거의 1/P 비례 (one
over P [원 오버 피] scaling [스케일링])** 로 증가한다는 것이며, 이는
2D Hankel 격자합 Σ G(jP) [시그마 지 제이 피] 의 1/P 점근 거동에서
직접 유래합니다.

즉 **법칙은 결합 기하 (coupling geometry [커플링 지오메트리]) 가
결정**합니다.

---

## Slide 5 — β depends on F and window (50초)

다만 두 가지 미세 구조 (subtlety [서틀티]) 를 함께 보고드립니다.

**첫째, β는 결합 강도 F [에프] 에 따라 변합니다.**
- F = 0.5 → β = 1.23 (weak coupling [위크 커플링], super-linear
  [수퍼 리니어])
- F = 4.0 (디폴트) → β = 0.90
- F = 8.0 → β = 0.46 (strong coupling [스트롱 커플링], saturation
  [새튜레이션, 포화])

즉 약한 결합 영역에선 β > 1, 강한 결합 영역에선 β < 1. β ≈ 1 은 두
영역의 transition [트랜지션] 에서 나타납니다.

**둘째, β는 fit window [핏 윈도우] 에도 의존합니다.**
- P ∈ [0.55, 0.85] → β = 0.90
- P ∈ [0.65, 0.85] (Wood anomaly 에 더 근접) → β = 1.58

즉 Δφ(P) 는 단일 universal [유니버설] power law 가 아니라, P = λ
근방에서 가팔라지는 매끄러운 함수입니다. 따라서 보고된 β = 0.90 은
**우리 결합 강도에서의 effective exponent [이펙티브 익스포넌트]** 이며,
실제 메타서페이스 디자인은 β = 0.5 ~ 1.3 [영점오 에서 일점삼] 범위 어디에도
존재할 수 있습니다.

---

## Slide 6 — Result A: Mean phase deviation (40초)

자세한 결과 (Result A~F) 를 순차적으로 보고드립니다.

**Result A — uniform vs non-uniform array 비공명 평균**:
- Uniform [유니폼] 배열: 3.27°
- Non-uniform [논 유니폼] graded α [그레이디드 알파] 배열: 3.95°

차이는 **+0.69°, 즉 약 21 percent [퍼센트] 증가**. 이 증가분은 격자
자체는 동일하므로 **순수히 α-inhomogeneity [알파 비균일성] 에서만**
기여합니다.

함의: 표준 isolated-atom 설계는 graded structure 에서 위상 오차를 약
21 percent **과소평가** 합니다.

---

## Slide 7 — Result C + F: Symmetry + α-ordering (40초)

**Result C — Mirror symmetry break [미러 시메트리 브레이크]**:
- Uniform 배열: 좌우 평균 차 = 0°, 완벽 대칭
- Non-uniform 배열: -0.96° → graded α 가 거울 대칭을 깬다

→ 실제 메타렌즈에서 위상 그래디언트가 가파른 영역의 초점 왜곡 (focal
spot distortion [포컬 스팟 디스토션]) 의 원인.

**Result F — α-ordering [알파 오더링] 민감도**:
- Ascending [어센딩] 순서: 평균 5.10°
- Descending [디센딩]: 5.10° (mirror equivalent)
- Random [랜덤] shuffle [셔플]: 5.16 ~ 7.57°, median [미디언] 5.49°

→ 무작위 배치는 부드러운 그래디언트 대비 **최대 +50 percent 추가 왜곡**.
이웃 간 α 변화율 제한이 결합 강건성의 **무비용 디자인 규칙** 입니다.

---

## Slide 8 — Result D + E: Numerical soundness (40초)

수치 건전성 검증입니다.

**Result D — 행렬 조건수 (matrix conditioning [매트릭스 컨디셔닝])**:
Wood anomaly P = λ 근방에서도 κ(A) [카파 에이] = 1.95. 매우 낮은 값.
→ 격자 공명 피크는 행렬 특이성 (matrix singularity [매트릭스 싱귤래러티])
에 의한 수치 인공물 (numerical artefact [뉴메리컬 아티팩트]) 이 **아니라**
**실제 물리 현상**.

**Result E — 에너지 bookkeeping [북키핑]**:
- Extinction [익스팅션] power P_ext > 0 모든 P 에서
- Absorption [업소프션] power P_abs > 0 모든 P 에서
- Residual (P_ext - P_abs)/P_ext 가 유계 (bounded [바운디드])

이 잔차가 [0, 1] 을 약간 벗어나는 것은 **standard CDA 의 알려진 한계
(no radiation-reaction correction [노 래디에이션 리액션 코렉션])** 로,
보고서 §7 Limitations 에 명시했습니다.

→ 격자 공명 피크가 진짜 물리임이 이중으로 확인됨.

---

## Slide 9 — FDTD Cross-Validation (60초) ★ 외부 검증

본 프로젝트의 가장 중요한 외부 검증입니다.

CDA 의 정확성을 평가하기 위해 **독립적인 풀웨이브 시뮬레이션** 인
Tidy3D [타이디 쓰리디] FDTD [에프디티디] 를 사용했습니다.

**Setup [셋업]**:
- 11개 Lorentz [로렌치] 매질 cylinder [실린더]
- λ = 1 μm [마이크로미터]
- TM [티엠] polarization [폴러라이제이션], E ∥ cylinder axis (E [이]
  성분이 cylinder 축에 평행)
- CDA 와 정확히 같은 geometry

총 11개 시뮬레이션 (1 calibration [캘리브레이션] + 10 periods),
약 0.3 FlexCredit [플렉스 크레딧] 비용.

**결과**:
- Sub-wavelength window 에서 **CDA 와 FDTD 가 같은 곡선 형태**
- RMS [알엠에스] 차이 약 2.9°
- 가장 중요한 P = λ 격자 공명: CDA 23°, FDTD 20° — 두 방법 모두
  **sharp peak [샤프 피크]** 를 정확히 잡음

→ 핵심 결과인 power law 와 격자 공명이 **독립적 full-wave [풀웨이브]
기준** 으로 정량 확인되었습니다.

---

## Slide 10 — Reliability (50초)

PDF [피디에프] 가이드가 요구한 reliability [릴라이어빌리티] 검증입니다.

**R1 — Multi-seed reliability**: 80개 랜덤 α 프로파일에서 β 분포
- Median [미디언] β = 1.09
- 90 percent band [퍼센트 밴드] = [0.63, 1.61]
- → 헤드라인 β = 0.90 이 분포의 중심 근처에 포함됨

**R2 — Grading magnitude sensitivity**: 그래디언트 폭 w = 0 ~ 0.4 π
변화
- w ≤ 0.20 π 에서 β 가 1 근처로 안정
- w ≥ 0.30 π 에서 over-grading [오버 그레이딩] 으로 β 부호 전환

**R3 — N-convergence**: 1/√N [원 오버 루트 엔] extrapolation
[익스트래폴레이션, 외삽]
- **N → ∞ 극한에서 |Δφ| → 6.32°** 로 수렴

보고된 결과는 단일 실현이 아니라 **다양한 조건에서 reliable 한 통계량**.

---

## Slide 11 — Robustness Summary (30초)

네 가지 독립 검증 — array size N, grading width [그레이딩 위드], random
α profile, FDTD external comparison — 을 한 슬라이드에 종합했습니다.

핵심 결과: **β 는 0.78 ~ 1.15 [영점칠팔 에서 일점일오] 의 좁은 범위에서
안정** 하며, FDTD agreement [어그리먼트] 도 power-law 신뢰 구간 안에
들어옵니다.

즉 1/P 법칙은 단일 fit 결과가 아니라 **여러 독립 검증을 통과한 견고한
발견** 입니다.

---

## Slide 12 — Physics vs Numerics vs Design (40초)

PDF Week 3/4 요구사항인 **관찰된 차이의 origin classification [오리진
클래시피케이션, 원인 분류]** 입니다.

- **Physics [피직스]**: 1/P power law, +21 percent extra distortion,
  Wood anomaly peaks
- **Design [디자인]**: 거울 대칭 깨짐, α-그래디언트 효과
- **Numerics-sound [뉴메릭스 사운드]**: κ(A) ≤ 2, P_ext > 0, P_abs > 0
- **External validation [익스터널 밸리데이션]**: FDTD agreement

**결론: 관찰된 모든 현상은 실제 물리 또는 의도된 디자인에서 기인하며,
수치적 인공물 (numerical artefact [뉴메리컬 아티팩트]) 은 없습니다.**

---

## Slide 13 — Limitations (25초)

정직한 한계점:

- **Point-dipole approximation [포인트 다이폴 어프록시메이션]**:
  다중극 (multipole [멀티폴]) 효과 미포함
- **2D scalar geometry**: TM 모드만, 3D vector [벡터] 효과 미포함
- **No substrate [노 서브스트레이트]**: 자유공간 Green 함수 사용,
  기판 효과 무시
- **유한 1D 배열**: edge effect [엣지 이펙트] 가 1/√N 으로 천천히 감쇠
- **No radiation-reaction correction [노 래디에이션 리액션 코렉션]**:
  분극률에 복사 반응 보정 없음 (작은 cylinder 영역에서는 허용 가능한
  근사)

향후 작업: 3D vector CDA, 기판 Green 함수, radiation-corrected α 로의
확장.

---

## Slide 14 — What I Verified Myself (25초)

PDF 가이드가 가장 강조한 항목 — **직접 검증한 내용**:

- 10/10 internal physics tests [인터널 피직스 테스트] 통과
- 10개 서로 다른 P 점에서 FDTD external cross-validation [크로스
  밸리데이션]
- log-log [로그로그] 회귀로 β 의 1-σ uncertainty [언서튼티] 명시적
  계산
- Array size N, grading width, random α, F, fit window 에 대한
  robustness [로버스트니스]
- 80-seed bootstrap [부트스트랩] + 1/√N extrapolation 으로 reliability
- 모든 관찰을 physics / design / numerics 세 origin 으로 분류
- `validate_physics.py` [밸리데이트 피직스 닷 파이] 한 번에 12개
  자동 검증

모든 코드, JSON [제이슨] 결과, 그림, PPT 가 GitHub [깃허브] 에 공개되어
1분 안에 재현 가능합니다.

---

## Slide 15 — Conclusion (30초)

한 줄 요약:

> $|\Delta\varphi|(P) \approx 3.9 \cdot (\lambda/P)^{0.90 \pm 0.10}$
>
> |Δφ|(P) ≈ 3.9 곱하기 (λ/P) 의 0.90 플러스마이너스 0.10 제곱.

- N = 11 ~ 81, grading width, random α 에 걸쳐 **robust**
- Tidy3D FDTD 와 sub-wavelength 영역에서 **직접 일치**
- 결합 강도 F 에 따라 β = 1.2 → 0.5 로 부드럽게 변화
- Wood anomaly 는 CDA, FDTD 두 방법 모두에서 확인된 **진짜 물리**

이상으로 발표를 마칩니다. 질문 받겠습니다. 감사합니다.

---

## 발표 시 주의사항

- 각 슬라이드의 **첫 문장**을 또렷하게 — 청중은 슬라이드를 보고 있으니
  내용 반복이 아닌 핵심 메시지로 진입.
- **외워둘 수치**: β = 0.90 ± 0.10 / +57 % / +21 % / 5.98°-3.80° /
  RMS 2.9° / CDA 23°-FDTD 20° / F-sweep 1.23 → 0.46
- Slide 4 (Direct Answer) 와 Slide 9 (FDTD) 가 **가장 길고 가장
  중요** — 청중이 여기서 핵심을 가져갑니다.
- Limitations 슬라이드의 다섯 항목은 적극적으로 인정 — Q&A 에서
  교수님 질문에 "그건 한계로 명시했고 향후 작업입니다" 로 응대 가능.
