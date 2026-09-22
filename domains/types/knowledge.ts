export interface KnowledgeGraph {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface OntologyRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface TaxonomyRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface SemanticRegistry {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface TruthEngine {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface InferenceEngine {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface ReasoningEngine {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface RelationshipEngine {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface LineageEngine {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}
