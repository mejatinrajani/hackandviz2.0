import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import '../Stylesheets/UserDetailForm.css';

const steps = ['Step 1', 'Step 2', 'Step 3', 'Step 4'];

const UserDetailForm = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [question, setQuestion] = useState('');
  const [options, setOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const data = await Promise.resolve({
        question: 'How often do you feel anxious?',
        options: [
          { text: 'Rarely', image: '/img.png' },
          { text: 'Sometimes', image: '/img.png' },
          { text: 'Often', image: '/img.png' },
          { text: 'Always', image: '/img.png' },
        ],
      });
      setQuestion(data.question);
      setOptions(data.options);
      setSelectedOption(null); // Reset selection on step change
    };
    fetchData();
  }, [currentStep]);

  const handleNext = () => {
    if (currentStep < steps.length - 1) setCurrentStep(currentStep + 1);
  };

  const handlePrev = () => {
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  };

  return (
    <div className="container">
      <header className="header">
        <motion.div 
          className="logo" 
          initial={{ x: -100, opacity: 0 }} 
          animate={{ x: 0, opacity: 1 }} 
          transition={{ duration: 0.5 }}
        >
          <img src="/logo.png" alt="Logo" className="logo-img" />
        </motion.div>
        <motion.nav 
          className="nav" 
          initial={{ x: 100, opacity: 0 }} 
          animate={{ x: 0, opacity: 1 }} 
          transition={{ duration: 0.5 }}
        >
          <a href="#home">Home</a>
          <a href="#about">About</a>
          <a href="#features">Features</a>
          <a href="#contact">Contact</a>
        </motion.nav>
      </header>

      <motion.h1 
        className="title" 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        User Detail Questionnaire
      </motion.h1>

      <div className="progress-bar">
        {steps.map((step, index) => (
          <div className="step-container" key={index}>
            <motion.div
              className={`circle ${index <= currentStep ? 'active' : ''}`}
              initial={{ scale: 0 }}
              animate={{ 
                scale: 1,
                boxShadow: index <= currentStep ? '0 0 15px rgba(0,123,255,0.5)' : 'none'
              }}
              transition={{ 
                type: 'spring',
                stiffness: 200,
                damping: 20,
                delay: index * 0.1
              }}
            >
              {index + 1}
            </motion.div>
            {index < steps.length - 1 && (
              <motion.div
                className="line"
                initial={{ scaleX: 0 }}
                animate={{ 
                  scaleX: 1,
                  backgroundColor: index < currentStep ? '#007bff' : 'black'
                }}
                transition={{ duration: 0.5, delay: 0.2 }}
              />
            )}
          </div>
        ))}
      </div>

      <AnimatePresence mode='wait'>
        <motion.div
          key={currentStep}
          className="question-section"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -50, opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h2>{question}</h2>
          <div className="options">
            {options.map((option, idx) => (
              <motion.div
                className={`card ${selectedOption === idx ? 'selected' : ''}`}
                key={idx}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedOption(idx)}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.1 }}
              >
                <img src={option.image} alt={option.text} />
                <p>{option.text}</p>
                {selectedOption === idx && (
                  <motion.div
                    className="selection-indicator"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring' }}
                  />
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      </AnimatePresence>

      <div className="navigation-buttons">
        <motion.button 
          className="nav-btn"
          whileTap={{ scale: 0.95 }} 
          onClick={handlePrev} 
          disabled={currentStep === 0}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          Previous
        </motion.button>
        <motion.button 
          className="nav-btn"
          whileTap={{ scale: 0.95 }} 
          onClick={handleNext} 
          disabled={currentStep === steps.length - 1}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          Next
        </motion.button>
      </div>
    </div>
  );
};

export default UserDetailForm;