import React, { useEffect, useState } from 'react';
import { MessageSquare, Trash2, Plus, X } from 'lucide-react';
import api from '../api/client';
import { formatDistanceToNow } from 'date-fns';

interface Session {
    id: string;
    store_url: string;
    created_at: string;
    last_active: string;
    preview?: string;
}

interface SessionSidebarProps {
    currentSessionId: string | null;
    onSelectSession: (sessionId: string, storeUrl: string) => void;
    onNewChat: () => void;
    isOpen?: boolean;     // For mobile drawer
    onClose?: () => void; // For mobile drawer
}

const SessionSidebar: React.FC<SessionSidebarProps> = ({ currentSessionId, onSelectSession, onNewChat, isOpen = true, onClose }) => {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchSessions();
    }, [currentSessionId]);

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
        e.stopPropagation();
        if (!confirm("Delete this chat?")) return;

        try {
            await api.deleteSession(sessionId);
            setSessions(prev => prev.filter(s => s.id !== sessionId));
            if (sessionId === currentSessionId) {
                onNewChat();
            }
        } catch (error) {
            console.error("Failed to delete session", error);
        }
    };

    return (
        <>
            {/* Mobile Overlay */}
            <div
                className={`sidebar-overlay ${isOpen ? 'open' : ''}`}
                onClick={onClose}
            />

            <div
                className={`session-sidebar glass-panel ${isOpen ? 'open' : ''}`}
                style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)' }} // Override opaque default
            >
                {/* Header */}
                <div style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>

                    {/* Mobile Close Button */}
                    <div className="mobile-only" style={{ alignSelf: 'flex-end', marginBottom: '-0.5rem' }}>
                        <button onClick={onClose} style={{ background: 'none', padding: '4px', color: 'var(--text-secondary)' }}>
                            <X size={24} />
                        </button>
                    </div>

                    <button
                        onClick={() => {
                            onNewChat();
                            if (onClose) onClose();
                        }}
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
                            fontWeight: 500,
                            boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.3)'
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
                        margin: 0,
                        letterSpacing: '0.05em'
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
                                    onClick={() => {
                                        onSelectSession(session.id, session.store_url);
                                        if (onClose) onClose();
                                    }}
                                    style={{
                                        padding: '0.75rem',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        backgroundColor: session.id === currentSessionId ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                                        border: session.id === currentSessionId ? '1px solid rgba(59, 130, 246, 0.2)' : '1px solid transparent',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between',
                                        fontSize: '0.875rem',
                                        color: session.id === currentSessionId ? 'var(--text-primary)' : 'var(--text-secondary)',
                                        transition: 'all 0.2s ease'
                                    }}
                                    className="sidebar-item"
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', overflow: 'hidden' }}>
                                        <MessageSquare size={16} color={session.id === currentSessionId ? 'var(--accent-color)' : 'currentColor'} />
                                        <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', width: '100%' }}>
                                                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontWeight: 500 }}>
                                                    Analysis #{sessions.length - sessions.indexOf(session)}
                                                </span>
                                                <span style={{ fontSize: '0.65rem', opacity: 0.5, marginLeft: '0.5rem', whiteSpace: 'nowrap' }}>
                                                    {formatDistanceToNow(new Date(session.last_active), { addSuffix: true }).replace('about ', '')}
                                                </span>
                                            </div>
                                            <span style={{ fontSize: '0.75rem', opacity: 0.8, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                {session.preview || session.store_url.replace('https://', '')}
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
        </>
    );
};

export default SessionSidebar;
