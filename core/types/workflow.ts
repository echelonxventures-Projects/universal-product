export interface WorkflowDefinition {
  id: string;
  name: string;
  version: string;
  steps: WorkflowStep[];
  triggers: WorkflowTrigger[];
  conditions: WorkflowCondition[];
  timeout: number;
  retry: RetryPolicy;
}

export interface WorkflowStep {
  id: string;
  type: 'task' | 'condition' | 'parallel' | 'sequence' | 'wait';
  action: string;
  parameters: Record<string, unknown>;
  condition?: string;
}

export interface WorkflowTrigger {
  type: 'event' | 'schedule' | 'manual' | 'api';
  config: Record<string, unknown>;
}

export interface WorkflowExecution {
  id: string;
  definitionId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  currentStep: string;
  variables: Record<string, unknown>;
  history: WorkflowHistory[];
}

export interface RetryPolicy {
  maxAttempts: number;
  delay: number;
  backoff?: 'linear' | 'exponential';
}
