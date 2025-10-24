import React, { useState } from 'react';
import { Play, AlertCircle } from 'lucide-react';
import { analyzeYouTubeVideo } from '../services/api';

const YouTubeAnalyzer = () => {
    const [videoUrl, setVideoUrl] = useState('');
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const extractVideoId = (url) => {
        const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
        const match = url.match(regex);
        return match ? match[1] : null;
    };

    const handleAnalyze = async (e) => {
        e.preventDefault();
        const videoId = extractVideoId(videoUrl);

        if (!videoId) {
            setError('Please enter a valid YouTube URL');
            return;
        }

        setLoading(true);
        setError('');
        setAnalysis(null);

        try {
            const result = await analyzeYouTubeVideo(videoId);
            setAnalysis(result);
        } catch (err) {
            console.error('YouTube analysis error:', err);
            
            // Provide more specific error messages
            if (err.response?.status === 404) {
                setError('This video does not have captions/transcripts available, or they may only be available in other languages. Please try a different video with English captions.');
            } else if (err.response?.status === 500) {
                setError(err.response?.data?.detail || 'Failed to analyze video. The video may not have transcripts available.');
            } else if (err.message?.includes('Network Error')) {
                setError('Cannot connect to the server. Make sure the backend is running.');
            } else {
                setError('Failed to analyze video. Please check the URL and try again, or try a different video.');
            }
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

    return (
        <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        YouTube Video Analysis
                    </h1>
                    <p className="text-lg text-gray-600">
                        Analyze financial content from YouTube videos using AI sentiment analysis
                    </p>
                </div>

                <form onSubmit={handleAnalyze} className="mb-8">
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <input
                                type="text"
                                value={videoUrl}
                                onChange={(e) => setVideoUrl(e.target.value)}
                                placeholder="Paste YouTube video URL here..."
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            />
                            <p className="mt-2 text-sm text-gray-500">
                                📌 Note: Video must have English captions/transcripts available
                            </p>
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 flex items-center"
                        >
                            <Play className="h-5 w-5 mr-2" />
                            {loading ? 'Analyzing...' : 'Analyze Video'}
                        </button>
                    </div>
                </form>

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
                        <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
                        <p className="text-red-700">{error}</p>
                    </div>
                )}

                {analysis && (
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h3 className="font-medium text-gray-600 mb-2">Video Information</h3>
                                <p className="text-sm text-gray-500 mb-1">Video ID: {analysis.video_id}</p>
                                <p className="text-sm text-gray-500">
                                    Transcript Preview: {analysis.transcript_preview}
                                </p>
                            </div>

                            <div>
                                <h3 className="font-medium text-gray-600 mb-2">Sentiment Analysis</h3>
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span>Overall Sentiment:</span>
                                        <span className={`px-2 py-1 rounded text-sm ${getSentimentColor(analysis.sentiment.sentiment)}`}>
                                            {analysis.sentiment.sentiment.toUpperCase()}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Confidence:</span>
                                        <span className="font-semibold">
                                            {(analysis.sentiment.confidence * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Positive Score:</span>
                                        <span>{(analysis.sentiment.raw_scores.positive * 100).toFixed(1)}%</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Negative Score:</span>
                                        <span>{(analysis.sentiment.raw_scores.negative * 100).toFixed(1)}%</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Neutral Score:</span>
                                        <span>{(analysis.sentiment.raw_scores.neutral * 100).toFixed(1)}%</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Embedded Video */}
                        <div className="mt-6">
                            <h3 className="font-medium text-gray-600 mb-2">Video Preview</h3>
                            <div className="aspect-w-16 aspect-h-9">
                                <iframe
                                    src={`https://www.youtube.com/embed/${analysis.video_id}`}
                                    title="YouTube video player"
                                    frameBorder="0"
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowFullScreen
                                    className="w-full h-64 rounded-lg"
                                ></iframe>
                            </div>
                        </div>
                    </div>
                )}

                {/* Instructions */}
                <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="font-semibold text-blue-900 mb-2">How to use:</h3>
                    <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
                        <li>Copy the URL of any YouTube video with financial content</li>
                        <li>Paste the URL in the input field above</li>
                        <li>Click "Analyze Video" to get sentiment analysis of the transcript</li>
                        <li>Works best with earnings calls, financial news, and analysis videos</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default YouTubeAnalyzer;
