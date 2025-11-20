from django.contrib import admin

from .models import Company, Vacancy, Application


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'website', 'employees_count', 'founded_year')
    search_fields = ('name', 'user__username', 'user__email', 'website')
    raw_id_fields = ('user',)
    readonly_fields = ()


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'salary_from', 'salary_to', 'location', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('title', 'company__name', 'description', 'location')
    raw_id_fields = ('company', 'category')
    filter_horizontal = ('skills',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('jobseeker', 'vacancy', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('jobseeker__user__username', 'vacancy__title', 'vacancy__company__name')
    raw_id_fields = ('jobseeker', 'vacancy')
    readonly_fields = ('applied_at',)
