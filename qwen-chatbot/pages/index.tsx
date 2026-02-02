import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // 重定向到聊天页面
    router.push('/chat');
  }, [router]);

  return <div>Redirecting...</div>;
}
