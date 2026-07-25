import React, { useState, useMemo } from 'react';
import { Bot, Rocket, ArrowRight, Zap, Shield, Search, Lock, AlertCircle, Loader2, Play, Code2, Server, Activity, CheckCircle, XCircle, Clock, Sparkles, ChevronDown, ChevronRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Endpoint {
  path: string;
  method: string;
  summary?: string;
  tags: string[];
  auth_required: boolean;
  auth_type?: string;
  supported: boolean;
  unsupported_reason?: string;
  risk_level: string;
}

// Module 8: AI Generator Output Interface
interface StructuredTestCase {
  name: string;
  url: string;
  method: string;
  headers_json: string;
  request_body_json: string;
  expected_status: number[];
}
// Module 8: Credential Highlighter
const detectSensitiveFields = (test: StructuredTestCase): string[] => {
  const sensitiveKeywords = ['password', 'token', 'api_key', 'apikey', 'secret', 'username', 'userid'];
  const found = new Set<string>();
  
  const searchString = `${test.url} ${test.request_body_json} ${test.headers_json}`.toLowerCase();
  
  sensitiveKeywords.forEach(keyword => {
    if (searchString.includes(keyword)) {
      found.add(keyword);
    }
  });
  
  return Array.from(found);
};

const Home: React.FC = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
  const [selectedPaths, setSelectedPaths] = useState<Set<string>>(new Set());

  // Module 7: Credential Collector States
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [requiredAuthType, setRequiredAuthType] = useState<string | null>(null);
  
  const [authForm, setAuthForm] = useState({
    token: '',
    username: '',
    password: ''
  });

  // Module 8: AI Generator States
  const [isGenerating, setIsGenerating] = useState(false);
  const [testCases, setTestCases] = useState<StructuredTestCase[]>([]);
  const [testCount, setTestCount] = useState<number>(2);
  
  // Module 9 & 10: Execution States
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResults, setExecutionResults] = useState<any[]>([]);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  
  // Module 12: AI Fix Explainer States
  const [explainingIdx, setExplainingIdx] = useState<number | null>(null);
  const [explanations, setExplanations] = useState<Record<number, string>>({});
  const [slaThreshold, setSlaThreshold] = useState(2000);
  
  // Module 11: Report States
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [reportUrl, setReportUrl] = useState<string | null>(null);

  // Module 11: Dashboard Metrics natively calculated in React
  const dashboardMetrics = useMemo(() => {
    if (executionResults.length === 0) return null;
    const total = executionResults.length;
    const passed = executionResults.filter(r => r.success).length;
    const failed = total - passed;
    const slow = executionResults.filter(r => r.is_slow).length;
    const passRate = Math.round((passed / total) * 100);
    const score = Math.max(0, Math.round(100 - (failed * (100 / Math.max(1, total))) - (slow * 5)));
    return { total, passed, failed, slow, passRate, score };
  }, [executionResults]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError(null);
    setEndpoints([]);
    setSelectedPaths(new Set());
    setShowAuthModal(false);
    setTestCases([]);

    try {
      const response = await fetch('http://localhost:8000/api/endpoints', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base_url: url }),
      });

      if (!response.ok) {
        const errData = await response.json();
        setError(errData.detail || 'Failed to discover OpenAPI spec.');
        return;
      }
      
      const data: Endpoint[] = await response.json();
      setEndpoints(data);

      const defaultSelected = new Set<string>();
      data.forEach(ep => {
        if (ep.supported && ep.risk_level === 'safe') {
          defaultSelected.add(`${ep.method} ${ep.path}`);
        }
      });
      setSelectedPaths(defaultSelected);

    } catch (error) {
      setError('Network error: Backend may not be running.');
    } finally {
      setLoading(false);
    }
  };

  const toggleSelection = (method: string, path: string) => {
    const key = `${method} ${path}`;
    const newSet = new Set(selectedPaths);
    if (newSet.has(key)) {
      newSet.delete(key);
    } else {
      newSet.add(key);
    }
    setSelectedPaths(newSet);
  };

  const handleProceed = () => {
    const selected = endpoints.filter(ep => selectedPaths.has(`${ep.method} ${ep.path}`));
    const authEndpoint = selected.find(ep => ep.auth_required);

    if (authEndpoint) {
      setRequiredAuthType(authEndpoint.auth_type || 'apikey');
      setShowAuthModal(true);
    } else {
      startAIGeneration();
    }
  };

  // Module 8: Integration
  const startAIGeneration = async () => {
    if (isGenerating) return; // Prevent accidental double-clicks from firing multiple requests
    setShowAuthModal(false);
    setIsGenerating(true);
    setError(null);
    
    // Get actual endpoint objects to send to Gemini
    const finalSelectedEndpoints = endpoints.filter(ep => selectedPaths.has(`${ep.method} ${ep.path}`));

    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ endpoints: finalSelectedEndpoints, test_count: testCount }),
      });

      if (!response.ok) {
        const errData = await response.json();
        setError(errData.detail || 'AI Generation Failed.');
        return;
      }
      
      const data: StructuredTestCase[] = await response.json();
      
      // Format the JSON perfectly before saving to state so it can be edited smoothly in the textareas
      const formattedData = data.map(test => {
        try {
          if (test.request_body_json !== "null") {
             test.request_body_json = JSON.stringify(JSON.parse(test.request_body_json), null, 2);
          }
          if (test.headers_json !== "null" && test.headers_json !== "{}") {
             test.headers_json = JSON.stringify(JSON.parse(test.headers_json), null, 2);
          }
        } catch(e) {
          // ignore parsing errors from AI output
        }
        return test;
      });
      
      setTestCases(formattedData);
      
    } catch (error) {
      setError('Network error during AI Generation.');
    } finally {
      setIsGenerating(false);
    }
  };

  // Module 9: Execution Handler
  const handleExecute = async () => {
    setIsExecuting(true);
    setError(null);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_url: url,
          credentials: {
            auth_type: requiredAuthType || 'none',
            token: authForm.token,
            username: authForm.username,
            password: authForm.password
          },
          test_cases: testCases,
          timeout: 10,
          sla_threshold_ms: slaThreshold
        })
      });
      
      if (!response.ok) {
        throw new Error(await response.text());
      }
      
      const results = await response.json();
      setExecutionResults(results);
      console.log("EXECUTION RESULTS:", results);
      alert(`Execution Complete! See browser console for detailed validation results.`);
      
    } catch (err: any) {
      setError(err.message || "Failed to execute tests");
    } finally {
      setIsExecuting(false);
    }
  };

  // Module 11: Report Download Handler
  const handleDownloadReport = async () => {
    if (executionResults.length === 0) return;
    setIsGeneratingReport(true);
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(executionResults)
      });
      
      if (!response.ok) throw new Error(await response.text());
      
      const metrics = await response.json();
      
      // Create a Blob from the HTML content and trigger a download
      const blob = new Blob([metrics.html_content], { type: 'text/html' });
      const url = window.URL.createObjectURL(blob);
      setReportUrl(url); // Keep it around if needed
      
      // Trigger native download
      const a = document.createElement('a');
      a.href = url;
      a.download = `API_Test_Report_${new Date().toISOString().split('T')[0]}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      
    } catch (e: any) {
      console.error(e);
      alert("Failed to download report.");
    } finally {
      setIsGeneratingReport(false);
    }
  };

  // Module 12: AI Fix Trigger
  const handleAskAIToFix = async (idx: number, result: any) => {
    setExplainingIdx(idx);
    try {
      const response = await fetch('http://localhost:8000/api/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
      });
      
      if (!response.ok) {
        throw new Error("Failed to get explanation");
      }
      
      const data = await response.json();
      setExplanations(prev => ({ ...prev, [idx]: data.explanation }));
    } catch (e) {
      alert("AI Explainer failed. Check the console.");
      console.error(e);
    } finally {
      setExplainingIdx(null);
    }
  };

  const groupedEndpoints = endpoints.reduce((acc, ep) => {
    const groupName = ep.tags && ep.tags.length > 0 ? ep.tags[0] : 'Other';
    if (!acc[groupName]) acc[groupName] = [];
    acc[groupName].push(ep);
    return acc;
  }, {} as Record<string, Endpoint[]>);

  const getMethodColor = (method: string) => {
    switch (method.toUpperCase()) {
      case 'GET': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'POST': return 'bg-green-100 text-green-700 border-green-200';
      case 'PUT': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'DELETE': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="min-h-screen bg-background font-sans selection:bg-primary/20 pb-24 relative">
      
      {/* Module 8: AI Generating Overlay */}
      {isGenerating && (
        <div className="fixed inset-0 z-[110] flex items-center justify-center bg-slate-900/60 backdrop-blur-md animate-fade-in">
          <div className="text-center space-y-6">
            <div className="relative w-24 h-24 mx-auto">
              <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping"></div>
              <div className="relative bg-primary text-white w-24 h-24 rounded-full flex items-center justify-center shadow-2xl">
                <Bot className="w-12 h-12 animate-pulse" />
              </div>
            </div>
            <div className="text-white space-y-2">
              <h2 className="text-2xl font-bold tracking-tight">Gemini is Thinking...</h2>
              <p className="text-slate-300 opacity-80">Generating optimal test payloads from schemas</p>
            </div>
          </div>
        </div>
      )}

      {/* Module 7: Auth Modal Overlay */}
      {showAuthModal && (
        // ... (existing modal logic)
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="bg-surface rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-scale-up">
            <div className="p-6 border-b border-slate-100 flex items-center gap-3 bg-blue-50/50">
              <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
                <Lock className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-lg">Authentication Required</h3>
                <p className="text-sm text-slate-500">Provide credentials for Execution</p>
              </div>
            </div>
            
            <div className="p-6 space-y-4">
              <div className="bg-amber-50 border border-amber-200 text-amber-800 text-sm px-4 py-3 rounded-xl flex items-start gap-2">
                <Shield className="w-4 h-4 mt-0.5 shrink-0" />
                <p>These credentials are stored locally in your browser and are <strong>never</strong> sent to the AI Model.</p>
              </div>

              {requiredAuthType === 'basic' ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-bold text-slate-700 mb-1">Username</label>
                    <input 
                      type="text" 
                      value={authForm.username}
                      onChange={e => setAuthForm({...authForm, username: e.target.value})}
                      className="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-slate-700 mb-1">Password</label>
                    <input 
                      type="password" 
                      value={authForm.password}
                      onChange={e => setAuthForm({...authForm, password: e.target.value})}
                      className="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                    />
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-1">API Key / Bearer Token</label>
                  <input 
                    type="password" 
                    placeholder="Paste your token here..."
                    value={authForm.token}
                    onChange={e => setAuthForm({...authForm, token: e.target.value})}
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                  />
                </div>
              )}
            </div>

            <div className="p-6 border-t border-slate-100 bg-slate-50 flex items-center justify-end gap-3">
              <button 
                onClick={() => setShowAuthModal(false)}
                className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={startAIGeneration}
                className="px-6 py-2 bg-primary hover:bg-primaryHover text-white text-sm font-bold rounded-lg flex items-center gap-2 transition-transform active:scale-95"
              >
                Start AI Generation
                <Zap className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      <nav className="flex items-center justify-between px-8 py-4 bg-surface border-b border-slate-200 sticky top-0 z-50">
        <div className="flex items-center gap-2 text-primary font-bold text-xl tracking-tight">
          <Rocket className="w-6 h-6" />
          <span>TestPilot AI</span>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-6 pt-16">
        
        {/* Only show Search UI if we haven't generated test cases yet */}
        {testCases.length === 0 && (
          <>
            {endpoints.length === 0 && (
              <div className="text-center space-y-6 animate-fade-in-up">
                <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
                  Autonomous API Testing <br /> 
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-cyan-500">
                    at Lightning Speed
                  </span>
                </h1>
                <p className="text-lg text-slate-500 max-w-2xl mx-auto leading-relaxed">
                  Instantly discover, generate, and execute comprehensive test suites.
                </p>
              </div>
            )}

            <form onSubmit={handleSubmit} className={`max-w-2xl mx-auto relative group transition-all duration-500 ${endpoints.length > 0 ? 'mt-4 mb-8' : 'mt-10'}`}>
              <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                <Search className="w-5 h-5 text-slate-400 group-focus-within:text-primary transition-colors" />
              </div>
              <input 
                type="url"
                required
                disabled={loading}
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter Swagger URL (e.g. https://petstore.swagger.io/v2)"
                className="w-full pl-12 pr-36 py-4 rounded-xl border border-slate-300 bg-surface text-slate-900 shadow-sm focus:ring-4 focus:ring-primary/20 focus:border-primary outline-none transition-all text-lg placeholder:text-slate-400 disabled:opacity-50"
              />
              <button 
                type="submit"
                disabled={loading}
                className="absolute right-2 top-2 bottom-2 px-6 bg-primary hover:bg-primaryHover text-white font-medium rounded-lg flex items-center gap-2 transition-colors active:scale-95 shadow-md shadow-primary/20 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Fetching</> : <><Search className="w-4 h-4" /> Discover</>}
              </button>
            </form>

            {error && (
              <div className="max-w-2xl mx-auto mt-4 p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 flex items-start gap-3 animate-fade-in-up">
                <AlertCircle className="w-6 h-6 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold">Error Occurred</h4>
                  <p className="text-sm opacity-90">{error}</p>
                </div>
              </div>
            )}

            {/* Module 6: Endpoint Selection UI */}
            {endpoints.length > 0 && !error && (
              <div className="animate-fade-in-up space-y-8 pb-10">
                <div className="flex items-center justify-between border-b border-slate-200 pb-4">
                  <h2 className="text-2xl font-bold text-slate-900">
                    Discovered Endpoints
                    <span className="ml-3 text-sm font-medium bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                      {endpoints.length} Total
                    </span>
                  </h2>
                  <div className="text-sm font-medium text-slate-500">
                    {selectedPaths.size} Selected
                  </div>
                </div>

                <div className="space-y-8">
                  {Object.entries(groupedEndpoints).map(([groupName, eps]) => (
                    <div key={groupName} className="bg-surface border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                      <div className="bg-slate-50 px-6 py-3 border-b border-slate-200 font-bold text-slate-700 flex items-center gap-2 uppercase tracking-wider text-sm">
                        {groupName} 
                        <span className="text-slate-400 text-xs normal-case">({eps.length})</span>
                      </div>
                      
                      <div className="divide-y divide-slate-100">
                        {eps.map((ep, idx) => {
                          const key = `${ep.method} ${ep.path}`;
                          const isSelected = selectedPaths.has(key);
                          const isSafe = ep.supported && ep.risk_level === 'safe';

                          return (
                            <div key={idx} className={`px-6 py-4 flex items-center gap-4 transition-colors ${!isSafe ? 'bg-slate-50/50 opacity-75 grayscale-[0.2]' : 'hover:bg-slate-50'}`}>
                              <input 
                                type="checkbox" 
                                disabled={!isSafe}
                                checked={isSelected}
                                onChange={() => toggleSelection(ep.method, ep.path)}
                                className="w-5 h-5 rounded border-slate-300 text-primary focus:ring-primary disabled:opacity-40 cursor-pointer disabled:cursor-not-allowed"
                              />
                              <div className={`w-20 text-center font-bold text-xs py-1 rounded border ${getMethodColor(ep.method)}`}>
                                {ep.method}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="font-mono text-sm text-slate-800 font-medium truncate">
                                  {ep.path}
                                </div>
                                {ep.summary && (
                                  <div className="text-xs text-slate-500 mt-1 truncate">
                                    {ep.summary}
                                  </div>
                                )}
                              </div>
                              <div className="flex items-center gap-2 shrink-0">
                                {ep.auth_required && (
                                  <div className="flex items-center gap-1 text-xs font-medium bg-amber-100 text-amber-700 px-2 py-1 rounded border border-amber-200">
                                    <Lock className="w-3 h-3" />
                                    {ep.auth_type || 'Auth'}
                                  </div>
                                )}
                                {!isSafe && (
                                  <div className="flex items-center gap-1 text-xs font-medium bg-slate-200 text-slate-600 px-2 py-1 rounded border border-slate-300">
                                    <AlertCircle className="w-3 h-3" />
                                    {ep.unsupported_reason || 'Unsupported'}
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="fixed bottom-0 left-0 right-0 bg-surface border-t border-slate-200 p-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-50">
                  <div className="max-w-5xl mx-auto flex items-center justify-between">
                    <div className="text-sm font-medium text-slate-600">
                      <span className="text-slate-900 font-bold">{selectedPaths.size}</span> endpoints ready for test generation
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <label className="text-sm font-bold text-slate-700">Tests/API:</label>
                        <input 
                          type="number" 
                          min="1" max="10" 
                          value={testCount} 
                          onChange={(e) => setTestCount(parseInt(e.target.value) || 2)} 
                          className="w-16 px-2 py-2 text-center rounded-lg border border-slate-300 focus:ring-2 focus:ring-primary outline-none" 
                        />
                      </div>
                      <button 
                        disabled={selectedPaths.size === 0 || isGenerating}
                        onClick={handleProceed}
                        className="px-8 py-3 bg-primary hover:bg-primaryHover text-white font-bold rounded-xl flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary/30"
                      >
                        {isGenerating ? 'Generating...' : 'Proceed to Testing'}
                        {!isGenerating && <ArrowRight className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* Module 8: Test Review UI (Hidden if Dashboard is active) */}
        {testCases.length > 0 && !error && executionResults.length === 0 && (
          <div className="animate-fade-in-up space-y-8 pb-20">
            <div className="flex flex-col space-y-2 border-b border-slate-200 pb-6">
              <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
                <SparklesIcon className="w-8 h-8 text-amber-500" />
                AI Generated Test Suite
              </h2>
              <p className="text-slate-500 text-lg">
                Gemini successfully generated <strong>{testCases.length}</strong> highly optimized test cases. Please review the payloads below.
              </p>
            </div>

            <div className="grid gap-6">
              {testCases.map((test, idx) => (
                <div key={idx} className="bg-surface border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col">
                  
                  {/* Card Header */}
                  <div className="bg-slate-50/80 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
                    <div className="flex flex-col gap-1">
                      <div className="font-bold text-slate-800 text-base">{test.name}</div>
                      <div className="flex items-center gap-3">
                        <div className={`w-14 text-center font-bold text-xs py-1 rounded border ${getMethodColor(test.method)}`}>
                          {test.method}
                        </div>
                        <div className="font-mono text-slate-500 font-medium text-sm">
                          {test.url}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 bg-slate-200 px-3 py-1 rounded-full text-sm font-bold text-slate-700">
                      <Server className="w-4 h-4 text-slate-500" />
                      Expects: {test.expected_status.join(' or ')}
                    </div>
                  </div>
                  
                  {/* Credential Highlighter Banner */}
                  {(() => {
                    const sensitiveFields = detectSensitiveFields(test);
                    if (sensitiveFields.length > 0) {
                      return (
                        <div className="bg-amber-500/10 border-l-4 border-amber-500 p-4 m-6 mb-0 rounded-r-lg flex items-start gap-3">
                          <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                          <div>
                            <h4 className="text-amber-800 font-bold text-sm">Action Required: Fake Credentials Detected</h4>
                            <p className="text-amber-700 text-sm mt-1">
                              The AI generated fake values for <strong className="bg-amber-200/50 px-1 rounded">{sensitiveFields.join(', ')}</strong>. 
                              Please replace them with your real testing credentials in the editor below before executing.
                            </p>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })()}

                  {/* Card Body - JSON Previews */}
                  <div className="p-6 grid md:grid-cols-2 gap-6 bg-slate-900 text-slate-300 font-mono text-sm">
                    {/* Headers */}
                    <div>
                      <div className="flex items-center gap-2 text-slate-400 mb-2 text-xs uppercase tracking-wider font-bold">
                        <Code2 className="w-4 h-4" /> Headers (Editable)
                      </div>
                      <textarea 
                        value={test.headers_json === "null" || test.headers_json === "{}" ? "" : test.headers_json}
                        onChange={e => {
                          const newTests = [...testCases];
                          newTests[idx].headers_json = e.target.value;
                          setTestCases(newTests);
                        }}
                        className="w-full h-48 bg-slate-950 p-4 rounded-lg border border-slate-800 text-slate-300 font-mono text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none resize-y"
                        placeholder="// No custom headers"
                        spellCheck="false"
                      />
                    </div>

                    {/* Body */}
                    <div>
                      <div className="flex items-center gap-2 text-slate-400 mb-2 text-xs uppercase tracking-wider font-bold">
                        <Code2 className="w-4 h-4" /> Request Body (Editable)
                      </div>
                      <textarea 
                        value={test.request_body_json === "null" ? "" : test.request_body_json}
                        onChange={e => {
                          const newTests = [...testCases];
                          newTests[idx].request_body_json = e.target.value;
                          setTestCases(newTests);
                        }}
                        className="w-full h-48 bg-slate-950 p-4 rounded-lg border border-slate-800 text-emerald-400 font-mono text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none resize-y"
                        placeholder="// No body required"
                        spellCheck="false"
                      />
                    </div>
                  </div>

                </div>
              ))}
            </div>

            {/* Floating Execute Button (Only when not executed yet) */}
            {executionResults.length === 0 && (
              <div className="fixed bottom-0 left-0 right-0 bg-surface border-t border-slate-200 p-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-50">
                <div className="max-w-5xl mx-auto flex items-center justify-between">
                  <div className="flex items-center gap-6">
                    <div className="text-sm font-medium text-slate-600">
                      <span className="text-slate-900 font-bold">{testCases.length}</span> tests are ready to be executed against the server.
                    </div>
                    <div className="flex items-center gap-2 border-l border-slate-300 pl-6">
                      <span className="text-sm font-bold text-slate-700">SLA Threshold (ms):</span>
                      <input 
                        type="number" 
                        value={slaThreshold}
                        onChange={e => setSlaThreshold(Number(e.target.value))}
                        className="w-24 px-3 py-1.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary outline-none font-mono"
                      />
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <button 
                      onClick={handleExecute}
                      disabled={isExecuting}
                      className={`px-8 py-3 font-bold rounded-xl flex items-center gap-2 transition-all shadow-lg ${
                        isExecuting 
                          ? "bg-slate-300 text-slate-500 cursor-not-allowed shadow-none" 
                          : "bg-green-600 hover:bg-green-700 text-white active:scale-95 shadow-green-600/30"
                      }`}
                    >
                      {isExecuting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5 fill-current" />}
                      {isExecuting ? "Executing..." : "Execute Test Suite"}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Module 11: In-App Results Dashboard */}
        {executionResults.length > 0 && dashboardMetrics && (
          <div className="animate-fade-in-up space-y-8 pb-20">
            <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 pb-6 gap-4">
              <div>
                <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
                  <Activity className="w-8 h-8 text-blue-500" />
                  Execution Dashboard
                </h2>
                <p className="text-slate-500 text-lg mt-2">
                  All tests completed. Review the health metrics and endpoints below.
                </p>
              </div>
              <button 
                onClick={handleDownloadReport}
                disabled={isGeneratingReport}
                className="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl flex items-center gap-2 transition-all active:scale-95 shadow-lg"
              >
                {isGeneratingReport ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
                Download HTML Report
              </button>
            </div>

            {/* Metric Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
                <div className="text-slate-500 font-bold text-sm mb-1 uppercase tracking-wider">Health Score</div>
                <div className={`text-4xl font-extrabold ${dashboardMetrics.score > 80 ? 'text-green-500' : 'text-red-500'}`}>
                  {dashboardMetrics.score}/100
                </div>
              </div>
              <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
                <div className="text-slate-500 font-bold text-sm mb-1 uppercase tracking-wider">Pass Rate</div>
                <div className="text-4xl font-extrabold text-slate-900">{dashboardMetrics.passRate}%</div>
              </div>
              <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
                <div className="text-slate-500 font-bold text-sm mb-1 uppercase tracking-wider">Failed Tests</div>
                <div className={`text-4xl font-extrabold ${dashboardMetrics.failed > 0 ? 'text-red-500' : 'text-green-500'}`}>
                  {dashboardMetrics.failed}
                </div>
              </div>
              <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
                <div className="text-slate-500 font-bold text-sm mb-1 uppercase tracking-wider">Slow APIs</div>
                <div className={`text-4xl font-extrabold ${dashboardMetrics.slow > 0 ? 'text-amber-500' : 'text-green-500'}`}>
                  {dashboardMetrics.slow}
                </div>
              </div>
            </div>

            {/* Results Table */}
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 text-sm uppercase tracking-wider text-slate-500">
                      <th className="p-4 font-bold">Status</th>
                      <th className="p-4 font-bold">Endpoint</th>
                      <th className="p-4 font-bold">Expected vs Actual</th>
                      <th className="p-4 font-bold">Speed</th>
                      <th className="p-4 font-bold text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {executionResults.map((result, idx) => {
                      const isExpanded = expandedRows.has(idx);
                      
                      const toggleExpand = () => {
                        const next = new Set(expandedRows);
                        if (next.has(idx)) next.delete(idx);
                        else next.add(idx);
                        setExpandedRows(next);
                      };

                      return (
                      <React.Fragment key={idx}>
                      <tr className="hover:bg-slate-50/50 transition-colors cursor-pointer" onClick={toggleExpand}>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                            {result.success ? (
                              <div className="flex items-center gap-2 text-green-600 font-bold text-sm bg-green-50 px-3 py-1 rounded-full w-fit">
                                <CheckCircle className="w-4 h-4" /> Passed
                              </div>
                            ) : (
                              <div className="flex items-center gap-2 text-red-600 font-bold text-sm bg-red-50 px-3 py-1 rounded-full w-fit">
                                <XCircle className="w-4 h-4" /> Failed
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex flex-col gap-1">
                            <span className="font-bold text-slate-800 text-sm">{result.test_case.name}</span>
                            <div className="flex items-center gap-2">
                              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${getMethodColor(result.test_case.method)}`}>
                                {result.test_case.method}
                              </span>
                              <span className="font-mono text-xs text-slate-500">{result.test_case.url}</span>
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex flex-col text-sm">
                            <span className="text-slate-500 text-xs">Expected: {result.test_case.expected_status.join(', ')}</span>
                            <span className={`font-bold ${result.success ? 'text-green-600' : 'text-red-600'}`}>
                              Actual: {result.status_code || 'Error'}
                            </span>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className={`flex items-center gap-1 font-mono text-sm font-bold ${result.is_slow ? 'text-amber-500' : 'text-slate-600'}`}>
                            {result.is_slow && <Clock className="w-4 h-4" />}
                            {result.response_time_ms}ms
                          </div>
                        </td>
                        <td className="p-4 text-right">
                          {!result.success && (
                            <button 
                              onClick={() => handleAskAIToFix(idx, result)}
                              disabled={explainingIdx === idx}
                              className={`px-3 py-1.5 rounded-lg text-sm font-bold flex items-center gap-2 ml-auto transition-all ${
                                explainingIdx === idx 
                                  ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
                                  : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100'
                              }`}
                            >
                              {explainingIdx === idx ? (
                                <>
                                  <div className="w-4 h-4 border-2 border-slate-300 border-t-slate-500 rounded-full animate-spin" />
                                  Analyzing...
                                </>
                              ) : (
                                <>
                                  <Sparkles className="w-4 h-4" /> Ask AI to Fix
                                </>
                              )}
                            </button>
                          )}
                        </td>
                      </tr>

                      {/* Expanded Details Row */}
                      {isExpanded && (
                        <tr className="bg-slate-50 border-b border-slate-200">
                          <td colSpan={5} className="p-0">
                            <div className="p-6 grid grid-cols-2 gap-6">
                              <div>
                                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Request Body</h4>
                                <pre className="bg-slate-900 text-slate-300 p-3 rounded-lg text-xs font-mono overflow-auto max-h-40">
                                  {result.test_case.request_body_json !== 'null' ? result.test_case.request_body_json : '// No body'}
                                </pre>
                              </div>
                              <div className="space-y-4">
                                <div>
                                  <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Response Details</h4>
                                  <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-white p-3 rounded border border-slate-200">
                                      <div className="text-xs text-slate-500">Expected Status</div>
                                      <div className="font-bold text-slate-700">{result.test_case.expected_status.join(', ')}</div>
                                    </div>
                                    <div className="bg-white p-3 rounded border border-slate-200">
                                      <div className="text-xs text-slate-500">Actual Status</div>
                                      <div className={`font-bold ${result.success ? 'text-green-600' : 'text-red-600'}`}>
                                        {result.status_code || 'Error'}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Response Body Sneak Peek */}
                                <div>
                                  <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Response Body (Snippet)</h4>
                                  <pre className="bg-slate-100 text-slate-600 p-3 rounded border border-slate-200 text-xs font-mono overflow-auto max-h-24">
                                    {result.response_body ? String(result.response_body).slice(0, 200) + '...' : '// None'}
                                  </pre>
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}

                      {/* Expanded AI Explanation Row */}
                      {explanations[idx] && (
                        <tr key={`ai-${idx}`} className="bg-indigo-50/30">
                          <td colSpan={5} className="p-6">
                            <div className="bg-white rounded-xl border border-indigo-100 shadow-inner overflow-hidden">
                              <div className="bg-indigo-500/10 px-4 py-2 border-b border-indigo-100 flex items-center gap-2">
                                <Sparkles className="w-4 h-4 text-indigo-600" />
                                <span className="font-bold text-indigo-900 text-sm">AI Fix Suggestion</span>
                              </div>
                              <div className="p-6 text-slate-800 text-sm prose prose-indigo max-w-none">
                                <ReactMarkdown>{explanations[idx]}</ReactMarkdown>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                    );
                  })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

// Quick helper for the sparkles icon
const SparklesIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className}>
    <path d="M12 1.5l1.8 5.7h6l-4.8 3.5 1.8 5.7-4.8-3.5-4.8 3.5 1.8-5.7-4.8-3.5h6z" />
  </svg>
);

export default Home;
