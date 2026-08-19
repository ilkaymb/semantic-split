# views.py

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

# Gerekli modülleri içe aktar
from semantic_split import (
    SimilarSentenceSplitter,  # Benzer cümleleri gruplandırmak için kullanılacak
    SentenceTransformersSimilarity,  # Cümleler arası benzerliği hesaplamak için kullanılacak model
    SpacySentenceSplitter,  # Metni cümlelere ayırmak için kullanılacak araç
)

# Model ve splitter process başına bir kez yüklenir (her istekte yeniden yüklemek
# hem yavaş hem de bellek açısından pahalı).
_splitter = SimilarSentenceSplitter(SentenceTransformersSimilarity(), SpacySentenceSplitter())


@csrf_exempt
@require_http_methods(["POST"])
def my_post_view(request):
    try:
        # Gelen JSON verisini alın
        data = json.loads(request.body)

        if "message" in data:
            # Metni işle ve benzer cümleleri gruplandır
            res = _splitter.split(data.get("message"))
            respond = {"message": res}
        else:
            respond = {"error": "Message anahtarı bulunamadı"}

        return JsonResponse(respond)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Geçersiz JSON verisi"}, status=400)
