from pgvector.django import CosineDistance
from blog.models import Question, QuestionCategory

QUESTION_REASSIGN_THRESHOLD = 0.35

def reassign_questions_from_others(new_category):
    others = QuestionCategory.objects.get(name="อื่นๆ")

    questions = (
        Question.objects
        .filter(category=others, embedding__isnull=False)
        .annotate(
            distance=CosineDistance("embedding", new_category.embedding)
        )
        .filter(distance__lt=QUESTION_REASSIGN_THRESHOLD)
    )

    for q in questions:
        q.category = new_category
        q.save(update_fields=["category"])
