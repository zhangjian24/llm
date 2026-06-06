import Head from 'next/head';
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useRoleContext } from '../contexts/RoleContext';
import { LoadingState } from '../components/LoadingState';
import Layout from '../components/Layout';

// RoleManager 较大（包含表单 + DEFAULT_ROLES），懒加载
const RoleManager = dynamic(() => import('../components/RoleManager'), { ssr: false });

export default function RolesPage() {
  const { roles, loading, createRole, updateRole, deleteRole, getDefaultRole, setDefaultRole } =
    useRoleContext();

  const [selectedRoleId, setSelectedRoleId] = useState<string | null>(null);

  // 初始化默认角色
  useEffect(() => {
    if (!loading && roles.length > 0 && !selectedRoleId) {
      const defaultRole = getDefaultRole();
      if (defaultRole) {
        setSelectedRoleId(defaultRole.id);
      } else {
        // 如果没有默认角色，选择第一个角色
        setSelectedRoleId(roles[0].id);
      }
    }
  }, [roles, loading, selectedRoleId, getDefaultRole]);

  if (loading) {
    return (
      <Layout>
        <LoadingState />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <Head>
          <title>Qwen Chatbot - AI角色管理</title>
          <meta name="description" content="Manage AI roles for Qwen Chatbot" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <header className="text-center py-6 border-b border-gray-200">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">AI角色管理</h1>
          <p className="text-gray-600">创建和管理不同的AI角色，为不同场景定制AI助手</p>
        </header>

        <RoleManager
          roles={roles}
          onSelectRole={setSelectedRoleId}
          onCreateRole={createRole}
          onUpdateRole={updateRole}
          onDeleteRole={deleteRole}
          setDefaultRole={setDefaultRole}
          selectedRoleId={selectedRoleId}
        />
      </div>
    </Layout>
  );
}
