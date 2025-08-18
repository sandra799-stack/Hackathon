'use client';

import { useState, useRef, useEffect } from 'react';
import { useChatStream, Message } from '@/hooks/useChatStream';
import { Send, MessageCircle, Trash2 } from 'lucide-react';

function ChatBubble({ message }: { message: Message }) {
  return (
    <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          message.isUser
            ? 'bg-blue-500 text-white rounded-br-none'
            : 'bg-gray-100 text-gray-800 rounded-bl-none'
        }`}
        role="article"
        aria-label={`${message.isUser ? 'Your message' : 'AI assistant message'} sent at ${message.timestamp.toLocaleTimeString()}`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        <p className="text-xs mt-1 opacity-70" aria-label="Message timestamp">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
}

function LoadingBubble() {
  return (
    <div className="flex justify-start mb-4">
      <div 
        className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-gray-100 text-gray-800 rounded-bl-none"
        role="status"
        aria-live="polite"
        aria-label="AI assistant is typing"
      >
        <div className="flex space-x-1" aria-hidden="true">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
        <span className="sr-only">AI assistant is typing a response</span>
      </div>
    </div>
  );
}

export default function Home() {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChatStream();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      sendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm" role="banner">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center" aria-hidden="true">
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">AI Chat Assistant</h1>
              <p className="text-sm text-gray-500">Powered by Server-Sent Events</p>
            </div>
          </div>
          
          <button
            onClick={clearMessages}
            className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isLoading}
            aria-label="Clear all messages from chat history"
            title="Clear chat history"
          >
            <Trash2 className="w-4 h-4" aria-hidden="true" />
            <span>Clear</span>
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-6 py-4" role="main">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12" role="region" aria-label="Welcome message">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4" aria-hidden="true">
                <MessageCircle className="w-8 h-8 text-blue-500" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Welcome to AI Chat</h2>
              <p className="text-gray-600 max-w-md">
                Start a conversation with our AI assistant. Type your message below and press Enter to begin!
              </p>
            </div>
          ) : (
            <div className="space-y-4" role="log" aria-live="polite" aria-label="Chat conversation">
              {messages.map((message) => (
                <ChatBubble key={message.id} message={message} />
              ))}
              {isLoading && <LoadingBubble />}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      {error && (
        <div className="px-6 py-2 bg-red-50 border-t border-red-200" role="alert" aria-live="assertive">
          <div className="max-w-4xl mx-auto">
            <p className="text-sm text-red-600" id="error-message">Error: {error}</p>
          </div>
        </div>
      )}

      <footer className="bg-white border-t border-gray-200 px-6 py-4" role="contentinfo">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex space-x-4" role="form" aria-label="Send message form">
            <div className="flex-1">
              <label htmlFor="message-input" className="sr-only">Type your message</label>
              <input
                ref={inputRef}
                id="message-input"
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-black"
                disabled={isLoading}
                aria-describedby={error ? 'error-message' : 'input-help'}
                aria-invalid={error ? 'true' : 'false'}
              />
            </div>
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
              aria-label={isLoading ? 'Sending message...' : 'Send message'}
            >
              <Send className="w-4 h-4" aria-hidden="true" />
              <span>Send</span>
            </button>
          </form>
          <p className="text-xs text-gray-500 mt-2 text-center" id="input-help">
            Press Enter to send • Shift + Enter for new line
          </p>
        </div>
      </footer>
    </div>
  );
}
