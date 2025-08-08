from django.urls import path
app_name = 'webmain'
from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contacts/', views.ContactView.as_view(), name='contact'),
    path("faqs/", views.FaqsView.as_view(), name="faqs"),
    path("blogs/", views.BlogView.as_view(), name="blogs"),
    path("blog/<slug:slug>/", views.BlogDetailView.as_view(), name="blog"),
    path("page/<slug:slug>/", views.PageDetailView.as_view(), name="page"),
    path("specialists/", views.SpecialistsView.as_view(), name="specialists"),
    path("documentation/", views.DocumentationView.as_view(), name="documentation"),
]