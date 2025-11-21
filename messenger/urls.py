from django.urls import path
from . import views

app_name = 'messenger'

urlpatterns = [
    path('inbox/', views.InboxView.as_view(), name='inbox'),
    path('dialog/<int:companion_id>/', views.DialogView.as_view(), name='dialog'),
    path('notifications/', views.NotificationsView.as_view(), name='notifications'),

    # HTMX
    path('htmx/send/', views.htmx_send_message, name='htmx_send_message'),
    path('htmx/notification/<int:notification_id>/read/', views.htmx_mark_notification_read, name='htmx_mark_read'),
    path('htmx/unread-notifications/', views.htmx_get_unread_notifications, name='htmx_unread_notifications'),
]