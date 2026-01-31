import React from 'react';
import styles from '../styles/ChatInput.module.css';

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
    <form onSubmit={handleSubmit} className={styles.chatInputForm}>
      <div className={styles.inputContainer}>
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message here..."
          className={styles.textInput}
          disabled={isLoading}
          rows={1}
        />
        <button 
          type="submit" 
          className={styles.submitButton}
          disabled={isLoading || !inputMessage.trim()}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </form>
  );
};

export default ChatInput;