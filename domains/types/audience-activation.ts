export interface AudienceActivation {
  id: string;
  audienceId: string;
  channel: string;
  status: 'pending' | 'active' | 'completed';
  createdAt: string;
  completedAt?: string;
}
