import React from 'react';
import { useParams } from 'react-router-dom';

const SymbolAnalysis = () => {
    const { symbol } = useParams();

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">
                    Analysis for {symbol}
                </h1>
                <p className="text-gray-600">
                    Detailed analysis page coming soon...
                </p>
            </div>
        </div>
    );
};

export default SymbolAnalysis;
