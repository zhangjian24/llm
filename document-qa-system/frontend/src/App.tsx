import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DocumentUpload from './components/DocumentUpload';
import ChatInterface from './components/ChatInterface';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<DocumentUpload />} />
            <Route path="/chat" element={<ChatInterface />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;