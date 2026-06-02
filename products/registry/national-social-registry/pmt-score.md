# PMT Score

## Overview

A **Proxy Means Test (PMT)** is a formula that estimates how vulnerable a household is by combining observable, verifiable characteristics into a single welfare score. Because actual income or consumption is difficult to measure reliably in a national registry — particularly in contexts with large informal economies — PMTs use physical and demographic proxies that field enumerators can observe or verify during a household visit.

This formula produces a score between **0 and 100** for every registered household in the National Social Registry. A lower score means greater vulnerability. Households whose score falls below the eligibility cutoff are flagged for program enrollment consideration.

{% hint style="info" %}
This is a **mock formula** designed for system illustration and testing. A production PMT must be estimated statistically from a nationally representative consumption or expenditure survey using OLS regression, validated against observed poverty rates by region, and reviewed by an independent technical committee before use in program targeting.
{% endhint %}

***

## The formula

```
PMT_score = 39.84
          + 6.50 × dwelling_wall_material
          + 6.10 × drinking_water_source
          − 2.85 × household_size
          − 4.88 × D_female
          − 6.50 × D_elderly
          − 9.76 × D_child
```

**Score range:** 0 (most vulnerable) to 100 (least vulnerable)\
**Eligibility cutoff:** ≤ 40 (placeholder — see [Setting the cutoff](pmt-score.md#setting-the-eligibility-cutoff))

***

## Variables

The formula uses four variables drawn from the data schema. They were selected because each is observable without requiring self-reported income, each varies meaningfully across the welfare distribution, and together they cover four distinct dimensions of deprivation: shelter quality, infrastructure access, demographic pressure, and household composition risk.

### Variable 1 — Wall material (`dwelling_wall_material`)

Wall construction quality is the single strongest observable asset proxy in household surveys. Households with permanent, reinforced materials are substantially better off on average than those relying on temporary organic materials.

| Code | Description               | Vulnerability |
| ---- | ------------------------- | ------------- |
| 1    | Grass, sticks, or mud     | Highest       |
| 2    | Wood planks               |               |
| 3    | Mud bricks or adobe       |               |
| 4    | Stone or burnt brick      |               |
| 5    | Concrete or cement blocks | Lowest        |

**Direction:** higher code = better outcome → positive weight (+6.50 scaled)

***

### Variable 2 — Drinking water source (`drinking_water_source`)

Water source captures both infrastructure access and the indirect cost burden of water collection — a major time and financial drain on poor rural households, falling disproportionately on women and children.

| Code | Description                           | Vulnerability |
| ---- | ------------------------------------- | ------------- |
| 1    | Unprotected well, river, or rainwater | Highest       |
| 2    | Protected well or spring              |               |
| 3    | Public tap or borehole                |               |
| 4    | Piped to yard or plot                 |               |
| 5    | Piped inside the dwelling             | Lowest        |

**Direction:** higher code = better outcome → positive weight (+6.10 scaled)

***

### Variable 3 — Household size (`household_size`)

Household size is used as a **continuous variable** — a raw integer count of members, with no binning or grouping into ranges. Each additional member reduces per-capita consumption and increases vulnerability. The negative weight means every additional member subtracts 2.85 scaled points from the score, regardless of total household size.

**Direction:** more members = greater vulnerability → negative weight (−2.85 per member, scaled)

***

### Variable 4 — Headship type (`headship_type`)

Headship type is treated as a **nominal categorical variable** — the four headship categories (male, female, elderly, child) have no natural numeric order, so they cannot be treated as an ordinal scale. Instead, they are encoded as **dummy variables**.

#### What is a dummy variable?

A dummy variable is a binary indicator that equals 1 if the household belongs to a particular category and 0 if it does not. For a nominal variable with four categories, three dummy variables are created and one category is left out as the **reference category**. The reference category's contribution to the score is zero — it is absorbed into the intercept — and each dummy variable measures how much more (or less) vulnerable that category is compared to the reference.

{% hint style="info" %}
**Why not assign codes 1, 2, 3, 4?** Treating headship as an ordinal scale would imply that the welfare gap between male-headed and female-headed households is identical to the gap between female-headed and elderly-headed. That assumption cannot be justified without data, and it would introduce bias into the scores. Dummy variables allow each category to have its own independently estimated penalty.
{% endhint %}

#### Why male-headed is the reference category

Male-headed households are the **reference** (score contribution = 0) for three reasons.

First, research consistently shows that male-headed households have higher average consumption than female-headed, child-headed, or elderly-headed households. Choosing the least-vulnerable group as the reference is standard practice because it ensures all other dummy penalties are negative, which is intuitive: every other headship type is compared downward from the strongest baseline.

Second, male-headed is the largest category in most registries, making it a stable statistical anchor.

Third, stakeholders can then read any score as: "this household scores X points lower than a male-headed household with identical housing, water access, and size." That framing is concrete and communicable in program communications.

#### Dummy variable coding

| Headship type  | Dummy variable | Raw weight | Scaled weight | Interpretation             |
| -------------- | -------------- | ---------- | ------------- | -------------------------- |
| Male-headed    | — (reference)  | 0.0        | 0.00          | Baseline — no penalty      |
| Female-headed  | `D_female`     | −6.0       | −4.88         | 4.88 pts below male-headed |
| Elderly-headed | `D_elderly`    | −8.0       | −6.50         | 6.50 pts below male-headed |
| Child-headed   | `D_child`      | −12.0      | −9.76         | 9.76 pts below male-headed |

The relative ordering of penalties reflects findings from household welfare surveys: child-headed households — typically orphaned children managing a household without a competent adult — face the most severe deprivation. Elderly-headed households face the next greatest challenge due to reduced earning capacity and higher health costs. Female-headed households face significant but comparatively lesser disadvantage than the other vulnerable headship types, though still substantially more than male-headed.

***

## Intercept derivation and 0–100 rescaling

Without an intercept, the raw weighted sum produces numbers (like −49 or +74) that have no intuitive meaning. The intercept anchors the scale so that the worst possible household scores exactly 0 and the best possible household scores exactly 100.

{% stepper %}
{% step %}
## Step 1 — Find the theoretical minimum

Plug in the worst possible values on every variable: wall=1, water=1, household size=15, child-headed (D\_child=1, all other dummies=0).

```
Raw minimum = 8.0×1 + 7.5×1 + (−3.5)×15 + (−12.0)×1 = −49.0
```
{% endstep %}

{% step %}
## Step 2 — Find the theoretical maximum

Plug in the best possible values: wall=5, water=5, household size=1, male-headed (all dummies=0).

```
Raw maximum = 8.0×5 + 7.5×5 + (−3.5)×1 + 0 = +74.0
```
{% endstep %}

{% step %}
## Step 3 — Calculate the scale factor

The raw range is 74 − (−49) = 123 points. To compress this into 100 points, divide 100 by 123.

```
Scale factor = 100 ÷ 123 = 0.8130
```
{% endstep %}

{% step %}
## Step 4 — Scale every weight

Multiply each raw weight by the scale factor.

| Variable                 | Raw weight | Scale factor | Scaled weight |
| ------------------------ | ---------- | ------------ | ------------- |
| Intercept                | —          | —            | **39.84**     |
| `dwelling_wall_material` | +8.0       | × 0.8130     | **+6.50**     |
| `drinking_water_source`  | +7.5       | × 0.8130     | **+6.10**     |
| `household_size`         | −3.5       | × 0.8130     | **−2.85**     |
| `D_female`               | −6.0       | × 0.8130     | **−4.88**     |
| `D_elderly`              | −8.0       | × 0.8130     | **−6.50**     |
| `D_child`                | −12.0      | × 0.8130     | **−9.76**     |
{% endstep %}

{% step %}
## Step 5 — Calculate the intercept

The intercept shifts the minimum from −49 to exactly 0.

```
Intercept = −(−49.0) × 0.8130 = 39.84
```
{% endstep %}
{% endstepper %}

{% hint style="info" %}
In a real PMT, the intercept is estimated through OLS regression on a nationally representative consumption or expenditure survey. Technically, it is the value of the outcome variable — log consumption per capita — when all predictor variables equal zero. This corresponds to a household with no walls, no water source, zero members, and no headship type: a combination that cannot exist in reality. The intercept is therefore not directly interpretable on its own. Its role is to position the entire regression line correctly relative to the data. Think of it as the formula's anchor — it ensures that when you plug in the actual values of a real household, the predicted score lands in the right place on the scale. Without it, the line would be forced through the origin, distorting every other coefficient in the formula.
{% endhint %}

### Verification

You can verify the formula is correctly scaled by checking the boundary cases:

```
Worst household (wall=1, water=1, size=15, child-headed):
  Score = 39.84 + 6.50×1 + 6.10×1 − 2.85×15 − 9.76 = 0 ✓

Best household (wall=5, water=5, size=1, male-headed):
  Score = 39.84 + 6.50×5 + 6.10×5 − 2.85×1 − 0 = 100 ✓
```

***

## Worked example

Consider two households registered in the system.

**Household A** — Somali region, child-headed, 9 members, grass walls, protected well (water=2):

```
Score = 39.84 + 6.50×1 + 6.10×2 − 2.85×9 − 9.76
      = 39.84 + 6.50 + 12.20 − 25.65 − 9.76
      = 23
```

With a score of 23, this household falls below the cutoff of 40 and would be flagged as eligible.

**Household B** — Amhara region, female-headed, 3 members, mud brick walls (wall=3), piped to yard (water=4):

```
Score = 39.84 + 6.50×3 + 6.10×4 − 2.85×3 − 4.88
      = 39.84 + 19.50 + 24.40 − 8.55 − 4.88
      = 70
```

With a score of 70, this household is above the cutoff and would not be flagged at this threshold. The better housing and water access outweigh the female headship penalty and moderate household size.

This illustrates a key design principle: the PMT reflects **cumulative deprivation**. No single characteristic alone determines eligibility — it is the combination that matters.

***

## Setting the eligibility cutoff

The cutoff of **40** used in this mock formula is a **policy parameter**, not a mathematical one. It does not emerge from the formula itself; it is set separately by the program team based on coverage targets and available budget.

In practice, the cutoff is determined by running the formula against the full registered population, generating the score distribution, and then choosing the percentile that corresponds to the intended coverage rate. For example, if the program aims to cover the poorest 30% of registered households, the cutoff is set at the 30th percentile score from the actual data.

***

## Sample scores

The table below shows eight illustrative households from the registry, ranked from most to least vulnerable.

| Rank | Household | Region      | Wall | Water | Size | Headship       | PMT score | Eligible? |
| ---- | --------- | ----------- | ---- | ----- | ---- | -------------- | --------- | --------- |
| #1   | HH-006    | Somali      | 1    | 2     | 9    | Child-headed   | 23        | Yes       |
| #2   | HH-002    | Afar        | 1    | 1     | 8    | Female-headed  | 25        | Yes       |
| #3   | HH-008    | Benishangul | 2    | 1     | 7    | Child-headed   | 29        | Yes       |
| #4   | HH-004    | Tigray      | 2    | 2     | 6    | Elderly-headed | 41        | No        |
| #5   | HH-003    | Oromia      | 3    | 3     | 5    | Female-headed  | 59        | No        |
| #6   | HH-007    | Amhara      | 3    | 4     | 3    | Female-headed  | 70        | No        |
| #7   | HH-005    | SNNPR       | 4    | 3     | 4    | Male-headed    | 73        | No        |
| #8   | HH-001    | Addis Ababa | 4    | 4     | 3    | Male-headed    | 82        | No        |

***

## Important caveats

**This is a mock formula.** The weights (8.0, 7.5, −3.5, etc.) were assigned manually for illustration purposes. In a production PMT, weights would be estimated from an OLS regression of log consumption per capita against these variables, using a nationally representative consumption survey. The estimated regression coefficients replace the manual weights, and they carry a precise economic interpretation: each coefficient represents the percentage change in per-capita consumption associated with a one-unit improvement in that variable, holding all others constant.

**The variable set is minimal.** Four variables is deliberately small for a mock formula. Production PMTs typically use 10–30 variables spanning housing, assets, land ownership, sanitation, lighting, cooking fuel, and demographic composition. Adding more well-chosen variables generally improves targeting accuracy.

**Headship type weights need empirical grounding.** The relative penalties assigned to female-headed (−6), elderly-headed (−8), and child-headed (−12) are not statistically estimated. In a regression-based PMT, the actual welfare gap between each headship type and the male-headed reference would be measured directly from consumption data, which may reveal different relativities than assumed here.
