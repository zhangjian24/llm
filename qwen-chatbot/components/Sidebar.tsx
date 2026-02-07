import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { AiOutlineMessage, AiOutlineUsergroupAdd } from 'react-icons/ai';

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
      icon: <AiOutlineMessage className="w-5 h-5" />
    },
    { 
      id: 'roles', 
      title: 'AI角色管理', 
      path: '/roles', 
      icon: <AiOutlineUsergroupAdd className="w-5 h-5" />
    }
  ];

  return (
    <div className={`fixed inset-y-0 left-0 w-64 sm:w-72 bg-white shadow-lg transform transition-transform duration-300 ease-in-out z-40 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}>
      <div className="p-4 sm:p-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-lg sm:text-xl font-bold text-gray-800 truncate">Qwen Chatbot</h2>
          {onClose && (
            <button 
              className="text-gray-500 hover:text-gray-700 text-2xl lg:hidden"
              onClick={onClose}
              aria-label="关闭侧边栏"
            >
              ×
            </button>
          )}
        </div>
      </div>
      
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-2 px-3 sm:px-4">
          {menuItems.map((item) => (
            <li key={item.id}>
              <Link 
                href={item.path}
                className={`flex items-center space-x-2 sm:space-x-3 px-3 py-2 sm:px-4 sm:py-3 rounded-lg transition-colors ${router.pathname === item.path ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
              >
                <span className="flex-shrink-0 w-5 h-5">{item.icon}</span>
                <span className="font-medium truncate">{item.title}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      
      <div className="p-3 sm:p-4 border-t border-gray-200">
        <p className="text-xs sm:text-sm text-gray-500 text-center truncate px-2">Powered by Tongyi Qianwen AI</p>
      </div>
    </div>
  );
};

export default Sidebar;