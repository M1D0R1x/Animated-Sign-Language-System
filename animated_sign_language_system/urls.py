from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from nltk.corpus.reader import documents

from animated_sign_language_system import views  # Correctly import views from your app

# Custom error handlers
handler404 = 'animated_sign_language_system.views.error_404_view'  # Correct import path
handler500 = 'animated_sign_language_system.views.error_500_view'  # Correct import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('animation/', views.animation_view, name='animation'),
    path('', views.home_view, name='home'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
