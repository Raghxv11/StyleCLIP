# StyleCLIP Tinder-like App

A Tinder-style clothing recommendation app that learns user preferences through swiping and provides personalized recommendations.

## 🎯 Features

### Core Functionality
- **Swipe Interface**: Like/dislike clothing items with smooth animations
- **Preference Learning**: System learns from user swiping patterns
- **Personalized Feed**: Recommendations based on learned preferences
- **User Profiles**: View your style preferences and statistics
- **Dual Mode**: Switch between Tinder-style swiping and traditional upload/analyze

### Technical Features
- **Real-time Learning**: Preferences update with each swipe
- **Smart Recommendations**: Items ranked by preference scores
- **Visual Feedback**: Swipe indicators and match scores
- **Responsive Design**: Works on desktop and mobile
- **Persistent Sessions**: User preferences saved across sessions

## 🚀 Quick Start

### 1. Initialize Database
```bash
cd backend
python -m app.scripts.init_tinder_db
```

### 2. Start Backend
```bash
cd backend
uvicorn app.server:app --reload
```

### 3. Start Frontend
```bash
cd frontend
npm start
```

### 4. Access the App
- Open http://localhost:3000
- Choose "Style Swiper" mode
- Create an account and start swiping!

## 📱 How to Use

### Getting Started
1. **Create Account**: Enter username and email
2. **Start Swiping**: Swipe right to like, left to dislike
3. **View Profile**: Click profile icon to see your preferences
4. **Get Recommendations**: System learns and improves over time

### Swiping Interface
- **Swipe Right**: Like the item (❤️)
- **Swipe Left**: Dislike the item (❌)
- **Tap Buttons**: Use the like/dislike buttons
- **Drag to Swipe**: Drag the card to see swipe indicators

### Understanding Recommendations
- **Match Score**: Shows how well the item matches your preferences
- **Reason**: Explains why the item was recommended
- **Tags**: Visual tags showing item characteristics

## 🧠 How It Works

### Preference Learning Algorithm
1. **Initial State**: User starts with no preferences
2. **Swipe Recording**: Each swipe updates preference scores
3. **Score Calculation**: Tags get +0.1 for likes, -0.1 for dislikes
4. **Normalization**: Scores kept between -1.0 and 1.0
5. **Recommendation**: Items ranked by weighted preference scores

### Recommendation Engine
```python
# Simplified algorithm
for item in available_items:
    score = 0
    matched_tags = 0
    for tag in item.tags:
        if tag in user_preferences:
            score += user_preferences[tag]
            matched_tags += 1
    
    if matched_tags > 0:
        final_score = score / matched_tags
    else:
        final_score = 0
```

### Database Schema
- **users**: User accounts with preference scores
- **swipes**: Individual swipe records
- **clothing_items**: Clothing items with tags and embeddings

## 🔧 API Endpoints

### User Management
- `POST /clothing/users` - Create new user
- `GET /clothing/users/{user_id}/preferences` - Get user preferences
- `GET /clothing/users/{user_id}/feed` - Get personalized feed
- `GET /clothing/users/{user_id}/next` - Get next item to swipe

### Swiping
- `POST /clothing/swipe` - Record a swipe action

### Original Features (Still Available)
- `POST /clothing/upload` - Upload and analyze clothing
- `GET /clothing/similar/{item_id}` - Get similar items
- `POST /clothing/tag` - Tag clothing image

## 🎨 UI Components

### SwipeCard
- Draggable card with swipe animations
- Visual feedback for like/dislike
- Tag display and match scores
- Touch and mouse support

### UserProfile
- Preference visualization
- Swipe statistics
- Liked/disliked tags with scores
- Clean, modern design

### TinderApp
- Main app container
- Login/signup flow
- Mode switching
- Error handling

## 📊 Data Flow

1. **User Creation**: New user account created
2. **Item Loading**: System fetches next item to swipe
3. **Swipe Recording**: User action recorded in database
4. **Preference Update**: User preferences updated based on swipe
5. **Next Item**: System calculates and serves next best item
6. **Learning Loop**: Process repeats, improving recommendations

## 🔮 Future Enhancements

### Planned Features
- **Social Features**: Share outfits, follow friends
- **Advanced ML**: Deep learning for better recommendations
- **Categories**: Filter by clothing type, brand, price
- **Wishlist**: Save liked items for later
- **Trends**: Show popular items and trends

### Technical Improvements
- **Caching**: Redis for better performance
- **Real-time**: WebSocket updates for live recommendations
- **Analytics**: User behavior tracking and insights
- **A/B Testing**: Test different recommendation algorithms

## 🐛 Troubleshooting

### Common Issues
1. **No items showing**: Check if clothing_items collection has data
2. **Swipes not recording**: Verify database connection
3. **Poor recommendations**: User needs more swipe history
4. **UI not responsive**: Check browser console for errors

### Debug Mode
```bash
# Backend with debug logging
uvicorn app.server:app --reload --log-level debug

# Frontend with detailed errors
REACT_APP_DEBUG=true npm start
```

## 📈 Performance

### Optimization Tips
- **Batch Processing**: Process multiple swipes at once
- **Indexing**: Proper database indexes for fast queries
- **Caching**: Cache frequently accessed data
- **Lazy Loading**: Load items as needed

### Monitoring
- Track user engagement metrics
- Monitor recommendation accuracy
- Measure system performance
- Analyze user preference patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy Swiping! 🎉**

Transform your style discovery with StyleCLIP's intelligent recommendation system.

python3 -m backend.app.scripts.reset_user_preferences 68bb595b32342cc4cdd5ee61