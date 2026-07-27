from django.db import models
import os

class Space(models.Model):
    space_id = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.space_id

class Note(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200, blank=True, default='Untitled Note')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.space.space_id} - {self.title}"

def space_upload_path(instance, filename):
    return f"spaces/{instance.space.space_id}/{filename}"

class SpaceFile(models.Model):
    FILE_TYPE_CHOICES = (
        ('image', 'Image'),
        ('text', 'Text File'),
        ('document', 'Document'),
        ('other', 'Other'),
    )
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=space_upload_path)
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='other')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.space.space_id} - {self.filename}"

    @property
    def formatted_size(self):
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"