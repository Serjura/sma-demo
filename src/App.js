import React, { useState } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [predictions, setPredictions] = useState([]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setPredictions([]); // Clear predictions when a new file is selected
  };

  const handlePredict = async () => {
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        const response = await fetch('http://max-human-pose-estimator:5000/model/predict', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          setPredictions(data.predictions);
        } else {
          console.error('Error predicting', response.statusText);
        }
      } catch (error) {
        console.error('Error predicting', error);
      }
    }
  };

  return (
    <div className="App">
      <h1>AI Pose Detection</h1>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button onClick={handlePredict}>Predict</button>
      {selectedFile && <img src={URL.createObjectURL(selectedFile)} alt="Uploaded" />}

      <div className="overlay">
        {predictions.map((prediction, index) => (
          <div key={index}>
            {prediction.pose_lines.map((line, lineIndex) => (
              <div
                key={lineIndex}
                className="line"
                style={{
                  left: line.line[0],
                  top: line.line[1],
                  width: Math.abs(line.line[2] - line.line[0]),
                  height: Math.abs(line.line[3] - line.line[1]),
                }}
              ></div>
            ))}
            {prediction.body_parts.map((part, partIndex) => (
              <div
                key={partIndex}
                className="body-part"
                style={{ left: part.x, top: part.y }}
              >
                {part.part_name}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
