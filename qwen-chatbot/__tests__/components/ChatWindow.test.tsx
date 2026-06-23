import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ChatWindow from '../../components/ChatWindow';

describe('ChatWindow', () => {
  it('renders TypeWriterEffect for assistant messages', () => {
    const messages = [
      {
        id: '1',
        role: 'assistant',
        content: 'Hello, I am Qwen.',
      },
    ];
    render(<ChatWindow messages={messages} isStreaming={true} />);
    
    // This assumes TypeWriterEffect renders something with data-testid="type-writer"
    expect(screen.getByTestId('type-writer')).toBeInTheDocument();
  });
});
