from django.urls import path
from apps.entity import views
from apps.entity.views import RegisterEntity, EntityProfile,\
    EditEntityProfile, DeactivateEntity, EntityListView, UploadEntityDocument, \
    DeactivateEntityAdmin, ReactivateEntityAdmin, ReactivateEntity, DeleteDocument


urlpatterns = [
    path('', EntityListView.as_view(), name='index'),
    path('add-entity/', views.add_entity, name='add-entity'),
    path('add-entity-info/<str:qr_value>/', views.add_entity_info, name='add-entity-info'),
    path('choose-scan-type/', views.choose_scan_type, name='choose-scan-type'),
    path('add-entity-admin/', views.add_entity_admin, name='add-entity-admin'),
    path('add-entity-admin-info/<str:qr_value>/', views.add_entity_admin_info, name='add-entity-admin-info'),
    path("<int:pk>/entityregister/", RegisterEntity.as_view(), name='register-entity'),
    path("<int:pk>/entityprofile/", EntityProfile.as_view(), name='entity-profile'),
    path("<int:pk>/editentityprofile/", EditEntityProfile.as_view(), name='edit-entity-profile'),
    path("<int:pk>/entitydeactivate/", DeactivateEntity.as_view(), name='deactivate-entity'),
    path("<int:pk>/entityreactivate/", ReactivateEntity.as_view(), name='reactivate-entity'),
    path("<int:pk>/<slug:user_id>/<str:member_name>/entity-admin-deactivate/", DeactivateEntityAdmin.as_view(), name='entity-admin-deactivate'),
    path("<int:pk>/<slug:user_id>/<str:admin_username>/entity-admin-reactivate/", ReactivateEntityAdmin.as_view(), name='entity-admin-reactivate'),
    path("<int:pk>/upload-entity-doc", UploadEntityDocument.as_view(), name='upload-entity-doc'),
    path("<int:pk>/delete-entity-document/", DeleteDocument.as_view(), name='delete-entity-document'),
]
