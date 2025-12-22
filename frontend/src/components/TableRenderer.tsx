import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface TableRendererProps {
    content: string;
}

const TableRenderer: React.FC<TableRendererProps> = ({ content }) => {
    return (
        <div className="markdown-table-wrapper">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content}
            </ReactMarkdown>
        </div>
    );
};

export default TableRenderer;
