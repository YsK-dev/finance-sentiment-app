import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import SymbolAnalysis from './pages/SymbolAnalysis';
import YouTubeAnalyzer from './pages/YouTubeAnalyzer';

function App() {
    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                <Header />
                <main>
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/analysis/:symbol" element={<SymbolAnalysis />} />
                        <Route path="/youtube" element={<YouTubeAnalyzer />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
