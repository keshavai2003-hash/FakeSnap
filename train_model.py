import pandas as pd
import nltk
import re
import pickle
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# 1. ISOT
print("Loading ISOT...")
fake = pd.read_csv('dataset/ISOT/Fake.csv')
true = pd.read_csv('dataset/ISOT/True.csv')
fake['label'] = 'FAKE'
true['label'] = 'REAL'
isot = pd.concat([fake, true], ignore_index=True)[['text', 'label']]

# 2. IFND
print("Loading IFND...")
ifnd = pd.read_csv(r'F:\fakenews\dataset\IFND\IFND.csv', encoding='latin-1')
ifnd = ifnd[['Statement', 'Label']]
ifnd.columns = ['text', 'label']
ifnd['label'] = ifnd['label'].replace({'TRUE': 'REAL', 'FALSE': 'FAKE'})

# MERGE
print("Merging...")
df = pd.concat([isot, ifnd], ignore_index=True)
df['label'] = df['label'].str.upper()
df = df.dropna(subset=['text'])
df = df[df['text'].str.strip() != '']

print("Total articles:", len(df))
print(df['label'].value_counts())

# CLEAN TEXT
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    text = ' '.join([w for w in text.split() if w not in stop_words])
    return text

print("\nCleaning text...")
df['text'] = df['text'].apply(clean_text)
print("Cleaning done!")

# TRAIN
X = df['text']
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training size:", len(X_train))
print("Testing size:", len(X_test))

# Improved parameters
tfidf = TfidfVectorizer(max_features=10000, ngram_range=(1,2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)
print("TF-IDF done!")

print("Training model... please wait!")
model = LogisticRegression(C=2, max_iter=1000)
model.fit(X_train_tfidf, y_train)

y_pred = model.predict(X_test_tfidf)
print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nDetailed Report:")
print(classification_report(y_test, y_pred))

# SAVE
with open(r'F:\fakenews\model\model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open(r'F:\fakenews\model\tfidf.pkl', 'wb') as f:
    pickle.dump(tfidf, f)

print("\nModel saved successfully!")
