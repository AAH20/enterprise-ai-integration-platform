# Comprehensive KPI framework

FlowForge evaluates whether enterprise integration creates business value rather than merely moving messages. The scorecard contains 25 KPIs across ten categories and distinguishes deterministic replay evidence from modeled economics and synthetic operational observations.

| Category | Executive question | KPIs |
|---|---|---|
| Business | Is the platform protecting and realizing revenue? | revenue realization, exposure, contribution, value-to-cost |
| Reliability | Do workflows finish exactly once? | straight-through processing, duplicates, suppression, compensation |
| Operations | Can failures be restored quickly? | mean time to recovery |
| Delivery | Can teams change safely and quickly? | deployment frequency, change failure, connector lead time |
| Data | Can AI and analytics trust the events? | schema validity, lineage, freshness p95 |
| AI | Do recommendations create accepted value economically? | acceptance, evaluation pass rate, accepted-recommendation cost |
| FinOps | Does consumption improve transaction economics? | transaction cost, operating-cost reduction |
| Customer | Is the promised outcome delivered on time? | on-time outcomes |
| Security | Are privileged and unauthorized actions controlled? | authorization blocks, policy coverage |
| Compliance | Is every material event supported by evidence? | evidence completeness |

## Promotion logic

An aggregate percentage is diagnostic, not an authorization mechanism. A sandbox canary requires at least 80% target attainment plus three non-negotiable gates: zero duplicate business transactions, every observed unauthorized action blocked, and complete evidence for the observed event population.

The fixture deliberately misses several targets and returns `improve-before-canary`. This prevents a polished dashboard from concealing weak revenue realization or data quality.

## Evidence classes

- **Deterministic replay:** calculated from checked-in workflow execution.
- **Modeled synthetic economics:** calculated from disclosed scenario assumptions.
- **Synthetic observation:** illustrative operational telemetry supplied by `kpi_context`.
- **Production measurement:** not present in this release; requires signed telemetry from deployed adapters.

Before a commercial claim, replace synthetic observations with time-bounded production measurements, publish numerator and denominator definitions, document exclusions, and retain the signed scorecard receipt.
