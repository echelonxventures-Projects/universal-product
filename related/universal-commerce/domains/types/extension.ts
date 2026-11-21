export interface PluginRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface ConnectorRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface WorkflowRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface PolicyRegistryConfig {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface CapabilityRegistryConfig {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface AIRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface AgentRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface ThirdPartyExtensions {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}
