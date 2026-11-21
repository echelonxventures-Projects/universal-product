export interface ApiRequest {
  method: string;
  path: string;
  headers: Record<string, string>;
  body?: unknown;
  query?: Record<string, string>;
}

export interface ApiResponse<T> {
  statusCode: number;
  headers: Record<string, string>;
  body: T;
}

export interface ApiHandler<TReq, TResp> {
  handle(request: ApiRequest): Promise<ApiResponse<TResp>>;
}

export interface ApiGateway {
  register(route: string, handler: ApiHandler<unknown, unknown>): void;
  authenticate(request: ApiRequest): Promise<AuthResult>;
}

export interface AuthResult {
  authenticated: boolean;
  userId?: string;
  tenantId?: string;
  permissions?: string[];
}
