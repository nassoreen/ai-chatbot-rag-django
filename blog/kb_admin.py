from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q,Sum
from .models import KnowledgeDocument,QuestionCategory,Question
from .embeddings import clean_text, embed_text
from .category_reassign import reassign_questions_from_others

def staff_required(user):
    return user.is_authenticated and user.is_staff

def make_full_text(title, content):
    return clean_text((title or "").strip() + "\n" + (content or "").strip())

@login_required
@user_passes_test(staff_required)
def kb_list(request):
    q = (request.GET.get("q") or "").strip()
    
    # ดึงข้อมูลทั้งหมด (ทั้ง active และ inactive)
    docs = KnowledgeDocument.objects.all().order_by("-updated_at")

    if q:
        docs = docs.filter(Q(title__icontains=q) | Q(content__icontains=q))

    # นับจำนวน
    active_count = docs.filter(is_active=True).count()
    inactive_count = docs.filter(is_active=False).count()

    return render(request, "kb/list.html", {
        "docs": docs, 
        "q": q,
        "active_count": active_count,
        "inactive_count": inactive_count
    })

@login_required
@user_passes_test(staff_required)
def kb_create(request):
    if request.method == "POST":
        content = (request.POST.get("content") or "").strip()
        is_active = request.POST.get("is_active") == "on"

        if not content:
            return render(request, "kb/form.html", {"mode": "create", "error": "กรุณากรอกเนื้อหา"})

        content = clean_text(content)
        emb = embed_text(content)

        # กันซ้ำ
        if KnowledgeDocument.objects.filter(content=content, is_active=True).exists():
            return render(request, "kb/form.html", {"mode": "create", "error": "มีข้อมูลนี้อยู่แล้ว"})

        KnowledgeDocument.objects.create(
            content=content,
            embedding=emb,
            is_active=is_active,
            created_by=request.user.username,
        )
        return redirect("kb_list")

    return render(request, "kb/form.html", {"mode": "create"})

@login_required
@user_passes_test(staff_required)
def kb_edit(request, pk):
    doc = get_object_or_404(KnowledgeDocument, pk=pk)

    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        content = (request.POST.get("content") or "").strip()
        is_active = request.POST.get("is_active") == "on"

        if not title or not content:
            return render(request, "kb/form.html", {"mode": "edit", "doc": doc, "error": "กรุณากรอกหัวข้อและเนื้อหาให้ครบ"})

        doc.title = title
        doc.content = content
        doc.is_active = is_active

        full_text = make_full_text(title, content)
        doc.embedding = embed_text(full_text)
        doc.save()
        return redirect("kb_list")

    return render(request, "kb/form.html", {"mode": "edit", "doc": doc})

@login_required
@user_passes_test(staff_required)
def kb_delete(request, pk):
    doc = get_object_or_404(KnowledgeDocument, pk=pk)
    doc.is_active = False
    doc.save()
    return redirect("kb_list")

@login_required
@user_passes_test(staff_required)
def staff_dashboard(request):
    total = KnowledgeDocument.objects.count()
    active = KnowledgeDocument.objects.filter(is_active=True).count()
    inactive = KnowledgeDocument.objects.filter(is_active=False).count()

    return render(
        request,
        "staff/dashboard.html",
        {
            "total": total,
            "active": active,
            "inactive": inactive,
        },
    )
 
####################### เพิ่มหมวดหมู่ #######################   

@login_required
@user_passes_test(staff_required)
def category_save(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        if not name:
            return redirect(request.META.get("HTTP_REFERER", "kb_list"))

        # 1. สร้าง embedding จาก description
        embedding = embed_text(description)

        # 2. สร้างหมวด
        new_category = QuestionCategory.objects.create(
            name=name,
            description=description,
            embedding=embedding
        )

        # 3. ดึงคำถามจาก "อื่นๆ" มาเข้าหมวดใหม่
        reassign_questions_from_others(new_category)

    return redirect(request.META.get("HTTP_REFERER", "kb_list"))
