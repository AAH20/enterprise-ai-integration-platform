targetScope = 'resourceGroup'

param suffix string
param location string = resourceGroup().location

@description('Deploy paid integration services only for a deliberate live demonstration. Disabled by default.')
param deployIntegrationServices bool = false

param tags object = {
  workload: 'enterprise-ai-integration-platform'
  evidence: 'synthetic-demo'
  managedBy: 'bicep'
}

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'law-flowforge-${suffix}'
  location: location
  tags: tags
  properties: {
    retentionInDays: 30
    sku: { name: 'PerGB2018' }
  }
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-flowforge-${suffix}'
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
  }
}

resource receipts 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stflowforge${suffix}'
  location: location
  tags: tags
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource serviceBus 'Microsoft.ServiceBus/namespaces@2024-01-01' = if (deployIntegrationServices) {
  name: 'sb-flowforge-${suffix}'
  location: location
  tags: tags
  sku: { name: 'Standard', tier: 'Standard' }
  properties: {
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
  }
}

resource commands 'Microsoft.ServiceBus/namespaces/queues@2024-01-01' = if (deployIntegrationServices) {
  parent: serviceBus
  name: 'order-commands'
  properties: {
    deadLetteringOnMessageExpiration: true
    defaultMessageTimeToLive: 'P1D'
    duplicateDetectionHistoryTimeWindow: 'PT10M'
    requiresDuplicateDetection: true
  }
}

output applicationInsightsId string = insights.id
output receiptStorageId string = receipts.id
output integrationServicesEnabled bool = deployIntegrationServices
