import React, { useEffect, useState } from 'react';
import { MessageSquare, Trash2, Plus, Clock } from 'lucide-react';
import api from '../api/client';

interface Session {
    id: string;
    store_url: string;
    created_at: string;
    last_active: string;
}

interface SessionSidebarProps {
    currentSessionId: string | null;
    onSelectSession: (sessionId: string, storeUrl: string) => void;
    onNewChat: () => void;
}

const SessionSidebar: React.FC<SessionSidebarProps> = ({ currentSessionId, onSelectSession, onNewChat }) => {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchSessions();
    }, [currentSessionId]); // Refresh list when session changes (e.g. new one created)

    const fetchSessions = async () => {
        try {
            const response = await api.listSessions();
            setSessions(response.data);
        } catch (error) {
            console.error("Failed to fetch sessions", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (e: React.MouseEvent, sessionId: string) => {
        e.stopPropagation(); // Prevent selection
        if (!confirm("Delete this chat?")) return;

        try {
            await api.deleteSession(sessionId);
            setSessions(prev => prev.filter(s => s.id !== sessionId));
            if (sessionId === currentSessionId) {
                onNewChat(); // Reset if deleted current
            }
        } catch (error) {
            console.error("Failed to delete session", error);
        }
    };

    return (
        <div style={{
            width: '260px',
            backgroundColor: 'var(--bg-secondary)',
            borderRight: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            height: '100vh'
        }}>
            {/* Header */}
            <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                <button
                    onClick={onNewChat}
                    style={{
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.5rem',
                        padding: '0.75rem',
                        backgroundColor: 'var(--accent-color)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: 500
                    }}
                >
                    <Plus size={18} />
                    New Analysis
                </button>
            </div>

            {/* List */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
                <h3 style={{
                    fontSize: '0.75rem',
                    textTransform: 'uppercase',
                    color: 'var(--text-secondary)',
                    padding: '0.5rem 0.75rem',
                    margin: 0
                }}>
                    Recent Chats
                </h3>

                {loading ? (
                    <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading...</div>
                ) : sessions.length === 0 ? (
                    <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                        No history yet.
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                        {sessions.map(session => (
                            <div
                                key={session.id}
                                onClick={() => onSelectSession(session.id, session.store_url)}
                                style={{
                                    padding: '0.75rem',
                                    borderRadius: '8px',
                                    cursor: 'pointer',
                                    backgroundColor: session.id === currentSessionId ? 'var(--bg-primary)' : 'transparent',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    fontSize: '0.875rem',
                                    color: session.id === currentSessionId ? 'var(--text-primary)' : 'var(--text-secondary)'
                                }}
                                className="sidebar-item" // Add for hover effect in CSS
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', overflow: 'hidden' }}>
                                    <MessageSquare size={16} />
                                    <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                                        <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                            {session.store_url.replace('https://', '').replace('.myshopify.com', '')}
                                        </span>
                                        <span style={{ fontSize: '0.7rem', opacity: 0.7 }}>
                                            {new Date(session.last_active).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                                <button
                                    onClick={(e) => handleDelete(e, session.id)}
                                    style={{
                                        background: 'none',
                                        border: 'none',
                                        padding: '4px',
                                        cursor: 'pointer',
                                        color: 'var(--text-secondary)',
                                        opacity: 0.6
                                    }}
                                    title="Delete chat"
                                >
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default SessionSidebar;
