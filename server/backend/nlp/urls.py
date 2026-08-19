from django.urls import path

from . import views

urlpatterns = [
    path("classify/", views.classify_view, name="classify"),
    path("sentiment/", views.sentiment_view, name="sentiment"),
    path("summarize/", views.summarize_view, name="summarize"),
    path("keywords/", views.keywords_view, name="keywords"),
    path("language/", views.language_view, name="language"),
    path("toxicity/", views.toxicity_view, name="toxicity"),
]
