import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, TrendingUp, AlertTriangle, Clock, Newspaper, Youtube, Globe, MessageCircle, ExternalLink } from 'lucide-react';
import { analyzeSymbol, getInvestmentAdvice, getNewsArticles, getBlogPosts } from '../services/api';

const Dashboard = () => {
    const [symbol, setSymbol] = useState('');
    const [analysis, setAnalysis] = useState(null);
    const [advice, setAdvice] = useState(null);
    const [newsArticles, setNewsArticles] = useState(null);
    const [blogPosts, setBlogPosts] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleAnalyze = async (e) => {
        e.preventDefault();
        if (!symbol.trim()) return;

        setLoading(true);
        setError('');

        try {
            const [analysisResult, adviceResult, newsResult, blogsResult] = await Promise.all([
                analyzeSymbol(symbol),
                getInvestmentAdvice(symbol),
                getNewsArticles(symbol),
                getBlogPosts(symbol)
            ]);

            setAnalysis(analysisResult);
            setAdvice(adviceResult);
            setNewsArticles(newsResult);
            setBlogPosts(blogsResult);
        } catch (err) {
            const errorMessage = err.message || 'Failed to analyze symbol. Please try again.';
            setError(errorMessage);
            console.error('Analysis error:', err);
        } finally {
            setLoading(false);
        }
    };

    const getSentimentColor = (sentiment) => {
        switch (sentiment) {
            case 'positive': return 'text-green-600 bg-green-50';
            case 'negative': return 'text-red-600 bg-red-50';
            default: return 'text-yellow-600 bg-yellow-50';
        }
    };

    const getRiskColor = (risk) => {
        switch (risk.toLowerCase()) {
            case 'low': return 'text-green-600';
            case 'medium': return 'text-yellow-600';
            case 'high': return 'text-red-600';
            default: return 'text-gray-600';
        }
    };

    const getSourceIcon = (source) => {
        const sourceLower = source.toLowerCase();
        if (sourceLower.includes('news')) return <Newspaper className="h-4 w-4" />;
        if (sourceLower.includes('youtube')) return <Youtube className="h-4 w-4" />;
        if (sourceLower.includes('blog')) return <Globe className="h-4 w-4" />;
        if (sourceLower.includes('social')) return <MessageCircle className="h-4 w-4" />;
        return <Globe className="h-4 w-4" />;
    };

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        Financial Sentiment Analysis
                    </h1>
                    <p className="text-lg text-gray-600">
                        AI-powered investment insights using sentiment analysis from multiple sources
                    </p>
                </div>

                {/* Search Form */}
                <form onSubmit={handleAnalyze} className="mb-8">
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <input
                                type="text"
                                value={symbol}
                                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                                placeholder="Enter stock symbol (e.g., AAPL, TSLA, MSFT)"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 flex items-center"
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

                {/* Results */}
                {analysis && advice && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Analysis Card */}
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h2 className="text-xl font-semibold mb-4 flex items-center">
                                <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                                Sentiment Analysis for {analysis.symbol}
                            </h2>

                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600">Overall Sentiment:</span>
                                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(analysis.overall_sentiment)}`}>
                                        {analysis.overall_sentiment.toUpperCase()}
                                    </span>
                                </div>

                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600">Confidence:</span>
                                    <span className="font-semibold">
                                        {(analysis.confidence_score * 100).toFixed(1)}%
                                    </span>
                                </div>

                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600">Risk Level:</span>
                                    <span className={`font-semibold ${getRiskColor(analysis.risk_level)}`}>
                                        {analysis.risk_level.toUpperCase()}
                                    </span>
                                </div>

                                <div>
                                    <h3 className="font-medium text-gray-600 mb-2">Key Insights:</h3>
                                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                                        {analysis.key_insights.map((insight, index) => (
                                            <li key={index}>{insight}</li>
                                        ))}
                                    </ul>
                                </div>

                                {/* Data Sources */}
                                {analysis.source_breakdown && Object.keys(analysis.source_breakdown).length > 0 && (
                                    <div>
                                        <h3 className="font-medium text-gray-600 mb-2">Data Sources Analyzed:</h3>
                                        <div className="space-y-2">
                                            {Object.entries(analysis.source_breakdown).map(([source, confidence]) => (
                                                <div key={source} className="flex items-center justify-between text-sm">
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-gray-500">
                                                            {getSourceIcon(source)}
                                                        </span>
                                                        <span className="capitalize text-gray-700">{source}</span>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                                            <div 
                                                                className="h-full bg-green-600 rounded-full"
                                                                style={{ width: `${confidence * 100}%` }}
                                                            />
                                                        </div>
                                                        <span className="text-gray-600 w-12 text-right">
                                                            {(confidence * 100).toFixed(0)}%
                                                        </span>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Timestamp */}
                                {analysis.timestamp && (
                                    <div className="pt-4 border-t border-gray-200">
                                        <p className="text-xs text-gray-500">
                                            Analyzed: {new Date(analysis.timestamp).toLocaleString()}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Advice Card */}
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h2 className="text-xl font-semibold mb-4 flex items-center">
                                <Clock className="h-5 w-5 mr-2 text-blue-600" />
                                Investment Advice
                            </h2>

                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600">Recommended Action:</span>
                                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${advice.action === 'BUY' ? 'bg-green-100 text-green-800' :
                                            advice.action === 'SELL' ? 'bg-red-100 text-red-800' :
                                                'bg-yellow-100 text-yellow-800'
                                        }`}>
                                        {advice.action}
                                    </span>
                                </div>

                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600">Confidence:</span>
                                    <span className="font-semibold">
                                        {(advice.confidence * 100).toFixed(1)}%
                                    </span>
                                </div>

                                <div className="flex justify-between items-center">
                                    <span className="text-gray-600">Time Horizon:</span>
                                    <span className="font-semibold">{advice.time_horizon}</span>
                                </div>

                                <div>
                                    <h3 className="font-medium text-gray-600 mb-2">Reasoning:</h3>
                                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                                        {advice.reasoning.map((reason, index) => (
                                            <li key={index}>{reason}</li>
                                        ))}
                                    </ul>
                                </div>

                                {advice.risk_factors.length > 0 && (
                                    <div>
                                        <h3 className="font-medium text-gray-600 mb-2 flex items-center">
                                            <AlertTriangle className="h-4 w-4 mr-1 text-yellow-500" />
                                            Risk Factors:
                                        </h3>
                                        <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700">
                                            {advice.risk_factors.map((risk, index) => (
                                                <li key={index}>{risk}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Resources Section - News & Blogs */}
                {(newsArticles || blogPosts) && (
                    <div className="mt-8">
                        <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                            Resources Analyzed
                        </h2>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* News Articles */}
                            {newsArticles && newsArticles.articles && newsArticles.articles.length > 0 && (
                                <div className="bg-white rounded-lg shadow-md p-6">
                                    <h3 className="text-lg font-semibold mb-4 flex items-center">
                                        <Newspaper className="h-5 w-5 mr-2 text-blue-600" />
                                        News Articles ({newsArticles.articles.length})
                                    </h3>
                                    <div className="space-y-4 max-h-96 overflow-y-auto">
                                        {newsArticles.articles.slice(0, 10).map((article, index) => (
                                            <div key={index} className="border-b border-gray-200 pb-3 last:border-b-0">
                                                <a 
                                                    href={article.url} 
                                                    target="_blank" 
                                                    rel="noopener noreferrer"
                                                    className="group"
                                                >
                                                    <h4 className="font-medium text-gray-900 group-hover:text-blue-600 flex items-start gap-2">
                                                        {article.title}
                                                        <ExternalLink className="h-3 w-3 mt-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                                                    </h4>
                                                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                                                        {article.content}
                                                    </p>
                                                    <div className="flex items-center gap-2 mt-2">
                                                        <span className="text-xs text-gray-500">{article.source}</span>
                                                        <span className="text-xs text-gray-400">•</span>
                                                        <span className="text-xs text-gray-500">
                                                            {new Date(article.published).toLocaleDateString()}
                                                        </span>
                                                    </div>
                                                </a>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Blog Posts */}
                            {blogPosts && blogPosts.posts && blogPosts.posts.length > 0 && (
                                <div className="bg-white rounded-lg shadow-md p-6">
                                    <h3 className="text-lg font-semibold mb-4 flex items-center">
                                        <Globe className="h-5 w-5 mr-2 text-purple-600" />
                                        Blog Posts ({blogPosts.posts.length})
                                    </h3>
                                    <div className="space-y-4 max-h-96 overflow-y-auto">
                                        {blogPosts.posts.slice(0, 10).map((post, index) => (
                                            <div key={index} className="border-b border-gray-200 pb-3 last:border-b-0">
                                                <a 
                                                    href={post.url} 
                                                    target="_blank" 
                                                    rel="noopener noreferrer"
                                                    className="group"
                                                >
                                                    <h4 className="font-medium text-gray-900 group-hover:text-purple-600 flex items-start gap-2">
                                                        {post.title}
                                                        <ExternalLink className="h-3 w-3 mt-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                                                    </h4>
                                                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                                                        {post.content}
                                                    </p>
                                                    <div className="flex items-center gap-2 mt-2">
                                                        <span className="text-xs text-gray-500">
                                                            {new Date(post.published).toLocaleDateString()}
                                                        </span>
                                                    </div>
                                                </a>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Sample Symbols */}
                <div className="mt-12">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        Try analyzing these popular symbols:
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NFLX', 'NVDA'].map((sampleSymbol) => (
                            <button
                                key={sampleSymbol}
                                onClick={() => {
                                    setSymbol(sampleSymbol);
                                    // Trigger analysis after a short delay to let symbol update
                                    setTimeout(() => {
                                        document.querySelector('form button[type="submit"]').click();
                                    }, 100);
                                }}
                                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                            >
                                {sampleSymbol}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
