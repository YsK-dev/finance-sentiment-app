import React, { useState } from 'react';
import { Search, TrendingUp, Scale, ExternalLink } from 'lucide-react';
import { analyzeSymbol } from '../services/api';

const SAMPLE_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NFLX', 'NVDA'];
const LABELS = ['positive', 'neutral', 'negative'];

const BADGE = {
    positive: 'text-green-700 bg-green-50',
    negative: 'text-red-700 bg-red-50',
    neutral: 'text-yellow-700 bg-yellow-50',
};
const BAR = { positive: 'bg-green-500', neutral: 'bg-yellow-400', negative: 'bg-red-500' };
const RULE_BADGE = { BUY: 'bg-green-100 text-green-800', SELL: 'bg-red-100 text-red-800', HOLD: 'bg-yellow-100 text-yellow-800' };

const Badge = ({ label }) => (
    <span className={`px-2 py-0.5 rounded text-xs font-medium uppercase ${BADGE[label]}`}>{label}</span>
);

const Dashboard = () => {
    const [symbol, setSymbol] = useState('');
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const run = async (value) => {
        const target = value.trim().toUpperCase();
        if (!target) return;
        setSymbol(target);
        setLoading(true);
        setError('');
        // Clear the previous symbol's result so it never shows under a new error.
        setAnalysis(null);
        try {
            setAnalysis(await analyzeSymbol(target));
        } catch (err) {
            setError(err.message || 'Failed to analyze symbol. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const total = analysis ? analysis.articles.length : 0;

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Financial Sentiment Analysis</h1>
                    <p className="text-lg text-gray-600">
                        Each recent news headline about a stock is labelled positive, negative or neutral with FinBERT
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                        A demo of text classification, not financial advice.
                    </p>
                </div>

                <form onSubmit={(e) => { e.preventDefault(); run(symbol); }} className="mb-8">
                    <div className="flex gap-4">
                        <input
                            type="text"
                            value={symbol}
                            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                            placeholder="Enter stock symbol (e.g., AAPL, TSLA, MSFT)"
                            className="flex-1 min-w-0 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        />
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center"
                        >
                            <Search className="h-5 w-5 mr-2" />
                            {loading ? 'Analyzing...' : 'Analyze'}
                        </button>
                    </div>
                </form>

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-red-700">{error}</p>
                    </div>
                )}

                {analysis && (
                    <>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                            <div className="bg-white rounded-lg shadow-md p-6">
                                <h2 className="text-xl font-semibold mb-4 flex items-center">
                                    <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                                    Headlines about {analysis.symbol}
                                </h2>
                                <div className="flex justify-between items-center mb-4">
                                    <span className="text-gray-600">Most common label:</span>
                                    <Badge label={analysis.overall_sentiment} />
                                </div>
                                <p className="text-sm text-gray-600 mb-3">
                                    {analysis.label_counts[analysis.overall_sentiment]} of {total} headlines
                                    ({Math.round(analysis.agreement * 100)}%) carry this label.
                                </p>
                                <div className="flex h-3 rounded overflow-hidden mb-2" aria-hidden="true">
                                    {LABELS.map((label) => (
                                        <div key={label} className={BAR[label]}
                                            style={{ width: `${(analysis.label_counts[label] / total) * 100}%` }} />
                                    ))}
                                </div>
                                <div className="flex gap-4 text-sm text-gray-600">
                                    {LABELS.map((label) => (
                                        <span key={label}>{analysis.label_counts[label]} {label}</span>
                                    ))}
                                </div>
                                <p className="text-xs text-gray-500 mt-4">
                                    Model: {analysis.model} · {new Date(analysis.timestamp).toLocaleString()}
                                </p>
                            </div>

                            <div className="bg-white rounded-lg shadow-md p-6">
                                <h2 className="text-xl font-semibold mb-4 flex items-center">
                                    <Scale className="h-5 w-5 mr-2 text-blue-600" />
                                    Rule-based label
                                </h2>
                                <div className="flex justify-between items-center mb-4">
                                    <span className="text-gray-600">Label:</span>
                                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${RULE_BADGE[analysis.rule_label]}`}>
                                        {analysis.rule_label}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-600">
                                    The rule uses the most common label: positive gives BUY, neutral gives HOLD,
                                    negative gives SELL. It has not been tested against prices.
                                </p>
                            </div>
                        </div>

                        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Headlines scored ({total})</h2>
                        <div className="bg-white rounded-lg shadow-md divide-y">
                            {analysis.articles.map((article, index) => (
                                <a key={index} href={article.url} target="_blank" rel="noopener noreferrer"
                                    className="flex items-start gap-4 p-4 hover:bg-gray-50 group">
                                    <div className="w-24 shrink-0 pt-0.5"><Badge label={article.sentiment} /></div>
                                    <div className="flex-1 min-w-0">
                                        <p className="font-medium text-gray-900 group-hover:text-blue-600">
                                            {article.title}
                                            <ExternalLink className="inline h-3 w-3 ml-1 opacity-0 group-hover:opacity-100" />
                                        </p>
                                        <p className="text-xs text-gray-500 mt-1">
                                            {article.source}{article.published ? ` · ${article.published}` : ''} · model score {Math.round(article.score * 100)}%
                                        </p>
                                    </div>
                                </a>
                            ))}
                        </div>
                    </>
                )}

                <div className="mt-12">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Try analyzing these popular symbols:</h3>
                    <div className="flex flex-wrap gap-2">
                        {SAMPLE_SYMBOLS.map((sample) => (
                            <button key={sample} onClick={() => run(sample)} disabled={loading}
                                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50">
                                {sample}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
