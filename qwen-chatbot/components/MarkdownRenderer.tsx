/**
 * MarkdownRenderer - 共享的 Markdown 渲染组件
 *
 * 替换 ChatWindow / TypeWriterEffect 中的内联 ReactMarkdown + remarkGfm + rehypeHighlight 三件套
 * - 统一 a 标签 target="_blank" rel="noopener noreferrer" 安全配置
 * - 减少 4 处重复引入
 */
import { useMemo } from 'react';
import type { AnchorHTMLAttributes } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

interface Props {
  children: string;
  className?: string;
}

export function MarkdownRenderer({ children, className }: Props) {
  const components = useMemo(
    () => ({
      a: ({ ...props }: AnchorHTMLAttributes<HTMLAnchorElement>) => (
        <a {...props} target="_blank" rel="noopener noreferrer" />
      ),
    }),
    [],
  );

  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={components}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
