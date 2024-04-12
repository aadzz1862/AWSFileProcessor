import React from 'react';
import './App.css';
import UploadForm from './components/UploadForm';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>File Processor</h1>
      </header>
      <UploadForm />
    </div>
  );
}

export default App;