import { Customer } from './customer';

export interface CRM {
  customerId: string;
  notes: Note[];
  interactions: Interaction[];
  tasks: Task[];
  opportunities: Opportunity[];
  createdAt: string;
  updatedAt: string;
}

export interface Note {
  id: string;
  text: string;
  author: string;
  createdAt: string;
}

export interface Interaction {
  id: string;
  type: 'call' | 'email' | 'meeting' | 'chat';
  subject: string;
  description: string;
  date: string;
  outcome?: string;
}

export interface Task {
  id: string;
  description: string;
  dueDate: string;
  status: 'pending' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
}

export interface Opportunity {
  id: string;
  name: string;
  value: number;
  stage: string;
  probability: number;
  expectedClose: string;
}
