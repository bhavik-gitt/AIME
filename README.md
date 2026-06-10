AIME - AI Mental Emotion Recognition System
<div align="center">










🎭 Real-Time Audio & Video Emotion Recognition using Deep Learning
</div>
📖 Overview

AIME (AI Mental Emotion Recognition System) is a deep learning-powered platform that detects human emotions using both voice and facial expressions.

The system analyzes audio and video inputs in real time, predicts emotions, provides confidence scores, and delivers emotion-based recommendations.

AIME combines:

🎤 Audio Emotion Recognition
🎥 Video Emotion Recognition
📊 Analytics Dashboard
🧠 Emotion Insights
🌐 Web-Based Interface
🎯 Problem Statement

Mental and emotional states are often difficult to identify in real time.

AIME aims to provide an intelligent system capable of automatically detecting emotions through speech and facial expressions using Artificial Intelligence and Deep Learning.

✨ Key Features
🎤 Audio Emotion Recognition
Upload audio files
Live microphone support
Emotion prediction
Confidence score visualization
Supported Emotions
Happy 😊
Sad 😔
Angry 😠
Fear 😨
Neutral 😐
Disgust 🤢
🎥 Video Emotion Recognition
Real-time webcam detection
Facial emotion classification
Confidence score display
Live prediction system
Supported Emotions
Neutral 😐
Calm 😌
Happy 😊
Sad 😔
Angry 😠
Fear 😨
Disgust 🤢
Surprise 😲
📊 Analytics Dashboard
Confusion Matrix
Classification Report
Accuracy Curves
Loss Curves
ROC-AUC Curves
Class Distribution Analysis
💡 Emotion-Based Recommendations

The system provides intelligent suggestions based on detected emotions.

Examples:

Emotion	Suggestion
Sad	Talk to a friend or family member
Angry	Practice deep breathing exercises
Fear	Try grounding techniques
Happy	Keep doing activities you enjoy
Neutral	Maintain a healthy routine
🏗️ System Architecture
User Input
     │
     ▼
Audio / Video Acquisition
     │
     ▼
Feature Extraction
     │
     ├── MFCC
     ├── Log-Mel Spectrogram
     └── Facial Features
     │
     ▼
Deep Learning Models
     │
     ▼
Emotion Prediction
     │
     ▼
Confidence Score
     │
     ▼
Recommendations & Insights
🧠 Deep Learning Models
Audio Model
Dataset

CREMA-D Dataset

Feature Extraction
MFCC
Log-Mel Spectrograms
Architecture
Input
 │
Conv2D
 │
BatchNormalization
 │
MaxPooling
 │
Dropout
 │
Dense Layers
 │
Softmax
Video Model
Dataset

RAVDESS Dataset

Architecture
MobileNetV2
      │
Global Average Pooling
      │
Dense Layer
      │
Softmax
Why MobileNetV2?
Lightweight
Fast inference
High accuracy
Suitable for real-time applications
📂 Dataset Information
🎤 CREMA-D

Used for Audio Emotion Recognition.

Contains:

7,000+ audio samples
Multiple speakers
Various emotional expressions
🎥 RAVDESS

Used for Video Emotion Recognition.

Contains:

Facial emotion videos
Speech-based emotional expressions
Multiple emotion categories
📈 Model Evaluation

The models were evaluated using:

Accuracy
Precision
Recall
F1-Score
ROC-AUC
Confusion Matrix
📸 Project Screenshots
Dashboard

Add dashboard screenshot here

![Dashboard](assets/dashboard.png)
Audio Emotion Detection

Add screenshot here

![Audio Detection](assets/audio_ui.png)
Video Emotion Detection

Add screenshot here

![Video Detection](assets/video_ui.png)
Analytics Dashboard

Add screenshot here

![Analytics](assets/analytics.png)
🛠️ Tech Stack
Programming Language
Python 3.10
Deep Learning
TensorFlow
Keras
Audio Processing
Librosa
SoundFile
PyAudio
Computer Vision
OpenCV
MTCNN
Web Development
Flask
HTML
CSS
JavaScript
Data Analysis
Pandas
NumPy
Scikit-Learn
Visualization
Matplotlib
Seaborn
📁 Project Structure
PROJECT
│
├── assets/
├── data/
├── dataset/
│   ├── CREMA-D/
│   └── RAVDESS/
│
├── models/
│   ├── audio_emotion_model.h5
│   ├── video_emotion_model.h5
│   └── audio_classes.npy
│
├── src/
│   ├── train_audio.py
│   ├── train_video.py
│   ├── predict_audio.py
│   ├── predict_video.py
│   ├── live_audio_emotion.py
│   ├── live_video_emotion.py
│   ├── evaluate_audio.py
│   └── evaluate_video.py
│
├── webapp/
│
├── requirements.txt
│
└── README.md
🚀 Installation
git clone https://github.com/yourusername/AIME.git

cd AIME

Create Virtual Environment

python -m venv venv

Activate

venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt
▶️ Run Project
Audio Recognition
python src/live_audio_emotion.py
Video Recognition
python src/live_video_emotion.py
Flask Web Application
cd webapp

python app.py
🔮 Future Scope
🤖 AI Mental Health Chatbot
📞 Tele-MANAS Integration
🗺️ Therapist Finder
📅 Appointment Booking
📊 Emotion History Tracking
☁️ Cloud Deployment
📱 Mobile Application
👨‍💻 Author

Bhavik Ratnottar

B.Tech Information Technology

AI • Machine Learning • Deep Learning • Full Stack Development

⭐ Support

If you found this project useful:

⭐ Star the repository

🍴 Fork the project

📢 Share with others
