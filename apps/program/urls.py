from django.urls import path
from . import views
from apps.program.views import ReactivateProgram, ReactivateTopic, \
    ProgramMemberReactivate, UploadProgramDocument
from .views import ProgramList, ProgramDetail, Content_Update, \
    DeleteProgram, ProgramMemberDeactivate, \
    CreateProgram, UpdateProgram, DeleteContent, \
    DeleteTopic, CreateTopic, Topic_Update, UpdateTopic1, DeleteDocument

urlpatterns = [
    path("<int:pk>/detail/", ProgramDetail.as_view(), name="program-detail"),
    path("", ProgramList.as_view(), name="program-list"),
    path("<int:pk>/createprogram/", CreateProgram.as_view(), name='program_create'),
    path("<int:pk>/createtopic/", CreateTopic.as_view(), name='topic_create'),
    path("<int:pk>/topicupdate1/", UpdateTopic1.as_view(), name='topic_update_1'),
    path("<int:pk>/deleteprogram/", DeleteProgram.as_view(), name="delete-program"),
    path("<int:pk>/reactivateprogram/", ReactivateProgram.as_view(), name="reactivate-program"),
    path("<int:pk>/deletetopic/", DeleteTopic.as_view(), name="delete-topic"),
    path("<int:pk>/reactivatetopic/", ReactivateTopic.as_view(), name="reactivate-topic"),
    path("<int:pk>/update/", UpdateProgram.as_view(), name='program_update'),
    path("<int:pk>/topicupdate/", Topic_Update.as_view(), name='topic_update'),
    path("<int:pk>/contentupdate/", Content_Update.as_view(), name='content_update'),
    path("<int:pk>/deletecontent/", DeleteContent.as_view(), name='delete-content'),
    path("<int:pk>/<slug:user_id>/<slug:role>/<str:admin_username>/deactivateprogrammember/", ProgramMemberDeactivate.as_view(), name='program_member_deactivate'),
    path("<int:pk>/<slug:user_id>/<slug:role>/<str:admin_username>/reactivateprogrammember/", ProgramMemberReactivate.as_view(), name='program_member_reactivate'),
    path('add-admin/', views.add_admin, name='add-admin'),
    path('add-admin-info/<str:qr_value>/', views.add_admin_info, name='add-admin-info'),
    path("<int:pk>/upload-program-doc", UploadProgramDocument.as_view(), name='upload-program-doc'),
    path("<int:pk>/delete-program-document/", DeleteDocument.as_view(), name='delete-program-document'),
    path("download-content/", views.content_download, name='download-content'),
    path("participant-list/<int:pk>/", views.get_participant_list, name='participant-list'),
    path("download-csv/<int:pk>/", views.csv_download, name='download-csv'),
]
