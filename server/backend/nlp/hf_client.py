import os
import time

import requests

HF_ROUTER_BASE = "https://router.huggingface.co/hf-inference/models"

MODELS = {
    "zero_shot": ["facebook/bart-large-mnli", "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"],
    "sentiment": ["cardiffnlp/twitter-xlm-roberta-base-sentiment", "nlptown/bert-base-multilingual-uncased-sentiment"],
    "summarization": ["csebuetnlp/mT5_multilingual_XLSum", "facebook/bart-large-cnn"],
    "keywords": ["savasy/bert-base-turkish-ner-cased", "dslim/bert-base-NER"],
    "language": ["papluca/xlm-roberta-base-language-detection"],
    "toxicity": ["citizenlab/distilbert-base-multilingual-cased-toxicity", "unitary/toxic-bert"],
}


class HFInferenceError(Exception):
    pass


def _resolve_model(model_key: str, requested: str | None) -> str:
    options = MODELS[model_key]
    if requested and requested in options:
        return requested
    return options[0]


def query(model_id: str, payload: dict, timeout: int = 30):
    token = os.environ.get("HUGGINGFACE_API_TOKEN")
    if not token:
        raise HFInferenceError("HUGGINGFACE_API_TOKEN is not set")

    url = f"{HF_ROUTER_BASE}/{model_id}"
    headers = {"Authorization": f"Bearer {token}"}

    for attempt in range(2):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.RequestException as exc:
            raise HFInferenceError(f"HF isteği başarısız: {exc}") from exc

        if resp.status_code == 503 and attempt == 0:
            try:
                wait = min(resp.json().get("estimated_time", 5), 15)
            except ValueError:
                wait = 5
            time.sleep(wait)
            continue

        if not resp.ok:
            raise HFInferenceError(f"HF API hatası {resp.status_code}: {resp.text[:300]}")

        return resp.json()

    raise HFInferenceError("Model tekrar denemeden sonra hala yükleniyor")


def classify(text: str, labels: list, model_id: str | None = None) -> dict:
    mid = _resolve_model("zero_shot", model_id)
    result = query(mid, {
        "inputs": text,
        "parameters": {"candidate_labels": labels, "multi_label": False},
    })

    if isinstance(result, dict) and "labels" in result:
        return {"label": result["labels"][0], "score": result["scores"][0]}
    if isinstance(result, list) and result:
        top = max(result, key=lambda r: r["score"])
        return {"label": top["label"], "score": top["score"]}
    raise HFInferenceError("Beklenmeyen zero-shot yanıt biçimi")


def _top_label_score(model_key: str, text: str, model_id: str | None = None) -> dict:
    mid = _resolve_model(model_key, model_id)
    result = query(mid, {"inputs": text})
    row = result[0] if result and isinstance(result[0], list) else result
    if not row:
        raise HFInferenceError(f"Beklenmeyen yanıt biçimi ({model_key})")
    top = max(row, key=lambda r: r["score"])
    return {"label": top["label"], "score": top["score"]}


def sentiment(text: str, model_id: str | None = None) -> dict:
    return _top_label_score("sentiment", text, model_id)


def detect_language(text: str, model_id: str | None = None) -> dict:
    return _top_label_score("language", text, model_id)


def detect_toxicity(text: str, model_id: str | None = None) -> dict:
    return _top_label_score("toxicity", text, model_id)


def summarize(text: str, model_id: str | None = None) -> str:
    mid = _resolve_model("summarization", model_id)
    result = query(mid, {"inputs": text})
    if isinstance(result, list) and result and "summary_text" in result[0]:
        return result[0]["summary_text"]
    raise HFInferenceError("Beklenmeyen özetleme yanıt biçimi")


def extract_keywords(text: str, model_id: str | None = None) -> list:
    mid = _resolve_model("keywords", model_id)
    result = query(mid, {
        "inputs": text,
        "parameters": {"aggregation_strategy": "simple"},
    })
    if not isinstance(result, list):
        raise HFInferenceError("Beklenmeyen anahtar kelime yanıt biçimi")

    merged = []
    for r in result:
        word = r["word"]
        if word.startswith("##") and merged:
            merged[-1]["text"] += word[2:]
        else:
            merged.append({"text": word, "type": r["entity_group"], "score": r["score"]})
    return merged
