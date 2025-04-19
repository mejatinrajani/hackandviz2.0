import React, { useState } from 'react';
import '../Stylesheets/Dashboard.css';

const Dashboard = () => {
  const [selectedMood, setSelectedMood] = useState(null);
  const [reflectionText, setReflectionText] = useState('');

  const moodEmojis = [
    { emoji: '😄', id: 'happy' },
    { emoji: '😔', id: 'sad' },
    { emoji: '😑', id: 'neutral' },
    { emoji: '🙂', id: 'pleased' },
    { emoji: '😊', id: 'content' }
  ];

  const handleMoodSelect = (id) => {
    setSelectedMood(id);
  };

  const features = [
    {
      title: 'AI ChatBot',
      icon: '🤖',
      description: 'Chat with an AI to share feelings, receive emotional support, and discover helpful mental health solutions.'
    },
    {
      title: 'Grief-Support Poet',
      icon: '📝',
      description: 'Share your loss, and the AI poet gently creates personalized poems to express your emotions.'
    },
    {
      title: 'Music For Mood Enhancement',
      icon: '🎵',
      description: 'AI generates personalized music tracks based on your mood to uplift, calm, or comfort you.'
    },
    {
      title: 'Mental Health Questionnaire',
      icon: '❓',
      description: 'Diagnose emotional states through guided questions, with AI support and real-time emotion detection insights.'
    }
  ];

  return (
    <div className="dashboard">
      <div className="navbar">
        <div className="logo-container">
          <img src="/api/placeholder/60/60" alt="Logo" className="logo" />
        </div>
        <div className="nav-links">
          <span className="nav-link active">Home</span>
          <span className="nav-link">About</span>
          <span className="nav-link">Features</span>
          <span className="nav-link">Contact</span>
          <div className="profile-circle">
            <img src="/api/placeholder/40/40" alt="Profile" className="profile-pic" />
          </div>
        </div>
      </div>

      <div className="content">
        <div className="welcome-section">
          <div className="welcome-text">
            <h1>Welcome Back, <br />Akshat</h1>
            <p>How was your day?</p>
            <div className="mood-selector">
              {moodEmojis.map((mood) => (
                <span 
                  key={mood.id} 
                  className={`mood-emoji ${selectedMood === mood.id ? 'selected' : ''}`}
                  onClick={() => handleMoodSelect(mood.id)}
                >
                  {mood.emoji}
                </span>
              ))}
            </div>
          </div>

          <div className="quick-actions">
            <div className="action-card therapist-finder">
              <h3>Find a Therapist Who Understands You <span className="arrow">→</span></h3>
              <p>Based on your recent mood and questionnaire results, here are therapists near you who can help.</p>
            </div>
          </div>
        </div>

        <div className="middle-section">
          <div className="quote-box">
            <h3>Daily Mental Health Quote 💡</h3>
            <p>"You don't have to control your thoughts. You just have to stop letting them control you."</p>
            <p className="quote-author">— Dan Millman</p>
          </div>

          <div className="reflection-box">
            <h3>Mini Journal <br />Reflection Box 📝</h3>
            <textarea 
              placeholder="What's something that made you smile this week???" 
              value={reflectionText}
              onChange={(e) => setReflectionText(e.target.value)}
            ></textarea>
            <div className="counselor-note">
              <p>Need a 1-minute reset?<br />Breathe with us.</p>
            </div>
          </div>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div className="feature-card" key={index}>
              <div className="feature-header">
                <h3>{feature.title}</h3>
                <span className="arrow-circle">→</span>
              </div>
              <div className="feature-icon">
                {feature.icon === '🤖' && <div className="robot-icon"><span>👀</span></div>}
                {feature.icon === '📝' && <div className="paper-icon"></div>}
                {feature.icon === '🎵' && <div className="music-icon"></div>}
                {feature.icon === '❓' && <div className="question-icon">?</div>}
              </div>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="health-report">
          <div className="report-header">
            <h2>Mental Health Report</h2>
          </div>
          <div className="report-content">
            <div className="report-image">
              <img src="/api/placeholder/120/120" alt="User" className="user-image" />
            </div>
            <div className="report-details">
              <p><strong>Name:</strong> Akshat Saxena</p>
              <p><strong>Diagnosis:</strong> <span className="not-completed">❌ Not Completed</span></p>
              <div className="report-message">
                <span className="red-dot"></span>
                <p>"You haven't completed the mental health questionnaire yet. Get personalized insights and tools by completing your emotional check-up."</p>
              </div>
              <button className="diagnosis-button">Get Diagnosis Now →</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;