import { useState } from 'react';
import Layout from '@/components/Layout';
import { products } from '@/services/api';
import { useRouter } from 'next/router';

export default function CreateProductPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    sku: '',
    name: '',
    description: '',
    status: 'draft' as const,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await products.create({
        ...formData,
        categoryIds: [],
        attributes: {},
        variants: [],
        tenantId: 'tenant-123',
        createdAt: new Date().toISOString(),
      });
      router.push('/admin/products');
    } catch (err) {
      alert('Failed to create product');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Create Product</h1>
        
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">SKU</label>
            <input
              type="text"
              className="border rounded px-3 py-2 w-full"
              value={formData.sku}
              onChange={e => setFormData({ ...formData, sku: e.target.value })}
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Product Name</label>
            <input
              type="text"
              className="border rounded px-3 py-2 w-full"
              value={formData.name}
              onChange={e => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              className="border rounded px-3 py-2 w-full"
              rows={4}
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Status</label>
            <select
              className="border rounded px-3 py-2 w-full"
              value={formData.status}
              onChange={e => setFormData({ ...formData, status: e.target.value as 'draft' | 'active' | 'archived' })}
            >
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="archived">Archived</option>
            </select>
          </div>

          <div className="flex gap-4">
            <button type="submit" disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">
              {loading ? 'Creating...' : 'Create Product'}
            </button>
            <button type="button" onClick={() => router.back()} className="bg-gray-200 px-4 py-2 rounded">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}
