import Head from 'next/head';
import { useState, useRef, useEffect } from 'react';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';
import ModelConfigPanel from '../components/ModelConfigPanel';
import RoleManager from '../components/RoleManager';
import RoleSelector from '../components/RoleSelector';
import { useRoleStorage } from '../components/useRoleStorage';
import { Role } from '../components/RoleManager';
import { ConversationHistory, Message } from '../types';
import HistoryModal from '../components/HistoryModal';
import Layout from '../components/Layout';
import { useAppContext } from '../contexts/AppContext';


export default function ChatPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  
  // 使用全局状态
  const { state, dispatch } = useAppContext();
  
  // 从全局状态获取数据
  const messages = state.messages;
  const inputMessage = state.inputMessage;
  const conversationHistory = state.conversationHistory;
  const selectedRoleId = state.selectedRoleId;
  
  // LLM参数配置
  const [modelConfig, setModelConfig] = useState({
    model: 'qwen-max', // 使用 qwen-max 作为默认模型，避免404错误
    temperature: 0.7,
    top_p: 0.9,
    max_tokens: 2048,
  });
  
  // 使用角色存储Hook
  const {
    roles,
    loading,
    createRole,
    updateRole,
    deleteRole,
    getDefaultRole,
    setDefaultRole
  } = useRoleStorage();
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 初始化默认角色
  useEffect(() => {
    if (!loading && roles.length > 0 && !selectedRoleId) {
      const defaultRole = getDefaultRole();
      if (defaultRole) {
        dispatch({ type: 'SET_SELECTED_ROLE', payload: defaultRole.id });
        setModelConfig(defaultRole.modelConfig);
      } else {
        // 如果没有默认角色，选择第一个角色
        dispatch({ type: 'SET_SELECTED_ROLE', payload: roles[0].id });
        setModelConfig(roles[0].modelConfig);
      }
    }
  }, [roles, loading, selectedRoleId, getDefaultRole]);

  // 处理角色切换
  const handleRoleChange = (roleId: string) => {
    dispatch({ type: 'SET_SELECTED_ROLE', payload: roleId });
    const role = roles.find(r => r.id === roleId);
    if (role) {
      setModelConfig(role.modelConfig);
    }
  };

  // 处理评估变更
  const handleEvaluationChange = (id: number, evaluation: string) => {
    dispatch({ type: 'UPDATE_HISTORY_EVALUATION', payload: { id, evaluation }});
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    // 添加用户消息
    const userMessage = { role: 'user', content: inputMessage };
    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    dispatch({ type: 'SET_INPUT_MESSAGE', payload: '' });
    setIsLoading(true);

    try {
      // 准备消息数组，如果选择了角色并且该角色有系统提示，则在开头添加系统消息
      let messagesToSend = [...messages, userMessage];
      
      if (selectedRoleId) {
        const selectedRole = roles.find(r => r.id === selectedRoleId);
        if (selectedRole && selectedRole.systemPrompt) {
          // 检查是否已经有系统消息，如果没有则添加
          const hasSystemMessage = messages.some(msg => msg.role === 'system');
          if (!hasSystemMessage) {
            messagesToSend = [{ role: 'system', content: selectedRole.systemPrompt }, ...messagesToSend];
          }
        }
      }
      
      // 发送请求到后端 API
      // 使用流式响应获取实时token使用情况
      const response = await fetch('/api/qwen', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messagesToSend,
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
      let assistantMessage: Message = { role: 'assistant', content: '', usage: undefined };
      
      // 在开始流式传输之前，先添加一个空的助手消息到列表
      const initialAssistantMessage: Message = { role: 'assistant', content: '', usage: undefined };
      const initialMessages = [...messages, userMessage, initialAssistantMessage];
      dispatch({ type: 'SET_MESSAGES', payload: initialMessages });

      // 创建一个引用，用于跟踪当前的消息状态
      let currentMessages = [...messages, userMessage, { ...initialAssistantMessage }];
      
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
              if (parsed.content !== undefined && parsed.content !== null) {
                // 更新最后一条消息的内容
                assistantMessage.content += String(parsed.content);
                // 创建一个新的助手消息
                const newAssistantMessage = { ...assistantMessage };
                // 更新当前消息引用
                currentMessages = [...currentMessages.slice(0, -1), newAssistantMessage];
                dispatch({ type: 'SET_MESSAGES', payload: currentMessages });
              } else if (parsed.usage && typeof parsed.usage === 'object') {
                // 更新最后一条消息的使用情况
                assistantMessage.usage = parsed.usage;
                const newAssistantMessage = { ...assistantMessage };
                // 更新当前消息引用
                currentMessages = [...currentMessages.slice(0, -1), newAssistantMessage];
                dispatch({ type: 'SET_MESSAGES', payload: currentMessages });
              }
            } catch (e) {
              // 忽略无法解析的数据行
              console.error('Error parsing data:', e);
            }
          }
        }
      }
      
      // 在流结束后记录对话历史
      const updatedMessages = [...messages, assistantMessage]; // 获取包含最新消息的完整消息列表
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
          tokenUsage: assistantMessage.usage ? {
            prompt_tokens: assistantMessage.usage.prompt_tokens,
            completion_tokens: assistantMessage.usage.completion_tokens,
            total_tokens: assistantMessage.usage.total_tokens
          } : undefined,
          evaluation: '' // 可以让使用者手动填写或系统自动生成
        };
        
        dispatch({ type: 'ADD_TO_HISTORY', payload: newHistoryEntry }); // 添加到历史记录开头
      }
    } catch (error: any) {
      console.error('Error:', error);
      dispatch({ type: 'ADD_MESSAGE', payload: {
        role: 'assistant',
        content: `Error: ${error.message || 'An unknown error occurred'}`
      }});
      
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
        tokenUsage: undefined, // 错误情况下无token使用数据
        evaluation: 'Error occurred' // 标记为错误
      };
      
      dispatch({ type: 'ADD_TO_HISTORY', payload: newHistoryEntry }); // 添加到历史记录开头
    } finally {
      setIsLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-500">加载中...</div>;
  }
  
  return (
    <Layout>
      <div className="space-y-6">
        <Head>
          <title>Qwen Chatbot - 对话</title>
          <meta name="description" content="Chatbot powered by Qwen AI" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <header className="text-center py-6 border-b border-gray-200">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Qwen Chatbot</h1>
          <p className="text-gray-600">Powered by Tongyi Qianwen AI</p>
        </header>
        
        {/* 角色选择器 */}
        <RoleSelector
          roles={roles}
          selectedRoleId={selectedRoleId}
          onSelectRole={handleRoleChange}
        />
        
        {/* 模型参数配置面板 - 当选择角色时禁用 */}
        <ModelConfigPanel 
          config={modelConfig}
          onUpdateConfig={setModelConfig}
          disabled={!!selectedRoleId} // 当选择了角色时，模型配置由角色决定
        />
        
        <ChatWindow messages={messages} />
        
        <ChatInput 
          inputMessage={inputMessage}
          setInputMessage={(value) => dispatch({ type: 'SET_INPUT_MESSAGE', payload: value })}
          handleSubmit={handleSubmit}
          isLoading={isLoading}
        />
        
        <div ref={messagesEndRef} />
        
        <div className="flex justify-center pt-4">
          <button 
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            onClick={() => setShowHistoryModal(true)}
          >
            查看历史
          </button>
        </div>
        
        {/* 对话历史记录模态框 */}
        <HistoryModal
          history={conversationHistory}
          isOpen={showHistoryModal}
          onClose={() => setShowHistoryModal(false)}
          onEvaluationChange={handleEvaluationChange}
        />
      </div>
    </Layout>
  );
}