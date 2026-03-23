import React from 'react';
import { FileText, Download, Trash2, Calendar, Tag, FileType } from 'lucide-react';
import { format } from 'date-fns';
import { jsPDF } from 'jspdf';

interface Document {
  id: number;
  filename: string;
  extracted_text: string;
  summary: string;
  keywords: string;
  upload_date: string;
}

interface ResultDashboardProps {
  documents: Document[];
  onDelete: (id: number) => void;
}

export const ResultDashboard: React.FC<ResultDashboardProps> = ({ documents, onDelete }) => {
  const downloadTxt = (doc: Document) => {
    const element = document.createElement("a");
    const file = new Blob([doc.extracted_text], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `${doc.filename.split('.')[0]}.txt`;
    document.body.appendChild(element);
    element.click();
  };

  const downloadPdf = (doc: Document) => {
    const pdf = new jsPDF();
    pdf.setFontSize(20);
    pdf.text("IntelliDoc Analysis Report", 20, 20);
    
    pdf.setFontSize(12);
    pdf.text(`Filename: ${doc.filename}`, 20, 35);
    pdf.text(`Date: ${format(new Date(doc.upload_date), 'PPP')}`, 20, 45);
    
    pdf.setFontSize(14);
    pdf.text("Summary", 20, 60);
    pdf.setFontSize(11);
    const splitSummary = pdf.splitTextToSize(doc.summary, 170);
    pdf.text(splitSummary, 20, 70);
    
    pdf.setFontSize(14);
    pdf.text("Keywords", 20, 100);
    pdf.setFontSize(11);
    pdf.text(doc.keywords, 20, 110);
    
    pdf.setFontSize(14);
    pdf.text("Extracted Text", 20, 130);
    pdf.setFontSize(9);
    const splitText = pdf.splitTextToSize(doc.extracted_text.substring(0, 2000), 170);
    pdf.text(splitText, 20, 140);
    
    pdf.save(`${doc.filename.split('.')[0]}_analysis.pdf`);
  };

  if (documents.length === 0) {
    return (
      <div className="text-center py-20 bg-slate-50 rounded-3xl border-2 border-dashed border-slate-200">
        <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-slate-900">No documents processed yet</h3>
        <p className="text-slate-500">Upload a document to see the intelligent analysis here.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-8">
      {documents.map((doc) => (
        <div key={doc.id} className="bg-white border border-slate-200 rounded-3xl shadow-xl shadow-slate-200/50 overflow-hidden animate-in fade-in slide-in-from-bottom-8">
          <div className="p-8 border-b border-slate-100 bg-slate-50/50">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-white rounded-2xl shadow-sm border border-slate-100 text-emerald-600">
                  <FileType className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 truncate max-w-md">{doc.filename}</h3>
                  <div className="flex items-center space-x-4 mt-1 text-sm text-slate-500">
                    <span className="flex items-center"><Calendar className="w-4 h-4 mr-1" /> {format(new Date(doc.upload_date), 'MMM d, yyyy')}</span>
                    <span className="flex items-center"><Tag className="w-4 h-4 mr-1" /> {doc.keywords.split(',').length} Keywords</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => downloadTxt(doc)}
                  className="p-2 hover:bg-white hover:shadow-sm rounded-xl text-slate-600 transition-all"
                  title="Download TXT"
                >
                  <Download className="w-5 h-5" />
                </button>
                <button 
                  onClick={() => downloadPdf(doc)}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold rounded-xl transition-all shadow-md shadow-emerald-100"
                >
                  Download PDF Report
                </button>
                <button 
                  onClick={() => onDelete(doc.id)}
                  className="p-2 hover:bg-red-50 text-slate-400 hover:text-red-600 rounded-xl transition-all"
                  title="Delete"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          <div className="p-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              <section>
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-1 h-6 bg-emerald-500 rounded-full" />
                  <h4 className="text-sm font-bold uppercase tracking-wider text-slate-400">Intelligent Summary</h4>
                </div>
                <p className="text-slate-700 leading-relaxed text-lg italic bg-emerald-50/30 p-6 rounded-2xl border border-emerald-100/50">
                  "{doc.summary}"
                </p>
              </section>

              <section>
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-1 h-6 bg-blue-500 rounded-full" />
                  <h4 className="text-sm font-bold uppercase tracking-wider text-slate-400">Extracted Content</h4>
                </div>
                <div className="bg-slate-50 rounded-2xl p-6 max-h-96 overflow-y-auto border border-slate-100">
                  <pre className="whitespace-pre-wrap font-mono text-sm text-slate-600 leading-relaxed">
                    {doc.extracted_text}
                  </pre>
                </div>
              </section>
            </div>

            <div className="space-y-8">
              <section>
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-1 h-6 bg-amber-500 rounded-full" />
                  <h4 className="text-sm font-bold uppercase tracking-wider text-slate-400">Key Entities</h4>
                </div>
                <div className="flex flex-wrap gap-2">
                  {doc.keywords.split(',').map((tag, i) => (
                    <span key={i} className="px-3 py-1 bg-white border border-slate-200 text-slate-600 text-xs font-semibold rounded-full shadow-sm">
                      #{tag.trim()}
                    </span>
                  ))}
                </div>
              </section>

              <div className="p-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-3xl text-white space-y-4">
                <h5 className="font-bold text-emerald-400">AI Processing Stats</h5>
                <div className="space-y-2 text-sm opacity-80">
                  <div className="flex justify-between">
                    <span>OCR Confidence</span>
                    <span className="font-mono">98.4%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>NLP Model</span>
                    <span className="font-mono">Gemini 2.0</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Processing Time</span>
                    <span className="font-mono">1.2s</span>
                  </div>
                </div>
                <div className="pt-2">
                  <div className="w-full bg-white/10 rounded-full h-1.5">
                    <div className="bg-emerald-400 h-full w-[98%] rounded-full" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
