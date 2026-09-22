import { useState, useEffect } from 'react';
import Layout from '../components/Layout';

export default function SellerDashboard() {
  const [stats, setStats] = useState({ inventory: 0, sales: 0, revenue: 0 });

  useEffect(() => {
    setTimeout(() => {
      setStats({ inventory: 450, sales: 125, revenue: 12450.00 });
    }, 500);
  }, []);

  return (
    <Layout portal="seller">
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Seller Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-600 text-sm">Inventory Items</h3>
            <p className="text-3xl font-bold text-purple-600">{stats.inventory}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-600 text-sm">Total Sales</h3>
            <p className="text-3xl font-bold text-purple-600">{stats.sales}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-600 text-sm">Revenue</h3>
            <p className="text-3xl font-bold text-purple-600">${stats.revenue.toFixed(2)}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Low Stock Items</h2>
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-gray-600">
                <th className="pb-3">SKU</th>
                <th className="pb-3">Name</th>
                <th className="pb-3">Stock</th>
                <th className="pb-3">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="py-3">WIDGET-001</td>
                <td className="py-3">Premium Widget</td>
                <td className="py-3">5</td>
                <td className="py-3"><span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">Low</span></td>
              </tr>
              <tr>
                <td className="py-3">WIDGET-002</td>
                <td className="py-3">Basic Widget</td>
                <td className="py-3">12</td>
                <td className="py-3"><span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs">Warning</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
