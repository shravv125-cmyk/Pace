from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    user_slug_id = models.PositiveIntegerField()
    

    class Meta:
        unique_together = ("user", "user_slug_id")

    def save(self, *args, **kwargs):
        if not self.pk:   # only when creating a new subject
            last = Subject.objects.filter(user=self.user).order_by("-user_slug_id").first()

            if last:
                self.user_slug_id = last.user_slug_id + 1
            else:
                self.user_slug_id = 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class SubjectDocument(models.Model):
    DOCUMENT_TYPES = (
        ('syllabus', 'Syllabus'),
        ('notes', 'Lecture Notes'),
    )
    
    # Clean, singular relationship link declaration
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES) # Added choices validation back
    file = models.FileField(upload_to='documents/') 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_doc_type_display()})" # type: ignore
        
    def filename(self):
        return os.path.basename(self.file.name)
    
class Document(models.Model):
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name='uploaded_notes'  # 👈 Changed this to be unique!
    )
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='subject_syllabi/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"

class Module(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=1) # Module 1, Module 2, etc.
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Mod {self.order}: {self.title}"



class Task(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True,blank=True)
    module = models.ForeignKey(Module,on_delete=models.SET_NULL,null=True,blank=True,related_name="tasks")
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

class StudyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_logs')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='study_logs')
    session_date = models.DateField(auto_now_add=True)
    duration_minutes = models.PositiveIntegerField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} read {self.module.title} for {self.duration_minutes} mins"