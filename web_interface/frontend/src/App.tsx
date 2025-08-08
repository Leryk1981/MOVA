import React from 'react';
import { Routes, Route } from 'react-router-dom';

import Layout from '@/components/common/Layout';
import Dashboard from '@/pages/Dashboard';
import Editor from '@/pages/Editor';
import Monitor from '@/pages/Monitor';
import ML from '@/pages/ML';
import Files from '@/pages/Files';
import NotFound from '@/pages/NotFound';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/editor" element={<Editor />} />
        <Route path="/monitor" element={<Monitor />} />
        <Route path="/ml" element={<ML />} />
        <Route path="/files" element={<Files />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}

export default App; 