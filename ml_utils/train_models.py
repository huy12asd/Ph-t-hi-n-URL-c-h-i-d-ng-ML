# ml_utils/train_models.py
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib, os
from ml_utils.feature_extractor import load_dataset


def train_all_models():
    X, y = load_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        'lr_model': LogisticRegression(max_iter=1000),
        'knn_model': KNeighborsClassifier(n_neighbors=5),
        'rf_model': RandomForestClassifier(n_estimators=200, random_state=42)
    }

    if not os.path.exists('models'):
        os.makedirs('models')

    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        acc = accuracy_score(y_test, y_pred)
        print(f"{name}: {acc:.4f}")
        print(classification_report(y_test, y_pred))
        joblib.dump({'model': model, 'scaler': scaler, 'features': X.columns.tolist()},
                    f'models/{name}.pkl')

if __name__ == "__main__":
    train_all_models()
