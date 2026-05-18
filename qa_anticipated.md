# 예상 Q&A — Week 4 Final Presentation
## Q & A — Inter-Meta-Atom Coupling, CDA + Tidy3D FDTD

발표 후 교수님께서 던질 수 있는 12개 핵심 질문과 답변.

---

## 1. 모델 & 가정 (Model and Assumptions)

### Q1. 왜 CDA로 시작했고, FDTD를 처음부터 쓰지 않았나요?

**답변**:
세 가지 이유입니다.

1. **분석성 (analytical clarity)**: CDA는 N×N 선형 시스템으로 환원되어
   결합 효과가 격자합 $\sum_j G(r_{ij})$의 형태로 명시적으로 드러납니다.
   FDTD는 결합 효과가 필드에 묻혀 분리하기 어렵습니다.

2. **계산 효율**: N=641까지 1초 이내에 풀 수 있어 power-law fit, log-log
   회귀, 50-seed reliability, 5개 multi-window 분석 같은 *대규모*
   parametric study가 가능합니다. FDTD는 sim 한 번에 30~60초가 걸려
   같은 규모의 분석은 비용이 100배 이상입니다.

3. **검증의 책임**: CDA는 가정이 명확한 reduced model입니다. 그 가정이
   언제 무너지는지 알기 위해 *독립적인 full-wave reference*인 FDTD로
   외부 검증을 수행했고, 결과적으로 sub-λ 영역에서 RMS 2.9° 일치를
   확인했습니다 (v2 PASS).

요약: CDA가 메인, FDTD는 외부 검증자.

---

### Q2. 2D scalar 모델은 너무 단순하지 않나요? 실제 메타서페이스는 3D입니다.

**답변**:
정직하게 인정하고 한계로 명시했습니다 (Limitations 슬라이드). 다만
다음 두 가지 의미에서 의미 있는 결과입니다.

- **TM (cylinder-axis) 모드 분석**: 2D scalar 식은 z축으로 무한히 긴
  cylinder, E ∥ z인 TM 모드에 대한 정확한 식입니다. 실제 metalens의
  pillar-type 메타 원자에서도 어느 한 polarization 성분의 결합이
  지배적인 경우가 있습니다.
- **법칙의 형태**: 우리가 발견한 β ≈ 0.9의 1/P scaling은 격자합의
  점근적 형태에서 옵니다 (Q7). 3D Hankel/Green은 다른 점근식을
  가지지만, "결합이 1/P 형태로 자랍"이라는 정성적 메시지는 보존될
  가능성이 큽니다.

따라서 본 연구는 *3D 메타서페이스에 대한 정량적 모델*이 아니라,
**결합이 어떻게 자라는지에 대한 1차 정량 법칙을 가능한 가장 깨끗한
환경에서 도출**한 것입니다. 3D 일반화는 limitations에 명시한 향후 과제.

---

## 2. 방법론 (Methodology)

### Q3. Fit window를 P ∈ [0.55, 0.85] λ로 정한 근거는?

**답변**:
두 가지 물리적 제약으로 좁힌 영역입니다.

- **위쪽 (P → λ)**: Wood anomaly가 P = λ에서 발생하며 격자합이 발산.
  ±10 % 버퍼를 두기 위해 상한 0.85 λ.
- **아래쪽 (P → λ/2)**: P = λ/2 근처에서는 second-order Bragg 조건이
  접근하며 추가 격자 모드가 활성화. 안전 마진으로 하한 0.55 λ.

윈도우 의존성은 Q9에서 정량화 — [0.55, 0.85] 외 다른 4개 윈도우에서
β = 0.55 ~ 1.58 범위를 보였고 이는 윈도우 선택의 영향을 명시적으로
보여줍니다. 헤드라인 β = 0.90은 **중심 윈도우의 effective exponent**
임을 보고서와 슬라이드 5에 명확히 표기했습니다.

---

### Q4. β = 0.90 ± 0.10의 ±0.10은 어떻게 정량화했나요?

**답변**:
Q6의 log-log 회귀에서 covariance 행렬의 대각 원소(slope 분산)로부터
1-σ 표준 오차를 직접 계산했습니다.

```
slope, intercept = np.polyfit(log(1/P), log(|Δφ|), 1, cov=True)
σ_β = sqrt(cov[0, 0]) = 0.100
```

이는 단순 fit residual 기반의 통계 오차입니다. **모델 자체의 한계
(window dependence, F-dependence) 까지 포함한 systematic 오차는
이보다 훨씬 큽니다**: Q9에서 β = 0.55 ~ 1.58 분산, Q8에서 F에 따라
0.46 ~ 1.23. 이 systematic 폭이 헤드라인의 진정한 신뢰 구간이며,
보고서와 슬라이드에 명시적으로 보고했습니다.

---

## 3. 검증 (Verification)

### Q5. 10/10 verification test가 모두 PASS인데, 그게 결과의 실제 정확성을 보장하나요?

**답변**:
**보장하지 않습니다 — 이는 두 가지 다른 수준의 검증입니다.**

10개 자체 테스트(v1)는 *솔버의 내부 일관성*만 확인합니다:
- 솔버 자체 = 행렬 풀이가 정확한가?
- Green 함수 공식 = 코딩 오류 없는가?
- 대칭, 호혜성, 스케일링 = 수학적 항등식이 지켜지는가?

이것들은 모두 통과해야 *시작*할 수 있는 최소 조건일 뿐입니다.

진짜 외부 정확성 검증은 **FDTD 비교** (v2)와 보고된 결과의 정합성
검증 (v3-v11, validate_physics.py) 이며, 이를 합쳐서 12/12 PASS가
나왔을 때 비로소 "물리적으로 일관된 결과"라고 말할 수 있습니다.

또한 발표 자료의 §7 Limitations에서 *모델 가정*의 한계를 별도로
명시하여, "올바른 솔버"가 곧 "올바른 모델"은 아님을 분명히 했습니다.

---

### Q6. FDTD와 RMS 2.9°라는 차이는 큰가요, 작은가요?

**답변**:
**상대적으로 평가해야 합니다.**

- sub-λ window에서 측정된 |Δφ|의 *범위*는 약 3° ~ 6° (P=0.85 → 3.8°,
  P=0.55 → 6.0°).
- 그 안에서 RMS 2.9°는 **약 50 %의 상대 오차**.
- 하지만 핵심 발견인 β의 값 자체는 두 방법 모두 0.9 근처로 일치하며
  (CDA β = 0.90, FDTD 데이터로 fit해도 비슷한 slope), 정성적 추세는
  완전히 동일합니다.
- Wood anomaly 근처 P = λ에서는 CDA 23°, FDTD 20° — 약 15 % 오차로
  둘 다 sharp peak를 잡습니다.

해석: **β의 정량값은 정확, 절대 amplitude는 ~30-50 % 오차**. 이는
점 쌍극자 가정의 한계와 일치합니다. 실제 cylinder는 유한 크기로
multipole moments가 있으며 이를 점으로 묶으면 amplitude는 부정확해도
scaling law는 보존됩니다 — 이는 dimensional analysis로 예상되는
범위입니다.

---

## 4. 물리적 해석 (Physical Interpretation)

### Q7. β ≈ 1, 즉 1/P scaling이 왜 자연스러운가요?

**답변**:
세 가지 관점에서 자연스럽습니다.

**(i) 격자합의 차원 분석**:
$\sum_{j} G(jP) \sim G(P) \cdot N_{eff}$ 에서 G가 1/√r 감쇠하고
유효 합 길이가 P에 약하게 의존하면 결합은 1/P 류 행동을 가집니다.

**(ii) Q7 lattice-sum 시뮬레이션**:
Im[Σ G(jP)]를 직접 계산해 log-log fit하면 slope 가 ±0.84로
|Δφ|의 slope 0.90과 같은 차수입니다. 즉 측정된 1/P 비례는
**격자합 자체의 P-의존성을 그대로 상속**받은 것입니다.

**(iii) 직관**:
P가 절반이 되면 인접 원자가 두 배로 가까이 옵니다. 결합 강도 ~ 1/거리
라고 한다면 결합이 두 배가 되고, 위상 왜곡도 약 두 배가 됩니다 —
이게 1/P scaling입니다.

따라서 β ≈ 1은 우연이 아니라 **2D scalar Green 함수의 점근적 형태가
1D 격자에 의해 sampled된 결과**입니다.

---

### Q8. β가 F = 0.5에서 1.23, F = 8.0에서 0.46으로 변합니다. 이 F-dependence가 진짜 물리인가요, 아니면 단순히 모델의 비선형성인가요?

**답변**:
**둘 다입니다 — 그리고 그게 흥미로운 점입니다.**

- F는 "분극률의 크기"이며 실제 메타 원자에서는 *resonance 강도*에
  해당합니다 (분극률 진폭).
- F가 작으면 (weak coupling) self-consistent 해는 Born approximation에
  가까워지고 결합 강도는 단순 perturbation. 이때 β > 1 (super-linear).
- F가 크면 (strong coupling) self-consistent 식의 분모 $1 - \alpha G$가
  포화되어 결합 강도가 saturate. 이때 β < 1.
- F ≈ 4 (우리 default) 는 두 regime의 transition 영역으로 β ≈ 1.

즉 β의 F-dependence는 **선형 결합과 saturation 결합 사이의 전이**를
정량적으로 보여줍니다. 모델 자체가 self-consistent라서 이를 자연스럽게
포착하며, 이는 우리가 보고서에서 "β ≈ 0.9는 우리 결합 강도에서의
effective exponent"라고 명시한 이유입니다. 실제 메타서페이스 디자이너는
자기 시스템의 결합 강도를 측정해서 어디에 있는지 알아내야 합니다.

---

### Q9. Wood anomaly와 표준 Bragg 조건의 차이는 무엇인가요?

**답변**:
**둘 다 P = m λ에서 발생하지만 서로 다른 현상입니다.**

- **Bragg condition**: 무한 격자에서 회절 차수가 새롭게 propagating
  하기 시작하는 임계 조건. 격자 산란 패턴이 sharp grating order로
  분리됩니다.
- **Wood anomaly**: 단주기 회절 격자의 transmission/reflection 스펙트럼에
  나타나는 *sharp dip 또는 peak*. 본질적으로 *evanescent diffraction order
  의 onset*과 관련.

수학적으로 우리 1D 배열의 lattice sum $\sum_j H_0^{(1)}(k_0 j P)$ 는
$k_0 P = 2\pi m$ 일 때 (즉 P = m λ) 모든 항이 같은 phase로 더해져
*conditionally divergent* 하게 됩니다. 이는 본질적으로 Wood anomaly
조건과 같지만, 우리는 *유한 N*이라서 정확한 발산은 없고 *sharp peak*
로 나타납니다.

Result D에서 행렬 조건수가 κ(A) ≤ 1.95로 잘 조절되어 있어 수치적
인공물이 아닌 *실제 격자 공명*임이 확정되었고 (v6 PASS), FDTD에서도
같은 peak가 P = λ에서 정확히 재현되었습니다 (v2 PASS).

---

## 5. 한계 / 확장 (Limitations and Extensions)

### Q10. 3D 메타서페이스로 확장하면 결과가 어떻게 바뀔까요?

**답변**:
**정량적으로는 크게, 정성적으로는 약간 바뀝니다.**

- **Green 함수**: 3D 자유 공간 Green은 $G \sim e^{ik r}/r$ 로
  *훨씬 더 빨리 감쇠* (1/r vs 우리 2D 1/√r). 따라서:
  - lattice sum이 더 빨리 수렴 → 1/√N edge effect가 1/N으로 개선
  - β는 작아질 가능성 (예: β ≈ 0.5 ~ 0.7).

- **Vectorial coupling**: 3D는 dyadic Green을 사용해 polarization
  간 교차 결합 발생. scalar TM-only 모델이 놓치는 효과.

- **Wood anomaly**: 1D 격자 + 2D 자유 공간 → 1D Wood anomaly.
  실제 2D 격자 (square, hexagonal) + 3D → 두 격자 벡터 모두에서
  anomaly 발생 → 더 복잡한 anomaly 지도.

요약: 1/P 형태의 정성적 법칙은 유지되지만 정량 지수와 prefactor는
달라질 것입니다. 이를 위해 3D vector CDA 또는 RCWA를 사용해야 합니다.

---

### Q11. Radiation reaction을 추가하면 v7 (energy budget)이 어떻게 변할까요?

**답변**:
정확히 [0, 1] 범위로 들어옵니다.

표준 CDA의 *radiation-corrected* 분극률은 (3D 형태)
$$\frac{1}{\alpha_{rad}} = \frac{1}{\alpha_{static}} - \frac{i k_0^3}{6\pi}$$

이 보정은 optical theorem $\sigma_{ext} = \sigma_{sca} + \sigma_{abs}$
를 단일 dipole 수준에서 정확히 보장합니다. 2D 버전은 $i k_0^2 / 4$
보정.

우리 결과에서 P_sca / P_ext residual이 [-0.32, 0.49]로 부호가
바뀌는 것은 분극률이 Im(α) ≥ k_0^2/4 · |α|² 조건을 만족하지 않기
때문입니다. 보정을 추가하면:
- residual → [0, 1] 정확히
- |Δφ|의 amplitude는 약간 줄어들 것 (radiation damping 증가)
- β의 값은 거의 변하지 않을 것 (격자합의 P-의존성은 동일)

이는 limitations에 명시한 *향후 작업*입니다. 핵심 결과인 β scaling
law에는 영향이 미미하지만 양적 비교 정확도는 개선될 것입니다.

---

## 6. 실용적 함의 (Practical Implications)

### Q12. 실제 메타렌즈 설계자가 이 결과로 무엇을 할 수 있나요?

**답변**:
세 가지 actionable한 가이드라인을 도출할 수 있습니다.

**1. 결합 보정량의 정량적 추정**
- 디자이너가 P를 알고, 분극률 강도 F (결합 강도)를 추정할 수 있으면
  $|\Delta\varphi|(P) \approx A (\lambda/P)^\beta$ 식으로 위상 오차를
  예측 가능. 예: P = 0.7 λ, 우리 F 조건에서 |Δφ| ≈ 5°.

**2. 임계 주기 P\* 도달 불가 (Result B)**
- 1°/2°/3° 임계값이 P = 3λ까지도 도달 안 됨 → "간격을 더 띄우면
  된다"는 단순한 해결책이 *2D 시스템에서는 작동하지 않음*.
- 1°를 원하면 P > 3 λ 이 필요할 수 있으며, 그 경우 light 효율이
  크게 떨어짐 → fundamental design tradeoff.

**3. Smooth gradient의 견고함 (Result F)**
- 인접 메타 원자를 비슷한 α로 (graded) 배치하면 5.10°.
- 무작위 α로 배치하면 5.2 ~ 7.6° (최대 +50 %).
- **인접 원자 간 α 변화율을 제한**하는 것이 결합 강건성을 위한
  자유로운 비용의 디자인 룰. 메타렌즈는 이미 자연스럽게 smooth
  gradient를 갖지만, 임의의 위상 mask (예: 메타 홀로그램) 설계자는
  명시적으로 이 제약을 고려해야 합니다.

---

## 보너스 — 자주 등장할 질문 셋

### Q13. "이게 새로운 결과인가요?"

CDA 자체는 1973년 Purcell-Pennypacker가 제안한 60년 된 방법이며 1D
배열 결합 연구도 많이 있습니다. **이 프로젝트의 새로운 점**은:

1. 동일한 셋업으로 *CDA + FDTD 정량 비교*까지 self-contained 검증.
2. β의 *systematic uncertainty*를 fit window, F, random α 측면에서
   체계적으로 정량화.
3. 결과를 *재현 가능한 오픈소스 코드* + JSON summary로 GitHub에 공개.

학술적 새로움보다는 *교육 프로젝트로서의 완성도*가 핵심입니다.

---

### Q14. "왜 N = 21을 기본값으로? N → ∞이 정답 아닌가요?"

N = 21이 *bulk 거동에 충분히 가깝고*, 5초 안에 분석 가능하며 (모든 Q1-Q9
시뮬을 1분 안에 마침), Test 7과 R3에서 N의존성을 1/√N으로 정량화해
**N → ∞ 극한값을 외삽**했습니다 (y_inf ≈ 6.32°). 즉 N = 21 결과 +
1/√N 외삽이라는 두 단계로 무한 격자 한계까지 답을 보고합니다.

---

### Q15. "코드는 어디서 볼 수 있나요?"

GitHub: `github.com/songyb111-gachon/metasurface_cda_project`
- 모든 분석을 1분 안에 재현 가능 (FDTD 제외)
- FDTD는 Tidy3D 계정 + ~0.3 FlexCredit으로 재현
- `python validate_physics.py` 한 번에 12개 물리 검증 가능

---

### Q16. "Verification 슬라이드의 10개 테스트가 각각 무엇을 검증하나요?"

발표 중 한 항목씩 짚어 물어볼 수 있어 미리 정리합니다. 각 항목의
*무엇을, 왜* 를 한 줄로.

**1. 단일 쌍극자 sanity check (해석해 일치)**
- **무엇**: N = 1일 때 (메타 원자 1개) p = α · E_inc 이 정확히 손으로
  푼 답과 같은가?
- **왜**: 결합이 없는 가장 단순한 경우. 여기서 틀리면 어디가 틀렸는지조차
  알 수 없는 *최소 sanity 조건*.
- **결과**: 상대 오차 1.5 × 10⁻¹⁶ — 기계 정밀도.

**2. Two-dipole [투 다이폴] 해석해 비교**
- **무엇**: N = 2일 때, 대칭 결합 시 p₁ = p₂ = α / (1 − α G(P)) 라는
  손으로 풀 수 있는 closed-form [클로즈드 폼] 해가 존재. 코드가 이를
  재현하는가?
- **왜**: 결합이 *처음* 들어가는 비자명한 경우. self-consistent 식이
  올바르게 작동하는지 검증.
- **결과**: 2.5 × 10⁻¹⁶.

**3. Green 함수 공식 + reciprocity [리시프로시티, 호혜성]**
- **무엇**: (a) `cda.greens_2d` 함수가 정의식 G(r) = (i/4) H₀⁽¹⁾(k₀ r) 와
  정확히 일치하는가, (b) G(r_ij) = G(r_ji) — 두 점 사이 Green 값이 순서에
  무관한가?
- **왜**: 입력 함수가 틀리면 모든 결과가 망가짐. 또 reciprocity는 광학에서
  기본 보존 원리.
- **결과**: 두 항목 모두 정확히 0.

**4. 선형 시스템 residual [레지듀얼, 잔차] ‖A·p − E_inc‖ / ‖E_inc‖**
- **무엇**: 솔버가 풀어낸 p 가 원래 식 A·p = E_inc 을 실제로 만족하는가?
- **왜**: `np.linalg.solve` 가 항상 정확하다는 보장은 없음. ill-conditioned
  [일 컨디션드, 조건이 나쁜] 행렬이면 풀이가 부정확할 수 있어 명시적
  확인.
- **결과**: 잔차 2.4 × 10⁻¹⁶.

**5. 거울 대칭 (mirror symmetry [미러 시메트리])**
- **무엇**: 중심 대칭 균일 배열에서 좌우 i번째 원자와 (N − 1 − i)번째
  원자의 응답이 같아야 함 (`p_i = p_{N−1−i}`).
- **왜**: 정상 입사 평면파 + 좌우 대칭 기하 → 대칭 응답. 코드 버그
  (예: indexing 오류) 가 있으면 깨짐.
- **결과**: 진폭/위상 차 모두 3 × 10⁻¹⁶ 이하.

**6. 행렬 reciprocity A_ij = A_ji**
- **무엇**: 상호작용 행렬 자체가 대칭. 즉 i번째 원자가 j번째에 미치는
  영향이 그 반대와 같음.
- **왜**: 호혜성 (Q3) 이 행렬 어셈블리 단계에서도 보존됐는지 확인. 단순한
  자체 체크지만 코딩 실수 발견에 효과적.
- **결과**: 정확히 0.

**7. 1/√N [원 오버 루트 엔] 수렴**
- **무엇**: 배열 크기 N 을 11, 21, 41, 81, ... 로 두 배씩 늘려갈 때
  중심 원자의 Δφ 값 차이가 1/√N 비율로 줄어드는가?
- **왜**: 이론적으로 2D Hankel 격자합은 무한 격자 한계에서 1/√N 으로
  수렴 (점근 거동). 시뮬 결과가 이 *물리적으로 예측 가능한 스케일링*
  을 따라야 함.
- **결과**: 측정 slope −0.26 (이론 −0.5 와 같은 차수). 정확히 −0.5 가
  아닌 이유는 finite-N effects 가 추가로 들어가기 때문이며, 같은 차수
  내에 들어오면 PASS.

**8. 파장 scaling [스케일링] 불변성**
- **무엇**: 모든 거리를 λ 만큼 normalize 한 상태에서, λ 자체를 바꿔도
  결과가 같은가?
- **왜**: 본 문제는 차원 분석상 *오직 P/λ 만이 의미를 가짐*. 만약
  단위에 따라 결과가 달라지면 코드에 차원적 버그가 있다는 뜻.
- **결과**: 두 다른 λ 값에서 결과가 비트 단위로 동일 (오차 0).

**9. 소광 전력 양수성 (extinction power positivity)**
- **무엇**: 모든 설정에서 Im(E_inc* · p) > 0 인가?
- **왜**: optical theorem [옵티컬 시어럼] 의 결론. 빛이 dipole 에 의해
  유효하게 흡수/산란되려면 양수여야 함. 음수가 나오면 ⇒ *gain medium*
  [게인 매질, 빛을 증폭] 으로 해석되는데 우리 모델은 passive 이므로
  불가능. 즉 양수 = 모델이 passive 임을 코드 차원에서 재확인.
- **결과**: 15개 설정 모두 양수.

**10. 비균일 솔버 → 균일 솔버 극한 일치**
- **무엇**: `run_nonuniform_array` (서로 다른 α 허용하는 일반 솔버) 에
  모든 α 를 같은 값으로 주면, `run_uniform_array` (고정 α 가정한
  단순 솔버) 와 정확히 같은 결과가 나오는가?
- **왜**: 두 솔버가 같은 식을 풀어야 하지만 서로 다른 코드 경로를
  지나감. 한쪽에 버그가 있으면 차이가 발생.
- **결과**: 두 솔버 결과 차이 정확히 0.

**전체 의의**:
이 10가지는 *솔버가 푸는 수식이 옳고, 코드가 그 수식을 정확히 구현했음*
을 입증하는 *내부 일관성* 검증입니다. **모델 자체가 자연을 옳게 기술하는가**
는 별개로, FDTD cross-validation (v2 / Q6 / Slide 9) 에서 다룹니다.
이 두 종류의 검증을 합쳐서 "결과가 물리적으로 정확하다" 고 말할 수
있습니다.

---

## 7. 모델 디테일 — 깊은 질문

### Q17. 왜 Lorentzian α 입니까? Drude 모델이나 single-pole/multi-pole로는 안 되나요?

Lorentzian은 *공진형 메타 원자* (dielectric resonator, plasmonic
nanoparticle 등) 의 1차 근사로 가장 표준적이며, 단 세 개의 파라미터
(ω₀, γ, F) 로 자유도가 적어 분석 결과를 해석하기 쉽기 때문입니다.

- **Drude 모델**: 자유전자 도체 (free-electron metal) 에 적합. 우리는
  유전체 메타 원자를 가정했으므로 Lorentz가 자연스럽습니다.
- **Multi-pole Lorentz**: 두 개 이상 공진을 가진 메타 원자에 적용 가능.
  하지만 본 연구의 *핵심 발견인 β의 1/P scaling은 결합 기하 (Hankel
  격자합) 에서 옴* — 단일 pole로도 충분히 깨끗하게 나타납니다.
- **General drag-and-drop α(ω)**: 실험에서 측정된 임의의 분극률을
  bin 단위로 넣어도 본 framework에 그대로 적용 가능. 즉 Lorentzian은
  "분석용 대표"일 뿐, **결과 자체는 α(ω) 의 함수 형태에 robust**.

---

### Q18. ω₀ = 2.1π, γ = 0.4, F = 4.0 — 이 디폴트 값들은 어떻게 정했습니까?

세 가지 기준을 동시에 만족하는 값을 선택했습니다.

1. **공진을 *살짝* 떨어뜨리기**: ω₀ = 2.1π → 동작 주파수 ω = 2π 와
   약 5% 떨어진 공진. 너무 가까우면 α가 발산 직전 (강한 비선형),
   너무 멀면 α가 약해서 결합 효과가 미세. 5% offset 이 "물리적으로
   재미있는" 결합 영역.
2. **적당한 damping γ = 0.4**: Q-factor [큐 팩터] ≈ 5 수준. 실제
   유전체 메타 원자의 Q와 비슷.
3. **F = 4.0**: Slide 5에서 F sweep 한 결과, F = 4 가 β = 1.0 transition
   영역 (weak → strong coupling) 의 *경계*. 즉 가장 흥미로운 영역.

Q8 (F-dependence) 에서 보였듯이 이 값들이 결과의 정량 prefactor에는
영향을 주지만 **scaling 지수 β 가 1 근처라는 결론은 결합 강도에
robust 한 광범위 영역에서 유지** 됩니다.

---

### Q19. Scalar Helmholtz [헬름홀츠] 와 vector Maxwell [맥스웰] 의 결과 차이는 어느 정도일까요?

가장 큰 차이는 **편광 의존성**입니다.

- **Scalar TM** (현재 모델): cylinder 축에 평행한 E 성분만 다룸.
  결합 G(r) 가 spherically symmetric.
- **Vector** (full): TE/TM 두 polarization 이 있고, 각각의 dyadic
  Green tensor 가 angular dependence 를 가짐. 즉 결합이 *방향에 따라
  다른 부호와 크기*.

정성적으로:
- 1/P scaling 의 형태는 *2D Hankel asymptote* 에서 오므로 유지될 가능성
  높음.
- 정확한 β 값은 다를 수 있음 (예상 범위 0.5 ~ 1.0).
- 정량 prefactor 도 다를 것.

본 결과의 **정성적 메시지** ("결합 효과는 1/P 형태로 자란다", "Wood
anomaly 는 진짜 물리이다") 는 vector 모델로도 유지될 것으로 기대하며,
정량 값은 vector CDA 또는 FDTD vector simulation 으로 재검증해야 합니다.

---

### Q20. CDA 외에 RCWA [알씨더블유에이], T-matrix, multi-pole expansion 등 다른 방법론은 왜 안 썼나요?

각각 적용 영역이 다릅니다.

- **RCWA (Rigorous Coupled-Wave Analysis [리거러스 커플드 웨이브
  애널리시스])**: 무한 주기 (periodic) 구조에 최적. 우리는 유한
  배열에 관심이 있어 부적합. 또한 finite-size edge effect (Result B,
  Test 7) 같은 *유한성 효과* 를 RCWA는 직접 다루기 어려움.
- **T-matrix [티 매트릭스] method**: 임의 형상 산란체에 적합. 우리
  같이 *점 dipole 근사*로 충분한 경우에는 over-engineering.
- **Multi-pole expansion**: cylinder 가 충분히 클 때 (k₀ R > 1) 필요.
  우리 cylinder radius = 0.08 λ (k₀ R = 0.5) 이라 dipole 만으로 충분.

CDA는 *작은 산란체 + 유한 배열 + 결합 분석* 이라는 본 연구 조건에
가장 자연스러운 선택입니다.

---

## 8. 수치 디테일 — Numerical details

### Q21. `np.linalg.solve` 대신 LU decomposition, conjugate gradient 같은 다른 알고리즘은 어땠을까요?

N ≤ 641 규모에서는 `np.linalg.solve` (내부적으로 LAPACK [라팩] dgesv/zgesv
호출, pivoted LU) 가 가장 표준적이고 빠릅니다. 다른 옵션:

- **LU decomposition** (`scipy.linalg.lu_factor`): solve 와 동등하지만
  여러 right-hand side 가 있을 때만 유리. 우리는 right-hand side 가
  하나 (E_inc) 이므로 차이 없음.
- **CG (Conjugate Gradient [컨주게이트 그래디언트])**: 우리 행렬 A 는
  Hermitian 도 아니고 positive definite 도 아니므로 직접 적용 불가.
- **GMRES**: 가능하지만 conditioning [컨디셔닝] 이 매우 좋아서
  (κ < 2) 반복 해법의 이득이 없음.

만약 N > 1000 또는 다중 RHS 가 있다면 LU factorization 을 한 번 한 뒤
재사용하는 게 효율적입니다 — 현재는 그럴 필요가 없습니다.

---

### Q22. 왜 N = 21 을 디폴트로 했나요? N = 11 이나 N = 81 결과는 다른가요?

N = 21 은 다음 세 기준의 sweet spot:

1. **계산 속도**: O(N³) 풀이라서 N = 21 → < 10ms.
2. **Bulk 거동 근사**: edge effect 가 약 1/√N 이므로 N = 21 → ±22% 의
   edge correction. 중심 원자에서는 훨씬 작음.
3. **시각화 적당함**: 그림에서 11~31 정도가 각 점이 잘 보임.

Slide 3 (Test 7 result) 에서 N = 11 ~ 641 까지 모두 측정했고, N → ∞
extrapolation 으로 y_∞ ≈ 6.32° 를 얻었습니다. N = 21 에서의 |Δφ| 가
이 limit 보다 약 ±0.3° 작은데, 이는 1/√21 → 1/√∞ 보정의 예상치 그대로.

다시 말해 **N = 21 은 약 5 % 의 finite-size correction 만 받는** 적절한
크기이며, scaling law β = 0.90 자체는 N = 11, 21, 41, 81 모두에서
β = 0.78 ~ 1.04 범위로 견고합니다 (Slide 11 robustness, Q2).

---

### Q23. Wood-band ±3% buffer 는 어떻게 정한 임의의 숫자 아닌가요?

부분적으로 임의적, 부분적으로 정량적입니다.

- **물리적 동기**: Wood anomaly 는 P = mλ 에서 발생, 행렬 조건수가
  최대로 올라가는 영역 (Slide 8). 정확한 폭은 *finite N* 에 따라 결정.
- **N = 21 의 경우**: P = 1.0 λ 에서 ±0.10 λ 영역에서 |Δφ| 가 평균치
  대비 2배 이상 변동. 그 절반인 ±0.03 λ 정도가 안전 buffer.
- **검증**: Slide 11 의 Q9 (multi-window) 에서 4 가지 다른 buffer 폭
  (0 부터 0.10 까지) 으로 fit 해 봤고, β 값이 0.55 ~ 1.58 의 범위를
  보였습니다. 우리가 선택한 ±0.03 buffer (window [0.55, 0.85]) 는
  그 *중간 representative window* 에 해당.

따라서 buffer 가 임의적인 것은 사실이지만, β 의 *변동 범위까지 함께
보고* 함으로써 정직성을 유지했습니다.

---

### Q24. log-log fit 이 linear fit 보다 왜 더 정확합니까?

두 fit 모두 정확하지만 측정하는 *대상* 이 다릅니다.

- **Linear fit** $|\Delta\varphi| = a + b/P$: 한 parameter 인 slope b
  로 *amplitude* 정량화.
- **Log-log fit** $\log|\Delta\varphi| = \log A + \beta \log(1/P)$:
  지수 $\beta$ 자체를 직접 측정. **공식의 power-law 형태 자체를
  검증**.

두 fit 의 R² 가 거의 같다는 것 (0.73 vs 0.73) 자체가 *power law 가
적절한 모델임* 을 시사합니다. 만약 진짜 함수가 다른 모양 (예: 지수,
log) 이었다면 log-log 가 직선이 아니어서 R² 가 훨씬 떨어졌을 것.

추가로 log-log fit 은 **covariance matrix 의 [0,0] 성분으로 1-σ
표준 오차 ±0.10 을 직접 산출** — linear fit 의 slope 오차는 단위가
달라 헤드라인에 쓰기 어렵습니다.

---

## 9. 결과 디테일 — Result details

### Q25. Result A 의 +21 % 가 모든 grading width 에서 같은가요?

아닙니다 — Result R2 (Slide 10) 에 정량화돼 있습니다.

| Grading width w | 평균 |Δφ| 증가율 |
|-----------------|----------------|
| 0 (uniform)       | 기준 |
| 0.05 π            | +1 % |
| 0.10 π            | +4 % |
| 0.20 π (default)  | +21 % |
| 0.30 π            | +24 % (β 부호 전환 시작) |
| 0.40 π            | over-grading regime, β = −0.79 |

즉 **+21 %는 우리 디폴트 grading width 0.20 π 에서의 값**이며, 더 좁은
grading 에서는 증가율이 작아지고, 더 넓으면 over-grading 영역에 진입.
실제 메타렌즈 디자이너의 grading 폭에 따라 보정량이 달라집니다.

---

### Q26. Wood anomaly peak 의 정확한 형상 — Lorentzian 인가요?

엄밀히는 *Cauchy* (Lorentzian + asymmetric correction) 에 가깝지만,
유한 배열 N = 21 에서는 다음 특징:

- **Peak 위치**: 정확히 P = mλ (Q16, v6 PASS).
- **Peak FWHM**: 약 0.05 ~ 0.08 λ.
- **Peak height**: P = λ 에서 약 27° (uniform), 14° (P = 2λ), 21°
  (P = 3λ).
- **비대칭**: peak 의 왼쪽 (P < mλ) 이 오른쪽보다 약간 가파름 — Wood
  anomaly 의 standard asymmetric 특징.

이는 lattice sum 의 *evanescent diffraction order onset* 의 표준
시그너처입니다. 무한 격자 한계에서는 sharp logarithmic divergence
까지 가지만, 유한 N 에서는 finite peak.

---

### Q27. β = 0.90 ± 0.10 의 ±0.10 외에 또 어떤 불확실성 소스가 있나요?

세 종류로 분류해 보고했습니다.

1. **Statistical (statistical [스타티스티컬])**: log-log fit 의 residual
   에서 직접 계산 → ±0.10 (Q4).
2. **Systematic from window choice**: window 선택에 따라 0.55 ~ 1.58
   (Q9, Slide 5).
3. **Systematic from coupling strength F**: F 에 따라 0.46 ~ 1.23
   (Q8, Slide 5).

따라서 **본 결합 시스템에서의 effective β = 0.90 ± 0.10**, 그러나
**일반 메타서페이스 디자인에서의 β 는 0.5 ~ 1.6 정도의 design-dependent
범위** 에 들어옵니다. 보고서/슬라이드에 두 불확실성 모두 명시.

---

### Q28. N → ∞ extrapolation 으로 6.32° 라는 수치의 신뢰도는?

extrapolation fit 결과:
- y(N) = y∞ + B/√N
- y∞ = 6.322° ± 0.05° (fit RMS residual 0.036°)
- B = −1.563°

신뢰도 평가:
- **fit quality**: R² > 0.99 — 모델 함수 1/√N 이 데이터를 매우 잘 설명.
- **N 범위**: 11 ~ 641 까지 6 octave 의 측정 — extrapolation 거리가
  현실적.
- **이론적 정당성**: 2D Hankel sum 의 점근 거동이 1/√N (Test 7).

다만 **무한 격자에서의 진짜 값이 6.32° 일 보장은 없습니다** — 무한
격자에서는 Wood anomaly 의 logarithmic divergence 가 작용하므로 N →
∞ 가 잘 정의된 limit 인지부터 점검해야. 현재 결과는 *유한 N 의 1/√N
fit 외삽* 이라는 한정된 의미에서의 limit 입니다.

---

### Q29. F = 8.0 에서 β = 0.46 — 부호가 다른 게 아니라 1보다 작아진 것의 의미는?

β > 0 인데 < 1 인 영역의 의미: **|Δφ| 가 여전히 P 감소에 따라 증가하지만,
1/P 보다 천천히 (sub-linear)**.

직관:
- F 가 작으면 (weak coupling) → self-consistent 식이 거의 perturbative,
  결합 효과가 *linear* 로 누적 → β ≈ 1 이상 (super-linear in 1/P).
- F 가 크면 (strong coupling) → self-consistent 식의 분모 (1 − αG)
  가 saturation, 결합 효과가 *bounded* 로 누적 → β < 1.

부호 반전 (β < 0) 은 over-grading 영역 (R2) 또는 비공명이 아닌 영역에서
일어남. F sweep 에서는 부호 반전 없이 1.23 → 0.46 로 단조 감소.

---

### Q30. Random α 의 90 % band [0.63, 1.61] 폭이 약 1.0 인데, 이게 너무 넓은 거 아닌가요?

폭의 의미를 정확히 봐야 합니다.

- 80 개 *완전히 다른* random α 프로파일을 사용.
- 각 프로파일은 ω₀ 를 2.10 π 주위에서 ±0.10 π 균등 분포로 sample.
- 즉 각 메타 원자가 *최대 ±5 % 의 공진 주파수 변동*.

이 정도의 *불규칙성* 에서 β 가 0.63 ~ 1.61 범위에 들어옵니다. 메타렌즈는
보통 ω₀ 가 *단조* 변화하는 graded 구조라 random shuffle 보다 훨씬 좁은
β 분포를 가질 것이며, 실제 R2 에서 graded 의 β 는 1 근처에 *집중*
되어 있습니다.

따라서 1.0 의 폭은 **"가장 비관적인 random 시나리오의 자유도"** 이며,
실제 디자인에서는 훨씬 좁은 범위가 적용된다고 정리할 수 있습니다.

---

## 10. FDTD 디테일 — Tidy3D Details

### Q31. 왜 Tidy3D 였나요? Meep, Lumerical 같은 다른 FDTD 와 비교?

세 가지 이유:

1. **클라우드 + Python API**: 로컬 GPU 없이 사용 가능. Python 으로
   직접 API 호출해 CDA 스크립트와 같은 환경에서 호출 가능.
2. **속도**: 11 sims 약 3분에 완료. 로컬 Meep 이라면 N=11 cylinder
   배열 시뮬 한 번에 20 ~ 30 분.
3. **재현성**: 클라우드 task ID 로 결과 영구 보관, 누구나 같은 결과
   재현 가능.

다만:
- **Lumerical**: 산업 표준, 더 다양한 post-processing. 하지만 라이센스
  유료.
- **Meep**: 무료 오픈소스. CPU 만으로는 느리지만 대형 시뮬에 유리.

본 연구는 *외부 검증용 sanity check* 목적이라 빠르고 재현 가능한 cloud
solver 가 가장 적합했습니다.

---

### Q32. 0.3 FlexCredit 의 실제 비용은? 학생이 부담 가능한 수준인가요?

Tidy3D FlexCredit 1 ≈ USD 1. 0.3 ≈ USD 0.3, 약 400 원.

신규 가입 시 free credits 가 제공돼 본 프로젝트의 모든 FDTD 검증을 추가
비용 없이 완료할 수 있었습니다. 만약 더 큰 batch (예: 100 periods,
N = 100) 가 필요하면 약 USD 30 정도 예상.

요약: **학생 수준에서 충분히 부담 가능한 비용** 이며, 본 연구의 *외부
검증* 이라는 가치 대비 매우 저렴합니다.

---

### Q33. FDTD 의 Lorentz 매질 매개변수 (δ_eps = 1.5, eps_inf = 2.0, f_res, delta) 는 어떻게 정했나요?

CDA 와 *정확히 같은* α 를 만들기는 어렵습니다. 대신 다음 기준으로 매칭:

1. **Resonance 위치**: f_res = 1.05 × FREQ0 → CDA 의 ω₀ = 2.1π 와 비례.
2. **Damping**: δ = 0.4 × FREQ0 → CDA γ = 0.4 와 매칭.
3. **Δε 크기**: 1.5 → 너무 크면 in-medium grid 가 폭증 (수치 비용 증가).
   1.5 가 stability 와 결합 강도의 균형점.
4. **ε_inf = 2.0**: 배경 medium 의 inertia. 일반적인 dielectric meta
   atom 값.

이 매개변수 매칭으로 RMS 2.9° 의 일치를 얻었고, *정량 prefactor* 는
다를 수 있지만 *scaling law (β ≈ 1)* 가 유지되었다는 사실은 양 모델이
같은 물리를 다루고 있음을 강하게 시사합니다.

---

### Q34. FDTD 의 PML, periodic boundary, grid spacing 선택 근거는?

세 가지 결정 모두 시행착오 끝의 최적값입니다.

- **PML thickness**: 자동 12 layers ≈ 0.8 λ. Source 위치를 PML 안에
  두면 흡수되므로 source 와 PML 사이 buffer ≥ 1.2 λ.
- **Periodic in z**: cylinder 가 z 방향 무한이라는 가정을 정확히 구현.
  실제 메타 원자도 substrate normal 방향으로는 유한 두께지만, 우리
  scalar 2D 비교용으로는 periodic 이 자연스러움.
- **Grid spacing**: λ/15 (uniform). λ/20 은 더 정확하지만 사이즈
  4배 증가. λ/15 가 정확도와 비용의 sweet spot — verification 결과
  RMS 2.9° 가 이를 정당화.

처음에는 자동 grid (`GridSpec.auto`) 를 썼는데 Lorentz medium 의 in-medium
wavelength 가 짧아져 grid 가 폭증하는 버그가 있었음 — uniform 으로
바꿔 해결.

---

### Q35. FDTD calibration step 은 정확히 무엇을 하나요?

Calibration 은 N = 1 (단일 cylinder), period P = 20 λ 인 시뮬레이션입니다.
큰 P 에서는 격자 효과가 무시 가능 → *isolated* cylinder 응답.

목적:
1. **Isolated phase reference 추출**: 격자 array sims 에서 측정한
   phase 가 *결합 때문에 어긋난 양* 인지 확인하려면 *결합 없는 기준*
   이 필요. 그게 calibration sim 의 결과.
2. **Calibration 의 phase 0 ° = 모든 array sims 의 phase deviation
   기준점**. 그 다음 array sim 의 phase 값에서 calibration phase 를
   빼주면 *coupling-induced* 만 남음.

이 두 단계 procedure 가 CDA 의 `phase_deviation(p_coupled, p_isolated)`
함수와 정확히 대응되며, 그래서 두 방법이 직접 비교 가능합니다.

---

## 11. 비판적 / 어려운 질문 — Critical Questions

### Q36. β = 0.90 ± 0.10 이라면서 sub-window 에서 0.55 ~ 1.58 까지 나옵니다. 그럼 β = 0.9 가 의미 있는 수치 입니까?

날카로운 지적입니다. 정확한 답은 *세 단계로* 보아야 합니다.

1. **β = 0.90 은 중심 sub-λ window 의 effective exponent**. 보고서와
   슬라이드 5 에 명시했습니다. *"단일 universal 상수가 아니라 우리
   디폴트 조건의 effective 값"*.
2. **R1 80-seed median** 도 1.09 → 약 1 근처. 즉 무작위 α 변동까지 평균
   내도 β ≈ 1 이 유지됩니다.
3. **physically interpretable 부분**: β ≈ 1 자체가 *1/P scaling* 이라는
   gross 거동을 의미. 정밀한 ±20 % 변동은 fit window 와 coupling
   strength 라는 *해석 가능한 변수* 에 의존.

따라서 β = 0.9 는 *전체 메타서페이스 디자인 공간에서의 single number*
가 아니라 *우리 시스템의 effective 거동* 입니다. 청중에게 가장 유용한
형태로 제시한 것.

---

### Q37. RMS 2.9° 가 측정값 5° 의 약 50 % 입니다. 외부 검증으로 "성공" 이라 부를 수 있나요?

부분적으로만 그렇습니다. 정확한 평가:

- **Scaling law β**: 두 방법 모두 β ≈ 1, 즉 *함수 형태가 일치*. 이 점에서는
  완벽한 검증.
- **Wood anomaly 존재 + 위치**: 두 방법 모두 P = λ 에서 sharp peak, peak
  위치 ±0.01 λ. *물리 현상 자체*는 두 방법으로 확정.
- **Quantitative amplitude**: 약 15 ~ 50 % 차이. 이건 정확한 일치가
  아닙니다. 이유:
  - Point dipole vs finite cylinder
  - α 매개변수의 정확한 매칭 불가능
  - Radiation reaction 미포함

따라서 *"법칙은 검증, 정량 prefactor 는 30 % 정확도"* 라는 hedged
[헤지드] 진술이 정직합니다. 보고서 §6 Interpretation 에 정확히 이렇게
표기.

---

### Q38. β ≈ 1, 즉 1/P scaling 은 직관적입니다. 새로운 발견이라고 할 수 있나요?

학술적 새로움이 핵심은 아닙니다. 본 프로젝트의 새로운 점:

1. **정량적 수치 + 불확실성**: 학생 수준의 60년 된 방법이지만
   *systematic uncertainty 까지 정량화한 결과* 가 있는 자료는 드뭅니다.
2. **CDA + FDTD self-contained 비교**: 두 방법을 같은 그림에 놓고 정확
   한 RMS 를 보고하는 연구 보고서/논문이 의외로 많지 않습니다.
3. **재현성**: 1 분 안에 모든 결과 재현, validate_physics.py 한 줄로
   12 검증.

학술 논문이 아닌 *교육 미니 프로젝트* 로서, **"60년 된 방법론을 끝까지
정직하게 정량화 + 검증"** 한 것이 본 작업의 가치입니다.

---

### Q39. 이 모델은 *실제* 메타서페이스에 transferable [트랜스퍼러블, 이식 가능] 합니까?

부분적으로 — 정성적으로는 YES, 정량적으로는 careful YES.

**Transferable parts**:
- 1/P scaling 의 *형태* (β ≈ 1).
- 격자 공명 위치 (P = mλ).
- Smooth gradient 가 random 보다 결합에 강건.

**Not directly transferable**:
- 정확한 β 값 (디자인마다 다름).
- |Δφ| 의 amplitude (Lorentz parameter 의존).
- 3D vector 효과 (TE/TM 모드 결합).

**실용적 응용**:
- Metalens designer 가 자기 시스템에서 *작은 N* 의 CDA 시뮬을 한 번
  해서 본인의 β 를 측정 → 1/P 형태로 전체 디자인 보정.
- 우리가 만든 코드를 그대로 사용 가능 (open source).

---

### Q40. Slide 8 Result E 에서 P_sca / P_ext residual 이 [0, 1] 을 벗어남 — 이건 우리 결과의 한계 아닌가요?

명확한 *모델의 한계* 이고 정직하게 보고합니다.

원인은 **bare Lorentzian α 가 optical theorem 의 lower bound 를
만족시키지 않기 때문**. 즉:

- σ_ext = (k₀) Im(α) 인데
- σ_sca = (k₀³ / 6π) |α|² 이 σ_ext 보다 클 수 있음
- 즉 σ_abs = σ_ext − σ_sca 가 음수가 됨

이를 고치려면 **radiation-reaction correction**:
1/α_correct = 1/α_static − i k₀²/4 (2D).

이 보정을 추가하면 σ_abs > 0 이 자동 보장되며, residual 이 [0, 1] 안에
들어옵니다. 본 연구에선 보정을 생략 (limitation §7) 했고, 그래도 *scaling
law* 인 β 값에는 영향이 미미함을 확인.

향후 작업: radiation-corrected α 로 다시 돌려서 v7 검증을 strict 한
[0, 1] 안으로 만들기.

---

## 12. 발표 운영 — Presentation Management

### Q41. (가장 어려운 질문) 모든 결과가 너무 깔끔해 보입니다. 실패한 실험은 없었나요?

좋은 질문입니다. 실제 과정에서 여러 번 실패하고 수정했습니다.

1. **초기 FDTD 셋업 (Slide 9)**: PlaneWave 의 polarization 을 잘못 설정해
   E_z 가 아닌 E_x 가 생성됨 → 첫 sweep 결과가 모두 0. PML 위치도
   너무 가까워 source 가 즉시 흡수됨 → 디버깅 4 회 후 수정.
2. **초기 part_E_energy_budget**: P_abs 부호가 반대로 들어가서 ratio
   가 > 1 → validate_physics.py 의 v7 FAIL 로 발견. 수정 후 [-0.3,
   0.5] 로 줄어듦.
3. **Wood anomaly 처리**: 처음에는 P = 1 λ 까지 평탄한 power law 가
   나올 줄 예상. 실제로는 27° peak. 처음에는 코드 버그로 의심했지만
   결국 진짜 물리임을 FDTD 로 확인.

이 과정을 통해 *언제 무엇을 의심해야 하는지* 의 감을 얻었습니다.

---

### Q42. AI 도구를 사용했나요? 사용했다면 어떻게 검증했습니까?

코드 작성과 텍스트 정리에 LLM 을 보조 도구로 사용했습니다. 단:

1. **모든 식과 알고리즘은 본인이 검증**: 10 개 verification test 가
   바로 그 검증 도구. 솔버가 옳다는 것을 *AI 의 말이 아니라 정량적
   결과로* 확인했습니다.
2. **FDTD 시뮬레이션 결과는 본인이 launch + 해석**: AI 가 결과를
   만들 수 없는 영역.
3. **물리적 해석**: F-dependence, Wood anomaly 의미, 격자합 1/P
   거동 등은 본인이 논리적으로 도출.

학교 정책상 보조 도구 사용은 *결과의 정확성을 본인이 보장* 한다는
조건에서 허용됩니다. 본 프로젝트의 12 / 12 PASS validation 이 그 보장
의 근거입니다.

---

### Q43. Track A 와 B 중 왜 A 를 선택했나요? 자체 평가는?

**Track A (build from scratch [빌드 프롬 스크래치])** 를 선택한 이유:

1. 학습 가치: 솔버 자체를 손으로 짜는 경험.
2. 자유도: 어떤 메타 원자 α, 어떤 배열, 어떤 결합 모드든 직접 다룰 수
   있는 framework.
3. 외부 의존성 최소: numpy + scipy 만으로 모두 처리.

**자체 평가**:
- 잘된 점: 12 / 12 validation 통과, FDTD 와 정량 비교, reliability
  분석까지 완성.
- 개선 여지: 3D vector CDA 미구현, radiation reaction 미포함.

Track B (use existing solver [유즈 이그지스팅 솔버]) 였다면 RCWA 또는
Lumerical 결과를 가져왔겠지만, 본 연구의 *결합 분석* 측면에서는 직접
짠 CDA 가 더 적합했습니다.

---

### Q44. 본 프로젝트에서 가장 자랑스러운 부분과 가장 후회되는 부분?

**자랑스러운 부분**:
- FDTD cross-validation 까지 *self-contained* 로 완성한 것.
- validate_physics.py 한 명령으로 12 개 검증 자동 실행.
- 모든 결과가 GitHub 에 오픈, 1 분 안에 재현 가능.

**후회되는 부분**:
- 3D vector CDA 까지 못 간 것 (시간 제약). 다음 단계.
- radiation-reaction correction 을 결과에 반영하지 못한 것 (v7 의
  한계).
- random α 시뮬 seed 수가 80 개 → 더 늘렸으면 90 % band 정밀도가
  올라갔을 것 (계산 비용 5 분 정도 추가).

---

### Q45. 이 결과를 어디에 publish 할 수 있을까요?

*학술적* publish 는 어렵습니다 (CDA + FDTD 비교 자체는 well-established).
다만 다음 활용 가능:

1. **Education resource**: 학생 / 신입 연구자가 결합 분석을 시작할
   때의 *재현 가능한 starting point*.
2. **Open source tool**: 누구나 fork 해서 자기 시스템에 적용 가능.
3. **Blog post / arXiv tutorial**: 학술지가 아니더라도 widely-read
   tutorial 로 가치 있음.

본 프로젝트의 가치는 *학술적 새로움* 보다 *완성도 + 재현성* 에 있습니다.

---

### Q46. 마지막 — 본 연구에서 *교수님께* 가장 듣고 싶은 피드백은 무엇입니까?

세 가지를 듣고 싶습니다.

1. **물리적 해석의 깊이**: 1/P scaling 의 해석을 *2D Hankel asymptote*
   로 충분히 정당화했는지, 아니면 더 깊은 이론적 배경 (예: SOI 메타서페이스
   특정 효과) 이 있는지.
2. **확장 방향의 우선순위**: 3D vector, 기판, multipole — 셋 중 어느
   방향이 *실제 메타서페이스 분야에 가장 영향력 있을지* 의견.
3. **재현성의 한계**: GitHub + 1 분 재현이라는 접근이 *학술적 가치*
   를 만드는 정도, 또는 단순히 학습 결과물에 머무르는지의 평가.

이 피드백을 바탕으로 학기 후 추가 작업 방향을 정하고 싶습니다.

---

## 답변 시 일반 원칙 (안내)

1. **확실한 것 / 추측인 것**을 분명히 구분: "정확히 확인된 결과는
   …", "정량 측정은 없지만 점근적으로 …", "추측이지만 …"
2. **모르는 것**은 솔직히 "모릅니다" — Q&A의 신뢰도를 결정합니다.
3. **숫자**는 외워두기:
   - β = 0.90 ± 0.10
   - P=0.55λ → 5.98°, P=0.85λ → 3.80°, ratio 1.57×
   - FDTD ↔ CDA sub-λ RMS = 2.9°
   - Wood peak: CDA 23°, FDTD 20°
   - +21 % uniform vs non-uniform
   - F sweep β: 1.23 (F=0.5) → 0.46 (F=8)
   - N → ∞ extrapolated y∞ = 6.32°
   - Random α 90 % β band = [0.63, 1.61]
4. **Limitations 슬라이드**에 명시한 한계는 적극적으로 인정.
   "그건 한계로 명시했고, 향후 …"
5. **항상 핵심 메시지로 회귀**:
   "β = 0.90, 1/P scaling, FDTD로 검증, smooth gradient가 robust."
6. **모르는 질문 대처**: "흥미로운 지적입니다. 정확한 답은 모르겠지만
   다음 작업에서 점검할 것입니다." → 정직성과 학습 의지 동시에 표현.
7. **공격적 질문 대처**: "정확한 비판입니다. 그 한계는 §7 에 명시했고
   향후 작업입니다." → 방어 대신 인정 + 전향적 자세.
