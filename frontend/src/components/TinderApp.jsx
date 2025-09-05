import React, { useState, useEffect } from 'react';
import SwipeCard from './SwipeCard';
import UserProfile from './UserProfile';
import { createUser, swipeItem, getNextItem } from '../utils/api';

const TinderApp = () => {
  const [userId, setUserId] = useState(null);
  const [currentItem, setCurrentItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showProfile, setShowProfile] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [showLogin, setShowLogin] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const savedUserId = localStorage.getItem('userId');
    if (savedUserId) {
      setUserId(savedUserId);
      setShowLogin(false);
      loadNextItem(savedUserId);
    } else {
      // For testing, auto-login with test user
      setUserId('68bb595b32342cc4cdd5ee61');
      setShowLogin(false);
      loadNextItem('68bb595b32342cc4cdd5ee61');
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username.trim() || !email.trim()) {
      setError('Please enter both username and email');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await createUser(username.trim(), email.trim());
      setUserId(response.user_id);
      localStorage.setItem('userId', response.user_id);
      setShowLogin(false);
      loadNextItem(response.user_id);
    } catch (error) {
      setError('Failed to create account. Please try again.');
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadNextItem = async (userId) => {
    try {
      setLoading(true);
      const response = await getNextItem(userId);
      if (response.id) {
        setCurrentItem(response);
      } else {
        setCurrentItem(null);
      }
    } catch (error) {
      console.error('Error loading next item:', error);
      setError('Failed to load items. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSwipe = async (itemId, action) => {
    try {
      await swipeItem(userId, itemId, action);
      // Load next item after swipe
      loadNextItem(userId);
    } catch (error) {
      console.error('Error recording swipe:', error);
      setError('Failed to record swipe. Please try again.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('userId');
    setUserId(null);
    setCurrentItem(null);
    setShowLogin(true);
    setUsername('');
    setEmail('');
    setError(null);
  };

  if (showLogin) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-400 via-red-500 to-yellow-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">StyleCLIP</h1>
            <p className="text-gray-600">Swipe your way to perfect style</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                placeholder="Enter your username"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                placeholder="Enter your email"
                required
              />
            </div>

            {error && (
              <div className="text-red-600 text-sm text-center">{error}</div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-pink-500 to-red-500 text-white py-3 rounded-lg font-semibold hover:from-pink-600 hover:to-red-600 transition-all duration-200 disabled:opacity-50"
            >
              {loading ? 'Creating Account...' : 'Start Swiping'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-400 via-red-500 to-yellow-500 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading your next style...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-400 via-red-500 to-yellow-500">
      {/* Header */}
      <div className="bg-white bg-opacity-20 backdrop-blur-sm p-4">
        <div className="max-w-md mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">StyleCLIP</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setShowProfile(true)}
              className="p-2 bg-white bg-opacity-20 rounded-full text-white hover:bg-opacity-30 transition-all"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </button>
            <button
              onClick={handleLogout}
              className="p-2 bg-white bg-opacity-20 rounded-full text-white hover:bg-opacity-30 transition-all"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4">
        {currentItem ? (
          <SwipeCard
            item={currentItem}
            onSwipe={handleSwipe}
          />
        ) : (
          <div className="text-center text-white">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-2xl font-bold mb-2">You've seen everything!</h2>
            <p className="text-lg opacity-90">Check back later for new items</p>
            <button
              onClick={() => loadNextItem(userId)}
              className="mt-4 px-6 py-3 bg-white bg-opacity-20 rounded-lg hover:bg-opacity-30 transition-all"
            >
              Refresh
            </button>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="fixed bottom-4 left-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg">
          <div className="flex justify-between items-center">
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-4 text-white hover:text-gray-200"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* User Profile Modal */}
      {showProfile && (
        <UserProfile
          userId={userId}
          onClose={() => setShowProfile(false)}
        />
      )}
    </div>
  );
};

export default TinderApp;
