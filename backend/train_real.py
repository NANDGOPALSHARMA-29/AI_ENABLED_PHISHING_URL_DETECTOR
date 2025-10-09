# train_real.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# ✅ Load datasets

phish = pd.read_csv("../data/openphish_norm.csv", encoding='utf-16')
benign = pd.read_csv("../data/benign_norm.csv", encoding='utf-8')


# ✅ Combine
df = pd.concat([phish, benign], ignore_index=True)
print("Total samples:", len(df))
print(df['label'].value_counts())

# ✅ Shuffle
df = df.sample(frac=1).reset_index(drop=True)

# ✅ Split features & labels
X = df['url']
y = df['label']

# ✅ Convert URL text → numeric (TF-IDF)
vectorizer = TfidfVectorizer(
    analyzer='char', ngram_range=(2,5), max_features=10000
)
X_vec = vectorizer.fit_transform(X)

# ✅ Split train/test
X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

# ✅ Train model
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# ✅ Evaluate
y_pred = model.predict(X_test)
print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nReport:\n", classification_report(y_test, y_pred))

# ✅ Save model + vectorizer
joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")
print("\n✅ Model & vectorizer saved successfully!")
