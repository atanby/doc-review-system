import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

classifier = joblib.load(os.path.join(BASE_DIR, "ml", "classifier.pkl"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "ml", "vectorizer.pkl"))

def predict_document_type(text: str) -> str:
    vector = vectorizer.transform([text])
    prediction = classifier.predict(vector)
    return prediction[0]