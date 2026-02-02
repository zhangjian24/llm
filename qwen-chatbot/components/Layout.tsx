import React, { useState } from 'react';
import Sidebar from './Sidebar';
import styles from '../styles/Layout.module.css';

interface LayoutProps {
  children: React.ReactNode;
  showHistoryModal?: boolean;
  onHideHistoryModal?: () => void;
}

const Layout: React.FC<LayoutProps> = ({ children, showHistoryModal, onHideHistoryModal }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className={styles.layout}>
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className={`${styles.mainContent} ${sidebarOpen ? styles.shifted : ''}`}>
        <div className={styles.contentWrapper}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;