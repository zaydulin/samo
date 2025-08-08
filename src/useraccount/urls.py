from django.urls import include, path
from django.contrib.auth import views as auth_views
app_name = 'useraccount'
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('edit_profile/', views.EditMyProfileView.as_view(), name='edit_profile'),
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    # Сброс
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),


    path('publish/', views.stream_publisher, name='stream_publisher'),
    path('view/<str:user_id>/', views.stream_viewer, name='stream_viewer'),
    path('conference/<slug:slug>/', views.VideoChatRoomDetailsView.as_view(), name='video_chat_root'),
    path('toggle_user_field/<int:user_id>/', views.UpdateUserFieldView.as_view(), name='toggle_user_field'),
    path('videochatroom/<int:pk>/toggle/', views.ToggleVideoChatRoomStatus.as_view(), name='toggle_videochatroom_status'),
    path('videochatroom/<int:pk>/add-user/', views.AddUserToGroup.as_view(), name='add_user_to_group'),
    path('toggle_myuser_field/<int:user_id>/', views.UpdateMyUserFieldView.as_view(), name='toggle_myuser_field'),
    path('update-group-url/<int:pk>/', views.UpdateGroup.as_view(), name='update-group'),
    path('update-my-group-url/<int:pk>/', views.UpdateMyGroup.as_view(), name='update-my-group'),
    path('videochat/<int:pk>/send-message/', views.SendMessageView.as_view(), name='send-message'),
    path('conference/request-access/<str:token>/', views.AddNotAddedView.as_view(), name='request_access'),
    # path('stream_video/<int:user_id>/', views.stream_video, name='stream_video'),
    path('conference/', views.VideoChatRoomView.as_view(), name='conference_list'),
    path('conferenceadd/<uuid:course_id>/', views.CreateVideoChatRoomView.as_view(), name='conference_add'),
    path('conference-search/', views.VideoChatRoomSearchView.as_view(), name='videochat_search'),
    path('conferencedashboard/', views.ConferenceDashboardView.as_view(), name='conferencedashboard'),
    path('feed/',views.FeedView.as_view(), name='feed'),
    # Закладки
    path('add_bookmark/', views.add_bookmark, name='add_bookmark'),
    path('remove_bookmark/', views.remove_bookmark, name='remove_bookmark'),
    # Закладки
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmark_list'),
    path('bookmarks/delete/', views.DeleteBookmarkView.as_view(), name='delete_bookmarks'),
    # Личные записи
    path('notebooks/', views.NotebookListView.as_view(), name='notebook_list'),
    path('notebook/events/', views.NotebookEventsView.as_view(), name='notebook-events'),
    path('notebook/<int:pk>/delete/', views.NotebookDeleteView.as_view(), name='notebook_delete'),

    path('dashboard/', views.DashboardTeacher.as_view(), name='dashboard'),
    path('yourtickets/', views.MyTicket.as_view(), name='user_tickets'),
    path('createtikcet/', views.CreateMyTicket.as_view(), name='create_user_tickets'),
]