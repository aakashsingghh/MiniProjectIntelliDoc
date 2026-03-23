import React, { useState, useEffect } from 'react';

import { motion, AnimatePresence } from 'motion/react';

import { 
  LayoutDashboard, 
  Upload as UploadIcon, 
  Search as SearchIcon, 
  Settings, 
  BrainCircuit, 
  FileText, 
  Zap, 
  ShieldCheck, 
  Database,
  Moon,
  Sun,
  Menu,
  X
} from 'lucide-react';
import { FileUpload } from './components/FileUpload';

import { ResultDashboard } from './components/ResultDashboard';

import { SearchBar } from './components/SearchBar';

import { processDocumentText } from './lib/gemini';


type View = 'home' | 'upload' | 'dashboard' | 'search';


export default function App() {

  const [view, setView] = useState<View>('home');
  
  const [documents, setDocuments] = useState<any[]>([]);
  
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  const [searchQuery, setSearchQuery] = useState('');

  
  useEffect(() => {
    fetchDocuments();
  }, [searchQuery]);

  const fetchDocuments = async () => {
    try {
      const res = await fetch(`/api/documents${searchQuery ? `?search=${searchQuery}` : ''}`);
      const data = await res.json();
      setDocuments(data);
    } catch (error) {
      console.error('Failed to fetch docs:', error);
    }
  };

  const handleUploadComplete = async (data: any) => {
    // Process text with Gemini
    const nlpResult = await processDocumentText(data.extracted_text);
    
    // Save to DB
    await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: data.filename,
        extracted_text: nlpResult.cleaned_text || data.extracted_text,
        summary: nlpResult.summary,
        keywords: nlpResult.keywords.join(', ')
      })
    });

    await fetchDocuments();
    setView('dashboard');
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    await fetch(`/api/documents/${id}`, { method: 'DELETE' });
    fetchDocuments();
  };

  const NavItem = ({ icon: Icon, label, target }: { icon: any, label: string, target: View }) => (
    <button
      onClick={() => { setView(target); setIsMobileMenuOpen(false); }}
      className={`flex items-center space-x-3 px-6 py-3 rounded-2xl transition-all duration-300 ${
        view === target 
          ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-200' 
          : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'
      }`}
    >
      <Icon className="w-5 h-5" />
      <span className="font-semibold">{label}</span>
    </button>
  );

  return (
    <div className={`min-h-screen transition-colors duration-500 ${isDarkMode ? 'bg-slate-950 text-white' : 'bg-slate-50 text-slate-900'}`}>
      {/* Sidebar / Navigation */}
      <nav className="fixed top-0 left-0 h-full w-72 bg-white border-r border-slate-100 hidden lg:flex flex-col p-8 z-50">
        <div className="flex items-center space-x-3 mb-12">
          <div className="p-2.5 bg-emerald-600 rounded-xl shadow-lg shadow-emerald-200">
            <BrainCircuit className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-black tracking-tighter text-slate-900">INTELLIDOC</h1>
        </div>

        <div className="space-y-2 flex-1">
          <NavItem icon={LayoutDashboard} label="Home" target="home" />
          <NavItem icon={UploadIcon} label="Upload" target="upload" />
          <NavItem icon={FileText} label="Dashboard" target="dashboard" />
          <NavItem icon={SearchIcon} label="Search" target="search" />
        </div>

        <div className="pt-8 border-t border-slate-100 space-y-4">
          <button 
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="flex items-center space-x-3 px-6 py-3 w-full rounded-2xl text-slate-500 hover:bg-slate-100 transition-all"
          >
            {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            <span className="font-semibold">{isDarkMode ? 'Light Mode' : 'Dark Mode'}</span>
          </button>
          <button className="flex items-center space-x-3 px-6 py-3 w-full rounded-2xl text-slate-500 hover:bg-slate-100 transition-all">
            <Settings className="w-5 h-5" />
            <span className="font-semibold">Settings</span>
          </button>
        </div>
      </nav>

      {/* Mobile Header */}
      <header className="lg:hidden fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-slate-100 p-4 flex justify-between items-center z-50">
        <div className="flex items-center space-x-2">
          <BrainCircuit className="w-6 h-6 text-emerald-600" />
          <span className="font-black text-xl">INTELLIDOC</span>
        </div>
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2">
          {isMobileMenuOpen ? <X /> : <Menu />}
        </button>
      </header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="lg:hidden fixed top-16 w-full bg-white border-b border-slate-100 p-6 z-40 space-y-2 shadow-xl"
          >
            <NavItem icon={LayoutDashboard} label="Home" target="home" />
            <NavItem icon={UploadIcon} label="Upload" target="upload" />
            <NavItem icon={FileText} label="Dashboard" target="dashboard" />
            <NavItem icon={SearchIcon} label="Search" target="search" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="lg:ml-72 p-8 pt-24 lg:pt-12 max-w-7xl mx-auto">
        <AnimatePresence mode="wait">
          {view === 'home' && (
            <motion.div 
              key="home"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-16 py-12"
            >
              <div className="max-w-3xl space-y-6">
                <div className="inline-flex items-center space-x-2 px-4 py-2 bg-emerald-50 text-emerald-700 rounded-full text-sm font-bold border border-emerald-100">
                  <Zap className="w-4 h-4" />
                  <span>v2.0 Enterprise Automation</span>
                </div>
                <h2 className="text-6xl lg:text-7xl font-black leading-[1.1] tracking-tight text-slate-900">
                  Intelligent Document <span className="text-emerald-600">Processing</span> Platform.
                </h2>
                <p className="text-xl text-slate-500 leading-relaxed max-w-2xl">
                  Convert unstructured documents into intelligent digital data using state-of-the-art OCR and AI-powered NLP. Automate your enterprise workflows today.
                </p>
                <div className="flex flex-wrap gap-4 pt-4">
                  <button 
                    onClick={() => setView('upload')}
                    className="px-8 py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-xl shadow-emerald-200 transition-all active:scale-95"
                  >
                    Start Processing
                  </button>
                  <button 
                    onClick={() => setView('dashboard')}
                    className="px-8 py-4 bg-white border-2 border-slate-100 hover:border-emerald-200 text-slate-900 font-bold rounded-2xl transition-all"
                  >
                    View Dashboard
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {[
                  { icon: Zap, title: "Lightning OCR", desc: "Extract text from images and PDFs with 99% accuracy using Tesseract engine.", color: "bg-amber-50 text-amber-600" },
                  { icon: BrainCircuit, title: "AI Summarization", desc: "Gemini-powered NLP generates concise summaries and extracts key entities automatically.", color: "bg-emerald-50 text-emerald-600" },
                  { icon: ShieldCheck, title: "Enterprise Secure", desc: "Structured data storage with SQLite ensures your document data is always accessible and searchable.", color: "bg-blue-50 text-blue-600" }
                ].map((feature, i) => (
                  <div key={i} className="p-8 bg-white border border-slate-100 rounded-3xl shadow-sm hover:shadow-xl transition-all duration-500 group">
                    <div className={`p-4 rounded-2xl w-fit mb-6 transition-transform group-hover:scale-110 ${feature.color}`}>
                      <feature.icon className="w-8 h-8" />
                    </div>
                    <h3 className="text-xl font-bold mb-3 text-slate-900">{feature.title}</h3>
                    <p className="text-slate-500 leading-relaxed">{feature.desc}</p>
                  </div>
                ))}
              </div>

              <div className="bg-slate-900 rounded-[3rem] p-12 lg:p-20 text-white overflow-hidden relative">
                <div className="relative z-10 grid lg:grid-cols-2 gap-12 items-center">
                  <div className="space-y-8">
                    <h3 className="text-4xl font-bold leading-tight">Ready to revolutionize your document workflow?</h3>
                    <p className="text-slate-400 text-lg">Join 500+ enterprises automating their data extraction with IntelliDoc.</p>
                    <div className="flex items-center space-x-8">
                      <div className="flex flex-col">
                        <span className="text-3xl font-bold text-emerald-400">1M+</span>
                        <span className="text-sm text-slate-500 uppercase tracking-widest">Docs Processed</span>
                      </div>
                      <div className="w-px h-12 bg-slate-800" />
                      <div className="flex flex-col">
                        <span className="text-3xl font-bold text-emerald-400">99.9%</span>
                        <span className="text-sm text-slate-500 uppercase tracking-widest">Uptime</span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 space-y-6">
                    <div className="flex items-center space-x-3">
                      <Database className="w-6 h-6 text-emerald-400" />
                      <span className="font-bold">Real-time Data Sync</span>
                    </div>
                    <div className="space-y-3">
                      {[1, 2, 3].map(i => (
                        <div key={i} className="h-4 bg-white/5 rounded-full w-full overflow-hidden">
                          <motion.div 
                            initial={{ x: '-100%' }}
                            animate={{ x: '100%' }}
                            transition={{ duration: 2, repeat: Infinity, delay: i * 0.5 }}
                            className="h-full w-1/3 bg-emerald-400/20"
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-600/20 blur-[120px] rounded-full -mr-48 -mt-48" />
              </div>
            </motion.div>
          )}

          {view === 'upload' && (
            <motion.div 
              key="upload"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="py-12 space-y-12"
            >
              <div className="text-center space-y-4">
                <h2 className="text-4xl font-black text-slate-900">Upload Document</h2>
                <p className="text-slate-500 max-w-xl mx-auto">Upload an image or PDF. Our AI will handle the preprocessing, OCR, and intelligent analysis automatically.</p>
              </div>
              <FileUpload onUploadComplete={handleUploadComplete} />
            </motion.div>
          )}

          {view === 'dashboard' && (
            <motion.div 
              key="dashboard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="py-12 space-y-12"
            >
              <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="space-y-2">
                  <h2 className="text-4xl font-black text-slate-900">Document Insights</h2>
                  <p className="text-slate-500">Manage and analyze your processed documents.</p>
                </div>
                <button 
                  onClick={() => setView('upload')}
                  className="px-6 py-3 bg-emerald-600 text-white font-bold rounded-xl shadow-lg hover:bg-emerald-700 transition-all"
                >
                  Process New Document
                </button>
              </div>
              <ResultDashboard documents={documents} onDelete={handleDelete} />
            </motion.div>
          )}

          {view === 'search' && (
            <motion.div 
              key="search"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="py-12 space-y-16"
            >
              <div className="text-center space-y-4">
                <h2 className="text-4xl font-black text-slate-900">Intelligent Search</h2>
                <p className="text-slate-500">Find any document instantly using keywords or content snippets.</p>
              </div>
              <SearchBar onSearch={setSearchQuery} />
              {searchQuery && (
                <div className="space-y-8">
                  <p className="text-slate-400 font-medium">Found {documents.length} results for "{searchQuery}"</p>
                  <ResultDashboard documents={documents} onDelete={handleDelete} />
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="lg:ml-72 p-12 border-t border-slate-100 text-center">
        <p className="text-slate-400 text-sm font-medium">
          © 2026 INTELLIDOC AI Platform. Built for Enterprise Automation.
        </p>
      </footer>
    </div>
  );
}
