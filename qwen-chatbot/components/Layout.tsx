import React, { useState } from 'react';
import Sidebar from './Sidebar';

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
      
      <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-0'} flex flex-col`}>
        <div className="p-8 w-full flex-1">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;