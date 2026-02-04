import React, { useState } from 'react';
import Sidebar from './Sidebar';
import { FiMenu, FiX } from 'react-icons/fi';

interface LayoutProps {
  children: React.ReactNode;
  showHistoryModal?: boolean;
  onHideHistoryModal?: () => void;
}

const Layout: React.FC<LayoutProps> = ({ children, showHistoryModal, onHideHistoryModal }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      {/* 汉堡菜单按钮 - 当侧边栏收起时显示 */}
      {!sidebarOpen && (
        <button
          className="fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md hover:bg-gray-100 transition-colors"
          onClick={() => setSidebarOpen(true)}
          aria-label="打开侧边栏"
        >
          <FiMenu className="w-6 h-6 text-gray-700" />
        </button>
      )}
      
      <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-0'} flex flex-col`}>
        <div className="p-8 w-full flex-1">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;