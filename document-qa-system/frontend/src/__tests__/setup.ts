import '@testing-library/jest-dom';

// Mock WebSocket globally
Object.defineProperty(window, 'WebSocket', {
  writable: true,
  value: jest.fn().mockImplementation(() => ({
    send: jest.fn(),
    close: jest.fn(),
    readyState: WebSocket.OPEN,
    onopen: jest.fn(),
    onmessage: jest.fn(),
    onerror: jest.fn(),
    onclose: jest.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});