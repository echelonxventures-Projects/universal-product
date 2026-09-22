export interface IdentityProvider {
  id: string;
  name: string;
  type: 'oauth2' | 'oidc' | 'saml' | 'ldap' | 'local';
  config: Record<string, unknown>;
}

export interface User {
  id: string;
  email: string;
  displayName: string;
  status: 'active' | 'inactive' | 'suspended';
  roles: string[];
  permissions: string[];
  tenantId: string;
  createdAt: string;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  inheritedRoles: string[];
}

export interface AuthorizationContext {
  user: User;
  resource: string;
  action: string;
  environment: Record<string, unknown>;
}

export interface AuthzService {
  check(context: AuthorizationContext): Promise<boolean>;
  checkBatch(contexts: AuthorizationContext[]): Promise<boolean[]>;
  getEffectivePermissions(userId: string): Promise<string[]>;
}
