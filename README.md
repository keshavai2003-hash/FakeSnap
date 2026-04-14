# FakeSnap 🔍

### AI-Powered Fake News Detection System

FakeSnap is a web application that detects fake news using Machine Learning, NLP, and OCR.
It supports both **text input** and **image-based news detection**.

---

## 🚀 Features

* 📰 Fake News Detection (ML Model)
* 🤖 AI Fact-Checking Integration
* 📷 OCR Support (Extract text from images)
* 👤 User Authentication (Login/Register)
* 🏆 Gamification (Badges System)
* 📊 Dashboard & History Tracking
* 🛡️ Admin Panel
* ⚡ Rate Limiting System

---

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **Machine Learning:** TF-IDF + Logistic Regression
* **Database:** MySQL
* **OCR:** Tesseract
* **Frontend:** HTML, CSS, JavaScript

---

## 📂 Project Structure

```
fakenews/
│
├── app.py
├── train_model.py
├── model/
├── dataset/        # (not included in repo)
├── templates/
├── static/
├── .env
├── .gitignore
```

---

## ⚙️ Setup Instructions

### 1. Clone Repository

git clone https://github.com/keshavai2003-hash/FakeSnap.git
cd FakeSnap

---

### 2. Install Dependencies

pip install -r requirements.txt

---

### 3. Setup Environment Variables

Create a `.env` file:

SECRET_KEY=your_secret_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=fakesnap
GROQ_API_KEY=your_api_key

---

### 4. Install Tesseract OCR

Download from:
https://github.com/tesseract-ocr/tesseract

Make sure it is added to system PATH.

---

### 5. Download Dataset

Dataset not included due to size.

Download from:
https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset

Place inside:

dataset/
├── ISOT/
├── IFND/

---

### 6. Train Model

python train_model.py

---

### 7. Run Application

python app.py

---

## 📊 Model Info

* Dataset: 100,000+ news articles
* Accuracy: ~95%
* Algorithm: Logistic Regression + TF-IDF

---

## 👨‍💻 My Contribution (Backend & ML)

* Developed complete backend using Flask
* Built and trained Machine Learning model
* Implemented text preprocessing and NLP pipeline
* Integrated OCR (Tesseract) for image-based news analysis
* Designed database structure and authentication system
* Implemented API routes and core logic

---

## ⚠️ Disclaimer

Always verify news from trusted sources.

### Install dependencies
pip install -r requirements.txt

### Download NLTK data
For nltk (stopwords), you need  need to run once this below code :
python -c 
import nltk
nltk.download('stopwords')


---

## 👤 Author

Keshav Sharma
https://github.com/keshavai2003-hash

---

## ⭐ Support

If you like this project, give it a star ⭐
