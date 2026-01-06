import os
from pathlib import Path

from src.models.train import main


def test_fast_training_creates_model(tmp_path, monkeypatch):
    # Ensure data exists
    from scripts.download_data import main as dl_main
    dl_main()

    # Run fast training
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "mlruns")
    # Simulate CLI
    import sys
    sys.argv = ["train.py", "--fast"]
    main()

    assert Path("models/model_pipeline.pkl").exists()
