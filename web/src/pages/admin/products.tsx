import { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { products } from '../../services/api';
import type { Product } from '../../types';

export default function ProductsPage() {
  const [items, setItems] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [tenantId] = useState('tenant-123');

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await products.list(tenantId);
        setItems(data.products || []);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [tenantId]);

  return (
    <Layout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Products</h1>
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            + New Product
          </button>
        </div>

        {loading ? (
          <p>Loading products...</p>
        ) : items.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500 mb-4">No products found</p>
            <button className="bg-blue-600 text-white px-4 py-2 rounded">Create First Product</button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">SKU</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map(p => (
                  <tr key={p.id} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-3">{p.sku}</td>
                    <td className="px-4 py-3">{p.name}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">{p.status}</span>
                    </td>
                    <td className="px-4 py-3">
                      <button className="text-blue-600 hover:underline mr-3">Edit</button>
                      <button className="text-red-600 hover:underline">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
