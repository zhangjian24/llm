import { useState, useCallback } from 'react';

const STORAGE_KEY = 'qwen_chatbot_api_key';

export const getStoredApiKey = (): string => {
  if (typeof window === 'undefined') return '';
  try {
    return localStorage.getItem(STORAGE_KEY) || '';
  } catch {
    return '';
  }
};

export const useAISettings = () => {
  const [apiKey, setApiKey] = useState<string>(getStoredApiKey());

  const saveApiKey = useCallback((key: string) => {
    setApiKey(key);
    try {
      if (key) {
        localStorage.setItem(STORAGE_KEY, key);
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    } catch (error) {
      console.error('Error saving API key:', error);
    }
  }, []);

  const clearApiKey = useCallback(() => {
    setApiKey('');
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Error clearing API key:', error);
    }
  }, []);

  return {
    apiKey,
    setApiKey,
    saveApiKey,
    clearApiKey,
    hasKey: !!apiKey,
  };
};
