export interface PolicyRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface AuthorityRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface DelegationRegistry {
  id: string;
  delegator: string;
  delegatee: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface CertificationRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface ApprovalRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface ComplianceRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface AuditRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface LifecycleRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface VersionRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}
