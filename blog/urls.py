from django.urls import path
from . import views, kb_admin, chat_admin

urlpatterns = [
    path("", views.chat_ui, name="chat_ui"),
    path("api/chat/", views.chatbot_api, name="chatbot_api"),
    
        # ===== หลังบ้านคลังความรู้ =====
    path("staff/kb/", kb_admin.kb_list, name="kb_list"),
    path("staff/kb/new/", kb_admin.kb_create, name="kb_create"),
    path("staff/kb/<int:pk>/edit/", kb_admin.kb_edit, name="kb_edit"),
    path("staff/kb/<int:pk>/delete/", kb_admin.kb_delete, name="kb_delete"),
    
    
    path("staff/", kb_admin.staff_dashboard, name="dashboard"),
    
    
    # ===== Chat History =====
    path("staff/chats/", chat_admin.chat_user_list, name="chat"),
    path("staff/chats/<int:session_id>/", chat_admin.chat_history, name="chat_history"),
    path("staff/chats/<int:session_id>/delete/", chat_admin.chat_delete, name="staff_chat_delete"),
    
    
    
    path("staff/questions/", chat_admin.question_list, name="staff_question_list"),
    
    
    
    path("staff/category/save/", kb_admin.category_save, name="category_save"),

]
