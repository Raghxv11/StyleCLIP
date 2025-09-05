import React, { useState, useRef } from 'react';

const SwipeCard = ({ item, onSwipe, onNext }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const cardRef = useRef(null);

  const handleStart = (clientX, clientY) => {
    setIsDragging(true);
    setStartPos({ x: clientX, y: clientY });
  };

  const handleMove = (clientX, clientY) => {
    if (!isDragging) return;
    
    const deltaX = clientX - startPos.x;
    const deltaY = clientY - startPos.y;
    setDragOffset({ x: deltaX, y: deltaY });
  };

  const handleEnd = () => {
    if (!isDragging) return;
    
    const threshold = 100;
    const rotation = dragOffset.x * 0.1;
    
    if (Math.abs(dragOffset.x) > threshold) {
      // Swipe detected
      const action = dragOffset.x > 0 ? 'like' : 'dislike';
      onSwipe(item.id, action);
    } else {
      // Return to center
      setDragOffset({ x: 0, y: 0 });
    }
    
    setIsDragging(false);
  };

  const handleMouseDown = (e) => {
    e.preventDefault();
    handleStart(e.clientX, e.clientY);
  };

  const handleMouseMove = (e) => {
    handleMove(e.clientX, e.clientY);
  };

  const handleMouseUp = () => {
    handleEnd();
  };

  const handleTouchStart = (e) => {
    const touch = e.touches[0];
    handleStart(touch.clientX, touch.clientY);
  };

  const handleTouchMove = (e) => {
    const touch = e.touches[0];
    handleMove(touch.clientX, touch.clientY);
  };

  const handleTouchEnd = () => {
    handleEnd();
  };

  const handleLike = () => {
    onSwipe(item.id, 'like');
  };

  const handleDislike = () => {
    onSwipe(item.id, 'dislike');
  };

  const rotation = dragOffset.x * 0.1;
  const opacity = Math.max(0.3, 1 - Math.abs(dragOffset.x) / 300);

  return (
    <div className="relative w-full max-w-sm mx-auto">
      <div
        ref={cardRef}
        className="relative bg-white rounded-2xl shadow-2xl overflow-hidden cursor-grab active:cursor-grabbing"
        style={{
          transform: `translate(${dragOffset.x}px, ${dragOffset.y}px) rotate(${rotation}deg)`,
          opacity: opacity,
          transition: isDragging ? 'none' : 'all 0.3s ease-out'
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Image */}
        <div className="relative h-96 bg-gray-200">
          {item.filename && (
            <img
              src={`http://localhost:8000/uploads/${item.filename}`}
              alt={item.filename}
              className="w-full h-full object-cover"
            />
          )}
          
          {/* Swipe indicators */}
          <div className={`absolute top-4 left-4 px-3 py-1 rounded-full text-white font-bold text-lg transform -rotate-12 ${
            dragOffset.x > 50 ? 'bg-green-500' : 'hidden'
          }`}>
            LIKE
          </div>
          <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-white font-bold text-lg transform rotate-12 ${
            dragOffset.x < -50 ? 'bg-red-500' : 'hidden'
          }`}>
            NOPE
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              {item.filename?.split('.')[0] || 'Clothing Item'}
            </h3>
            
            {item.reason && (
              <p className="text-sm text-blue-600 font-medium mb-2">
                {item.reason}
              </p>
            )}
            
            {item.similarity_score && (
              <div className="text-xs text-gray-500 mb-3">
                Match Score: {(item.similarity_score * 100).toFixed(0)}%
              </div>
            )}
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            {item.tags?.map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex justify-center gap-8 mt-6">
        <button
          onClick={handleDislike}
          className="w-14 h-14 bg-red-500 text-white rounded-full flex items-center justify-center shadow-lg hover:bg-red-600 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        <button
          onClick={handleLike}
          className="w-14 h-14 bg-green-500 text-white rounded-full flex items-center justify-center shadow-lg hover:bg-green-600 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default SwipeCard;
