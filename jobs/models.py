# jobs/models.py
from django.db import models
from django.utils import timezone

class Job(models.Model):
    title       = models.CharField(max_length=255)
    company     = models.CharField(max_length=255)
    location    = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    link        = models.URLField()
    source      = models.CharField(max_length=100)
    raw_html    = models.TextField(blank=True)
    created_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["link", "source"], name="uniq_job_per_source"),
        ]
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["location"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.title} at {self.company}"


