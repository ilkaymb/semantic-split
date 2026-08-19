import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import hf_client

DEFAULT_LABELS = ["spor", "teknoloji", "siyaset", "ekonomi", "sağlık", "kültür-sanat", "magazin"]


def _run_batch(texts, fn):
    results = []
    for text in texts:
        try:
            results.append(fn(text))
        except hf_client.HFInferenceError as exc:
            results.append({"error": str(exc)})
    return results


@csrf_exempt
@require_http_methods(["POST"])
def classify_view(request):
    try:
        data = json.loads(request.body)
        texts = data.get("texts", [])
        labels = data.get("labels") or DEFAULT_LABELS
        model = data.get("model")
        results = _run_batch(texts, lambda t: hf_client.classify(t, labels, model))
        return JsonResponse({"results": results})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Geçersiz JSON verisi"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def sentiment_view(request):
    try:
        data = json.loads(request.body)
        texts = data.get("texts", [])
        model = data.get("model")
        results = _run_batch(texts, lambda t: hf_client.sentiment(t, model))
        return JsonResponse({"results": results})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Geçersiz JSON verisi"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def summarize_view(request):
    try:
        data = json.loads(request.body)
        texts = data.get("texts", [])
        model = data.get("model")
        results = _run_batch(texts, lambda t: {"summary": hf_client.summarize(t, model)})
        return JsonResponse({"results": results})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Geçersiz JSON verisi"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def keywords_view(request):
    try:
        data = json.loads(request.body)
        texts = data.get("texts", [])
        model = data.get("model")
        results = _run_batch(texts, lambda t: {"keywords": hf_client.extract_keywords(t, model)})
        return JsonResponse({"results": results})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Geçersiz JSON verisi"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def language_view(request):
    try:
        data = json.loads(request.body)
        texts = data.get("texts", [])
        model = data.get("model")
        results = _run_batch(texts, lambda t: hf_client.detect_language(t, model))
        return JsonResponse({"results": results})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Geçersiz JSON verisi"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def toxicity_view(request):
    try:
        data = json.loads(request.body)
        texts = data.get("texts", [])
        model = data.get("model")
        results = _run_batch(texts, lambda t: hf_client.detect_toxicity(t, model))
        return JsonResponse({"results": results})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Geçersiz JSON verisi"}, status=400)
