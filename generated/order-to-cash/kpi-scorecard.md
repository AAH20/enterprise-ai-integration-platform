# FlowForge comprehensive KPI scorecard

**Decision:** `improve-before-canary`  
**Target attainment:** `19/25` (`76.0%`)  
**Evidence:** `deterministic replay plus synthetic observations`

> All business values and observations are synthetic. Replace them with signed production telemetry before commercial claims.

## Business KPIs

| KPI | Value | Target | Result | Evidence |
|---|---:|---:|---|---|
| revenue realization | 52.5788 % | ≥ 90 % | GAP | synthetic replay |
| revenue at risk | 33100 USD | ≤ 5000 USD | GAP | synthetic replay |
| margin at risk | 13136.0 USD | ≤ 2000 USD | GAP | synthetic replay |
| completed contribution | 12009.63 USD | ≥ 10000 USD | PASS | modeled synthetic economics |
| value-to-platform-cost ratio | 21835.6909 ratio | ≥ 100 ratio | PASS | modeled synthetic economics |

## Reliability KPIs

| KPI | Value | Target | Result | Evidence |
|---|---:|---:|---|---|
| straight-through processing | 66.67 % | ≥ 95 % | GAP | deterministic replay |
| duplicate business transactions | 0 count | ≤ 0 count | PASS | deterministic replay |
| duplicate suppression | 100 % | ≥ 100 % | PASS | deterministic replay |
| compensation success | 100 % | ≥ 100 % | PASS | deterministic replay |

## Operations KPIs

| KPI | Value | Target | Result | Evidence |
|---|---:|---:|---|---|
| mean time to recovery | 24.0 minutes | ≤ 30 minutes | PASS | synthetic observation |

## Delivery KPIs

| KPI | Value | Target | Result | Evidence |
|---|---:|---:|---|---|
| deployment frequency | 6.0 per week | ≥ 5 per week | PASS | synthetic observation |
| change failure rate | 8.3333 % | ≤ 10 % | PASS | synthetic observation |
| connector onboarding lead time | 8.0 days | ≤ 10 days | PASS | synthetic observation |

## Data KPIs

| KPI | Value | Target | Result | Evidence |
|---|---:|---:|---|---|
| schema-valid events | 99.8 % | ≥ 99.9 % | GAP | synthetic observation |
| data lineage coverage | 99.0 % | ≥ 99 % | PASS | synthetic observation |
| event freshness p95 | 42.0 seconds | ≤ 60 seconds | PASS | synthetic observation |

## Ai KPIs

| KPI | Value | Target | Result | Evidence |
|---|---:|---:|---|---|
| AI recommendation acceptance | 67.5 % | ≥ 60 % | PASS | synthetic observation |
| AI evaluation pass rate | 96.0 % | ≥ 95 % | PASS | synthetic observation |
| AI cost per accepted recommendation | 0.16 USD | ≤ 0.25 USD | PASS | modeled synthetic cost |

## Finops KPIs

| KPI | Value | Target | Result | Evidence |
|---|---:|---:|---|---|
| cost per unique transaction | 0.09 USD | ≤ 1 USD | PASS | modeled synthetic economics |
| operating cost reduction | 97.8175 % | ≥ 50 % | PASS | modeled synthetic economics |

## Customer KPIs

| KPI | Value | Target | Result | Evidence |
|---|---:|---:|---|---|
| on-time customer outcomes | 83.3333 % | ≥ 95 % | GAP | synthetic observation |

## Security KPIs

| KPI | Value | Target | Result | Evidence |
|---|---:|---:|---|---|
| unauthorized actions blocked | 100.0 % | ≥ 100 % | PASS | synthetic observation |
| policy coverage | 100.0 % | ≥ 100 % | PASS | synthetic observation |

## Compliance KPIs

| KPI | Value | Target | Result | Evidence |
|---|---:|---:|---|---|
| evidence completeness | 100.0 % | ≥ 100 % | PASS | synthetic observation |

## Hard promotion gates

- PASS — `zero_duplicate_business_transactions`
- PASS — `all_unauthorized_actions_blocked`
- PASS — `complete_evidence`

Receipt: `bae662f90d75fd1d7617d1cd295997178b99a750fba3fcc9c006ff14bf89c0a8`
