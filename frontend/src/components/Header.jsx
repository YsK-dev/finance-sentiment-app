import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { TrendingUp, Youtube, Home } from 'lucide-react';

const Header = () => {
    const location = useLocation();

    return (
        <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center">
                        <TrendingUp className="h-8 w-8 text-green-600" />
                        <span className="ml-2 text-xl font-bold text-gray-900">
                            FinanceSentiment
                        </span>
                    </div>

                    <nav className="flex space-x-8">
                        <Link
                            to="/"
                            className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${location.pathname === '/'
                                    ? 'text-green-600 bg-green-50'
                                    : 'text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            <Home className="h-4 w-4 mr-1" />
                            Dashboard
                        </Link>
                        <Link
                            to="/youtube"
                            className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${location.pathname === '/youtube'
                                    ? 'text-green-600 bg-green-50'
                                    : 'text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            <Youtube className="h-4 w-4 mr-1" />
                            YouTube Analysis
                        </Link>
                    </nav>
                </div>
            </div>
        </header>
    );
};

export default Header;
