import React, { useState, useRef } from 'react';
import { Link } from 'react-router-dom';

const TestInterface = () => {
  const [textInput, setTextInput] = useState('');
  const [audioRecording, setAudioRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState('');
  const [videoFile, setVideoFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [testResults, setTestResults] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startAudioRecording = async () => {
    audioChunksRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setAudioRecording(true);
    } catch (err) {
      console.error('Audio recording error:', err);
    }
  };

  const stopAudioRecording = () => {
    if (mediaRecorderRef.current && audioRecording) {
      mediaRecorderRef.current.stop();
      setAudioRecording(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); // Ensure form doesn't redirect
    if (!textInput || !audioBlob || !videoFile) return;

    setIsSubmitting(true);
    setTestResults(null);

    const token = localStorage.getItem('token');

    try {
      // 1. Send text input
      const textResponse = await fetch('/api/sentiment/text/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ text: textInput }),
      });
      const textData = await textResponse.json();
      if (!textResponse.ok) throw new Error(textData.error || 'Text analysis failed');
      const textPrediction = textData.text_prediction;

      // 2. Send audio blob
      const audioForm = new FormData();
      audioForm.append('audio', audioBlob, 'audio.wav');
      const audioResponse = await fetch('/api/sentiment/audio/', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: audioForm,
      });
      const audioData = await audioResponse.json();
      if (!audioResponse.ok) throw new Error(audioData.error || 'Audio analysis failed');
      const audioPrediction = audioData.audio_prediction;

      // 3. Send video file
      const videoForm = new FormData();
      videoForm.append('video', videoFile, 'video.mp4');
      const videoResponse = await fetch('/api/emotion/analyze-video/', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: videoForm,
      });
      const videoData = await videoResponse.json();
      if (!videoResponse.ok) throw new Error(videoData.error || 'Video analysis failed');
      const videoPrediction = videoData.video_prediction;

      // 4. Send combined results to /final/predict/
      const finalForm = new FormData();
      finalForm.append('text_prediction', textPrediction);
      finalForm.append('audio_prediction', audioPrediction);
      finalForm.append('video_prediction', videoPrediction);

      const finalResponse = await fetch('/final/predict/', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: finalForm,
      });
      const finalData = await finalResponse.json();
      if (!finalResponse.ok) throw new Error(finalData.error || 'Final prediction failed');

      setTestResults({
        score: finalData.final_prediction ? 85 : 0,
        analysis: finalData.message.split('\n')[0],
        recommendations: finalData.message.split('\n')[1],
        recommendedTest: finalData.recommended_test,
        predictionId: finalData.prediction_id,
        clinicalTest: finalData.clinical_test,
      });

    } catch (err) {
      console.error('Submission error:', err);
      setTestResults({
        score: 0,
        analysis: 'Error processing your test',
        recommendations: `Please try again later: ${err.message}`,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-xl font-semibold text-gray-800">Speech Evaluation Test</h1>
          <nav className="flex items-center space-x-4">
            <Link
              to="/test-interface"
              className="px-3 py-2 rounded-md text-sm font-medium text-blue-600 bg-blue-50"
            >
              Test Interface
            </Link>
            <Link
              to="/assessment"
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              Assessment Test
            </Link>
            <button
              onClick={() => {
                localStorage.removeItem('token');
                window.location.href = '/login';
              }}
              className="px-3 py-2 text-sm font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50"
            >
              Logout
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label htmlFor="text-input" className="block mb-2 text-sm font-medium text-gray-700">
                Text Prompt:
              </label>
              <textarea
                id="text-input"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Enter text to read aloud..."
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md h-32 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="mb-6">
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Audio Recording:
              </label>
              <div className="space-y-4">
                {!audioRecording ? (
                  <button
                    type="button"
                    onClick={startAudioRecording}
                    className="px-4 py-2 bg-green-600 text-white font-medium rounded-md hover:bg-green-700"
                  >
                    Start Audio Recording
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={stopAudioRecording}
                    className="px-4 py-2 bg-red-600 text-white font-medium rounded-md hover:bg-red-700"
                  >
                    Stop Audio Recording
                  </button>
                )}
                {audioUrl && (
                  <audio src={audioUrl} controls className="w-full mt-4" />
                )}
              </div>
            </div>

            <div className="mb-6">
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Upload Video:
              </label>
              <input
                type="file"
                accept="video/*"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    setVideoFile(file);
                    setVideoUrl(URL.createObjectURL(file));
                  }
                }}
                required
                className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {videoUrl && (
                <video src={videoUrl} controls className="w-full mt-4 rounded-lg shadow" />
              )}
            </div>
            <div className="flex justify-center">
              <button
                type="submit"
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 w-full disabled:opacity-50"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Test'}
              </button>
            </div>
          </form>
        </div>

        {testResults && (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-xl font-semibold text-gray-800">Test Results</h3>
            <div className="mt-4">
              <p><strong>Score:</strong> {testResults.score}</p>
              <p><strong>Analysis:</strong> {testResults.analysis}</p>
              <p><strong>Recommendations:</strong> {testResults.recommendations}</p>
              <p><strong>Recommended Test:</strong> {testResults.recommendedTest}</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default TestInterface;
