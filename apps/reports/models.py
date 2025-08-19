from django.db import models
from django.conf import settings

class Report(models.Model):
    GRANULARITY_CHOICES = [
        ("daily","日报"), ("weekly","周报"), ("monthly","月报"), ("yearly","年报"), ("custom","自定义")
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    granularity = models.CharField(max_length=20, choices=GRANULARITY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    prompt_prefs = models.TextField(blank=True, help_text="可选：额外提示，例如希望突出指标/风险等")
    content_md = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} {self.granularity} {self.start_date}~{self.end_date}"
