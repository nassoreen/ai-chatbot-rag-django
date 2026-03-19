from .models import Question
from difflib import get_close_matches

def suggest_if_typo(text):
    all_q = list(set(Question.objects.values_list("question_text", flat=True)))

    matches = get_close_matches(text, all_q, n=3, cutoff=0.6)

    return Question.objects.filter(question_text__in=matches).distinct()
