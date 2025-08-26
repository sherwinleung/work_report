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


class APIConfig(models.Model):
    """
    API配置模型 - 管理用户的大模型API配置
    """
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('deepseek', 'DeepSeek'),
        ('claude', 'Claude'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_configs")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=500, help_text="API密钥")
    api_base = models.URLField(blank=True, help_text="API服务器地址（可选，使用默认地址则留空）")
    is_active = models.BooleanField(default=False, help_text="是否启用此配置")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'provider']
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        # 确保同一用户只有一个活跃的API配置
        if self.is_active:
            APIConfig.objects.filter(user=self.user, is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.provider} ({'启用' if self.is_active else '禁用'})"

    @classmethod
    def create_default_configs_for_user(cls, user):
        """
        为新用户创建默认的API配置
        """
        created_configs = []
        
        # 创建OpenAI配置（使用LLMHub代理，默认启用）
        openai_config, created = cls.objects.get_or_create(
            user=user,
            provider='openai',
            defaults={
                'api_key': 'sk-QLZDJaU1a8uuoYfdaN52FPzpoFFUmPlhEOmgmyMZ5g=',
                'api_base': 'https://llmhub.app',
                'is_active': True,  # 默认启用OpenAI
            }
        )
        if created:
            created_configs.append(openai_config)
        
        # 创建DeepSeek配置（不启用）
        deepseek_config, created = cls.objects.get_or_create(
            user=user,
            provider='deepseek',
            defaults={
                'api_key': 'sk-d40ba7f7a4b242268876d3ca27d72684',
                'api_base': 'https://api.deepseek.com',
                'is_active': False,
            }
        )
        if created:
            created_configs.append(deepseek_config)
        
        return created_configs
