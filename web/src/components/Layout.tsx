import { useState } from 'react';

interface LayoutProps {
  children: React.ReactNode;
  portal?: 'admin' | 'merchant' | 'seller';
}

export default function Layout({ children, portal = 'admin' }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems = {
    admin: [
      { icon: '📊', label: 'Dashboard', path: '/admin' },
      { icon: '📦', label: 'Products', path: '/admin/products' },
      { icon: '📋', label: 'Orders', path: '/admin/orders' },
      { icon: '🎁', label: 'Offers', path: '/admin/offers' },
      { icon: '📈', label: 'Analytics', path: '/admin/analytics' },
      { icon: '⚙️', label: 'Settings', path: '/admin/settings' },
    ],
    merchant: [
      { icon: '📊', label: 'Dashboard', path: '/merchant' },
      { icon: '📦', label: 'My Products', path: '/merchant/products' },
      { icon: '📋', label: 'Orders', path: '/merchant/orders' },
      { icon: '💰', label: 'Payouts', path: '/merchant/payouts' },
    ],
    seller: [
      { icon: '📊', label: 'Dashboard', path: '/seller' },
      { icon: '📦', label: 'Inventory', path: '/seller/inventory' },
      { icon: '📋', label: 'Sales', path: '/seller/sales' },
    ],
  };

  const items = menuItems[portal];
  const colors = { admin: 'blue', merchant: 'green', seller: 'purple' };
  const color = colors[portal];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-${color}-800 text-white transition-all duration-300`}>
        <div className="p-4">
          <h1 className={`text-xl font-bold ${!sidebarOpen && 'hidden'}`}>UCII {portal}</h1>
          <h1 className="text-xl font-bold">{!sidebarOpen && 'UCII'}</h1>
        </div>
        
        <nav className="mt-6">
          {items.map(item => (
            <a
              key={item.path}
              href={item.path}
              className="flex items-center px-4 py-3 hover:bg-${color}-700 transition-colors"
            >
              <span className="text-2xl">{item.icon}</span>
              <span className={`ml-3 font-medium ${!sidebarOpen && 'hidden'}`}>{item.label}</span>
            </a>
          ))}
        </nav>

        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute right-0 top-1/2 transform -translate-y-1/2 bg-${color}-700 p-2 rounded-full"
        >
          {sidebarOpen ? '‹' : '›'}
        </button>
      </aside>

      {/* Main content */}
      <div className="flex-1 overflow-auto">
        {/* Top bar */}
        <header className="bg-white shadow p-4 flex justify-between items-center">
          <h2 className="text-lg font-semibold">UCII {portal} Portal</h2>
          <div className="flex items-center gap-4">
            <button className="text-gray-600">🔔</button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
              <span className="text-sm">Admin User</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main>{children}</main>
      </div>
    </div>
  );
}
