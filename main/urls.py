from django.urls import path
from . import views

urlpatterns = [
    # Основные страницы
    path('', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('projects/', views.ProjectsView.as_view(), name='projects'),
    path('achievements/', views.AchievementsView.as_view(), name='achievements'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),

    # Блог
    path('blog/', views.BlogView.as_view(), name='blog'),
    path('blog/category/<slug:category_slug>/', views.BlogView.as_view(), name='blog_category'),
    path('blog/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),

    # Аутентификация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # API
    path('api/article/<int:article_id>/comment/', views.add_comment, name='add_comment'),
    path('api/article/<int:article_id>/like/', views.toggle_article_like, name='toggle_article_like'),
    path('api/comment/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
]