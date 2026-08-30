# Durable multi-system order-to-cash integration replay

**Evidence:** `deterministic-synthetic-integration-test`  
**Receipt:** `c34bee5f76414d0155de0cf01fcd5dba1f9aaea38ba3b514f4e2cc94633694ce`  
**Production execution:** `disabled`

## Executive scorecard

- Unique transactions: `6`
- Straight-through processing: `66.67%`
- Duplicate deliveries suppressed: `1`
- Duplicate business transactions: `0`
- Successful compensations: `7`
- Modeled completed contribution: `$12,009.63`
- Modeled transaction-platform cost: `$0.55`

## Workflow outcomes

| Transaction | Status | Steps | Compensations | Cost | Net contribution |
|---|---|---:|---:|---:|---:|
| TX-1001 | completed | 6 | 0 | $0.14 | $4,499.86 |
| TX-1002 | completed | 6 | 0 | $0.17 | $2,572.83 |
| TX-1003 | compensated | 3 | 3 | $0.14 | $-0.15 |
| TX-1004 | completed | 6 | 0 | $0.03 | $1,735.97 |
| TX-1005 | completed | 6 | 0 | $0.03 | $3,200.97 |
| TX-1006 | compensated | 4 | 4 | $0.04 | $-0.04 |
| TX-1001 | duplicate-suppressed | 6 | 0 | $0.14 | $4,499.86 |

## Claim boundary

- No Salesforce, SAP, Oracle, Odoo, ERPNext, SuiteCRM, EspoCRM or cloud tenant was called
- All transactions, failures, revenue, contribution and costs are synthetic inputs
- Adapter names describe target contracts rather than certified vendor integrations
- Modeled contribution and cost deltas are not realized customer revenue or savings
