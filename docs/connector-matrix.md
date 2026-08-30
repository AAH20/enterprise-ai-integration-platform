# Enterprise and open-source connector matrix

These are target contracts, not claims of certified vendor partnership or completed production integration.

| Domain | Enterprise target | OSS alternative | Required contract tests |
|---|---|---|---|
| CRM | Salesforce Sales Cloud | SuiteCRM, EspoCRM | create/update account, opportunity webhook, pagination, rate limit, duplicate event |
| ERP | SAP S/4HANA | Odoo, ERPNext | inventory reservation, sales order, reversal, concurrency, stale stock |
| Finance | Oracle Fusion Cloud ERP | ERPNext Accounts, PostgreSQL service | journal request, authorization, reconciliation, duplicate charge |
| Billing | Oracle billing contract | Kill Bill | invoice creation, credit note, tax boundary, retry after lost response |
| Integration gateway | Azure API Management | Apache APISIX, Kong OSS, Envoy Gateway | OpenAPI validation, OAuth/OIDC, quota, transformation, correlation |
| Workflow | Logic Apps / Durable Functions | Temporal, Dapr, Camunda | deterministic replay, timeout, compensation, version migration |
| Messaging | Azure Service Bus / Event Grid | Kafka, Redpanda, RabbitMQ, NATS | ordering, redelivery, DLQ, poison message, schema evolution |
| Identity | Microsoft Entra ID | Keycloak | workload identity, delegated authorization, token expiration |
| Provisioning | Azure Resource Manager | Crossplane, OpenTofu | plan, approval, apply, rollback and drift |

## Oracle scope

- Oracle Fusion Cloud ERP-compatible finance and billing contracts
- Oracle Database modernization boundary
- PostgreSQL-backed OSS finance alternative
- No Oracle credentials, SDKs, licensed software or tenant access in the reference release

## Salesforce scope

- Salesforce-compatible CRM account and opportunity contracts
- SuiteCRM and EspoCRM alternative profile
- Webhook redelivery and API-rate-limit failure fixtures
- No Salesforce org or credentials in the reference release

## SAP scope

- SAP S/4HANA-compatible inventory and sales-order contracts
- Odoo and ERPNext alternative profile
- Inventory-race and order-compensation fixtures
- No SAP system, connector certification or licensed runtime in the reference release
