/**
 * 手动测试前端文档状态更新逻辑
 * 运行方式：node manual-test-document-status.js
 */

// 模拟浏览器环境
global.WebSocket = class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = WebSocket.CONNECTING;
    this.onopen = null;
    this.onmessage = null;
    this.onerror = null;
    this.onclose = null;
    
    // 模拟连接过程
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) {
        this.onopen();
      }
    }, 100);
  }
  
  send(data) {
    console.log('📤 WebSocket发送:', data);
  }
  
  close(code, reason) {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      this.onclose({ code, reason });
    }
  }
};

WebSocket.CONNECTING = 0;
WebSocket.OPEN = 1;
WebSocket.CLOSING = 2;
WebSocket.CLOSED = 3;

// 模拟Zustand store
class MockDocumentStore {
  constructor() {
    this.state = {
      documents: [],
      total: 0,
      isLoading: false,
      error: null
    };
    this.listeners = [];
  }
  
  getState() {
    return this.state;
  }
  
  setState(newState) {
    this.state = { ...this.state, ...newState };
    this.listeners.forEach(listener => listener(this.state));
  }
  
  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }
  
  // Store方法实现
  setDocuments(documents, total) {
    console.log('📋 设置文档列表:', documents.length, '个文档');
    this.setState({ documents, total, isLoading: false });
  }
  
  addDocument(document) {
    console.log('➕ 添加文档:', document.filename);
    const newDocuments = [document, ...this.state.documents];
    this.setState({
      documents: newDocuments,
      total: this.state.total + 1
    });
  }
  
  removeDocument(id) {
    console.log('➖ 删除文档:', id);
    const newDocuments = this.state.documents.filter(doc => doc.id !== id);
    this.setState({
      documents: newDocuments,
      total: this.state.total - 1
    });
  }
  
  updateDocumentStatus(id, status, chunksCount) {
    console.log('🔄 更新文档状态:', id, '->', status, chunksCount ? `(chunks: ${chunksCount})` : '');
    const newDocuments = this.state.documents.map(doc =>
      doc.id === id 
        ? { ...doc, status, chunks_count: chunksCount, updated_at: new Date().toISOString() }
        : doc
    );
    this.setState({ documents: newDocuments });
  }
  
  setLoading(loading) {
    this.setState({ isLoading: loading });
  }
  
  setError(error) {
    console.log('❌ 设置错误:', error);
    this.setState({ error, isLoading: false });
  }
}

// 创建store实例
const documentStore = new MockDocumentStore();

// 订阅状态变化
const unsubscribe = documentStore.subscribe((state) => {
  console.log('📊 状态更新:', {
    documents: state.documents.length,
    total: state.total,
    isLoading: state.isLoading,
    error: state.error
  });
  
  // 显示每个文档的状态
  state.documents.forEach(doc => {
    console.log(`   📄 ${doc.filename}: ${doc.status} (${doc.chunks_count || 0} chunks)`);
  });
});

console.log('🚀 开始测试前端文档状态更新逻辑...\n');

// 测试1: 初始化状态
console.log('🧪 测试1: 初始化状态');
console.log('当前状态:', documentStore.getState());
console.log('');

// 测试2: 设置文档列表
console.log('🧪 测试2: 设置文档列表');
const initialDocuments = [
  {
    id: '1',
    filename: 'test-document.pdf',
    file_size: 1024000,
    mime_type: 'application/pdf',
    status: 'processing',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: '2',
    filename: 'another-doc.docx',
    file_size: 2048000,
    mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    status: 'ready',
    chunks_count: 15,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }
];

documentStore.setDocuments(initialDocuments, 2);
console.log('');

// 测试3: 添加新文档
console.log('🧪 测试3: 添加新文档');
const newDocument = {
  id: '3',
  filename: 'uploaded-file.txt',
  file_size: 512000,
  mime_type: 'text/plain',
  status: 'processing',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

documentStore.addDocument(newDocument);
console.log('');

// 测试4: 更新文档状态
console.log('🧪 测试4: 更新文档状态');
setTimeout(() => {
  console.log('模拟WebSocket消息: 文档1处理完成');
  documentStore.updateDocumentStatus('1', 'ready', 8);
  
  console.log('');
  
  console.log('模拟WebSocket消息: 文档3处理中...');
  documentStore.updateDocumentStatus('3', 'processing');
  
  console.log('');
  
  // 测试5: 删除文档
  console.log('🧪 测试5: 删除文档');
  documentStore.removeDocument('2');
  
  console.log('');
  
  // 测试6: 错误处理
  console.log('🧪 测试6: 错误处理');
  documentStore.setError('网络连接失败');
  
  console.log('');
  
  // 测试7: 加载状态
  console.log('🧪 测试7: 加载状态');
  documentStore.setLoading(true);
  setTimeout(() => {
    documentStore.setLoading(false);
    console.log('');
    
    // 最终状态
    console.log('🏁 测试完成! 最终状态:');
    console.log('========================');
    const finalState = documentStore.getState();
    console.log('文档总数:', finalState.total);
    console.log('加载中:', finalState.isLoading);
    console.log('错误信息:', finalState.error);
    console.log('文档列表:');
    finalState.documents.forEach(doc => {
      console.log(`  - ${doc.filename} (${doc.status})`);
    });
    
    // 取消订阅
    unsubscribe();
  }, 500);
  
}, 500);