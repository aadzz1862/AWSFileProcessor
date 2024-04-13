// src/components/UploadForm.js

import React, { useState } from 'react';
// import AWS from 'aws-sdk';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import axios from 'axios';

const UploadForm = () => {
  const [inputText, setInputText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  const handleTextInputChange = (event) => {
    setInputText(event.target.value);
  };

  const handleFileInputChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (selectedFile) {

      const bucket_name = 'pocprojectbucket';

      const apiGatewayUrl_SignedUrl = 'https://35v451qfkc.execute-api.us-east-2.amazonaws.com/dev/s3-signedurl';
      const apiKey = '1L1KKXWm3X3IBbuvsmBn55t8gH0JQdzl2OIB5rxe'; 

      try {

        // Define headers for the request
        const config = {
          headers: {
              'x-api-key': apiKey, 
              'Content-Type': 'application/json' 
          }
        };

        const getSignedUrl = async (fileName, contentType) => {
          const response = await axios.post(apiGatewayUrl_SignedUrl, {
            fileName,
            contentType
          }, config);

          return response.data.url;
        };


        const uploadFile = async (file) => {
          const url = await getSignedUrl(file.name, file.type);

          // PUT request: upload file to S3
          const result = await fetch(url, {
            method: "PUT",
            body: file,
          });


        };

        uploadFile(selectedFile);

        // Show success notification
        toast.success('File uploaded successfully !', {
          autoClose: 3000, // Close after 3 seconds
        });

        const s3Path = `s3://${bucket_name }/${selectedFile.name}`;

        
        const apiGatewayUrl_fileinfo = 'https://08lgx212oh.execute-api.us-east-2.amazonaws.com/dev/fileprocessor';
        

        const apiResponse = await fetch(apiGatewayUrl_fileinfo, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': apiKey,
          },
          body: JSON.stringify({
            input_text: inputText, 
            input_file_path: s3Path,
          }),
        });

        if (!apiResponse.ok) {
          throw new Error(`HTTP error! status: ${apiResponse.status}`);
        }

        const apiData = await apiResponse.json();
        console.log('Data saved to DynamoDB:', apiData);
        // alert('File information saved successfully!');

        // Show success notification
        toast.success('Input information saved successfully!', {
          autoClose: 3000, // Close after 3 seconds
        });

        // Reset input text and chosen file after successful upload and save
        setInputText('');
        setSelectedFile(null);
        document.getElementById('file-input').value = '';


      } catch (err) {
        console.error('Error:', err);
        alert('Error uploading file or saving data: ' + err.message);
      }
    } else {
      alert('Please select a file to upload.');
    }
  };

  return (
    <div class="container">
  <div class="form-box">
    <form onSubmit={handleSubmit}>
      <label for="text-input">Text input:</label>
      <input
        id="text-input"
        type="text"
        value={inputText}
        onChange={handleTextInputChange}
        placeholder="Enter text here"
      />
      <br />
      <label for="file-input">File input:</label>
      <input
        id="file-input"
        type="file"
        onChange={handleFileInputChange}
      />
      <br />
      <button type="submit">Submit</button>
      <br/>
      <ToastContainer />
    </form>
  </div>
</div>
  );
};

export default UploadForm;
