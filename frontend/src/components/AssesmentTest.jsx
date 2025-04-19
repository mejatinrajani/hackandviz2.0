// src/components/AssessmentTest.js
import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const AssessmentTest = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [testCompleted, setTestCompleted] = useState(false);
  const [testReport, setTestReport] = useState(null);
  
  // Sample questions - would come from backend in real implementation
  const questions = [
    {
      id: 1,
      question: "What is the most effective way to manage anxiety before public speaking?",
      options: [
        "Avoid thinking about the speech until the last minute",
        "Practice deep breathing and visualization techniques",
        "Memorize the entire speech word for word",
        "Consume caffeine to stay alert"
      ]
    },
    {
      id: 2,
      question: "When addressing a diverse audience, what should you prioritize?",
      options: [
        "Using complex technical terms to sound authoritative",
        "Using simple language accessible to everyone",
        "Speaking as fast as possible to cover more content",
        "Focusing only on the most important people in the room"
      ]
    },
    {
      id: 3,
      question: "Which element is most important for maintaining audience engagement?",
      options: [
        "Reading directly from slides or notes",
        "Speaking in a monotone voice for clarity",
        "Varying your tone, pace, and volume",
        "Avoiding all pauses or silence"
      ]
    },
    {
      id: 4,
      question: "What technique can help you recover if you lose your place during a presentation?",
      options: [
        "Apologize repeatedly for the mistake",
        "Pause, take a breath, and briefly summarize your last point",
        "End the presentation early",
        "Speed up to make up for lost time"
      ]
    },
    {
      id: 5,
      question: "How should you respond to challenging questions from your audience?",
      options: [
        "Dismiss questions that seem critical",
        "Listen carefully, acknowledge the question, and respond thoughtfully",
        "Answer quickly without reflection",
        "Defer all difficult questions to someone else"
      ]
    }
  ];
  
  const handleAnswer = (questionId, answerIndex) => {
    setAnswers({
      ...answers,
      [questionId]: answerIndex
    });
  };
  
  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };
  
  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };
  
  const submitTest = () => {
    // Check if all questions are answered
    if (Object.keys(answers).length < questions.length) {
      alert('Please answer all questions before submitting.');
      return;
    }
    
    // Generate report
    generateReport();
    setTestCompleted(true);
  };
  
  const generateReport = () => {
    // This would be replaced with actual backend logic
    // For now, we'll simulate a report
    
    // Correct answers for our sample questions (0-indexed)
    const correctAnswers = {
      1: 1, // Practice deep breathing
      2: 1, // Using simple language
      3: 2, // Varying tone
      4: 1, // Pause and summarize
      5: 1  // Listen and respond thoughtfully
    };
    
    let correctCount = 0;
    Object.keys(answers).forEach(questionId => {
      if (answers[questionId] === correctAnswers[questionId]) {
        correctCount++;
      }
    });
    
    const score = (correctCount / questions.length) * 100;
    
    let feedbackLevel;
    if (score >= 80) {
      feedbackLevel = "Excellent";
    } else if (score >= 60) {
      feedbackLevel = "Good";
    } else if (score >= 40) {
      feedbackLevel = "Average";
    } else {
      feedbackLevel = "Needs Improvement";
    }
    
    setTestReport({
      score,
      correctAnswers: correctCount,
      totalQuestions: questions.length,
      feedbackLevel,
      recommendations: getRecommendations(feedbackLevel),
      date: new Date().toLocaleDateString()
    });
  };
  
  const getRecommendations = (level) => {
    switch (level) {
      case "Excellent":
        return "You demonstrate strong knowledge of effective communication principles. Continue practicing these skills in real-world scenarios.";
      case "Good":
        return "You have a solid understanding of communication fundamentals. Focus on areas where you were unsure to strengthen your skills further.";
      case "Average":
        return "You have a basic grasp of communication concepts. Consider reviewing resources on public speaking and interpersonal communication.";
      case "Needs Improvement":
        return "You would benefit from studying communication principles more thoroughly. Consider taking a course or working with a speech coach.";
      default:
        return "";
    }
  };
  
  const downloadReport = () => {
    // In a real application, this would generate a PDF or other format
    // This is a placeholder for backend integration
    alert("Report download functionality will be integrated with backend");
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-xl font-semibold text-gray-800">Communication Skills Assessment</h1>
          <nav className="flex items-center space-x-4">
            <Link to="/test-interface" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
              Test Interface
            </Link>
            <Link to="/assessment" className="px-3 py-2 rounded-md text-sm font-medium text-blue-600 bg-blue-50">
              Assessment Test
            </Link>
            <button 
              onClick={() => {
                localStorage.removeItem('isLoggedIn');
                localStorage.removeItem('user');
                window.location.href = '/login';
              }}
              className="px-3 py-2 text-sm font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 transition duration-150"
            >
              Logout
            </button>
          </nav>
        </div>
      </header>
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!testCompleted ? (
          <div className="bg-white shadow rounded-lg p-6">
            <div className="relative mb-6">
              <div className="h-2 bg-gray-200 rounded-full">
                <div 
                  className="h-2 bg-blue-500 rounded-full" 
                  style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
                ></div>
              </div>
              <p className="mt-2 text-sm text-gray-600 text-center">
                Question {currentQuestion + 1} of {questions.length}
              </p>
            </div>
            
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                {questions[currentQuestion].question}
              </h2>
              
              <div className="space-y-3">
                {questions[currentQuestion].options.map((option, index) => (
                  <div 
                    key={index}
                    onClick={() => handleAnswer(questions[currentQuestion].id, index)}
                    className={`p-4 border rounded-lg cursor-pointer transition duration-150 ${
                      answers[questions[currentQuestion].id] === index 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start">
                      <div className={`flex items-center justify-center w-6 h-6 rounded-full mr-3 ${
                        answers[questions[currentQuestion].id] === index 
                          ? 'bg-blue-500 text-white' 
                          : 'bg-gray-200 text-gray-700'
                      }`}>
                        {String.fromCharCode(65 + index)}
                      </div>
                      <span className="text-gray-700">{option}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex justify-between">
              <button 
                onClick={prevQuestion}
                disabled={currentQuestion === 0}
                className={`px-4 py-2 rounded-md font-medium ${
                  currentQuestion === 0 
                    ? 'bg-gray-300 cursor-not-allowed text-gray-500' 
                    : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
                }`}
              >
                Previous
              </button>
              
              {currentQuestion < questions.length - 1 ? (
                <button 
                  onClick={nextQuestion}
                  className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150"
                >
                  Next
                </button>
              ) : (
                <button 
                  onClick={submitTest}
                  className="px-4 py-2 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-150"
                >
                  Submit Test
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-6 text-center">Assessment Results</h2>
            
            <div className="flex flex-col items-center mb-8">
              <div className="flex flex-col items-center justify-center w-40 h-40 rounded-full bg-blue-500 text-white shadow-lg mb-4">
                <span className="text-5xl font-bold">{Math.round(testReport.score)}</span>
                <span className="text-sm mt-1">Score</span>
              </div>
              
              <div className="text-center">
                <p className="font-semibold text-lg text-gray-800">{testReport.feedbackLevel}</p>
                <p className="text-gray-600">
                  {testReport.correctAnswers} out of {testReport.totalQuestions} correct
                </p>
                <p className="text-sm text-gray-500">Completed on {testReport.date}</p>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-6 mb-6">
              <h3 className="text-lg font-medium text-gray-800 mb-2">Recommendations</h3>
              <p className="text-gray-600">{testReport.recommendations}</p>
            </div>
            
            <div className="flex flex-col space-y-4">
              <button 
                onClick={downloadReport}
                className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150"
              >
                Download Full Report
              </button>
              
              <Link 
                to="/test-interface"
                className="w-full px-4 py-3 bg-gray-200 text-gray-800 font-medium rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition duration-150 text-center"
              >
                Go to Speech Test
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AssessmentTest;