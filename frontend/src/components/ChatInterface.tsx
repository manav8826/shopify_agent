import React, { useState, useEffect, useRef } from 'react';
import { Send, Terminal, Loader, AlertCircle } from 'lucide-react';
import api from '../api/client';
import TableRenderer from './TableRenderer';
import SessionSidebar from './SessionSidebar';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    isStreaming?: boolean;
}

const ChatInterface: React.FC = () => {
    const [storeUrl, setStoreUrl] = useState('');
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Load session from localStorage on mount
    useEffect(() => {
        const savedSession = localStorage.getItem('shopify_session_id');
        const savedUrl = localStorage.getItem('shopify_store_url');
        if (savedSession && savedUrl) {
            setSessionId(savedSession);
            setStoreUrl(savedUrl);
            fetchHistory(savedSession);
        }
    }, []);

    // Auto-scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const fetchHistory = async (sid: string) => {
        try {
            const history = await api.getHistory(sid);
            // Convert history to UI messages
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const uiMessages: Message[] = history.data.map((h: any) => ({
                id: h.timestamp || Date.now().toString() + Math.random(),
                role: h.role,
                content: h.content
            }));
            setMessages(uiMessages);
        } catch (err) {
            console.error("Failed to load history", err);
            // If failed, likely session deleted or expired. Clear local state.
            // localStorage.removeItem('shopify_session_id');
            // setSessionId(null);
        }
    };

    const handleStartSession = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!storeUrl) return;

        setLoading(true);
        setError(null);
        try {
            const response = await api.createSession(storeUrl);
            const newSid = response.data.session_id;

            setSessionId(newSid);
            localStorage.setItem('shopify_session_id', newSid);
            localStorage.setItem('shopify_store_url', storeUrl);

            // Initial greeting
            setMessages([{
                id: 'init',
                role: 'assistant',
                content: `Connected to ${storeUrl}. I'm ready to analyze your shopify data. How can I help you?`
            }]);
        } catch (err) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            setError(err instanceof Error ? err.message : 'Failed to create session');
        } finally {
            setLoading(false);
        }
    };

    const handleSwitchSession = (sid: string, url: string) => {
        setSessionId(sid);
        setStoreUrl(url);
        localStorage.setItem('shopify_session_id', sid);
        localStorage.setItem('shopify_store_url', url);
        fetchHistory(sid);
    };

    const handleNewChat = () => {
        setSessionId(null);
        setStoreUrl('');
        setMessages([]);
        localStorage.removeItem('shopify_session_id');
        localStorage.removeItem('shopify_store_url');
    };

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputValue.trim() || !sessionId || loading) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue
        };

        setMessages(prev => [...prev, userMsg]);
        setInputValue('');
        setLoading(true);
        setError(null);

        try {
            const response = await api.chat(sessionId, userMsg.content);
            const agentMsgText = response.data.message;

            const agentMsgId = Date.now().toString();

            // Add message
            setMessages(prev => [...prev, {
                id: agentMsgId,
                role: 'assistant',
                content: agentMsgText
            }]);

        } catch (err) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
            setError(errorMessage);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                content: `Error: ${errorMessage}. Please check backend logs.`
            }]);
        } finally {
            setLoading(false);
        }
    };

    if (!sessionId) {
        return (
            <div style={{ display: 'flex', height: '100vh', width: '100%', backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
                <SessionSidebar
                    currentSessionId={sessionId}
                    onSelectSession={handleSwitchSession}
                    onNewChat={handleNewChat}
                />
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <div style={{ width: '100%', maxWidth: '400px', textAlign: 'center', padding: '1rem' }}>
                        <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'center' }}>
                            <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: '50%' }}>
                                <Terminal size={48} color="var(--accent-color)" />
                            </div>
                        </div>
                        <h1 style={{ marginBottom: '0.5rem' }}>Shopify Analyst AI</h1>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
                            Enter your store URL to begin analyzing data.
                        </p>

                        <form onSubmit={handleStartSession} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <input
                                type="url"
                                placeholder="https://your-store.myshopify.com"
                                value={storeUrl}
                                onChange={(e) => setStoreUrl(e.target.value)}
                                required
                                disabled={loading}
                            />
                            {error && (
                                <div style={{ color: '#ef4444', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
                                    <AlertCircle size={16} />
                                    {error}
                                </div>
                            )}
                            <button type="submit" disabled={loading}>
                                {loading ? <Loader className="animate-spin" size={20} /> : 'Start Session'}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div style={{ display: 'flex', height: '100vh', width: '100%', backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
            <SessionSidebar
                currentSessionId={sessionId}
                onSelectSession={handleSwitchSession}
                onNewChat={handleNewChat}
            />

            <div className="container" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '1rem', height: '100vh', maxWidth: 'none' }}>
                {/* Header */}
                <header style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '1rem',
                    paddingBottom: '1rem',
                    borderBottom: '1px solid var(--border-color)'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <Terminal color="var(--accent-color)" />
                        <span style={{ fontWeight: 600 }}>Shopify Analyst</span>
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                        {storeUrl}
                    </div>
                </header>

                {/* Messages Area */}
                <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.5rem', paddingRight: '0.5rem' }}>
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            style={{
                                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                                maxWidth: '85%',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start'
                            }}
                        >
                            <div
                                style={{
                                    fontSize: '0.75rem',
                                    color: 'var(--text-secondary)',
                                    marginBottom: '0.25rem',
                                    marginLeft: msg.role === 'assistant' ? '0.5rem' : 0,
                                    marginRight: msg.role === 'user' ? '0.5rem' : 0
                                }}
                            >
                                {msg.role === 'user' ? 'You' : 'Analyst'}
                            </div>
                            <div
                                style={{
                                    backgroundColor: msg.role === 'user' ? 'var(--user-msg-bg)' : 'var(--agent-msg-bg)',
                                    color: 'var(--text-primary)',
                                    padding: '1rem',
                                    borderRadius: '12px',
                                    borderBottomRightRadius: msg.role === 'user' ? '2px' : '12px',
                                    borderBottomLeftRadius: msg.role === 'assistant' ? '2px' : '12px',
                                    lineHeight: 1.5,
                                    width: '100%' // Allow markdown tables to take space
                                }}
                            >
                                {msg.role === 'assistant' ? (
                                    <TableRenderer content={msg.content} />
                                ) : (
                                    msg.content
                                )}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem', padding: '0 1rem' }}>
                            <Loader className="animate-spin" size={16} />
                            <span>Analyst is thinking...</span>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <form onSubmit={handleSendMessage} style={{ marginTop: '1rem', position: 'relative' }}>
                    {error && (
                        <div style={{ position: 'absolute', top: '-2rem', left: 0, right: 0, textAlign: 'center', color: '#ef4444', fontSize: '0.875rem' }}>
                            {error}
                        </div>
                    )}
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                        <input
                            style={{ flex: 1 }}
                            type="text"
                            placeholder="Ask about your orders, products, or revenue..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={loading || !inputValue.trim()}
                            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                        >
                            <Send size={20} />
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ChatInterface;
