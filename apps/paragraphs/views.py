from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.paragraphs.serializers import (
    ParagraphInputSerializer,
    ParagraphSerializer,
    WordSearchSerializer,
)


class ParagraphCreateView(APIView):
    # api endpoint to accept text, split by double newline, and queue celery tasks

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ParagraphInputSerializer,
        responses={201: ParagraphSerializer(many=True)},
    )
    def post(self, request):
        # validate text, bulk create paragraphs, and dispatch celery tasks
        serializer = ParagraphInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_paragraphs = serializer.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        return Response(
            {
                "message": f"{len(created_paragraphs)} paragraph(s) created. Word-frequency processing has been queued.",
                "paragraphs": [{"id": str(p.id)} for p in created_paragraphs],
            },
            status=status.HTTP_201_CREATED,
        )


class WordSearchView(APIView):
    # api endpoint to search paragraphs for a word and rank by occurrence

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="word",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Word to search for across the user's paragraphs.",
            )
        ],
        responses={
            200: ParagraphSerializer(many=True),
            400: None,
        },
    )
    def get(self, request):
        # validate query param and delegate lookup to serializer
        word = request.query_params.get("word", "").strip()
        if not word:
            return Response(
                {"error": "Query parameter 'word' is required and must not be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = WordSearchSerializer(data={"word": word})
        serializer.is_valid(raise_exception=True)

        paragraphs = serializer.get_results(user=request.user)

        results = [
            {
                "id": str(p.id),
                "content": p.content,
                "word_count": p.word_occurrence,
            }
            for p in paragraphs
        ]

        return Response(results, status=status.HTTP_200_OK)
