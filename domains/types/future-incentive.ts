export interface FutureIncentive {
  id: string;
  name: string;
  type: string;
  status: 'concept' | 'development' | 'active';
  createdAt: string;
}
