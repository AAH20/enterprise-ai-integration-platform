# Transaction-level unit economics

## Core equation

```text
net contribution per completed transaction =
revenue × gross margin
− API and message cost
− workflow compute cost
− AI/model cost
− human exception cost
− expected retry and compensation cost
```

## Required measures

- Cost per initiated, completed and compensated transaction
- Straight-through processing rate
- Human minutes per exception
- Duplicate-delivery suppression rate
- Duplicate business-transaction rate
- Revenue and contribution blocked in failed workflows
- Compensation cost by participant
- Time and cost to onboard a new connector
- Reusable workflow-template utilization
- Net contribution by workflow and adapter profile

## Causal boundary

Modeled operating-cost delta is not realized savings. Production value requires observed labor, platform invoices and an agreed counterfactual. Completed contribution is scenario input and must reconcile to a finance system before executive reporting.
