import { create } from 'zustand';
import type { Document } from '../types';
import { documentAPI } from '../services/api';

interface DocumentState {
  // 数据状态
  documents: Document[];
  total: number;
  page: number;
  limit: number;
  statusFilter: string;
  
  // UI 状态
  isLoading: boolean;
  error: string | null;

  // Actions
  setDocuments: (documents: Document[], total: number) => void;
  addDocument: (document: Document) => void;
  removeDocument: (id: string) => void;
  updateDocumentStatus: (id: string, status: Document['status'], chunksCount?: number) => void;
  
  setPage: (page: number) => void;
  setStatusFilter: (status: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // API 调用
  fetchDocuments: (page: number, limit: number, status?: string) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
  reprocessDocument: (id: string) => Promise<void>;
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  // 初始状态
  documents: [],
  total: 0,
  page: 1,
  limit: 20,
  statusFilter: '',
  isLoading: false,
  error: null,

  // 基础 Actions
  setDocuments: (documents, total) =>
    set({ documents, total, isLoading: false }),

  addDocument: (document) =>
    set((state) => ({
      documents: [document, ...state.documents],
      total: state.total + 1,
    })),

  removeDocument: (id) =>
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== id),
      total: state.total - 1,
    })),

  updateDocumentStatus: (id, status, chunksCount) =>
    set((state) => ({
      documents: state.documents.map((doc) =>
        doc.id === id 
          ? { ...doc, status, chunks_count: chunksCount, updated_at: new Date().toISOString() }
          : doc
      ),
    })),

  setPage: (page) =>
    set({ page }),

  setStatusFilter: (status) =>
    set({ statusFilter: status }),

  setLoading: (loading) =>
    set({ isLoading: loading }),

  setError: (error) =>
    set({ error, isLoading: false }),

  // API Actions
  fetchDocuments: async (page, limit, status) => {
    set({ isLoading: true, error: null });
    try {
      const response = await documentAPI.getList(page, limit, status);
      set({
        documents: response.data.items,
        total: response.data.total,
        page: response.data.page,
        limit: response.data.limit,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '加载失败',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteDocument: async (id) => {
    try {
      await documentAPI.delete(id);
      get().removeDocument(id);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '删除失败';
      set({ error: errorMsg });
      throw error;
    }
  },

  reprocessDocument: async (id) => {
    try {
      // 调用后端 API
      await documentAPI.reprocess(id);
      
      // API 调用成功后，更新本地状态为 processing
      // 注意：后端会先验证状态，只有 failed/ready 才能重新处理
      get().updateDocumentStatus(id, 'processing');
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '重新处理失败';
      set({ error: errorMsg });
      throw error;
    }
  },
}));
