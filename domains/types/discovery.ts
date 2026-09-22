export interface Discovery {
  id: string;
  name: string;
  type: 'homepage' | 'category' | 'email' | 'push';
  status: 'active' | 'inactive';
  configuration: Record<string, unknown>;
}

export interface DiscoveryItem {
  id: string;
  type: string;
  position: number;
  data: Record<string, unknown>;
}
