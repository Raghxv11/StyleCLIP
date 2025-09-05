import React, { useState, useEffect } from 'react';
import { getUserPreferences } from '../utils/api';

const UserProfile = ({ userId, onClose }) => {
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId) {
      fetchPreferences();
    }
  }, [userId]);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const data = await getUserPreferences(userId);
      setPreferences(data);
    } catch (error) {
      console.error('Error fetching preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading preferences...</p>
        </div>
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="text-center">
            <p className="text-red-600 mb-4">Error loading preferences</p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Sort preferences by score
  const sortedPreferences = Object.entries(preferences.preferences)
    .sort(([,a], [,b]) => b - a);

  const likedTags = sortedPreferences.filter(([, score]) => score > 0);
  const dislikedTags = sortedPreferences.filter(([, score]) => score < 0);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Your Style Profile</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{preferences.total_swipes}</div>
            <div className="text-sm text-gray-600">Total Swipes</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{preferences.likes}</div>
            <div className="text-sm text-gray-600">Likes</div>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{preferences.dislikes}</div>
            <div className="text-sm text-gray-600">Dislikes</div>
          </div>
        </div>

        {/* Liked Tags */}
        {likedTags.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              What you love
            </h3>
            <div className="flex flex-wrap gap-2">
              {likedTags.map(([tag, score]) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                  style={{ opacity: Math.min(1, 0.5 + Math.abs(score)) }}
                >
                  {tag} ({score.toFixed(2)})
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Disliked Tags */}
        {dislikedTags.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
              <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
              What you avoid
            </h3>
            <div className="flex flex-wrap gap-2">
              {dislikedTags.map(([tag, score]) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium"
                  style={{ opacity: Math.min(1, 0.5 + Math.abs(score)) }}
                >
                  {tag} ({score.toFixed(2)})
                </span>
              ))}
            </div>
          </div>
        )}

        {/* No preferences yet */}
        {sortedPreferences.length === 0 && (
          <div className="text-center py-8">
            <div className="text-gray-400 text-6xl mb-4">🎯</div>
            <h3 className="text-lg font-semibold text-gray-600 mb-2">No preferences yet</h3>
            <p className="text-gray-500">Start swiping to build your style profile!</p>
          </div>
        )}

        <div className="mt-6 text-center">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
