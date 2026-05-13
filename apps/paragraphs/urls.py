from django.urls import path
from apps.paragraphs.views import ParagraphCreateView, WordSearchView

urlpatterns = [
    path("", ParagraphCreateView.as_view(), name="paragraph-create"),
    path("search/", WordSearchView.as_view(), name="paragraph-search"),
]
