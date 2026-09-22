import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';

export default function MerchantDashboard() {
  const [stats, setStats] = useState({ products: 0, orders: 0, earnings: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading stats
    setTimeout(() => {
      setStats({ products: 12, orders: 45, earnings: 3450.00 });
      setLoading(false);
    }, 500);
  }, []);

  return (
    <Layout portal="merchant">
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Merchant Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-600 text-sm">My Products</h3>
            <p className="text-3xl font-bold text-green-600">{stats.products}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-600 text-sm">Orders</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.orders}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-600 text-sm">Earnings</h3>
            <p className="text-3xl font-bold text-green-600">${stats.earnings.toFixed(2)}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Recent Orders</h2>
            <div className="space-y-3">
              <div className="flex justify-between p-3 bg-gray-50 rounded">
                <span>ORD-100234</span>
                <span className="text-green-600">$234.50</span>
              </div>
              <div className="flex justify-between p-3 bg-gray-50 rounded">
                <span>ORD-100235</span>
                <span className="text-green-600">$156.75</span>
              </div>
              <div className="flex justify-between p-3 bg-gray-50 rounded">
                <span>ORD-100236</span>
                <span className="text-green-600">$89.00</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">My Products</h2>
            <div className="space-y-3">
              <div className="flex justify-between p-3 bg-gray-50 rounded">
                <span>Premium Widget</span>
                <span className="text-green-600">12 sold</span>
              </div>
              <div className="flex justify-between p-3 bg-gray-50 rounded">
                <span>Basic Widget</span>
                <span className="text-green-600">8 sold</span>
              </div>
              <div className="flex justify-between p-3 bg-gray-50 rounded">
                <span>Deluxe Widget</span>
                <span className="text-green-600">25 sold</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
