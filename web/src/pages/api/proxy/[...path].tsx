// Proxy API requests to backend
export default async function handler(req: any, res: any) {
  const baseUrl = process.env.API_URL || 'http://localhost:3000';
  const targetPath = `/api${req.url || ''}`;
  
  try {
    const response = await fetch(`${baseUrl}${targetPath}`, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': 'tenant-123',
      },
      body: ['POST', 'PUT', 'PATCH'].includes(req.method) ? JSON.stringify(req.body) : undefined,
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (err) {
    res.status(500).json({ error: 'Backend unavailable' });
  }
}
