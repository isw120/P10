from django.conf import settings
from django.db import models


class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    author_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)
    objects = models.Manager()


class Contributors(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(to=Projects, on_delete=models.CASCADE, blank=True)
    permission = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    objects = models.Manager()

    class Meta:
        unique_together = ('user', 'project',)


class Issues(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    project = models.ForeignKey(to=Projects, on_delete=models.CASCADE, blank=True)
    status = models.CharField(max_length=255)
    author_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)
    assignee_user = models.ForeignKey(to=Contributors, on_delete=models.CASCADE, blank=True)
    created_time = models.DateTimeField(auto_now_add=True, blank=True)
    objects = models.Manager()


class Comments(models.Model):
    comment_id = models.AutoField(primary_key=True, blank=True)
    description = models.CharField(max_length=255)
    author_user = models.ForeignKey(to=Contributors, on_delete=models.CASCADE, blank=True)
    issue = models.ForeignKey(to=Issues, on_delete=models.CASCADE, blank=True)
    created_time = models.DateTimeField(auto_now_add=True, blank=True)
    objects = models.Manager()
