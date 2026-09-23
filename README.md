# 🧠 AIME – AI Mental Emotion Recognition System

> A real-time AI-powered platform for detecting human emotions using voice and facial expressions.


## 🚀 Overview

AIME (AI Mental Emotion Recognition System) is a deep learning project that recognizes emotions from both audio and video inputs.

The system uses trained AI models to analyze speech and facial expressions, predict emotions in real time, and provide meaningful insights through an interactive web dashboard.

### Supported Emotions

**Audio**

* Angry
* Disgust
* Fear
* Happy
* Neutral
* Sad

**Video**

* Neutral
* Calm
* Happy
* Sad
* Angry
* Fear
* Disgust
* Surprise

---

## ✨ Features

* 🎤 Audio Emotion Recognition
* 🎥 Real-Time Video Emotion Recognition
* 📊 Analytics Dashboard
* 📈 Confusion Matrix & Performance Analysis
* 🎯 Confidence Score Prediction
* 💡 Emotion-Based Recommendations
* 🌐 Flask Web Application
* 📱 Responsive Dashboard UI

---

## 🏗️ Architecture

Input (Audio / Video)

↓

Feature Extraction

↓

Deep Learning Models

↓

Emotion Prediction

↓

Confidence Score

↓

Insights & Recommendations

---

## 🧠 Models Used

### Audio Emotion Recognition

* CNN-Based Deep Learning Model
* MFCC & Log-Mel Features
* Dataset: CREMA-D

### Video Emotion Recognition

* MobileNetV2
* Transfer Learning
* Dataset: RAVDESS

---

## 🛠️ Tech Stack

**Languages**

* Python

**AI / Deep Learning**

* TensorFlow
* Keras

**Computer Vision**

* OpenCV
* MTCNN

**Audio Processing**

* Librosa
* SoundFile

**Backend**

* Flask

**Frontend**

* HTML
* CSS
* JavaScript

**Visualization**

* Matplotlib
* Seaborn

---

## 📂 Project Structure

```bash
PROJECT/
│
├── models/
├── dataset/
├── assets/
├── src/
├── webapp/
└── requirements.txt
```

---

## ⚙️ Installation

```bash
git clone <repository-url>

cd PROJECT

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

---

## ▶️ Run

### Audio

```bash
python src/live_audio_emotion.py
```

### Video

```bash
python src/live_video_emotion.py
```

### Web Application

```bash
cd webapp

python app.py
```

---

## 📊 Evaluation

The models are evaluated using:

* Accuracy
* Precision
* Recall
* F1 Score
* Confusion Matrix
* ROC Curve
* Class Distribution Analysis

---

## 🔮 Future Enhancements

* AI Mental Health Companion
* Tele-MANAS Integration
* Therapist Finder
* Emotion History Tracking
* Appointment Booking System
* Mobile Application

---

## 👨‍💻 Author

**Bhavik Ratnottar**

B.Tech Information Technology

AI • Machine Learning • Deep Learning
