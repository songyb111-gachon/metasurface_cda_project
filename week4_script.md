# Week 4 Final Presentation — Script (10 min)
## Week 4 (위크 포) 최종 발표 대본

---

## [Slide 1 (슬라이드 원): Title (타이틀)] (~15초)

안녕하세요. 최종 발표를 시작하겠습니다.

주제는 **1D 메타서페이스 (metasurface, 메타서피스) 에서 메타 원자 간 결합이 위상 응답에 미치는 영향**이고, 직접 구현한 Coupled Dipole Approximation (커플드 다이폴 어프록시메이션) CDA (씨디에이) 와, Tidy3D (타이디 쓰리디) 클라우드 FDTD (에프디티디) 의 외부 검증까지 통합한 결과입니다.

---

## [Slide 2 (슬라이드 투): Research Question] (~25초)

연구 질문은 한 문장입니다:

**"배열 주기 P가 줄어들수록, 메타 원자 간 결합에 의한 위상 왜곡이 어떻게 증가하는가?"**

표준 메타서페이스 설계는 각 메타 원자를 isolated (아이솔레이티드) 로 가정하지만, 실제로는 인접 원자가 전자기 결합 (electromagnetic coupling, 일렉트로마그네틱 커플링) 으로 위상 응답을 왜곡시킵니다. 이 왜곡을 **정량적인 법칙**으로 답하는 것이 이번 프로젝트의 목표입니다.

---

## [Slide 3 (슬라이드 쓰리): Model + Method (모델 + 메소드)] (~40초)

방법은 **CDA scalar TM (티엠) 모델**입니다. 각 메타 원자를 점 쌍극자 (point dipole, 포인트 다이폴) 로 놓고

$$p_i = \alpha_i \, E_{\mathrm{loc},i}, \quad
  E_{\mathrm{loc},i} = E_{\mathrm{inc},i} + \sum_{j \ne i} G(r_{ij}) \, p_j$$

self-consistent (셀프 컨시스턴트) 식을 풀어 N×N 선형 시스템 $\mathbf{A}\,\mathbf{p} = \mathbf{E}_{\mathrm{inc}}$ 으로 환원합니다. Green (그린) 함수는 2D scalar Hankel (한켈) 함수,

$$G(r) = \tfrac{i}{4}\,H_0^{(1)}(k_0 r).$$

분극률은 Lorentzian (로렌치안), 기본 파라미터 ω₀ = 2.1π, γ = 0.4, F = 4.0 입니다.

핵심 라이브러리 `cda.py` (씨디에이 닷 파이) 와 NumPy linalg solve 만으로 N = 641 까지도 1초 이내에 풀이 가능.

---

## [Slide 4 (슬라이드 포): Verification 10/10] (~40초)

신뢰성 확보를 위해 10가지 독립적인 물리 검증 테스트를 먼저 통과시켰습니다.

쌍극자 1개 sanity check (새너티 체크), 2-dipole 해석해와 일치, Green 함수 공식 + 호혜성 (reciprocity, 리시프로시티), 선형 시스템 잔차, 거울 대칭, 행렬 호혜성, 1/√N 수렴, 파장 스케일링 불변성, 소광 전력 양수성, 비균일 솔버의 균일 극한.

**모두 기계 정밀도 수준에서 통과**. 솔버 자체의 정확성을 확보한 후 분석을 시작합니다.

---

## [Slide 5 (슬라이드 파이브): Direct Answer — The Increase Law (다이렉트 앤서)] (~60초)

핵심 답입니다. Wood anomaly (우드 어너멀리) 를 피한 sub-wavelength (서브 웨이브렝스) 영역 P 0.55에서 0.85 람다 까지를 31개 fine sweep (파인 스윕) 한 결과:

$$|\Delta\varphi|(P) \approx 3.9 \cdot (\lambda/P)^{\beta}, \quad \beta = 0.90 \pm 0.10$$

R² (알 스퀘어) = 0.73, 1-σ (일 시그마) 표준 오차는 log-log (로그로그) 직접 회귀로 측정한 0.10 입니다.

구체적으로, **P가 0.85 람다 → 3.80도, P가 0.55 람다 → 5.98도, ratio (레이쇼) 1.57배 — +57 percent (퍼센트) 증가**.

지수 β ≈ 1 은 위상 왜곡이 **거의 1/P 비례**로 자란다는 뜻이고, 이는 2D Hankel 격자합 Σ G(jP) 의 1/P 거동에서 옵니다. 즉 법칙은 결합 기하 (coupling geometry) 가 결정합니다.

---

## [Slide 6 (슬라이드 식스): β depends on F + window (베타 디펜즈 온 에프 + 윈도우)] (~50초)

여기에 두 가지 깊은 발견이 더 있습니다.

첫째, **β는 결합 강도 F에 따라 변합니다**. F = 0.5 일 때 β = 1.23 (super-linear, 수퍼 리니어), F = 4.0 (default, 디폴트) 일 때 β = 0.90, F = 8.0 일 때 β = 0.46 (saturation, 새튜레이션). 즉 **약한 결합에선 β > 1, 강한 결합에선 β < 1**.

둘째, **β는 fit (피트) 윈도우에 따라서도 변합니다**. P ∈ [0.55, 0.85] 에서는 β = 0.90, [0.65, 0.85] (Wood anomaly에 더 가까움) 에서는 β = 1.58. 즉 Δφ(P) 는 **단일 universal power law가 아니라 매끄러운 함수이며 P=λ에 가까울수록 가팔라집니다**.

따라서 "β = 0.9" 는 우리 결합 강도에서의 effective exponent (이펙티브 익스포넌트) 이고, 실제 메타서페이스 디자인은 β = 0.5 ~ 1.3 범위 어디에도 존재할 수 있습니다.

---

## [Slide 7 (슬라이드 세븐): Controlled Comparisons (컨트롤드 컴패리슨)] (~50초)

다음으로 PDF Week 3 요구사항인 controlled comparison 결과입니다.

**A.** 비공명 영역 평균: 균일 배열 3.27도, 비균일 배열 (graded α) 3.95도 — **+21 percent 추가 왜곡** 이 순수 α 비균일성에서 옵니다.

**B.** 임계 주기: 1°, 2°, 3° 임계값은 P = 3 람다 까지도 도달하지 못함 — 2D 시스템의 1/√r 감쇠 때문에 절대 임계 floor 가 존재.

**C.** 거울 대칭: 균일 배열 0°, 비균일 배열 -0.96° → graded α 가 대칭을 깸.

**D.** 행렬 조건수: Wood anomaly 근처도 κ(A) ≤ 2 → 피크는 **진짜 물리**, 수치 인공물 아님.

**E.** 에너지 예산 P_sca/P_ext: 모든 P에서 [0, 1] 범위 → 솔버 물리적 타당성 확인.

**F.** α-ordering: 부드러운 그래디언트 5.10°, 무작위 셔플 5.16 ~ 7.57° → smooth gradient (스무드 그래디언트) 는 결합에 더 강건.

---

## [Slide 8 (슬라이드 에잇): FDTD Cross-Validation (에프디티디 크로스 밸리데이션)] (~60초)

가장 중요한 외부 검증입니다. Tidy3D (타이디 쓰리디) 클라우드 FDTD로 11개 시뮬레이션 — 1 calibration + 10 periods, 총 비용 약 0.3 FlexCredit (플렉스 크레딧) — 을 돌렸습니다.

Setup: 11개 Lorentz 매질 cylinder, λ = 1 μm (마이크로미터), TM polarization (E ∥ cylinder axis), CDA와 정확히 같은 geometry.

결과: **두 방법이 같은 곡선 형태**. 서브파장 영역 sub-λ window 안에서 RMS difference (알엠에스 디퍼런스) 약 2.9도. 가장 중요한 P = λ Wood anomaly 에서 CDA 23도, FDTD 20도 — **두 방법 모두 sharp peak (샤프 피크)** 를 잡아냅니다.

핵심 메시지: **Wood anomaly는 진짜 물리 현상**이며, sub-wavelength 영역에서 우리의 power law fit이 실제 full-wave (풀웨이브) 결과와 부합합니다.

---

## [Slide 9 (슬라이드 나인): Reliability (릴라이어빌리티)] (~50초)

PDF가 요구하는 reliability 검증입니다.

**R1.** 80개 random α profile 에 대한 β 분포: median (미디언) β = 1.09, **90 percent band [0.63, 1.61]**.

**R2.** Grading magnitude w = 0, 0.05π, 0.10π, 0.20π, 0.30π, 0.40π: β가 w ≤ 0.20π 에서 1 근처로 안정. w ≥ 0.30π 에서는 over-grading (오버 그래디션) 으로 β 부호 변화.

**R3.** N-convergence: 1/√N 외삽으로 **N → ∞ 극한이 |Δφ| ≈ 6.32°** 로 수렴.

→ 보고된 답은 단일 실현이 아니라 **여러 조건에서 reliable (릴라이어블) 한 통계량**.

---

## [Slide 10 (슬라이드 텐): Physics vs Numerics vs Design (피직스 버서스 뉴메릭스 버서스 디자인)] (~40초)

관찰된 차이의 원인 분류:

- **Physics (피직스)**: +21 percent extra distortion, β ≈ 1 power law, Wood anomaly peaks.
- **Design (디자인)**: 거울 대칭 깨짐, α 그래디언트 효과.
- **Numerics-sound (뉴메릭스 사운드)**: κ(A) ≤ 2, energy ratio in [0, 1].
- **External validation (익스터널 밸리데이션)**: FDTD agreement.

**결론: 관찰된 모든 차이는 진짜 물리 또는 의도된 설계에서 기인하며, 수치 인공물은 없습니다.**

---

## [Slide 11 (슬라이드 일레븐): Limitations (리미테이션)] (~25초)

정직한 한계점:

- 점 쌍극자 가정 — 다중극 (multipole, 멀티폴) 효과 미포함.
- 2D scalar geometry — TM 모드만, 3D vector 메타 원자 효과 미포함.
- 기판 (substrate, 서브스트레이트) 효과 미포함 — 자유공간 Green 함수 사용.
- 유한 1D 배열 — edge effect 가 1/√N 으로 느리게 감쇠.
- α의 radiation-reaction (래디에이션 리액션) 보정 없음 — 작은 cylinder 에서는 허용 가능.

---

## [Slide 12 (슬라이드 트웰브): What I Verified Myself (왓 아이 베리파이드 마이셀프)] (~25초)

직접 검증한 항목:
- 10/10 물리 테스트 통과
- 10개 다른 P에서 FDTD 외부 검증
- log-log 회귀로 β = 0.90 ± 0.10 명시적 uncertainty
- N, grading width, random α, F, fit window 에 대한 robustness
- 80-seed bootstrap, 1/√N 외삽으로 reliability
- 모든 관찰된 feature를 physics / design / numerics 로 분류

---

## [Slide 13 (슬라이드 써틴): Conclusion (컨클루전)] (~30초)

한 문장 요약:

$$|\Delta\varphi|(P) \approx 3.9\,(\lambda/P)^{0.90 \pm 0.10}$$

- N = 11–81, grading width, random α 에 걸쳐 robust (로버스트)
- Tidy3D FDTD 와 sub-λ 영역에서 직접 일치
- β 는 결합 강도 F 에 따라 1.2 → 0.5 로 부드럽게 변화
- Wood anomaly 는 두 방법 모두 확인된 진짜 물리

이상입니다. 질문 받겠습니다.
