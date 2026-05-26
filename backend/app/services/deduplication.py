"""Duplicate / benzer çağrı tespiti.

Yaklaşım:
  1. Yeni çağrı geldiğinde son N (varsayılan 500) çağrıyı çek.
  2. TF-IDF üzerinden cosine similarity hesapla.
  3. Şehir/ilçe eşleşirse eşik düşür.
  4. Eşiği geçen çağrılar -> benzer; aynı veya aşırı benzer -> duplicate_suspected.
  5. Cluster ID: en yüksek benzeyenin cluster_id'sini paylaş; yoksa yeni ID.

Uyarı: Bu bir batch/offline yaklaşımdır. Yüksek hacimde çevrimiçi yaklaşık
komşu arama (faiss, hnswlib) tercih edilmelidir - README "Geliştirme Fikirleri"
bölümünde belirtildi.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class SimilarCall:
    id: int
    similarity: float
    cluster_id: Optional[int]
    city: str
    district: Optional[str]


# Eşikler
DUPLICATE_THRESHOLD = 0.78   # üstü -> duplicate_suspected
SIMILAR_THRESHOLD = 0.55     # üstü -> aynı cluster
LOCAL_BOOST = 0.08           # şehir+ilçe aynıysa eşikleri bu kadar düşür


def _build_corpus_texts(existing: Sequence) -> List[str]:
    return [c.text for c in existing]


def find_similar(
    new_text: str,
    new_city: str,
    new_district: Optional[str],
    existing: Sequence,
) -> Tuple[List[SimilarCall], bool, Optional[int]]:
    """
    Returns:
        (benzer çağrılar listesi sıralı, duplicate_suspected, cluster_id)
    """
    if not existing:
        return [], False, None

    texts = _build_corpus_texts(existing)
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, lowercase=True)
    try:
        matrix = vec.fit_transform(texts + [new_text])
    except ValueError:
        # Boş vocabulary olabilir (örn. çok kısa metinler)
        return [], False, None

    sims = cosine_similarity(matrix[-1], matrix[:-1]).ravel()

    results: List[SimilarCall] = []
    duplicate_flag = False
    best_cluster: Optional[int] = None
    best_sim = -1.0

    for idx, sim in enumerate(sims):
        call = existing[idx]
        # Yerel boost: şehir+ilçe eşleşirse eşikleri düşür
        local = new_city.lower() == (call.city or "").lower()
        if new_district and call.district:
            local = local and new_district.lower() == call.district.lower()

        sim_threshold = SIMILAR_THRESHOLD - (LOCAL_BOOST if local else 0)
        dup_threshold = DUPLICATE_THRESHOLD - (LOCAL_BOOST if local else 0)

        if sim >= sim_threshold:
            results.append(
                SimilarCall(
                    id=call.id,
                    similarity=float(sim),
                    cluster_id=call.cluster_id,
                    city=call.city,
                    district=call.district,
                )
            )
            if sim >= dup_threshold:
                duplicate_flag = True
            if sim > best_sim:
                best_sim = float(sim)
                best_cluster = call.cluster_id

    results.sort(key=lambda r: r.similarity, reverse=True)
    return results, duplicate_flag, best_cluster


def next_cluster_id(existing: Sequence) -> int:
    """Mevcut cluster'lardaki en yüksek + 1."""
    ids = [c.cluster_id for c in existing if c.cluster_id is not None]
    return (max(ids) + 1) if ids else 1
