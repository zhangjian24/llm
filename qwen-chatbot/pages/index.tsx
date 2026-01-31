import Head from 'next/head';
import { useState, useRef, useEffect } from 'react';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';
import styles from '../styles/Home.module.css';

export default function Home() {
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    // 添加用户消息
    const userMessage = { role: 'user', content: inputMessage };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // 发送请求到后端 API
      const response = await fetch('/api/qwen', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          stream: true, // 使用流式响应
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get response from API');
      }

      // 处理流式响应
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Could not read response body');
      }

      const decoder = new TextDecoder();
      let assistantMessage = { role: 'assistant', content: '' };
      
      // 更新消息列表，添加一个空的助手回复
      setMessages(prev => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6); // 移除 'data: ' 前缀
            
            if (data === '[DONE]') {
              // 流结束
              break;
            }

            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                // 更新最后一条消息的内容
                assistantMessage.content += parsed.content;
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = assistantMessage;
                  return updated;
                });
              }
            } catch (e) {
              // 忽略无法解析的数据行
              console.error('Error parsing data:', e);
            }
          }
        }
      }
    } catch (error: any) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message || 'An unknown error occurred'}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Qwen Chatbot</title>
        <meta name="description" content="Chatbot powered by Qwen AI" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <div className={styles.chatContainer}>
          <header className={styles.header}>
            <h1>Qwen Chatbot</h1>
            <p>Powered by Tongyi Qianwen AI</p>
          </header>
          
          <ChatWindow messages={messages} />
          
          <ChatInput 
            inputMessage={inputMessage}
            setInputMessage={setInputMessage}
            handleSubmit={handleSubmit}
            isLoading={isLoading}
          />
          
          <div ref={messagesEndRef} />
        </div>
      </main>
    </div>
  );
}