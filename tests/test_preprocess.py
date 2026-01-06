import pandas as pd
from src.data.preprocess import get_preprocessor, FEATURES


def test_preprocess_transform_shapes():
    df = pd.DataFrame({
        "age": [63, 67, 67],
        "sex": [1, 1, 1],
        "cp": [3, 2, 2],
        "trestbps": [145, 160, 120],
        "chol": [233, 286, 229],
        "fbs": [1, 0, 0],
        "restecg": [0, 0, 1],
        "thalach": [150, 108, 129],
        "exang": [0, 1, 1],
        "oldpeak": [2.3, 1.5, 2.6],
        "slope": [0, 2, 1],
        "ca": [0, 3, 2],
        "thal": [1, 2, 2],
    })
    X = df[FEATURES]
    pre = get_preprocessor()
    Xt = pre.fit_transform(X)
    assert Xt.shape[0] == 3
    assert Xt.shape[1] > 10  # one-hot expands categorical features
