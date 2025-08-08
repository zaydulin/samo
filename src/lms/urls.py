from django.urls import include, path
from django.contrib.auth import views as auth_views
app_name = 'useraccount'
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('publish/', views.stream_publisher, name='stream_publisher'),
    path('view/<str:user_id>/', views.stream_viewer, name='stream_viewer'),
    path('conference/<slug:slug>/', views.VideoChatRoomDetailsView.as_view(), name='video_chat_root'),
    path("", views.HomeView.as_view(), name='con_home'),
    path("", views.PagesView.as_view(), name='con_pages'),
    path("page/<slug:slug>/", views.PagesDetailView.as_view(), name="con_page"),
    path("blogs/", views.BlogView.as_view(), name="con_blogs"),
    path("blog/<slug:slug>/", views.BlogDetailView.as_view(), name="con_blog"),
    path("faq/", views.FaqView.as_view(), name='con_faq'),
    path("helping/", views.HelpingView.as_view(), name='con_helping'),
    path('privacy-policy/', views.PrivacyGeneratorView.as_view(), name='con_privacy-policy'),
    path('requisites/', views.RequisitesView.as_view(), name='con_requisites'),
    path('terms_of_use/', views.TermsOfUserView.as_view(), name='con_terms_of_use'),
    path('about/', views.AboutView.as_view(), name='con_about'),

    path('signup/', views.SignUpView.as_view(), name='con_signup'),
    path('login/', views.CustomLoginView.as_view(), name='con_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='conference:con_home'), name='con_logout'),
    path('toggle_user_field/<int:user_id>/', views.UpdateUserFieldView.as_view(), name='toggle_user_field'),
    path('videochatroom/<int:pk>/toggle/', views.ToggleVideoChatRoomStatus.as_view(), name='toggle_videochatroom_status'),
    path('videochatroom/<int:pk>/add-user/', views.AddUserToGroup.as_view(), name='add_user_to_group'),
    path('toggle_myuser_field/<int:user_id>/', views.UpdateMyUserFieldView.as_view(), name='toggle_myuser_field'),
    path('update-group-url/<int:pk>/', views.UpdateGroup.as_view(), name='update-group'),
    path('update-my-group-url/<int:pk>/', views.UpdateMyGroup.as_view(), name='update-my-group'),
    path('videochat/<int:pk>/send-message/', views.SendMessageView.as_view(), name='send-message'),
    path('conference/request-access/<str:token>/', views.AddNotAddedView.as_view(), name='request_access'),
    # path('stream_video/<int:user_id>/', views.stream_video, name='stream_video'),

]