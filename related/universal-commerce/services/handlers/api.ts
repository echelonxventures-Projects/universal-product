import { UCIClientConfig, ApiRequest, ApiResponse } from '../types/api';

export class ApiHandler<TReq, TResp> {
  constructor(
    private path: string,
    private method: string,
    private handler: (req: TReq) => Promise<TResp>
  ) {}

  async handle(request: ApiRequest): Promise<ApiResponse<TResp>> {
    if (request.method !== this.method || request.path !== this.path) {
      return { statusCode: 404, headers: {}, body: { error: 'Not found' } as unknown as TResp };
    }

    try {
      const result = await this.handler(request.body as TReq);
      return { statusCode: 200, headers: { 'Content-Type': 'application/json' }, body: result };
    } catch (err) {
      return { statusCode: 500, headers: {}, body: { error: String(err) } as unknown as TResp };
    }
  }
}

export class ApiRouter {
  private handlers: Map<string, ApiHandler<unknown, unknown>> = new Map();

  get<TReq, TResp>(path: string, handler: (req: TReq) => Promise<TResp>): void {
    this.handlers.set(`GET:${path}`, new ApiHandler(path, 'GET', handler));
  }

  post<TReq, TResp>(path: string, handler: (req: TReq) => Promise<TResp>): void {
    this.handlers.set(`POST:${path}`, new ApiHandler(path, 'POST', handler));
  }

  async route(request: ApiRequest): Promise<ApiResponse<unknown>> {
    const key = `${request.method}:${request.path}`;
    const handler = this.handlers.get(key);
    
    if (!handler) {
      return { statusCode: 404, headers: {}, body: { error: 'Not found' } };
    }

    return handler.handle(request);
  }
}
