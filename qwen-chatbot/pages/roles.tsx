import Head from 'next/head';
import { useState, useEffect } from 'react';
import RoleManager from '../components/RoleManager';
import { useRoleStorage } from '../components/useRoleStorage';
import { Role } from '../components/RoleManager';
import Layout from '../components/Layout';
import styles from '../styles/RolesPage.module.css';

export default function RolesPage() {
  const {
    roles,
    loading,
    createRole,
    updateRole,
    deleteRole,
    getDefaultRole,
    setDefaultRole
  } = useRoleStorage();
  
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
    return <div className={styles.loading}>加载中...</div>;
  }
  
  return (
    <Layout>
      <div className={styles.rolesPage}>
        <Head>
          <title>Qwen Chatbot - AI角色管理</title>
          <meta name="description" content="Manage AI roles for Qwen Chatbot" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <header className={styles.header}>
          <h1>AI角色管理</h1>
          <p>创建和管理不同的AI角色，为不同场景定制AI助手</p>
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