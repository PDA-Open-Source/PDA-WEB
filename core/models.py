from django.db import models


class Notification(models.Model):

    title = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=100000, null=True)
    notification_type = models.CharField(max_length=255, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    role = models.CharField(max_length=255, null=True)
    user_id = models.CharField(max_length=255, null=True)
    session_id = models.BigIntegerField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "notification"


class Session(models.Model):

    address = models.CharField(max_length=255, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    program_name = models.CharField(max_length=255, null=True)
    session_creator = models.CharField(max_length=255, null=True)
    session_description = models.TextField(null=True)
    session_end_date = models.CharField(max_length=255, null=True)
    session_name = models.CharField(max_length=255, null=True)
    session_start_date = models.CharField(max_length=255, null=True)
    session_status = models.IntegerField()
    program_id = models.BigIntegerField(null=True)
    topic_id = models.BigIntegerField(null=True)
    training_organization = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session_name

    class Meta:
        db_table = "session"


class Attendance(models.Model):

    attestation_url = models.CharField(max_length=255, null=True)
    deleted = models.BooleanField(default=False)
    is_scan_in = models.BooleanField(default=False, null=True)
    is_scan_out = models.BooleanField(default=False, null=True)
    role = models.CharField(max_length=255, null=True)
    scan_in_date_time = models.CharField(max_length=255, null=True)
    scan_out_date_time = models.CharField(max_length=255, null=True)
    session_id = models.BigIntegerField(null=True)
    user_id = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.attestation_url

    class Meta:
        db_table = "attendance"


class Session_Links(models.Model):

    session_url = models.CharField(max_length=255, null=True)
    user_id = models.CharField(max_length=255, null=True)
    session_id = models.BigIntegerField(null=True)

    def __str__(self):
        return self.session_url

    class Meta:
        db_table = "session_links"
