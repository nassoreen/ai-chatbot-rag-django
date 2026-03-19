from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from .models import ChatSession, QuestionCategory

def staff_required(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(staff_required)
def chat_user_list(request):
    sessions = ChatSession.objects.order_by("-created_at")
    return render(request, "staff/chat_user_list.html", {
        "sessions": sessions
    })


@login_required
@user_passes_test(staff_required)
def chat_history(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id)
    messages = session.messages.all().order_by("created_at")

    return render(request, "staff/chat_detail.html", {
        "session": session,
        "messages": messages
    })


@login_required
@user_passes_test(staff_required)
def chat_delete(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id)

    if request.method == "POST":
        session.delete()   # 🔥 ลบทั้ง session + messages
        return redirect("staff_chat_list")

    return render(request, "staff/chat_confirm_delete.html", {
        "session": session
    })
    
    

@login_required
def question_list(request):
    categories = QuestionCategory.objects.prefetch_related("questions")
    return render(request, "staff/question_list.html", {
        "categories": categories
    })
