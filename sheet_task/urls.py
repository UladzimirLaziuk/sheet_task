from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('telegram_webhook/', views.TelegramViews.as_view(), name='telegram_api'),
    path('sheet_webhook/', views.SheetCreateUpdateAPIView.as_view(), name='sheet_api'),
    path('sheet_parse/', views.AdSheetBaseViews.as_view(), name='parse_sheet'),
    path('start/', views.StartViews.as_view(), name='start_app'),

]
