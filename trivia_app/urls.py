from django.conf.urls import url
from django.urls import path

from trivia_app import views

app_name = 'trivial'
urlpatterns = [
    path('', views.home, name = 'home'),
    path('<int:numero>/', views.preguntas, name = 'preguntas'),
    url(r'^signup/$', views.signup, name = 'signup'),
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout_view, name = 'logout'),
    path('ranking/', views.ranking, name = 'ranking'),
]