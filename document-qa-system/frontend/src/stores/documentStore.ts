import { create } from 'zustand';
import type { Document } from '../types';

interface DocumentState {
  documents: Document[];
  total: number;
  page: number;
  limit: number;
  isLoading: boolean;
  error: string | null;

  // Actions
  setDocuments: (documents: Document[], total: number) => void;
  addDocument: (document: Document) => void;
  removeDocument: (id: string) => void;
  setPage: (page: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useDocumentStore = create<DocumentState>((set) => ({
  documents: [],
  total: 0,
  page: 1,
  limit: 20,
  isLoading: false,
  error: null,

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

  setPage: (page) =>
    set({ page }),

  setLoading: (loading) =>
    set({ isLoading: loading }),

  setError: (error) =>
    set({ error, isLoading: false }),
}));
