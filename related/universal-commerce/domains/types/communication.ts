export interface Communication {
  id: string;
  type: 'email' | 'sms' | 'push' | 'in-app' | 'webhook';
  subject?: string;
  template: string;
  variables: Record<string, unknown>;
  recipients: string[];
  scheduledAt?: string;
  status: 'scheduled' | 'sent' | 'delivered' | 'failed';
  sentAt?: string;
  deliveredAt?: string;
  createdAt: string;
}

export interface CommunicationTemplate {
  id: string;
  name: string;
  type: string;
  subject: string;
  body: string;
  variables: string[];
  status: 'active' | 'inactive';
}

export interface CommunicationPreference {
  customerId: string;
  email: boolean;
  sms: boolean;
  push: boolean;
  inApp: boolean;
  unsubscribeAll: boolean;
  updatedAt: string;
}

export interface CommunicationChannel {
  id: string;
  type: string;
  provider: string;
  status: 'active' | 'inactive';
  configuration: Record<string, string>;
}
