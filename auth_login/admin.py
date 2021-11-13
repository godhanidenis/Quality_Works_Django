from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Reporting_Manager, User,Teams, Agents, SOP_Types, SOP, LOB, Reporting

admin.site.site_header = 'Quality_Works_Adminpanel'

admin.site.register(User, UserAdmin)

class Lobadmin(admin.ModelAdmin):
    search_fields= ['Lob_name']
    list_filter=['Lob_name']
    list_display = ['Lob_name']
admin.site.register(LOB,Lobadmin)

class Teamsadmin(admin.ModelAdmin):
    search_fields= ['Team_name']
    list_filter=['Team_name']
    list_display = ['Team_name']
admin.site.register(Teams,Teamsadmin)

class Agentsadmin(admin.ModelAdmin):
    search_fields= ['Agent_name']
    list_filter=['Agent_name']
    list_display = ['Agent_name']
admin.site.register(Agents, Agentsadmin)

class Reporting_manager_admin(admin.ModelAdmin):
    search_fields= ['Manager_name']
    list_filter=['Manager_name']
    list_display = ['Manager_name']
admin.site.register(Reporting_Manager, Reporting_manager_admin)

class SOP_Types_admin(admin.ModelAdmin):
    search_fields= ['Sop_name']
    list_filter=['Sop_name']
    list_display = ['Sop_name']
admin.site.register(SOP_Types, SOP_Types_admin)

class Reporting_admin(admin.ModelAdmin):
    search_fields= ['Matrix_type']
    list_filter=['Matrix_type']
    list_display = ['Matrix_type']
admin.site.register(Reporting, Reporting_admin)

admin.site.register(SOP)