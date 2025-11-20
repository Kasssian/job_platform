from django.contrib import admin
from .models import JobseekerProfile, Education, Experience, JobseekerSkill


@admin.register(JobseekerProfile)
class JobseekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'desired_position', 'desired_salary_from', 'desired_salary_to', 'experience_years', 'is_open_to_work', 'updated_at')
    list_filter = ('is_open_to_work', 'experience_years', 'updated_at')
    search_fields = ('user__username', 'user__email', 'desired_position')
    readonly_fields = ('updated_at',)
    raw_id_fields = ('user',)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'institution', 'specialty', 'degree', 'start_year', 'end_year', 'is_current')
    list_filter = ('degree', 'is_current', 'start_year', 'end_year')
    search_fields = ('institution', 'specialty', 'profile__user__username')
    raw_id_fields = ('profile',)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('profile', 'company', 'position', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date', 'end_date')
    search_fields = ('company', 'position', 'profile__user__username')
    raw_id_fields = ('profile',)


@admin.register(JobseekerSkill)
class JobseekerSkillAdmin(admin.ModelAdmin):
    list_display = ('profile', 'skill', 'level')
    list_filter = ('level', 'skill')
    search_fields = ('profile__user__username', 'skill__name')
    raw_id_fields = ('profile', 'skill')