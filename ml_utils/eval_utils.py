# ml_utils/eval_utils.py
import joblib
import pandas as pd
from .feature_extractor import extract_features_from_url, features_dict_to_vector

def predict_from_url(url, model_path='models/rf_model.pkl'):
    """
    Given a URL string, build features, load model bundle and return (prediction, confidence, feature_vector)
    prediction: 1 = benign/safe, 0 = malicious (matches how models were trained if you used replace -1->0 for label)
    confidence: probability of positive class if available, else None
    """
    bundle = joblib.load(model_path)
    model = bundle['model']
    scaler = bundle.get('scaler', None)
    trained_order = bundle.get('features', None)

    feat_dict = extract_features_from_url(url)
    vec = features_dict_to_vector(feat_dict, ordered_keys=trained_order if trained_order is not None else None)
    X = pd.DataFrame([vec], columns=trained_order if trained_order is not None else None)

    if scaler is not None:
        X_scaled = scaler.transform(X)
    else:
        X_scaled = X.values

    pred = model.predict(X_scaled)[0]
    proba = None
    if hasattr(model, "predict_proba"):
    # Lấy index của lớp 1 trong model.classes_
        class_index = list(model.classes_).index(1)
        proba = float(model.predict_proba(X_scaled)[0, class_index])

    return int(pred), proba, feat_dict
