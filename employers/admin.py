from django.contrib import admin

from .models import Company, Vacancy


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'website', 'is_verified')
    list_filter = ('is_verified', 'city')
    search_fields = ('name', 'user__email', 'description')
    readonly_fields = ('created_at',)


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'salary_from', 'salary_to', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'employment_type', 'experience', 'created_at')
    search_fields = ('title', 'company__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
