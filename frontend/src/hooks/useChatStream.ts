"use client";

import { useState, useCallback } from 'react';

export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export interface UseChatStreamReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  updateLastMessage: (content: string) => void;
  clearMessages: () => void;
}

export function useChatStream(): UseChatStreamReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateLastMessage = useCallback((content: string) => {
    setMessages(prev => {
      if (prev.length === 0) return prev;
      const lastMessage = prev[prev.length - 1];
      if (lastMessage.isUser) return prev;
      
      return [
        ...prev.slice(0, -1),
        { ...lastMessage, content }
      ];
    });
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: message,
      isUser: true,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      if (!response.body) {
        throw new Error('No response body');
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let accumulatedContent = '';
      let assistantMessageAdded = false;
      
      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                switch (data.type) {
                  case 'start':
                     const assistantMessage: Message = {
                       id: (Date.now() + 1).toString(),
                       content: '',
                       isUser: false,
                       timestamp: new Date()
                     };
                    setMessages(prev => [...prev, assistantMessage]);
                    assistantMessageAdded = true;
                    accumulatedContent = '';
                    break;
                    
                  case 'chunk':
                    if (assistantMessageAdded) {
                      if (data.fullText) {
                        updateLastMessage(data.fullText);
                      } else {
                        accumulatedContent += data.content;
                        updateLastMessage(accumulatedContent);
                      }
                    }
                    break;
                    
                  case 'complete':
                    if (assistantMessageAdded) {
                      updateLastMessage(data.content);
                    }
                    setIsLoading(false);
                    return;
                    
                  default:
                    break;
                }
              } catch (parseError) {
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsLoading(false);
      
      setMessages(prev => {
        if (prev.length > 0 && !prev[prev.length - 1].isUser && prev[prev.length - 1].content === '') {
          return prev.slice(0, -1);
        }
        return prev;
      });
    }
  }, [updateLastMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    updateLastMessage,
    clearMessages,
  };
}