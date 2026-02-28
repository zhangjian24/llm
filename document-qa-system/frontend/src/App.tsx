import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DocumentUpload from './components/DocumentUpload';
import ChatInterface from './components/ChatInterface';
import { FiDatabase, FiCpu, FiHardDrive, FiActivity } from 'react-icons/fi';
import { healthApi, documentApi } from './services/api';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [systemStats, setSystemStats] = useState<any>(null);
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSystemData();
  }, []);

  const loadSystemData = async () => {
    try {
      setLoading(true);
      const [health, stats] = await Promise.all([
        healthApi.checkHealth(),
        healthApi.getStats()
      ]);
      setHealthStatus(health);
      setSystemStats(stats);
    } catch (error) {
      console.error('加载系统数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return <HomePage stats={systemStats} health={healthStatus} loading={loading} />;
      case 'upload':
        return <DocumentUpload onUploadSuccess={loadSystemData} />;
      case 'chat':
        return <ChatInterface />;
      case 'stats':
        return <StatsPage stats={systemStats} health={healthStatus} />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <HomePage stats={systemStats} health={healthStatus} loading={loading} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      
      <main className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {renderContent()}
        </div>
      </main>
    </div>
  );
};

const HomePage: React.FC<{ stats: any; health: any; loading: boolean }> = ({ stats, health, loading }) => {
  const serviceStatus = health?.services || {};
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '🟢';
      case 'warning': return '🟡';
      case 'error': return '🔴';
      default: return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* 系统概览卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <FiDatabase className="h-8 w-8 text-blue-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">文档总数</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.total_documents || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <FiCpu className="h-8 w-8 text-green-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">系统状态</p>
              <p className={`text-lg font-semibold ${getStatusColor(health?.status || 'unknown')}`}>
                {getStatusIcon(health?.status || 'unknown')} {health?.status || '未知'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <FiHardDrive className="h-8 w-8 text-purple-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">已处理查询</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.total_queries || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <FiActivity className="h-8 w-8 text-orange-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">运行时间</p>
              <p className="text-lg font-semibold text-gray-900">{stats?.uptime || '0天'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 服务状态监控 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">服务状态监控</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(serviceStatus).map(([service, status]) => (
            <div key={service} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium text-gray-700 capitalize">
                {service.replace('_', ' ')}
              </span>
              <span className={`font-medium ${getStatusColor(status as string)}`}>
                {getStatusIcon(status as string)} {(status as string).toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* 快速操作 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">快速开始</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
            <h4 className="font-medium text-gray-900 mb-2">1. 上传文档</h4>
            <p className="text-gray-600 text-sm">上传PDF、TXT、DOCX等格式文档</p>
          </div>
          <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
            <h4 className="font-medium text-gray-900 mb-2">2. 建立索引</h4>
            <p className="text-gray-600 text-sm">系统自动处理文档并建立向量索引</p>
          </div>
          <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
            <h4 className="font-medium text-gray-900 mb-2">3. 智能问答</h4>
            <p className="text-gray-600 text-sm">基于文档内容进行智能问答</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatsPage: React.FC<{ stats: any; health: any }> = ({ stats, health }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">系统统计</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">性能指标</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">内存使用</span>
              <span className="font-medium">{stats?.memory_usage || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">CPU使用率</span>
              <span className="font-medium">N/A</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">磁盘空间</span>
              <span className="font-medium">N/A</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">系统信息</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">版本</span>
              <span className="font-medium">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">最后更新</span>
              <span className="font-medium">N/A</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">运行模式</span>
              <span className="font-medium">Production</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">系统设置</h2>
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-600">系统设置功能正在开发中...</p>
      </div>
    </div>
  );
};

export default App;