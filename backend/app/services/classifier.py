"""Türkçe çağrı sınıflandırma servisi.

TF-IDF + Logistic Regression pipeline. Model diske pickle'lanır,
yoksa sentetik veri ile otomatik eğitilir.

İleride multi-label'a geçmek için: LogisticRegression yerine
OneVsRestClassifier(LinearSVC) + MultiLabelBinarizer kullanılabilir.
"""
from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

CATEGORIES = [
    "enkaz",
    "saglik",
    "su",
    "gida",
    "barinma",
    "ilac",
    "ulasim",
    "kayip_kisi",
    "elektrik_isinma",
    "diger",
]

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BACKEND_DIR / "data" / "classifier.pkl"
DATA_PATH = BACKEND_DIR / "data" / "synthetic_calls.csv"


@dataclass
class ClassifierService:
    """Singleton benzeri servis; FastAPI startup'ta load_or_train() çağrılır."""

    pipeline: Optional[Pipeline] = None
    accuracy: float = 0.0
    samples_used: int = 0
    _lock: Lock = Lock()

    def is_ready(self) -> bool:
        return self.pipeline is not None

    def load_or_train(self) -> None:
        """Diskte model varsa yükle, yoksa eğit."""
        with self._lock:
            if MODEL_PATH.exists():
                try:
                    with open(MODEL_PATH, "rb") as f:
                        bundle = pickle.load(f)
                    self.pipeline = bundle["pipeline"]
                    self.accuracy = bundle.get("accuracy", 0.0)
                    self.samples_used = bundle.get("samples_used", 0)
                    logger.info(
                        "Sınıflandırıcı diskten yüklendi (acc=%.3f, n=%d)",
                        self.accuracy,
                        self.samples_used,
                    )
                    return
                except Exception as exc:  # pragma: no cover - bozuk pickle
                    logger.warning("Model yüklenemedi: %s. Yeniden eğitilecek.", exc)
            self._train_internal()

    def retrain(self) -> Tuple[float, int]:
        with self._lock:
            return self._train_internal()

    def _train_internal(self) -> Tuple[float, int]:
        if not DATA_PATH.exists():
            raise FileNotFoundError(
                f"Sentetik veri bulunamadı: {DATA_PATH}. "
                "Önce `python -m data.generate_synthetic_data` komutunu çalıştır."
            )

        df = pd.read_csv(DATA_PATH)
        if "text" not in df.columns or "label" not in df.columns:
            raise ValueError("synthetic_calls.csv 'text' ve 'label' sütunları içermeli")

        df = df.dropna(subset=["text", "label"])
        df = df[df["label"].isin(CATEGORIES)]

        X = df["text"].astype(str).values
        y = df["label"].astype(str).values

        # Az sınıf varsa stratify atlamak gerek
        try:
            X_tr, X_te, y_tr, y_te = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        except ValueError:
            X_tr, X_te, y_tr, y_te = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

        pipeline = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        min_df=1,
                        max_df=0.95,
                        sublinear_tf=True,
                        lowercase=True,
                    ),
                ),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=1000,
                        C=2.0,
                        class_weight="balanced",
                        n_jobs=None,
                    ),
                ),
            ]
        )
        pipeline.fit(X_tr, y_tr)
        preds = pipeline.predict(X_te)
        acc = float(accuracy_score(y_te, preds))

        self.pipeline = pipeline
        self.accuracy = acc
        self.samples_used = int(len(X))

        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(
                {"pipeline": pipeline, "accuracy": acc, "samples_used": len(X)},
                f,
            )
        logger.info("Sınıflandırıcı eğitildi (acc=%.3f, n=%d)", acc, len(X))
        return acc, int(len(X))

    def predict(self, text: str) -> Tuple[str, Dict[str, float]]:
        """Tahmin döndür: (kategori, kategori->olasılık)."""
        if self.pipeline is None:
            self.load_or_train()
        assert self.pipeline is not None
        proba = self.pipeline.predict_proba([text])[0]
        classes: List[str] = list(self.pipeline.classes_)
        scores = {c: float(p) for c, p in zip(classes, proba)}
        # En yüksek olasılıklı kategori
        category = max(scores.items(), key=lambda kv: kv[1])[0]
        return category, scores


# Modül seviyesi tekil instance
classifier_service = ClassifierService()
