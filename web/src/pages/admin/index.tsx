import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { products, orders, offers } from '../services/api';
import type { Product, Order, Offer } from '../types';

export default function AdminDashboard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [orderCount, setOrderCount] = useState(0);
  const [offerCount, setOfferCount] = useState(0);
  const [activeTab, setActiveTab] = useState('overview');
  const [tenantId] = useState('tenant-123');

  useEffect(() => {
    // Load dashboard data
    const loadData = async () => {
      try {
        const [p, o, f] = await Promise.all([
          products.list(tenantId),
          orders.list(tenantId),
          offers.list(tenantId),
        ]);
        setProducts(p.products || []);
        setOrderCount(o.orders?.length || 0);
        setOfferCount(f.offers?.length || 0);
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      }
    };
    loadData();
  }, [tenantId]);

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">UCII Admin Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <StatCard title="Products" value={products.length} color="blue" />
          <StatCard title="Orders" value={orderCount} color="green" />
          <StatCard title="Offers" value={offerCount} color="purple" />
        </div>

        <div className="flex gap-4 mb-6">
          <button 
            className={`px-4 py-2 rounded ${activeTab === 'overview' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`px-4 py-2 rounded ${activeTab === 'products' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            onClick={() => setActiveTab('products')}
          >
            Products
          </button>
          <button 
            className={`px-4 py-2 rounded ${activeTab === 'offers' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            onClick={() => setActiveTab('offers')}
          >
            Offers
          </button>
        </div>

        {activeTab === 'overview' && <OverviewTab products={products} orderCount={orderCount} />}
        {activeTab === 'products' && <ProductsTab products={products} />}
        {activeTab === 'offers' && <OffersTab />}
      </div>
    </Layout>
  );
}

function StatCard({ title, value, color }: { title: string; value: number; color: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-gray-600 text-sm">{title}</h3>
      <p className={`text-3xl font-bold text-${color}-600`}>{value}</p>
    </div>
  );
}

function OverviewTab({ products, orderCount }: { products: Product[]; orderCount: number }) {
  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Recent Products</h2>
      <table className="w-full bg-white rounded shadow">
        <thead>
          <tr className="bg-gray-50">
            <th className="p-3 text-left">SKU</th>
            <th className="p-3 text-left">Name</th>
            <th className="p-3 text-left">Status</th>
          </tr>
        </thead>
        <tbody>
          {products.slice(0, 5).map(p => (
            <tr key={p.id} className="border-t">
              <td className="p-3">{p.sku}</td>
              <td className="p-3">{p.name}</td>
              <td className="p-3"><span className="px-2 py-1 bg-green-100 rounded text-green-800">{p.status}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ProductsTab({ products }: { products: Product[] }) {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Products</h2>
        <button className="bg-blue-600 text-white px-4 py-2 rounded">+ New Product</button>
      </div>
      <table className="w-full bg-white rounded shadow">
        <thead>
          <tr className="bg-gray-50">
            <th className="p-3 text-left">SKU</th>
            <th className="p-3 text-left">Name</th>
            <th className="p-3 text-left">Status</th>
            <th className="p-3 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map(p => (
            <tr key={p.id} className="border-t">
              <td className="p-3">{p.sku}</td>
              <td className="p-3">{p.name}</td>
              <td className="p-3"><span className="px-2 py-1 bg-green-100 rounded text-green-800">{p.status}</span></td>
              <td className="p-3">
                <button className="text-blue-600 mr-3">Edit</button>
                <button className="text-red-600">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function OffersTab() {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Offers & Promotions</h2>
        <button className="bg-purple-600 text-white px-4 py-2 rounded">+ New Offer</button>
      </div>
      <div className="bg-white rounded shadow p-8 text-center text-gray-500">
        No offers configured yet. Create your first offer to start promotions.
      </div>
    </div>
  );
}
