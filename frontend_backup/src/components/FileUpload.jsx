import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { FiUploadCloud } from 'react-icons/fi';

const FileUpload = ({ onUploadSuccess, loading, setLoading }) => {
  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file || loading) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/upload-report', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      onUploadSuccess(response.data);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error uploading file. Please try again.');
      setLoading(false);
    }
  }, [onUploadSuccess, setLoading, loading]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: loading
  });

  return (
    <div className="upload-container">
      <div
        {...getRootProps()}
        className={`upload-box ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />

        {loading ? (
          <>
            <div className="spinner" />
            <div className="upload-text">Analyzing your report…</div>
            <div className="upload-hint">This may take a few moments</div>
          </>
        ) : (
          <>
            <FiUploadCloud className="upload-icon" />
            <div className="upload-text">
              {isDragActive ? 'Drop your PDF here' : 'Drag & drop your medical report'}
            </div>
            <div className="upload-hint">or click to browse (PDF only)</div>
          </>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
