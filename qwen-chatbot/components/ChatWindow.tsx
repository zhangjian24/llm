import React from 'react';
import TypeWriterEffect from './TypeWriterEffect';
import styles from '../styles/ChatWindow.module.css';

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
    <div className={styles.chatWindow}>
      {messages.length === 0 ? (
        <div className={styles.welcomeMessage}>
          <h2>Welcome to Qwen Chatbot!</h2>
          <p>Ask me anything, and I'll do my best to assist you.</p>
        </div>
      ) : (
        <div className={styles.messagesContainer}>
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`${styles.message} ${message.role === 'user' ? styles.userMessage : styles.assistantMessage}`}
            >
              <div className={styles.avatar}>
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className={styles.content}>
                {message.role === 'assistant' && message.content ? (
                  <TypeWriterEffect 
                    key={`typewriter-${index}-${message.content.length}`} 
                    text={message.content} 
                    speed={50} // 放慢速度，让效果更明显
                    className={styles.assistantContent}
                  />
                ) : (
                  message.content
                )}
                {message.usage && (
                  <div className={styles.tokenUsage}>
                    <small>
                      Tokens: In {message.usage.prompt_tokens} | Out {message.usage.completion_tokens} | Total {message.usage.total_tokens}
                    </small>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatWindow;