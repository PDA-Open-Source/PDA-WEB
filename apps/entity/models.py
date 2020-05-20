from django.db import models
from django.core.validators import RegexValidator

# numeric = RegexValidator(r'^[0-9]*$', 'Only numeric characters are allowed.')


class Entity(models.Model):

    name = models.CharField(max_length=255, blank=False)
    business_registration_number = models.CharField(max_length=255, null=True)
    tax_registration_number = models.CharField(max_length=255, null=True)
    address_line1 = models.CharField(max_length=255, null=True)
    address_line2 = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    pin_code = models.CharField(max_length=10, null=True)
    deleted = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "entity"

    def delete(self, **kwargs):
        try:
            id = kwargs['pk']
            Entity.objects.filter(id=id).update(deleted=True)
            return True
        except ValueError:
            return False

    def reactivate(self, **kwargs):
        try:
            id = kwargs['pk']
            Entity.objects.filter(id=id).update(deleted=False)
            return True
        except ValueError:
            return False

    def register(self, **kwargs):
        try:
            self.is_registered = True
            self.save()
            return True
        except ValueError:
            return False


class EntityDocument(models.Model):

    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name="entity_documents"
    )
    content_type = models.CharField(max_length=255, null=True)
    content_url = models.CharField(max_length=255, null=True)
    vimeo_url = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    deleted = models.BooleanField(default=False)
    attachment = models.FileField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "entity_documents"

    def delete(self, **kwargs):
        try:
            id = kwargs['pk']
            EntityDocument.objects.filter(id=id).update(deleted=True)
            return True
        except ValueError:
            return False


class Entity_Role(models.Model):

    role = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)

    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name="entity_role", null=False
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255, null=True)

    class Meta:
        unique_together = (('role', 'user_id', 'entity'),)
        db_table = "entity_role"

    def __str__(self):
        return self.role

    def delete(self, **kwargs):
        try:
            user_id = kwargs['user_id']
            entity_id = kwargs['pk']
            Entity_Role.objects.filter(user_id=user_id, entity_id=entity_id).update(deleted=True)
            return True
        except ValueError:
            return False

    def reactivate(self, **kwargs):
        try:
            user_id = kwargs['user_id']
            entity_id = kwargs['pk']
            Entity_Role.objects.filter(user_id=user_id, entity_id=entity_id).update(deleted=False)
            return True
        except ValueError:
            return False
