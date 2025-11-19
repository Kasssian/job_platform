from django.contrib import admin

from .models import Resume, Education, Experience


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'desired_salary', 'created_at', 'is_active')
    list_filter = ('is_active', 'city', 'category', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('resume', 'institution', 'faculty', 'specialty', 'end_year')
    search_fields = ('institution', 'specialty')
    list_filter = ('end_year',)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('resume', 'company', 'position', 'start_date', 'end_date', 'current_job')
    list_filter = ('current_job', 'start_date', 'end_date')
    search_fields = ('company', 'position')
