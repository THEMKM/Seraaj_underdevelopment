"use client";

import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import { useLanguage } from './LanguageContext';
import { useAuth } from './AuthContext';

export interface Message {
  id: string;
  conversationId: string;
  senderId: string;
  senderName: string;
  senderAvatar?: string;
  content: string;
  type: 'text' | 'image' | 'file' | 'system';
  timestamp: string;
  status: 'sending' | 'sent' | 'delivered' | 'read';
  replyTo?: string;
}

export interface Conversation {
  id: string;
  participants: ConversationParticipant[];
  lastMessage?: Message;
  unreadCount: number;
  type: 'direct' | 'group' | 'support';
  title?: string;
  avatar?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ConversationParticipant {
  id: string;
  name: string;
  avatar?: string;
  role: 'volunteer' | 'organization' | 'admin';
  isOnline: boolean;
  lastSeen?: string;
}

export interface NotificationMessage {
  id: string;
  type: 'message' | 'application' | 'match' | 'system';
  title: string;
  content: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
  data?: any;
}

interface WebSocketContextType {
  isConnected: boolean;
  conversations: Conversation[];
  activeConversation: Conversation | null;
  messages: Record<string, Message[]>;
  notifications: NotificationMessage[];
  unreadCount: number;
  onlineUsers: string[];
  
  // Connection methods
  connect: (conversationId: string, token: string) => void;
  disconnect: () => void;
  
  // Conversation methods
  setActiveConversation: (conversationId: string | null) => void;
  createConversation: (participantIds: string[], title?: string) => void;
  
  // Message methods
  sendMessage: (conversationId: string, content: string, type?: Message['type']) => void;
  markAsRead: (conversationId: string, messageId?: string) => void;
  
  // Notification methods
  markNotificationAsRead: (notificationId: string) => void;
  clearAllNotifications: () => void;
  
  // Typing indicators
  startTyping: (conversationId: string) => void;
  stopTyping: (conversationId: string) => void;
  typingUsers: Record<string, string[]>;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { t } = useLanguage();
  const { user, isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversationState] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Record<string, Message[]>>({});
  const [notifications, setNotifications] = useState<NotificationMessage[]>([]);
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [typingUsers, setTypingUsers] = useState<Record<string, string[]>>({});
  
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const typingTimeoutRef = useRef<Record<string, NodeJS.Timeout>>({});
  
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const maxReconnectAttempts = 5;

  // Auto-connect when user is authenticated
  useEffect(() => {
    if (isAuthenticated && user && !isConnected) {
      const token = localStorage.getItem('access_token') || '';
      connect('1', token); // Demo connects to conversation 1
    }
  }, [isAuthenticated, user, isConnected]);

  // Mock data for demonstration
  const initializeMockData = () => {
    const currentUserIdStr = user?.id?.toString() || 'user-1';
    const mockConversations: Conversation[] = [
      {
        id: 'conv-1',
        participants: [
          {
            id: currentUserIdStr,
            name: user?.full_name || 'Current User',
            avatar: undefined,
            role: user?.role || 'volunteer',
            isOnline: true
          },
          {
            id: 'org-1',
            name: 'Hope Foundation',
            avatar: undefined,
            role: 'organization',
            isOnline: false,
            lastSeen: '2024-01-22T09:30:00Z'
          }
        ],
        lastMessage: {
          id: 'msg-3',
          conversationId: 'conv-1',
          senderId: 'org-1',
          senderName: 'Hope Foundation',
          content: 'Great! We\'d love to have you join our English tutoring program. When would be a good time for an interview?',
          type: 'text',
          timestamp: '2024-01-22T10:15:00Z',
          status: 'delivered'
        },
        unreadCount: 1,
        type: 'direct',
        isActive: true,
        createdAt: '2024-01-22T09:00:00Z',
        updatedAt: '2024-01-22T10:15:00Z'
      },
      {
        id: 'conv-2',
        participants: [
          {
            id: currentUserIdStr,
            name: user?.full_name || 'Current User',
            avatar: undefined,
            role: user?.role || 'volunteer',
            isOnline: true
          },
          {
            id: 'org-2',
            name: 'Green Lebanon Initiative',
            avatar: undefined,
            role: 'organization',
            isOnline: true
          }
        ],
        lastMessage: {
          id: 'msg-6',
          conversationId: 'conv-2',
          senderId: currentUserIdStr,
          senderName: 'Ahmed Hassan',
          content: 'I have experience with social media campaigns and would love to contribute to your environmental awareness project.',
          type: 'text',
          timestamp: '2024-01-21T16:30:00Z',
          status: 'read'
        },
        unreadCount: 0,
        type: 'direct',
        isActive: true,
        createdAt: '2024-01-21T15:00:00Z',
        updatedAt: '2024-01-21T16:30:00Z'
      }
    ];

    const mockMessages: Record<string, Message[]> = {
      'conv-1': [
        {
          id: 'msg-1',
          conversationId: 'conv-1',
          senderId: currentUserIdStr,
          senderName: 'Ahmed Hassan',
          content: 'Hello! I saw your English tutoring opportunity and I\'m very interested. I have 5+ years of teaching experience.',
          type: 'text',
          timestamp: '2024-01-22T09:00:00Z',
          status: 'read'
        },
        {
          id: 'msg-2',
          conversationId: 'conv-1',
          senderId: 'org-1',
          senderName: 'Hope Foundation',
          content: 'Hi Ahmed! Thank you for your interest. We\'ve reviewed your profile and you seem like a perfect fit for our program.',
          type: 'text',
          timestamp: '2024-01-22T09:30:00Z',
          status: 'read'
        },
        {
          id: 'msg-3',
          conversationId: 'conv-1',
          senderId: 'org-1',
          senderName: 'Hope Foundation',
          content: 'Great! We\'d love to have you join our English tutoring program. When would be a good time for an interview?',
          type: 'text',
          timestamp: '2024-01-22T10:15:00Z',
          status: 'delivered'
        }
      ],
      'conv-2': [
        {
          id: 'msg-4',
          conversationId: 'conv-2',
          senderId: 'org-2',
          senderName: 'Green Lebanon Initiative',
          content: 'Hi! We noticed you applied for our Social Media Manager position. Would you like to discuss the role further?',
          type: 'text',
          timestamp: '2024-01-21T15:00:00Z',
          status: 'read'
        },
        {
          id: 'msg-5',
          conversationId: 'conv-2',
          senderId: currentUserIdStr,
          senderName: 'Ahmed Hassan',
          content: 'Absolutely! I\'m passionate about environmental causes and have experience creating engaging content.',
          type: 'text',
          timestamp: '2024-01-21T15:15:00Z',
          status: 'read'
        },
        {
          id: 'msg-6',
          conversationId: 'conv-2',
          senderId: currentUserIdStr,
          senderName: 'Ahmed Hassan',
          content: 'I have experience with social media campaigns and would love to contribute to your environmental awareness project.',
          type: 'text',
          timestamp: '2024-01-21T16:30:00Z',
          status: 'read'
        }
      ]
    };

    const mockNotifications: NotificationMessage[] = [
      {
        id: 'notif-1',
        type: 'message',
        title: 'New message from Hope Foundation',
        content: 'Great! We\'d love to have you join our English tutoring program...',
        timestamp: '2024-01-22T10:15:00Z',
        read: false,
        actionUrl: '/messages/conv-1'
      },
      {
        id: 'notif-2',
        type: 'application',
        title: 'Application Status Update',
        content: 'Your application for "Community Health Educator" has been reviewed',
        timestamp: '2024-01-22T08:30:00Z',
        read: false,
        actionUrl: '/applications'
      },
      {
        id: 'notif-3',
        type: 'match',
        title: 'New Opportunity Match',
        content: '3 new opportunities match your profile criteria',
        timestamp: '2024-01-21T18:00:00Z',
        read: true,
        actionUrl: '/feed'
      }
    ];

    setConversations(mockConversations);
    setMessages(mockMessages);
    setNotifications(mockNotifications);
    setOnlineUsers([currentUserIdStr, 'org-2']);
  };

  const connect = (conversationId: string, token: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setCurrentUserId(user?.id?.toString() || null);

    try {
      const wsUrl = `${process.env.NEXT_PUBLIC_API_URL || ''}/ws/${conversationId}?token=${token}`;
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setReconnectAttempts(0);
        pingIntervalRef.current = setInterval(() => {
          ws.send(JSON.stringify({ type: 'ping' }));
        }, 30000);
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'new_message') {
          const msg = message.data as Message;
          setMessages(prev => ({
            ...prev,
            [msg.conversationId]: [...(prev[msg.conversationId] || []), msg]
          }));
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
      };
    } catch (err) {
      // Fallback to demo data on failure
      setIsConnected(true);
      initializeMockData();
    }

    const simulateIncomingMessage = () => {
      setTimeout(() => {
        if (Math.random() > 0.7) { // 30% chance of receiving a message
          const newMessage: Message = {
            id: `msg-${Date.now()}`,
            conversationId: 'conv-1',
            senderId: 'org-1',
            senderName: 'Hope Foundation',
            content: 'Looking forward to hearing from you!',
            type: 'text',
            timestamp: new Date().toISOString(),
            status: 'delivered'
          };
          
          setMessages(prev => ({
            ...prev,
            'conv-1': [...(prev['conv-1'] || []), newMessage]
          }));
          
          setConversations(prev => prev.map(conv => 
            conv.id === 'conv-1' 
              ? { ...conv, lastMessage: newMessage, unreadCount: conv.unreadCount + 1, updatedAt: newMessage.timestamp }
              : conv
          ));
        }
        simulateIncomingMessage(); // Continue simulation
      }, 10000 + Math.random() * 20000); // Random interval between 10-30 seconds
    };
    
    simulateIncomingMessage();
  };

  const disconnect = () => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    
    setIsConnected(false);
    setCurrentUserId(null);
  };

  const setActiveConversation = (conversationId: string | null) => {
    const conversation = conversationId ? conversations.find(c => c.id === conversationId) : null;
    setActiveConversationState(conversation || null);
    
    // Mark messages as read when opening conversation
    if (conversationId && conversation) {
      markAsRead(conversationId);
    }
  };

  const createConversation = (participantIds: string[], title?: string) => {
    const newConversation: Conversation = {
      id: `conv-${Date.now()}`,
      participants: participantIds.map(id => ({
        id,
        name: `User ${id}`,
        role: 'volunteer',
        isOnline: false
      })),
      unreadCount: 0,
      type: participantIds.length > 2 ? 'group' : 'direct',
      title,
      isActive: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    setConversations(prev => [newConversation, ...prev]);
    setMessages(prev => ({ ...prev, [newConversation.id]: [] }));
    return newConversation;
  };

  const sendMessage = (conversationId: string, content: string, type: Message['type'] = 'text') => {
    if (!currentUserId) return;

    const newMessage: Message = {
      id: `msg-${Date.now()}`,
      conversationId,
      senderId: currentUserId,
      senderName: 'You',
      content,
      type,
      timestamp: new Date().toISOString(),
      status: 'sending'
    };

    // Add message to state
    setMessages(prev => ({
      ...prev,
      [conversationId]: [...(prev[conversationId] || []), newMessage]
    }));

    // Update conversation
    setConversations(prev => prev.map(conv =>
      conv.id === conversationId
        ? { ...conv, lastMessage: newMessage, updatedAt: newMessage.timestamp }
        : conv
    ));

    // Simulate message sending
    setTimeout(() => {
      setMessages(prev => ({
        ...prev,
        [conversationId]: prev[conversationId]?.map(msg =>
          msg.id === newMessage.id ? { ...msg, status: 'sent' } : msg
        ) || []
      }));
      
      // Simulate delivery after another delay
      setTimeout(() => {
        setMessages(prev => ({
          ...prev,
          [conversationId]: prev[conversationId]?.map(msg =>
            msg.id === newMessage.id ? { ...msg, status: 'delivered' } : msg
          ) || []
        }));
      }, 1000);
    }, 500);
  };

  const markAsRead = (conversationId: string, messageId?: string) => {
    // Update conversation unread count
    setConversations(prev => prev.map(conv =>
      conv.id === conversationId ? { ...conv, unreadCount: 0 } : conv
    ));

    // Mark messages as read
    if (messageId) {
      setMessages(prev => ({
        ...prev,
        [conversationId]: prev[conversationId]?.map(msg =>
          msg.id === messageId ? { ...msg, status: 'read' } : msg
        ) || []
      }));
    } else {
      // Mark all messages as read
      setMessages(prev => ({
        ...prev,
        [conversationId]: prev[conversationId]?.map(msg => ({ ...msg, status: 'read' })) || []
      }));
    }
  };

  const markNotificationAsRead = (notificationId: string) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === notificationId ? { ...notif, read: true } : notif
      )
    );
  };

  const clearAllNotifications = () => {
    setNotifications(prev => prev.map(notif => ({ ...notif, read: true })));
  };

  const startTyping = (conversationId: string) => {
    if (!currentUserId) return;
    
    // In real implementation, send typing indicator to server
    // For demo, we'll simulate others typing
  };

  const stopTyping = (conversationId: string) => {
    if (!currentUserId) return;
    
    // Clear typing timeout
    if (typingTimeoutRef.current[conversationId]) {
      clearTimeout(typingTimeoutRef.current[conversationId]);
      delete typingTimeoutRef.current[conversationId];
    }
  };

  // Calculate total unread count
  const unreadCount = conversations.reduce((total, conv) => total + conv.unreadCount, 0) +
                     notifications.filter(notif => !notif.read).length;

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  const value: WebSocketContextType = {
    isConnected,
    conversations,
    activeConversation,
    messages,
    notifications,
    unreadCount,
    onlineUsers,
    typingUsers,
    connect,
    disconnect,
    setActiveConversation,
    createConversation,
    sendMessage,
    markAsRead,
    markNotificationAsRead,
    clearAllNotifications,
    startTyping,
    stopTyping
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};