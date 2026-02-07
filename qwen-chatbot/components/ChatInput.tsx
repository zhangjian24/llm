import React from 'react';

interface ChatInputProps {
  inputMessage: string;
  setInputMessage: (message: string) => void;
  handleSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  inputMessage, 
  setInputMessage, 
  handleSubmit,
  isLoading
}) => {
  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white p-4 sticky bottom-0 z-30">
      <div className="flex items-center gap-3 w-full">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="在此输入您的消息..."
          className="flex-grow basis-4/5 border-2 border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none transition-colors min-h-[56px]"
          disabled={isLoading}
          rows={1}
        />
        <button 
          type="submit" 
          className={`flex-shrink-0 px-6 py-3 rounded-lg font-medium transition-colors shadow-md min-w-[80px] ${
            isLoading || !inputMessage.trim() 
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'
          }`}
          disabled={isLoading || !inputMessage.trim()}
        >
          {isLoading ? '发送中...' : '发送'}
        </button>
      </div>
    </form>
  );
};

export default ChatInput;