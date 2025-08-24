from django.db import models
from django.conf import settings
from datetime import datetime, timedelta

class WorkEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="work_entries")
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True, help_text="开始时间")
    end_time = models.TimeField(null=True, blank=True, help_text="结束时间")
    title = models.CharField(max_length=200, blank=True, help_text="简要标题（可选）")
    content = models.TextField(help_text="工作内容/事项")
    duration_minutes = models.PositiveIntegerField(default=0, help_text="本条记录的工作时长（分钟，自动计算）")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [models.Index(fields=["user","date"])]

    def __str__(self):
        return f"{self.user.email} {self.date} {self.title or self.content[:10]}"

    def clean(self):
        if self.start_time and self.end_time:
            start_dt = datetime.combine(self.date, self.start_time)
            end_dt = datetime.combine(self.date, self.end_time)
            if end_dt < start_dt:
                from datetime import timedelta
                end_dt += timedelta(days=1)
            mins = int((end_dt - start_dt).total_seconds() // 60)
            if mins < 0:
                mins = 0
            self.duration_minutes = mins

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
