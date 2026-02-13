import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaHome, FaComments, FaUpload, FaGithub } from 'react-icons/fa';

const Navbar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: '文档上传', icon: FaUpload },
    { path: '/chat', label: '问答聊天', icon: FaComments },
  ];

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <FaHome className="text-blue-600 text-xl" />
            <span className="text-xl font-bold text-gray-800">文档问答系统</span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    isActive
                      ? 'text-blue-600 bg-blue-50 border-b-2 border-blue-600'
                      : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                  }`}
                >
                  <Icon className="text-lg" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* GitHub Link */}
          <div className="flex items-center">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-blue-600 transition-colors duration-200"
            >
              <FaGithub className="text-xl" />
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;