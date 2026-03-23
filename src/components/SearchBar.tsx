import React, { useState } from 'react';
import { Search, Filter, X } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSearch} className="relative w-full max-w-3xl mx-auto group">
      <div className="relative flex items-center">
        <div className="absolute left-6 text-slate-400 group-focus-within:text-emerald-500 transition-colors">
          <Search className="w-6 h-6" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search documents by filename, keyword, or content..."
          className="w-full pl-16 pr-24 py-5 bg-white border-2 border-slate-100 rounded-3xl shadow-xl shadow-slate-200/50 focus:border-emerald-500 focus:ring-0 transition-all text-lg placeholder:text-slate-300"
        />
        <div className="absolute right-4 flex items-center space-x-2">
          {query && (
            <button
              type="button"
              onClick={() => { setQuery(''); onSearch(''); }}
              className="p-2 hover:bg-slate-100 rounded-full text-slate-400 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
          <button
            type="submit"
            className="px-6 py-2.5 bg-slate-900 hover:bg-black text-white font-bold rounded-2xl transition-all active:scale-95"
          >
            Search
          </button>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-center space-x-6 text-sm text-slate-400">
        <span className="flex items-center"><Filter className="w-4 h-4 mr-1.5" /> Filter by:</span>
        <button type="button" className="hover:text-emerald-600 font-medium transition-colors">Recent</button>
        <span className="w-1 h-1 bg-slate-200 rounded-full" />
        <button type="button" className="hover:text-emerald-600 font-medium transition-colors">PDFs Only</button>
        <span className="w-1 h-1 bg-slate-200 rounded-full" />
        <button type="button" className="hover:text-emerald-600 font-medium transition-colors">High Confidence</button>
      </div>
    </form>
  );
};
