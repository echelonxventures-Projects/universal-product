import { Customer } from './customer';

export interface Audience {
  id: string;
  name: string;
  description: string;
  criteria: AudienceCriteria;
  size: number;
  status: 'active' | 'inactive' | 'draft';
  createdAt: string;
  updatedAt: string;
}

export interface AudienceCriteria {
  type: 'rule' | 'segment' | 'export' | 'lookup';
  rules: Rule[];
  segments: string[];
}

export interface Rule {
  field: string;
  operator: 'eq' | 'neq' | 'gte' | 'lte' | 'in' | 'contains';
  value: unknown;
}

export interface CustomerSegment {
  id: string;
  name: string;
  description: string;
  attributes: string[];
  status: 'active' | 'inactive';
}

export interface LookalikeAudience {
  id: string;
  name: string;
  sourceAudienceId: string;
  size: number;
  status: 'active' | 'inactive';
  expansionRate: number;
}
