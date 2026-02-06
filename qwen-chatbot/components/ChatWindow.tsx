import React from 'react';
import TypeWriterEffect from './TypeWriterEffect';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { AiOutlineRobot, AiOutlineUser } from 'react-icons/ai';

interface Message {
  role: string;
  content: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

interface ChatWindowProps {
  messages: Message[];
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages }) => {
  return (
    <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
      {messages.length === 0 ? (
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-700 mb-2">Welcome to Qwen Chatbot!</h2>
          <p className="text-gray-500">Ask me anything, and I'll do my best to assist you.</p>
        </div>
      ) : (
        <div className="space-y-4 w-full">
          {messages.map((message, index) => {
            // Find the index of the last assistant message
            const lastAssistantIndex = messages.map((msg, i) => msg.role === 'assistant' ? i : -1).filter(i => i !== -1).pop() ?? -1;
            const isLastAssistant = message.role === 'assistant' && index === lastAssistantIndex;
            
            return (
              <div 
                key={index} 
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm">
                    <AiOutlineRobot className="w-4 h-4" />
                  </div>
                )}
                <div className={`max-w-[80%] ${message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-white text-gray-800'} rounded-2xl px-4 py-3 shadow-sm`}>
                  {message.role === 'assistant' && message.content ? (
                    isLastAssistant ? (
                      <TypeWriterEffect 
                        key={`typewriter-${index}-${message.content.length}`} 
                        text={message.content} 
                        speed={50}
                        className=""
                      />
                    ) : (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    )
                  ) : (
                    message.content
                  )}
                  {message.usage && (
                    <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
                      <small>
                        Tokens: In {message.usage.prompt_tokens} | Out {message.usage.completion_tokens} | Total {message.usage.total_tokens}
                      </small>
                    </div>
                  )}
                </div>
                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white text-sm">
                    <AiOutlineUser className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ChatWindow;