export interface RegistryEntry {
  key: string;
  value: unknown;
  version: number;
  metadata: RegistryMetadata;
  createdAt: string;
  updatedAt: string;
}

export interface RegistryMetadata {
  source: string;
  tenantId: string;
  scope: 'global' | 'tenant' | 'local';
  tags: string[];
}

export interface TypedRegistry<T> {
  get(key: string): Promise<T | null>;
  set(key: string, value: T, metadata?: Partial<RegistryMetadata>): Promise<void>;
  delete(key: string): Promise<void>;
  list(pattern?: string): Promise<RegistryEntry[]>;
  watch(key: string, callback: (entry: RegistryEntry | null) => void): () => void;
}

export interface CapabilityRegistry {
  register(capability: Capability): void;
  get(capabilityId: string): Capability | null;
  query(filters: CapabilityQuery): Capability[];
}

export interface Capability {
  id: string;
  name: string;
  version: string;
  status: 'available' | 'deprecated' | 'removed';
  interfaces: string[];
  dependencies: string[];
}
