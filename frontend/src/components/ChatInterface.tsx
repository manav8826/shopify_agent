import React, { useState, useEffect, useRef } from 'react';
import { Send, Terminal, Loader, Menu } from 'lucide-react';
import { toast, Toaster } from 'react-hot-toast';
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
    // const [error, setError] = useState<string | null>(null); // Replaced by toast
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
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
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const uiMessages: Message[] = history.data.map((h: any) => ({
                id: h.timestamp || Date.now().toString() + Math.random(),
                role: h.role,
                content: h.content
            }));
            setMessages(uiMessages);
        } catch (err) {
            console.error("Failed to load history", err);
            toast.error("Failed to load history");
        }
    };

    const handleStartSession = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!storeUrl) return;

        setLoading(true);
        try {
            const response = await api.createSession(storeUrl);
            const newSid = response.data.session_id;

            setSessionId(newSid);
            localStorage.setItem('shopify_session_id', newSid);
            localStorage.setItem('shopify_store_url', storeUrl);

            setMessages([{
                id: 'init',
                role: 'assistant',
                content: `Connected to ${storeUrl}. I'm ready to analyze your shopify data. How can I help you?`
            }]);
            toast.success('Connected to store!');
        } catch (err) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const msg = err instanceof Error ? err.message : 'Failed to create session';
            toast.error(msg);
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
        setIsSidebarOpen(false);
    };

    const handleNewChat = () => {
        setSessionId(null);
        setStoreUrl('');
        setMessages([]);
        localStorage.removeItem('shopify_session_id');
        localStorage.removeItem('shopify_store_url');
        setIsSidebarOpen(false);
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

        try {
            const response = await api.chat(sessionId, userMsg.content);
            const agentMsgText = response.data.message;
            const agentMsgId = Date.now().toString();

            setMessages(prev => [...prev, {
                id: agentMsgId,
                role: 'assistant',
                content: agentMsgText
            }]);

        } catch (err) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
            toast.error(errorMessage);
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
                    isOpen={isSidebarOpen}
                    onClose={() => setIsSidebarOpen(false)}
                />

                <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                    <div className="mobile-header mobile-only" style={{ width: '100%', padding: '1rem', display: 'flex', justifyContent: 'flex-start' }}>
                        <button onClick={() => setIsSidebarOpen(true)} style={{ background: 'none', color: 'var(--text-primary)', padding: 0 }}>
                            <Menu />
                        </button>
                    </div>

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
                            <button type="submit" disabled={loading}>
                                {loading ? <Loader className="animate-spin" size={20} /> : 'Start Session'}
                            </button>
                        </form>
                    </div>
                </div>
                <Toaster position="top-center" toastOptions={{
                    style: {
                        background: '#334155',
                        color: '#fff',
                    },
                }} />
            </div>
        );
    }

    return (
        <div style={{ display: 'flex', height: '100vh', width: '100%', backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
            <SessionSidebar
                currentSessionId={sessionId}
                onSelectSession={handleSwitchSession}
                onNewChat={handleNewChat}
                isOpen={isSidebarOpen}
                onClose={() => setIsSidebarOpen(false)}
            />

            <div className="main-content" style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', position: 'relative' }}>
                {/* Header */}
                <header style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '1rem',
                    borderBottom: '1px solid var(--border-color)',
                    backgroundColor: 'var(--bg-primary)',
                    zIndex: 10
                }}>
                    <button
                        className="mobile-only"
                        onClick={() => setIsSidebarOpen(true)}
                        style={{ background: 'none', padding: 0, color: 'var(--text-primary)', display: 'none' }}
                    >
                        <Menu size={24} />
                    </button>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <Terminal color="var(--accent-color)" />
                        <span style={{ fontWeight: 600 }}>Shopify Analyst</span>
                        <span style={{
                            display: 'flex', alignItems: 'center', gap: '0.25rem',
                            fontSize: '0.75rem', color: '#22c55e',
                            backgroundColor: 'rgba(34, 197, 94, 0.1)', padding: '0.25rem 0.5rem', borderRadius: '999px',
                            marginLeft: '0.5rem'
                        }}>
                            <span style={{ width: '6px', height: '6px', backgroundColor: '#22c55e', borderRadius: '50%' }}></span>
                            Connected
                        </span>
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <span>{storeUrl.replace('https://', '').replace('.myshopify.com', '')}</span>
                        <button
                            onClick={handleNewChat}
                            style={{
                                padding: '0.25rem 0.75rem', fontSize: '0.75rem',
                                backgroundColor: 'transparent', border: '1px solid var(--border-color)',
                                color: 'var(--text-secondary)',
                                cursor: 'pointer',
                                borderRadius: '4px'
                            }}
                        >
                            Change Store
                        </button>
                    </div>
                </header>

                <Toaster position="top-center" toastOptions={{
                    style: {
                        background: '#334155',
                        color: '#fff',
                    },
                }} />

                {/* Messages Area */}
                <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
                    <div className="container" style={{ flex: 1, padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '900px', margin: '0 auto', width: '100%' }}>
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
                                    className="message-bubble"
                                    style={{
                                        backgroundColor: msg.role === 'user' ? 'var(--user-msg-bg)' : 'var(--agent-msg-bg)',
                                        color: 'var(--text-primary)',
                                        padding: '1rem',
                                        borderRadius: '12px',
                                        borderBottomRightRadius: msg.role === 'user' ? '2px' : '12px',
                                        borderBottomLeftRadius: msg.role === 'assistant' ? '2px' : '12px',
                                        lineHeight: 1.5,
                                        width: '100%'
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
                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem', padding: '0 1rem', marginLeft: '0.5rem' }}>
                                <div className="typing-dot"></div>
                                <div className="typing-dot"></div>
                                <div className="typing-dot"></div>
                                <span style={{ marginLeft: '0.5rem', opacity: 0.8 }}>Analyzing your data...</span>
                            </div>
                        )}
                        <div ref={messagesEndRef} style={{ height: '1px' }} />
                    </div>
                </div>

                {/* Input Area */}
                <div
                    className="glass-panel"
                    style={{
                        borderTop: 'none',
                        padding: '1rem',
                    }}
                >
                    <div style={{ maxWidth: '900px', margin: '0 auto', width: '100%', position: 'relative' }}>
                        <form onSubmit={handleSendMessage}>
                            <div style={{ display: 'flex', gap: '0.75rem' }}>
                                <input
                                    style={{ flex: 1, padding: '1rem', background: 'rgba(30, 41, 59, 0.5)', border: '1px solid rgba(255,255,255,0.05)' }}
                                    type="text"
                                    placeholder="Ask about your orders, products, or revenue..."
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    disabled={loading}
                                />
                                <button
                                    type="submit"
                                    disabled={loading || !inputValue.trim()}
                                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 1.5rem', borderRadius: '8px' }}
                                >
                                    <Send size={24} />
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
