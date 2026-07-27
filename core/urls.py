from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("create/", views.create_space, name="create_space"),
    path("open/", views.open_space, name="open_space"),
    path("exit/", views.exit_space, name="exit_space"),
    path("space/<str:space_id>/", views.dashboard, name="dashboard"),
    path("space/<str:space_id>/note/add/", views.add_note, name="add_note"),
    path("space/<str:space_id>/note/<int:note_id>/delete/", views.delete_note, name="delete_note"),
    path("space/<str:space_id>/file/upload/", views.upload_file, name="upload_file"),
    path("space/<str:space_id>/file/<int:file_id>/delete/", views.delete_file, name="delete_file"),
]