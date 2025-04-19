import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import TestInterface from './components/TestInterface.jsx';
import AssessmentTest from './components/AssesmentTest.jsx';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/test-interface"
            element={
                <TestInterface />
            }
          />
          <Route
            path="/assessment"
            element={
                <AssessmentTest />
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;