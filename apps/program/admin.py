from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from .models import Program
from .models import Topic
from .models import Content

class ProgramAdmin(admin.ModelAdmin):

    date_hierarchy = 'start_date'
    list_display = ('name_with_detail_link', 'start_date', 'end_date', 'deleted', 'update_link')
    search_fields = ('name',)
    actions = ('archive_action',)
    exclude = ('deleted',)
    list_filter = ('deleted',)
    def name_with_detail_link(self, obj):
        """
        custom list display field with detail page link
        """
        detail_url = reverse("admin:program_program_detail", kwargs={"object_id": obj.pk})
        return format_html(f"<a href='{detail_url}'>{obj.name}</a>")
    name_with_detail_link.short_description = 'NAME'
    name_with_detail_link.admin_order_field = 'name'

    def update_link(self, obj):
        """
        custom change link in list display
        """
        update_url = reverse("admin:program_program_change", kwargs={"object_id": obj.pk})
        return format_html(f"<a href='{update_url}'>&#9998;</a>")
        update_link.short_description = 'CHANGE'

    def archive_action(self, request, queryset):
        """
        Custom Action for Archive Program
        """
        rows_updated = queryset.update(deleted=True)
        if rows_updated == 1:
            message_bit = "1 Program was"
        else:
            message_bit = f"{rows_updated} Programs were"
        self.message_user(request, f"{message_bit} successfully archived.")
    archive_action.short_description = "Archive Selected Programs."

    def get_actions(self, request):
        """
        Remove Delete Selected Action
        """
        actions = super().get_actions(request)
        # try:
        #     del actions['delete_selected']
        # except IndexError:
        #     pass
        return actions

    def get_urls(self):
        """
        Add custom URL's to this App.
        """
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/detail/', self.admin_site.admin_view(self.detail_view), name="program_program_detail")
        ]
        return custom_urls + urls

    def detail_view(self, request, object_id=None):
        """
        Detail View
        """
        program = get_object_or_404(Program, pk=object_id)
        context = dict(self.admin_site.each_context(request), opts=Program._meta, object=program)
        return TemplateResponse(request, "admin/admin_program_detail.html", context)

class TopicAdmin(admin.ModelAdmin):

    list_display = ('name', 'program')
    list_filter = ('program',)
    search_fields = ('name',)

    def get_urls(self):
        """
        Add custom URL's to this App.
        """
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/detail/', self.admin_site.admin_view(self.detail_view), name="program_topic_detail")
        ]
        return custom_urls + urls
    def detail_view(self, request, object_id=None):
        """
        Detail View
        """
        topic = get_object_or_404(Topic, pk=object_id)
        context = dict(self.admin_site.each_context(request), opts=Program._meta, object=topic)
        return TemplateResponse(request, "admin/admin_topic_detail.html", context)



admin_site_name = 'pda'
admin.site.site_header = admin_site_name
admin.site.site_title = admin_site_name
admin.site.register(Program, ProgramAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Content)
