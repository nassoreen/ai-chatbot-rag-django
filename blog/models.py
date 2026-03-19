from django.db import models
from pgvector.django import VectorField

class ChatSession(models.Model):
    session_key = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ChatSession({self.session_key})"


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("bot", "Bot"),
        ("system", "System"),
    )

    chat_session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.text[:30]}"


class KnowledgeDocument(models.Model):
    content = models.TextField()
    embedding = VectorField(dimensions=1024)

    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=150, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
# ---------------------------------------  เก็บคำถามของผู้ใช้แยกเป็นหมวดหมู่  -----------------------------------
    
class QuestionCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    embedding = VectorField(dimensions=1024, null=True, blank=True)


class Question(models.Model):
    category = models.ForeignKey(
        QuestionCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions"
    )
    question_text = models.TextField()
    answer_text = models.TextField(blank=True)

    embedding = VectorField(dimensions=1024, null=True, blank=True)

    count = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question_text[:50]} : {self.answer_text[:50]}"