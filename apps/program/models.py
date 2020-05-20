from django.db import models
from apps.entity.models import Entity


class Program(models.Model):

    name = models.CharField(max_length=260)
    deleted = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    description = models.TextField()
    start_date = models.DateField(null=True)
    email = models.EmailField(null=True)
    end_date = models.DateField(null=True)
    user_limit = models.IntegerField(null=True, default=0)

    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name="programs", null=True, default=31
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255, null=True)
    is_hyperlinked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "program"

    def delete(self, **kwargs):
        try:
            program_id = kwargs['pk']
            Program.objects.filter(id=program_id).update(deleted=True)
            return True
        except ValueError:
            return False

    def reactivate(self, **kwargs):
        try:
            program_id = kwargs['pk']
            Program.objects.filter(id=program_id).update(deleted=False)
            return True
        except ValueError:
            return False


class ProgramDocument(models.Model):

    name = models.CharField(max_length=255, null=True)
    deleted = models.BooleanField(default=False)
    content_type = models.CharField(max_length=255, null=True)
    content_url = models.CharField(max_length=255, null=True)
    vimeo_url = models.CharField(max_length=255, null=True)
    attachment = models.FileField(null=True)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="documents", null=True
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "program_documents"

    def delete(self, **kwargs):
        try:
            doc_id = kwargs['pk']
            ProgramDocument.objects.filter(id=doc_id).update(deleted=True)
            return True
        except ValueError:
            return False


class Topic(models.Model):

    name = models.CharField(max_length=100000)
    deleted = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    description = models.TextField(null=True)
    is_session_linked = models.BooleanField(default=False)
    session_linked = models.BooleanField(default=False)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="topics", null=True
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "topic"

    def delete(self, **kwargs):
        try:
            topic_id = kwargs['pk']
            Topic.objects.filter(id=topic_id).update(deleted=True)
            return True
        except ValueError:
            return False

    def reactivate(self, **kwargs):
        try:
            topic_id = kwargs['pk']
            Topic.objects.filter(id=topic_id).update(deleted=False)
            return True
        except ValueError:
            return False


class Content(models.Model):

    name = models.CharField(max_length=255, null=True)
    deleted = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    content_type = models.CharField(max_length=255, null=True)
    content_url = models.CharField(max_length=255, null=True)
    vimeo_url = models.CharField(max_length=255, null=True)
    attachment = models.FileField(null=True)
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="contents", null=True
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content"

    def deletecontent(self, **kwargs):
        try:
            self.deleted = True
            self.save()
            return True
        except ValueError:
            return False


class Eligible_Program_Admin(models.Model):

    user_id = models.CharField(primary_key=True, max_length=255)
    created_at = models.DateTimeField()
    deleted = models.BooleanField(default=False)
    updated_at = models.DateField(auto_now=True, null=True, blank=True)
    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name="eligible_program_admin", null=True
    )

    class Meta:
        db_table = "eligible_program_admin"
        unique_together = (('user_id', 'entity'),)

    def __str__(self):
        return self.user_id

    def delete(self, **kwargs):
        try:
            user_id = kwargs['user_id']
            entity_id = kwargs['pk']
            Eligible_Program_Admin.objects.filter(user_id=user_id, entity_id=entity_id).update(deleted=True)
            return True
        except ValueError:
            return False

    def reactivate(self, **kwargs):
        try:
            user_id = kwargs['user_id']
            entity_id = kwargs['pk']
            Eligible_Program_Admin.objects.filter(user_id=user_id, entity_id=entity_id).update(deleted=False)
            return True
        except ValueError:
            return False


class Program_Roles(models.Model):

    role = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="program_roles", null=False
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255, null=True)

    class Meta:
        unique_together = (('role', 'user_id', 'program'),)
        db_table = "program_roles"

    def __str__(self):
        return self.role

    def delete(self, **kwargs):
        try:
            user_id = kwargs['user_id']
            program_id = kwargs['pk']
            role = kwargs['role']
            Program_Roles.objects.filter(user_id=user_id, program_id=program_id, role=role).update(deleted=True)
            return True
        except ValueError:
            return False

    def reactivate(self, **kwargs):
        try:
            user_id = kwargs['user_id']
            program_id = kwargs['pk']
            role = kwargs['role']
            Program_Roles.objects.filter(user_id=user_id, program_id=program_id, role=role).update(deleted=False)
            return True
        except ValueError:
            return False
