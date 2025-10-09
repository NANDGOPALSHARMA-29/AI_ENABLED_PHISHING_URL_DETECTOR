# backend/train.py
import random
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from model_utils import extract_features_from_url

def generate_synthetic_dataset(n_phish=1500, n_benign=1500):
    phishing_templates = [
        "http://{host}/login",
        "https://{host}/secure/verify",
        "http://{host}/account/update",
        "https://{host}/auth/{path}",
        "http://{ip}/login",
    ]
    benign_templates = [
        "https://www.{domain}/",
        "https://{domain}/about",
        "https://{domain}/products/{path}",
        "https://{domain}/login",
    ]
    common_domains = ['google.com','microsoft.com','amazon.com','github.com','example.com','wikipedia.org']
    phish_hosts = ['paypal-secure-login.com','verify-account-paypal.xyz','secure-bank-login.co','signin-paypal.webscr.xyz']
    data = []
    for _ in range(n_phish):
        t = random.choice(phishing_templates)
        host = random.choice(phish_hosts)
        ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        path = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        url = t.format(host=host, ip=ip, path=path, domain=host)
        data.append((url, 1))
    for _ in range(n_benign):
        t = random.choice(benign_templates)
        domain = random.choice(common_domains)
        path = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))
        url = t.format(domain=domain, path=path)
        data.append((url, 0))
    random.shuffle(data)
    return data

def build_feature_dataframe(data):
    rows = []
    for url, label in data:
        feats = extract_features_from_url(url)
        feats['url'] = url
        feats['label'] = label
        rows.append(feats)
    df = pd.DataFrame(rows)
    return df

def main():
    print("Generating dataset...")
    data = generate_synthetic_dataset(1500, 1500)
    df = build_feature_dataframe(data)
    X = df.drop(columns=['url','label'])
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Training RandomForest...")
    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    proba = clf.predict_proba(X_test)[:,1]
    print("Eval:")
    print(classification_report(y_test, preds))
    try:
        auc = roc_auc_score(y_test, proba)
        print("ROC AUC:", auc)
    except Exception:
        pass
    # Save model and feature column order
    joblib.dump({'model': clf, 'features': list(X.columns)}, 'model.joblib')
    print("Saved model.joblib")

if __name__ == '__main__':
    main()
