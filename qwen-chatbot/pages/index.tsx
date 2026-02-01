import Head from 'next/head';
import { useState, useRef, useEffect } from 'react';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';
import ModelConfigPanel from '../components/ModelConfigPanel';
import ConversationHistoryTable from '../components/ConversationHistoryTable';
import styles from '../styles/Home.module.css';

// 定义对话历史记录的类型
interface ConversationHistory {
  id: number;
  timestamp: string; // 使用字符串格式存储时间戳
  input: string;
  output: string;
  model: string;
  params: {
    temperature: number;
    top_p: number;
    max_tokens: number;
  };
  tokenUsage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  evaluation: string;
}

export default function Home() {
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{role: string, content: string, usage?: {prompt_tokens: number, completion_tokens: number, total_tokens: number}}>>([]);
  
  // LLM参数配置
  const [modelConfig, setModelConfig] = useState({
    model: 'qwen-max', // 使用 qwen-max 作为默认模型，避免404错误
    temperature: 0.7,
    top_p: 0.9,
    max_tokens: 2048,
  });
  
  // 对话历史记录
  const [conversationHistory, setConversationHistory] = useState<ConversationHistory[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 处理评估变更
  const handleEvaluationChange = (id: number, evaluation: string) => {
    setConversationHistory(prev => 
      prev.map(item => 
        item.id === id ? { ...item, evaluation } : item
      )
    );
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
      // 使用流式响应获取实时token使用情况
      const response = await fetch('/api/qwen', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          stream: true, // 使用流式响应
          model: modelConfig.model,
          temperature: modelConfig.temperature,
          top_p: modelConfig.top_p,
          max_tokens: modelConfig.max_tokens,
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
      let assistantMessage: { role: string, content: string, usage?: {prompt_tokens: number, completion_tokens: number, total_tokens: number} } = { role: 'assistant', content: '' };
      
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
              } else if (parsed.usage) {
                // 更新最后一条消息的使用情况
                assistantMessage.usage = parsed.usage;
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
      
      // 在流结束后记录对话历史
      const updatedMessages = [...messages, userMessage, assistantMessage]; // 获取包含最新消息的完整消息列表
      const lastAssistantMessage = updatedMessages[updatedMessages.length - 1]; // 最后一条消息应该是助手的回复
      
      if (lastAssistantMessage && lastAssistantMessage.role === 'assistant') {
        const newHistoryEntry: ConversationHistory = {
          id: Date.now(), // 使用时间戳作为唯一ID
          timestamp: new Date().toISOString(),
          input: inputMessage,
          output: lastAssistantMessage.content,
          model: modelConfig.model,
          params: {
            temperature: modelConfig.temperature,
            top_p: modelConfig.top_p,
            max_tokens: modelConfig.max_tokens,
          },
          tokenUsage: lastAssistantMessage.usage,
          evaluation: '' // 可以让使用者手动填写或系统自动生成
        };
        
        setConversationHistory(prev => [newHistoryEntry, ...prev]); // 添加到历史记录开头
      }
    } catch (error: any) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message || 'An unknown error occurred'}`
      }]);
      
      // 即使出错也记录历史
      const errorMessage = `Error: ${error.message || 'An unknown error occurred'}`;
      const newHistoryEntry: ConversationHistory = {
        id: Date.now(), // 使用时间戳作为唯一ID
        timestamp: new Date().toISOString(),
        input: inputMessage,
        output: errorMessage,
        model: modelConfig.model,
        params: {
          temperature: modelConfig.temperature,
          top_p: modelConfig.top_p,
          max_tokens: modelConfig.max_tokens,
        },
        evaluation: 'Error occurred' // 标记为错误
      };
      
      setConversationHistory(prev => [newHistoryEntry, ...prev]); // 添加到历史记录开头
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
          
          {/* 模型参数配置面板 */}
          <ModelConfigPanel 
            config={modelConfig}
            onUpdateConfig={setModelConfig}
          />
          
          <ChatWindow messages={messages} />
          
          <ChatInput 
            inputMessage={inputMessage}
            setInputMessage={setInputMessage}
            handleSubmit={handleSubmit}
            isLoading={isLoading}
          />
          
          <div ref={messagesEndRef} />
          
          {/* 对话历史记录表格 */}
          <ConversationHistoryTable 
            history={conversationHistory}
            onEvaluationChange={handleEvaluationChange}
          />
        </div>
      </main>
    </div>
  );
}