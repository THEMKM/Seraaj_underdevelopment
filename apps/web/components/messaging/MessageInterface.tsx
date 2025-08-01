"use client";

import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { useWebSocket, Message, Conversation } from '../../contexts/WebSocketContext';
import { useAuth } from '../../contexts/AuthContext';
import { PxButton, PxInput, PxCard, PxBadge } from '../ui';

interface MessageInterfaceProps {
  className?: string;
}

export const MessageInterface: React.FC<MessageInterfaceProps> = ({ className }) => {
  const { t } = useLanguage();
  const { user } = useAuth();
  const {
    conversations,
    activeConversation,
    messages,
    setActiveConversation,
    sendMessage,
    markAsRead,
    typingUsers,
    startTyping,
    stopTyping,
    onlineUsers
  } = useWebSocket();

  const [messageInput, setMessageInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, activeConversation]);

  const handleSendMessage = () => {
    if (!messageInput.trim() || !activeConversation) return;

    sendMessage(activeConversation.id, messageInput.trim());
    setMessageInput('');
    setIsTyping(false);
    stopTyping(activeConversation.id);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMessageInput(e.target.value);
    
    if (!activeConversation) return;

    // Handle typing indicators
    if (!isTyping) {
      setIsTyping(true);
      startTyping(activeConversation.id);
    }

    // Reset typing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      stopTyping(activeConversation.id);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatLastSeen = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffMinutes < 1) return t('messaging.online');
    if (diffMinutes < 60) return t('messaging.lastSeen.minutes', { minutes: diffMinutes });
    if (diffMinutes < 1440) return t('messaging.lastSeen.hours', { hours: Math.floor(diffMinutes / 60) });
    return t('messaging.lastSeen.days', { days: Math.floor(diffMinutes / 1440) });
  };

  const getParticipantInfo = (conversation: Conversation) => {
    // For direct conversations, show the other participant
    if (conversation.type === 'direct') {
      const otherParticipant = conversation.participants.find(p => p.id !== user?.id?.toString());
      return {
        name: otherParticipant?.name || 'Unknown',
        avatar: otherParticipant?.avatar,
        isOnline: otherParticipant ? onlineUsers.includes(otherParticipant.id) : false,
        lastSeen: otherParticipant?.lastSeen
      };
    }
    
    // For group conversations
    return {
      name: conversation.title || `${conversation.participants.length} participants`,
      avatar: conversation.avatar,
      isOnline: conversation.participants.some(p => onlineUsers.includes(p.id)),
      lastSeen: undefined
    };
  };

  const getMessageStatus = (message: Message) => {
    switch (message.status) {
      case 'sending': return '⏳';
      case 'sent': return '✓';
      case 'delivered': return '✓✓';
      case 'read': return '✓✓';
      default: return '';
    }
  };

  const activeMessages = activeConversation ? messages[activeConversation.id] || [] : [];
  const typingInActiveConversation = activeConversation ? typingUsers[activeConversation.id] || [] : [];

  return (
    <div className={`flex h-full ${className}`}>
      {/* Conversations List */}
      <div className="w-80 bg-white dark:bg-dark-surface border-r-2 border-ink dark:border-dark-border flex flex-col">
        <div className="p-4 border-b-2 border-ink dark:border-dark-border">
          <h2 className="text-lg font-pixel text-ink dark:text-white">
            {t('messaging.conversations')}
          </h2>
          <p className="text-sm text-ink dark:text-gray-400">
            {conversations.length} {t('messaging.active')}
          </p>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 ? (
            <div className="p-6 text-center">
              <div className="w-12 h-12 mx-auto mb-3 bg-gray-100 dark:bg-dark-border rounded-lg flex items-center justify-center">
                <span className="text-xl">💬</span>
              </div>
              <p className="text-sm text-ink dark:text-gray-400">
                {t('messaging.noConversations')}
              </p>
            </div>
          ) : (
            conversations.map((conversation) => {
              const participantInfo = getParticipantInfo(conversation);
              const isActive = activeConversation?.id === conversation.id;
              
              return (
                <div
                  key={conversation.id}
                  className={`p-4 border-b border-ink/10 dark:border-dark-border cursor-pointer hover:bg-gray-50 dark:hover:bg-dark-border/50 transition-colors duration-200 ${
                    isActive ? 'bg-primary/10 dark:bg-neon-cyan/10 border-r-2 border-r-primary dark:border-r-neon-cyan' : ''
                  }`}
                  onClick={() => setActiveConversation(conversation.id)}
                >
                  <div className="flex items-start gap-3">
                    {/* Avatar */}
                    <div className="relative flex-shrink-0">
                      <div className="w-10 h-10 bg-electric-teal dark:bg-neon-pink rounded-lg flex items-center justify-center">
                        {participantInfo.avatar ? (
                          <img 
                            src={participantInfo.avatar} 
                            alt={participantInfo.name} 
                            className="w-full h-full rounded-lg object-cover" 
                          />
                        ) : (
                          <span className="text-sm font-pixel text-white">
                            {participantInfo.name.charAt(0).toUpperCase()}
                          </span>
                        )}
                      </div>
                      {participantInfo.isOnline && (
                        <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-dark-surface"></div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-pixel text-sm text-ink dark:text-white truncate">
                          {participantInfo.name}
                        </h3>
                        <div className="flex items-center gap-1">
                          {conversation.unreadCount > 0 && (
                            <PxBadge variant="error" size="sm">
                              {conversation.unreadCount}
                            </PxBadge>
                          )}
                          {conversation.lastMessage && (
                            <span className="text-xs text-ink dark:text-gray-400">
                              {formatTime(conversation.lastMessage.timestamp)}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-ink dark:text-gray-400 truncate">
                          {conversation.lastMessage ? conversation.lastMessage.content : t('messaging.noMessages')}
                        </p>
                        {!participantInfo.isOnline && participantInfo.lastSeen && (
                          <span className="text-xs text-ink dark:text-gray-400">
                            {formatLastSeen(participantInfo.lastSeen)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-white dark:bg-dark-bg">
        {activeConversation ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b-2 border-ink dark:border-dark-border bg-white dark:bg-dark-surface">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {(() => {
                    const participantInfo = getParticipantInfo(activeConversation);
                    return (
                      <>
                        <div className="relative">
                          <div className="w-10 h-10 bg-electric-teal dark:bg-neon-pink rounded-lg flex items-center justify-center">
                            {participantInfo.avatar ? (
                              <img 
                                src={participantInfo.avatar} 
                                alt={participantInfo.name} 
                                className="w-full h-full rounded-lg object-cover" 
                              />
                            ) : (
                              <span className="text-sm font-pixel text-white">
                                {participantInfo.name.charAt(0).toUpperCase()}
                              </span>
                            )}
                          </div>
                          {participantInfo.isOnline && (
                            <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-dark-surface"></div>
                          )}
                        </div>
                        <div>
                          <h2 className="font-pixel text-ink dark:text-white">
                            {participantInfo.name}
                          </h2>
                          <p className="text-xs text-ink dark:text-gray-400">
                            {participantInfo.isOnline 
                              ? t('messaging.online')
                              : participantInfo.lastSeen 
                                ? formatLastSeen(participantInfo.lastSeen)
                                : t('messaging.offline')
                            }
                          </p>
                        </div>
                      </>
                    );
                  })()}
                </div>
                
                <div className="flex gap-2">
                  <PxButton variant="secondary" size="sm">
                    📞 {t('messaging.call')}
                  </PxButton>
                  <PxButton variant="secondary" size="sm">
                    ⋮
                  </PxButton>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {activeMessages.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-dark-border rounded-lg flex items-center justify-center">
                    <span className="text-2xl">👋</span>
                  </div>
                  <h3 className="font-pixel text-ink dark:text-white mb-2">
                    {t('messaging.startConversation')}
                  </h3>
                  <p className="text-sm text-ink dark:text-gray-400">
                    {t('messaging.firstMessage')}
                  </p>
                </div>
              ) : (
                activeMessages.map((message, index) => {
                  const isOwnMessage = message.senderId === user?.id?.toString();
                  const showAvatar = index === 0 || activeMessages[index - 1].senderId !== message.senderId;
                  
                  return (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${isOwnMessage ? 'flex-row-reverse' : 'flex-row'}`}
                    >
                      {/* Avatar */}
                      <div className="flex-shrink-0">
                        {showAvatar && !isOwnMessage ? (
                          <div className="w-8 h-8 bg-electric-teal dark:bg-neon-pink rounded-lg flex items-center justify-center">
                            <span className="text-xs font-pixel text-white">
                              {message.senderName.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        ) : (
                          <div className="w-8"></div>
                        )}
                      </div>

                      {/* Message */}
                      <div className={`max-w-xs lg:max-w-md ${isOwnMessage ? 'text-right' : 'text-left'}`}>
                        {showAvatar && !isOwnMessage && (
                          <p className="text-xs text-ink dark:text-gray-400 mb-1 px-3">
                            {message.senderName}
                          </p>
                        )}
                        
                        <div
                          className={`inline-block px-4 py-2 rounded-lg ${
                            isOwnMessage
                              ? 'bg-primary dark:bg-neon-cyan text-ink dark:text-dark-bg'
                              : 'bg-gray-100 dark:bg-dark-surface text-ink dark:text-white border border-ink/20 dark:border-dark-border'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap break-words">
                            {message.content}
                          </p>
                        </div>
                        
                        <div className={`flex items-center gap-1 mt-1 text-xs text-ink dark:text-gray-400 ${isOwnMessage ? 'justify-end' : 'justify-start'}`}>
                          <span>{formatTime(message.timestamp)}</span>
                          {isOwnMessage && (
                            <span className={message.status === 'read' ? 'text-primary dark:text-neon-cyan' : ''}>
                              {getMessageStatus(message)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
              
              {/* Typing Indicator */}
              {typingInActiveConversation.length > 0 && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 bg-electric-teal dark:bg-neon-pink rounded-lg flex items-center justify-center">
                    <span className="text-xs font-pixel text-white">
                      {typingInActiveConversation[0].charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="bg-gray-100 dark:bg-dark-surface rounded-lg px-4 py-2 border border-ink/20 dark:border-dark-border">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-4 border-t-2 border-ink dark:border-dark-border bg-white dark:bg-dark-surface">
              <div className="flex gap-3 items-end">
                <PxButton variant="secondary" size="sm" className="flex-shrink-0">
                  📎
                </PxButton>
                
                <div className="flex-1">
                  <PxInput
                    value={messageInput}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    placeholder={t('messaging.typeMessage')}
                    className="resize-none"
                  />
                </div>
                
                <PxButton
                  variant="primary"
                  onClick={handleSendMessage}
                  disabled={!messageInput.trim()}
                  className="flex-shrink-0 hover:shadow-px-glow"
                >
                  ➤
                </PxButton>
              </div>
            </div>
          </>
        ) : (
          /* No Conversation Selected */
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-24 h-24 mx-auto mb-6 bg-gray-100 dark:bg-dark-border rounded-lg flex items-center justify-center">
                <span className="text-4xl">💬</span>
              </div>
              <h2 className="text-xl font-pixel text-ink dark:text-white mb-2">
                {t('messaging.selectConversation')}
              </h2>
              <p className="text-ink dark:text-gray-400">
                {t('messaging.selectConversation.desc')}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};