from django.urls import path
from . import views
app_name = 'moderation'
from django.http import HttpResponse

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),



    path('notifications/', views.UserNotificationListView.as_view(), name='user_notifications'),
    path('notifications/delete/', views.DeleteNotificationView.as_view(), name='delete_notification'),

    # """ Основное """

    # Панель управления
    path('dashboard_moder/', views.DashboardModer.as_view(), name='dashboard_moder'),

    # Личные записи модератора
    path('modernotebooks/', views.NotebookListView.as_view(), name='notebook_list'),
    path('modernotebook/events/', views.NotebookEventsView.as_view(), name='notebook-events'),
    path('modernotebook/<int:pk>/delete/', views.NotebookDeleteView.as_view(), name='notebook_delete'),

    # Тикеты
    path('tickets_moderation/', views.TicketsView.as_view(), name='tickets'),
    path('tickets/delete/', views.TicketDeleteView.as_view(), name='ticket_delete'),
    path('tickets/<uuid:ticket_id>/add_comment/', views.TicketCommentCreateView.as_view(), name='add_comment'),
    path('tickets/<slug:pk>/', views.TicketMessageView.as_view(), name='ticket_message'),
    # Пользователи
    path('groups/', views.CompanyModerationGroups.as_view(), name='groups'),
    path('groups/create/', views.ModerationGroupsCreateView.as_view(), name='groups_create'),
    path('groups/<uuid:pk>/update/', views.ModerationGroupsUpdateView.as_view(), name='groups_update'),
    path('groups/<uuid:group_id>/delete/', views.ModerationGroupsDeleteView.as_view(), name='delete_group'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('workerslist/', views.WorkerListView.as_view(), name='worker_list'),
    path('user/<slug:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('worker/<slug:pk>/delete/', views.WorkerDeleteView.as_view(), name='worker_delete'),
    path('profile/block/<uuid:pk>/', views.BlockUserView.as_view(), name='block_user'),
    path('profile/unblock/<uuid:pk>/', views.UnblockUserView.as_view(), name='unblock_user'),
    path('profile/restore/<uuid:pk>/', views.RestoreUserView.as_view(), name='restore_user'),
    path('profile/deleteuser/<uuid:pk>/', views.DeleteUserView.as_view(), name='delete_user'),
    path('profile/edit/<slug:pk>/', views.EditProfileView.as_view(), name='edit_profiles'),
    path('user-detail/<uuid:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('profileworker/edit/<uuid:user_id>/', views.EditWorkerProfileView.as_view(), name='edit_worker_profiles'),

    path('create_user/', views.SignUpWorkerView.as_view(), name='create_user'),

    # """ Lms """
    # Сертификаты
    path('coursesertificateuser/', views.CoursesertificateuserListView.as_view(), name='coursesertificateuser'),
    path('course/<uuid:course_id>/payment/', views.CoursePaymentView.as_view(), name='course_payment'),
    # Курсы
    path('courses/', views.CourseListView.as_view(), name='courses'),
    path('coursesavailable/', views.CourseAvailableListView.as_view(), name='coursesavailable'),
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='course'),
    path('coursepassing/<uuid:course_id>/', views.CoursePassingDetailView.as_view(), name='coursepassing'),
    path('quiz/<int:theme_id>/', views.QuizPassView.as_view(), name='quiz_pass'),
    path('start-free-course/<uuid:course_id>/', views.StartFreeCourseView.as_view(), name='start_free_course'),
    path('get_theme_description/<int:theme_id>/', views.get_theme_description, name='get_theme_description'),
    path('courses/<slug:slug>/reviews/', views.CourseReviewsView.as_view(), name='coursereviews'),
    path('courses/<slug:slug>/comment/', views.CourseCommentView.as_view(), name='coursecomment'),
    path('create-comment/', views.create_comment, name='create_comment'),
    path('create-reviews/', views.create_reviews, name='create_reviews'),
    path('mycourses/', views.MyCourseListView.as_view(), name='mycourses'),
    path('mycourse-comment/<uuid:pk>/', views.MyCourseCommentView.as_view(), name='mycourse_comment'),
    path('delete-comment/<int:comment_id>/', views.DeleteCourseCommentView.as_view(), name='delete_course_comment'),
    path('mycourse-reviews/<uuid:pk>/', views.MyCourseReviewsView.as_view(), name='mycourse_reviews'),
    path('mycourse-student/<uuid:pk>/', views.MyCourseStudentView.as_view(), name='mycourse_student'),
    path('download_certificate/<uuid:course_id>/', views.download_certificate, name='download_certificate'),
    path('submit_homework/', views.SubmitHomeWorkView.as_view(), name='submit_homework'),
    # Расписание
    path('mycourse-schedules/<uuid:pk>/', views.MyCourseSchedulesView.as_view(), name='mycourse_schedules'),
    path('mycourse-schedules/get_users/<int:schedule_id>/', views.GetUsersByScheduleView.as_view(), name='get_users_by_schedule'),
    path('courses/get_users/<uuid:course_id>/', views.GetUsersByCourseView.as_view(), name='get_users_by_course'),
    path('mycourse-schedules/<int:schedule_id>/remove_user/<uuid:user_id>/', views.RemoveUserFromScheduleView.as_view(), name='remove_user_from_schedule'),
    path('mycourse-schedules/create/<uuid:course_id>/', views.MyCourseSchedulesCreateView.as_view(), name='mycourse_schedules_create'),
    path('mycourse-schedules/update/<uuid:course_id>/<int:pk>/', views.MyCourseSchedulesUpdateView.as_view(), name='mycourse_schedules_update'),
    path('send_user_password/<uuid:user_id>/', views.SendUserPasswordView.as_view(), name='send_user_password'),

    path('mycourse-dashboard/<uuid:pk>/', views.CourseDashboard.as_view(), name='mycourse_dashboard'),

    path('delete-reviews/<int:rewievs_id>/', views.DeleteCourseReviewsView.as_view(), name='delete_course_reviews'),
    path('delete-schedules/<int:schedules_id>/', views.DeleteCourseSchedulesView.as_view(), name='delete_course_schedules'),


    path('course/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('course/<uuid:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    path('delete-course/<uuid:course_id>/', views.delete_course, name='delete_course'),
    path('course/data/', views.CourseDataView.as_view(), name='course_data'),
    path('course/<uuid:pk>/data/', views.CourseDataView.as_view(), name='course_data_edit'),
    path('course-themes/<uuid:course_id>/data/', views.ThemesCreateView.as_view(), name='create_theme'),
    path('themes/delete/<int:theme_id>/', views.ThemesDeleteView.as_view(), name='themes_delete'),
    path('quiz/delete/<int:quiz_id>/', views.QwizDeleteView.as_view(), name='quiz_delete'),
    path('themes-edit/<int:theme_id>/', views.ThemesEditView.as_view(), name='themes_edit'),
    path('themes-edit-get/<int:theme_id>/', views.ThemesEditGetView.as_view(), name='themes_edit_get'),
    path('file-upload/<int:theme_id>/', views.FileUploadView.as_view(), name='file_upload'),
    path('file-delete/<int:file_id>/', views.FileDeleteView.as_view(), name='file_delete'),
    path('update-file-link/<int:file_id>/', views.UpdateFileLinkView.as_view(), name='update_file_link'),
    path('move-theme/<int:theme_id>/<str:direction>/<int:position>/', views.move_theme, name='move_theme'),
    path('move-quiz/<int:quiz_id>/<str:direction>/<int:position>/', views.move_quiz, name='move_qwiz'),
    path('delete-question/<int:quiz_id>/<int:question_id>/', views.QuestionDeleteView.as_view(), name='delete_question'),
    path('theme-detail/', views.ThemeDetailView.as_view(), name='theme_detail'),
    path('qwiz-detail/', views.QwizDetailView.as_view(), name='qwiz_detail'),
    path('edit-module/<int:module_id>/', views.EditModuleView.as_view(), name='edit_module'),
    path('delete-module/<int:module_id>/', views.DeleteModuleView.as_view(), name='delete_module'),
    path('move-module/<int:module_id>/<str:direction>/', views.move_module, name='move_module'),
    path('create_module/<uuid:course_id>/', views.ModuleCreateView.as_view(), name='create_module'),
    path('create-qwiz/',  views.QwizCreateView.as_view(), name='create_qwiz'),
    path('certificate/update/<uuid:course_id>/', views.UpdateCourseCertificateView.as_view(), name='update_certificate'),
    # Для получения данных теста (GET)
    path('get-quiz/<int:quiz_id>/', views.QwizUpdateView.as_view(), name='get_quiz'),
    # Для обновления теста (POST)
    path('update-quiz/<int:quiz_id>/', views.QwizUpdateView.as_view(), name='update_quiz'),

    path('course/<uuid:course_id>/assistants/', views.CourseAssistantsListView.as_view(), name='course_assistants_list'),
    path('course/<uuid:course_id>/assistants/create/', views.CourseAssistantCreateView.as_view(),
         name='course_assistant_create'),
    path('course/<uuid:course_id>/assistants/<int:pk>/update/', views.CourseAssistantUpdateView.as_view(),
         name='course_assistant_edit'),

    path('course/<uuid:course_id>/assistants/<int:pk>/delete/', views.CourseAssistantDeleteView.as_view(),
         name='course_assistant_delete'),
    path('settings/<uuid:course_id>/', views.UpdateCourseSettingsView.as_view(), name='update_course_settings'),

    # Категории курсов
    path('courses-categorys/', views.CategoryscourseList.as_view(), name='categoryscourse'),
    path('categoryscourse/create/', views.CategoryscourseCreateView.as_view(), name='categoryscourse_create'),
    path('categoryscourse/<int:pk>/update/', views.CategoryscourseUpdateView.as_view(), name='categoryscourse_update'),
    path('categoryscourse/delete/', views.CategoryscourseDeleteView.as_view(), name='categoryscourse_delete'),

    # Преподаватели
    path('teacher-list/', views.TeacherListView.as_view(), name='teacher_list'),
    path('certificate-list/', views.CertificateListView.as_view(), name='certificate_list'),
    #path('teacher/<slug:pk>/', views.TeacherView.as_view(), name='teacher'),

    # Прохождение
    # Трансляции
    path('schedulestream/', views.SchedulestreamListView.as_view(), name='schedulestream_list'),
    path('schedulestream/events/', views.SchedulestreamEventsView.as_view(), name='schedulestream-events'),

    path('conferences/<uuid:course_id>/', views.VideoChatRoomListView.as_view(), name='conferences_list'),

    path('conferences/<uuid:course_id>/events/', views.ConferenceEventsView.as_view(), name='conferences-events'),
    # Требуется
    path('needcourses/', views.NeedcourseList.as_view(), name='needcourses'),


    # Правила
    path('curces_base/', views.CurcesDocPage.as_view(), name='curces_base'),

    # """ Сайт """

    # Домены

    # Общие настройки
    # SEO
    path('site/seo/', views.SeoSettings.as_view(), name='seo_settings'),
    path('site/seo/create/', views.SeoCreateView.as_view(), name='seo_create'),
    path('site/seo/<int:pk>/update/', views.SeoUpdateView.as_view(), name='seo_update'),
    path('seo/delete/', views.SeoDeleteMultipleView.as_view(), name='seo_delete'),
    # Групповое уведомления
    path('site/notifications/', views.NotificationSettings.as_view(), name='notifications_settings'),
    path('site/notifications/create/', views.NotificationCreateView.as_view(), name='notifications_create'),
    path('notification/delete_multiple/', views.NotificationDeleteMultipleView.as_view(), name='notification_delete_multiple'),
    # Страницы
    path('site/pages/', views.PagesSettings.as_view(), name='pages_settings'),
    path('site/pages/create/', views.PagesCreateView.as_view(), name='pages_create'),
    path('site/pages/<slug:slug>/update/', views.PagesUpdateView.as_view(), name='pages_update'),
    path('pages/delete/', views.PagesDeleteView.as_view(), name='pages_delete'),
    # Вакансии
    path('site/jobs/', views.JobsSettings.as_view(), name='jobs_settings'),
    path('site/jobs/create/', views.JobsCreateView.as_view(), name='jobs_create'),
    path('site/jobs/<slug:slug>/update/', views.JobsUpdateView.as_view(), name='jobs_update'),
    path('jobs/delete/', views.JobsDeleteView.as_view(), name='jobs_delete'),
    # Требуется курсы
    path('site/needcourse/', views.NeedcourseSettings.as_view(), name='needcourse_settings'),
    path('site/needcourse/create/', views.NeedcourseCreateView.as_view(), name='needcourse_create'),
    path('site/needcourse/<slug:slug>/update/', views.NeedcourseUpdateView.as_view(), name='needcourse_update'),
    path('needcourse/delete/', views.NeedcourseDeleteView.as_view(), name='needcourse_delete'),
    # Организации
    path('site/organizations/', views.OrganizationsSettings.as_view(), name='organizations_settings'),
    path('site/organizations/create/', views.OrganizationsCreateView.as_view(), name='organizations_create'),
    path('site/organizations/<slug:slug>/update/', views.OrganizationsUpdateView.as_view(), name='organizations_update'),
    path('organizations/delete/', views.OrganizationsDeleteView.as_view(), name='organizations_delete'),
    # Новости
    path('site/blog/', views.BlogsSettings.as_view(), name='blog_settings'),
    path('site/blog/create/', views.BlogCreateView.as_view(), name='blog_create'),
    path('site/blog/<slug:slug>/update/', views.BlogUpdateView.as_view(), name='blog_update'),
    path('blogs/delete/', views.BlogDeleteView.as_view(), name='blogs_delete'),
    path('create-category/', views.create_category, name='category_create'),
    path('category_list/', views.category_list, name='category_list'),
    path('site/category/', views.CategorysSettings.as_view(), name='categorys_settings'),
    path('site/category/create/', views.CategorysCreateView.as_view(), name='categorys_create'),
    path('site/category/<int:pk>/update/', views.CategorysUpdateView.as_view(), name='categorys_update'),
    path('categorys/delete/', views.CategorysDeleteView.as_view(), name='categorys_delete'),
    path('save_categories/<slug:slug>/', views.save_categories, name='save_categories'),
    # ЧаВо
    path('site/faq/', views.FaqSettings.as_view(), name='faq_settings'),
    path('site/faq/create/', views.FaqCreateView.as_view(), name='faq_create'),
    path('site/faq/<int:pk>/update/', views.FaqUpdateView.as_view(), name='faq_update'),
    path('faq/delete/', views.FaqDeleteView.as_view(), name='faq_delete'),

    path('landings/', views.LandingListView.as_view(), name='landing_list'),
    path('landing/create/', views.LandingCreateView.as_view(), name='landing_create'),
    path('landing/<slug:slug>/edit/', views.LandingEditorView.as_view(), name='landing_editor'),
    path('landing/save/', views.SaveLandingView.as_view(), name='save_landing'),
    # Типы оплаты
    path('site/payment_type/', views.PaymentSettings.as_view(), name='payment_settings'),
    path('site/payment_type/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('site/payment_type/<int:pk>/update/', views.PaymentUpdateView.as_view(), name='payment_update'),
    path('payment_type/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),
    # Документация
    path('documentation_moder/', views.Documentation.as_view(), name='documentation_moder'),
    path('documentation/create/', views.DocumentationCreateView.as_view(), name='docs_create'),
    path('documentation/update/<int:pk>/', views.DocumentationUpdateView.as_view(), name='docs_update'),
    path('documentation/delete/', views.DocumentationDeleteView.as_view(), name='docs_delete'),
    path('documentation/add_files/<int:documentation_id>/', views.UploadFileView.as_view(), name='add_files'),
    path('documentation/delete_file/<int:file_id>/', views.DeleteFileView.as_view(), name='delete_file'),
    # """ Личное """

    # График
    path('schedules/', views.ScheduleListView.as_view(), name='schedule_list'),
    path('schedule/events/', views.ScheduleEventsView.as_view(), name='schedule-events'),
    path('schedule/<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='schedule_delete'),
    # Тайминги
    path('user-sessions/', views.UserSessionListView.as_view(), name='user_session_list'),
    path('user-sessions/<uuid:moderator_id>', views.UserOtherSessionListView.as_view(), name='other_moderator_timing'),
    path('get_user_session/', views.getusersession, name='get_user_session'),
    # База знаний
    path('knowledge_base/', views.KnowledgePage.as_view(), name='knowledge'),
    # Выплаты
    path('withdraw/', views.WithdrawPage.as_view(), name='withdraw'),
    path('withdraw_all/', views.WithdrawAllPage.as_view(), name='withdraw_all'),
    path('withdraw/create/', views.WithdrawCreateView.as_view(), name='withdraw_create'),
    # HTMX
    path('usershtmx/', views.UserListHtmxView.as_view(), name='user_list_htmx'),
    path('documentation_moder/', views.Documentation.as_view(), name='documentation_moder'),
    # TinyMCE
    path('tinymce/image_upload/', views.tinymce_image_upload, name='tinymce_upload'),

    path('get_modules/', views.get_modules, name='get_modules'),

    path('libraryupdates/', views.libraryupdates, name='libraryupdates'),

    path('delete_hint/', views.delete_hint, name='delete_hint'),
    path('delete_question_type_six/', views.delete_question_type_six, name='delete_question_type_six'),

    path('quizcomplete/<int:theme_id>', views.QuizCompleteView.as_view(), name='quiz_completed'),

]