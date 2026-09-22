import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { offers } from '../services/api';
import type { Offer } from '../types';

export default function OffersPage() {
  const [items, setItems] = useState<Offer[]>([]);
  const [loading, setLoading] = useState(true);
  const [tenantId] = useState('tenant-123');

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await offers.list(tenantId);
        setItems(data.offers || []);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [tenantId]);

  const statusColors = {
    draft: 'bg-gray-100 text-gray-800',
    active: 'bg-green-100 text-green-800',
    paused: 'bg-yellow-100 text-yellow-800',
    expired: 'bg-red-100 text-red-800',
  };

  return (
    <Layout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Offers</h1>
          <button className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
            + New Offer
          </button>
        </div>

        {loading ? (
          <p>Loading offers...</p>
        ) : items.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500 mb-4">No offers configured</p>
            <button className="bg-purple-600 text-white px-4 py-2 rounded">Create First Offer</button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">Code</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Value</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map(o => (
                  <tr key={o.id} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono">{o.code}</td>
                    <td className="px-4 py-3">{o.name}</td>
                    <td className="px-4 py-3">{o.type}</td>
                    <td className="px-4 py-3">{o.value} {o.currency}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${statusColors[o.status]}`}>
                        {o.status}
                      </span>
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
