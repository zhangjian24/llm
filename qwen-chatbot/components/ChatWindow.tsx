import React from 'react';
import styles from '../styles/ChatWindow.module.css';

interface Message {
  role: string;
  content: string;
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
                {message.content}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatWindow;