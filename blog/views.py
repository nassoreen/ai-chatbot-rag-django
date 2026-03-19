import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .rag_engine import rag_answer
from .models import ChatSession, ChatMessage


def _get_or_create_chat_session(request):
    if not request.session.session_key:
        request.session.create()

    sess, _ = ChatSession.objects.get_or_create(
        session_key=request.session.session_key
    )
    return sess


@csrf_protect
def chat_ui(request):
    chat_sess = _get_or_create_chat_session(request)
    history = chat_sess.messages.all().order_by("created_at")  # แนะนำให้เรียงเวลา
    return render(request, "blog/home.html", {"history": history})


@csrf_protect
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except:
        payload = {}

    user_msg = (payload.get("message") or "").strip()
    if not user_msg:
        return JsonResponse({"ok": False, "error": "Empty message"}, status=400)

    chat_sess = _get_or_create_chat_session(request)

    # 1) บันทึก user ลง DB
    ChatMessage.objects.create(
        chat_session=chat_sess,
        role="user",
        text=user_msg
    )

    # 2) ดึง history ล่าสุดจาก DB เพื่อส่งเข้า rag_answer (กัน prompt ยาวเกิน)
    recent_msgs = (
        chat_sess.messages
        .all()
        .order_by("-created_at")[:8]   # เอา 8 ล่าสุดพอ
    )
    # กลับลำดับให้เป็นเก่า -> ใหม่
    recent_msgs = list(reversed(recent_msgs))

    history_for_llm = [{"role": m.role, "text": m.text} for m in recent_msgs]

    # 3) เรียก bot โดยส่ง history เข้าไป
    try:
        bot_msg = rag_answer(user_msg, history=history_for_llm)
    except:
        bot_msg = "ขออภัย ระบบขัดข้องชั่วคราว"

    # 4) บันทึก bot ลง DB
    ChatMessage.objects.create(
        chat_session=chat_sess,
        role="bot",
        text=bot_msg
    )

    return JsonResponse({"ok": True, "reply": bot_msg})
