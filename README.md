# FakeSnap 🔍

### AI-Powered Fake News Detection System

FakeSnap is a web application that detects fake news using Machine Learning, NLP, and OCR.
It supports both **text input** and **image-based news detection**, providing a complete misinformation analysis system.

---

## 🚀 Features

* 📰 Fake News Detection (ML Model)
* 🤖 AI Fact-Checking Integration
* 📷 OCR Support (Image → Text)
* 👤 User Authentication (Login/Register)
* 🏆 Gamification (Badges System)
* 📊 Dashboard & History Tracking
* 🛡️ Admin Panel
* ⚡ Rate Limiting

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
├── database.sql
├── requirements.txt
├── .env
├── .gitignore
```

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```
git clone https://github.com/keshavai2003-hash/FakeSnap.git
cd FakeSnap
```

---

### 2. Install Dependencies

```
pip install -r requirements.txt
```

---

### 3. Setup Environment Variables

Create a `.env` file:

```
SECRET_KEY=your_secret_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=itt
GROQ_API_KEY=your_api_key
ADMIN_CODE=your_admin_code
```

---

## 🗄️ Database Setup

Run the SQL file in MySQL:

```
database.sql
```

---

## 🔍 OCR Setup (Tesseract)

Download from:
https://github.com/tesseract-ocr/tesseract

After installation, add it to your system PATH.

If not detected, manually set path in `app.py`:

```
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

## 📂 Dataset

Dataset is not included due to large size.

Download from:
https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset

Place inside:

```
dataset/
 ├── ISOT/
 │    ├── Fake.csv
 │    └── True.csv
 └── IFND/
      └── IFND.csv
```

---

## 🧠 Train Model

```
python train_model.py
```

---

## ▶️ Run Application

```
python app.py
```

---

## 👑 Admin Setup

To create an admin account:

1. Run the application
2. Open:
   http://127.0.0.1:5000/admin_setup
3. Enter details along with the Admin Code from `.env`

If the correct code is provided, the account will be created with admin privileges.

---

## 📊 Model Info

* Dataset Size: 100,000+ articles
* Accuracy: ~95%
* Algorithm: Logistic Regression + TF-IDF

---

## 👨‍💻 My Contribution (Backend & ML)

* Developed complete backend using Flask
* Built and trained Machine Learning model
* Implemented NLP preprocessing pipeline
* Integrated OCR (Tesseract) for image analysis
* Designed database and authentication system
* Implemented API routes and core logic

---

## ⚠️ Disclaimer

This system provides AI-based predictions and may not be 100% accurate.
Always verify news from trusted sources.

---

## 👤 Author

**Keshav Sharma**
https://github.com/keshavai2003-hash

---

## ⭐ Support

If you like this project, give it a star ⭐
