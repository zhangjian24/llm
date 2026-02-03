import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import styles from '../styles/Sidebar.module.css';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const router = useRouter();

  // 菜单项配置
  const menuItems = [
    { 
      id: 'chat', 
      title: '对话', 
      path: '/', 
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={styles.icon}>
          <path fillRule="evenodd" d="M4.804 21.644A6.707 6.707 0 006 21.75a6.721 6.721 0 003.583-1.029c.774.182 1.584.279 2.417.279 5.322 0 9.75-3.97 9.75-9 0-5.03-4.428-9-9.75-9s-9.75 3.97-9.75 9c0 2.409 1.025 4.587 2.674 6.192.232.226.277.428.254.543a3.73 3.73 0 01-.814 1.686.75.75 0 00.44 1.223zM8.25 10.875a1.125 1.125 0 100 2.25 1.125 1.125 0 000-2.25zM10.875 12a1.125 1.125 0 112.25 0 1.125 1.125 0 01-2.25 0zm4.875-1.125a1.125 1.125 0 100 2.25 1.125 1.125 0 000-2.25z" clipRule="evenodd" />
        </svg>
      )
    },
    { 
      id: 'roles', 
      title: 'AI角色管理', 
      path: '/roles', 
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={styles.icon}>
          <path fillRule="evenodd" d="M8.25 6.75a3.75 3.75 0 117.5 0 3.75 3.75 0 01-7.5 0zM15.75 9.75a3 3 0 116 0 3 3 0 01-6 0zM2.25 9.75a3 3 0 116 0 3 3 0 01-6 0zM6.31 15.117A6.745 6.745 0 0112 12a6.745 6.745 0 016.709 3.128c.894.047 1.787.138 2.679.284v3.043a3.75 3.75 0 01-4.194 3.746L12 18.75l-3.806 2.208a3.75 3.75 0 01-4.194-3.746V14.199c.894-.146 1.787-.237 2.681-.284z" clipRule="evenodd" />
        </svg>
      )
    }
  ];

  return (
    <div className={`${styles.sidebar} ${isOpen ? styles.open : styles.closed}`}>
      <div className={styles.header}>
        <h2>Qwen Chatbot</h2>
        {onClose && (
          <button className={styles.closeBtn} onClick={onClose}>
            ×
          </button>
        )}
      </div>
      
      <nav className={styles.nav}>
        <ul className={styles.menuList}>
          {menuItems.map((item) => (
            <li key={item.id} className={styles.menuItem}>
              <Link 
                href={item.path}
                className={`${styles.menuLink} ${router.pathname === item.path ? styles.active : ''}`}
              >
                <span className={styles.iconWrapper}>{item.icon}</span>
                <span className={styles.menuText}>{item.title}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      
      <div className={styles.footer}>
        <p>Powered by Tongyi Qianwen AI</p>
      </div>
    </div>
  );
};

export default Sidebar;