import Head from 'next/head';
import { useState } from 'react';
import Layout from '../components/Layout';
import { useAISettings } from '../components/useAISettings';

export default function SettingsPage() {
  const { apiKey, saveApiKey, hasKey } = useAISettings();
  const [inputValue, setInputValue] = useState(apiKey);
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; message: string } | null>(null);

  const handleSave = () => {
    saveApiKey(inputValue);
    setSaved(true);
    setTestResult(null);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleTest = async () => {
    if (!inputValue.trim()) {
      setTestResult({ ok: false, message: '请先填写 API Key' });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const res = await fetch('/api/verify-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey: inputValue }),
      });
      const data = await res.json();
      setTestResult({
        ok: data.success,
        message: data.success ? '连接成功' : data.error || '连接失败',
      });
    } catch {
      setTestResult({ ok: false, message: '网络错误，请检查连接' });
    } finally {
      setTesting(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <Head>
          <title>Qwen Chatbot - 设置</title>
          <meta name="description" content="Qwen Chatbot settings" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <header className="text-center py-6 border-b border-gray-200">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">设置</h1>
          <p className="text-gray-600">配置 AI 服务连接信息</p>
        </header>

        <div className="max-w-lg mx-auto">
          <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <div className="relative">
                <input
                  type={showKey ? 'text' : 'password'}
                  value={inputValue}
                  onChange={(e) => {
                    setInputValue(e.target.value);
                    setTestResult(null);
                  }}
                  placeholder="请输入阿里云百炼 API Key"
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 text-sm"
                >
                  {showKey ? '隐藏' : '显示'}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                从阿里云百炼控制台获取
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                保存配置
              </button>
              <button
                onClick={handleTest}
                disabled={testing}
                className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                  testing
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {testing ? '测试中...' : '测试连接'}
              </button>
            </div>

            {saved && (
              <p className="text-green-600 text-sm font-medium">✓ 配置已保存</p>
            )}

            {testResult && (
              <p
                className={`text-sm font-medium ${
                  testResult.ok ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {testResult.ok ? '✓ ' : '✗ '}
                {testResult.message}
              </p>
            )}

            {hasKey && (
              <p className="text-xs text-gray-400 pt-2 border-t border-gray-100">
                当前已配置 API Key
              </p>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
