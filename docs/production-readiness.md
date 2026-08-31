# Production acceptance

FlowForge implements a persistent revenue-event control plane, but a customer installation becomes production-ready only after its environment passes acceptance.

- Replace reference SQLite with managed PostgreSQL or Cosmos DB plus transactional outbox for multi-replica operation.
- Replace the reference bearer token with Entra workload identity/OIDC and source-specific authorization.
- Contract-test each Salesforce, SAP, Oracle, Dynamics, payment and banking adapter against an authorized sandbox.
- Establish schema evolution, replay, poison-message and dead-letter policies.
- Prove idempotency during lost acknowledgements, duplicate delivery and concurrent processing.
- Reconcile every automated action against the source-of-record financial ledger.
- Exercise regional failure, backup restore, RTO/RPO and rollback.
- Sign images and schemas, generate SBOMs and enforce admission policy.
- Connect metrics, logs and traces to owned alerts and on-call operations.
- Require business approval for price, credit, accounting, payment and revenue-recognition actions.

The repository’s synthetic economics and adapters are never customer revenue evidence. Real recovery claims require before/after ledger reconciliation approved by finance.
