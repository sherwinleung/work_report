#!/usr/bin/env python
"""
Django管理命令：为现有用户初始化默认API配置
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.reports.models import APIConfig

User = get_user_model()

class Command(BaseCommand):
    help = '为现有用户初始化默认API配置'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制更新现有配置',
        )
        parser.add_argument(
            '--openai-key',
            type=str,
            help='OpenAI API密钥（默认使用LLMHub代理）',
        )

    def handle(self, *args, **options):
        self.stdout.write('开始初始化默认API配置...')
        
        # 获取所有用户
        users = User.objects.all()
        self.stdout.write(f'找到 {users.count()} 个用户')
        
        total_created = 0
        total_updated = 0
        
        for user in users:
            self.stdout.write(f'\n处理用户: {user.email}')
            
            # 为每个用户创建默认配置
            created_configs = self._create_default_configs_for_user(user, options)
            
            if created_configs:
                total_created += len(created_configs)
                for config in created_configs:
                    self.stdout.write(f'  ✓ 创建 {config.provider} 配置')
            
            # 检查是否需要更新现有配置
            if options['force']:
                updated_configs = self._update_existing_configs(user, options)
                if updated_configs:
                    total_updated += len(updated_configs)
                    for config in updated_configs:
                        self.stdout.write(f'  ✓ 更新 {config.provider} 配置')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n完成！创建了 {total_created} 个新配置，更新了 {total_updated} 个现有配置'
            )
        )

    def _create_default_configs_for_user(self, user, options):
        """为用户创建默认API配置"""
        created_configs = []
        
        # 检查是否已有OpenAI配置
        openai_config, created = APIConfig.objects.get_or_create(
            user=user,
            provider='openai',
            defaults={
                'api_key': options.get('openai_key') or 'sk-QLZDJaU1a8uuoYfdaN52FPzpoFFUmPlhEOmgmyMZ5g=',
                'api_base': 'https://llmhub.app',
                'is_active': True,  # 默认启用OpenAI
            }
        )
        if created:
            created_configs.append(openai_config)
        
        # 检查是否已有DeepSeek配置
        deepseek_config, created = APIConfig.objects.get_or_create(
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

    def _update_existing_configs(self, user, options):
        """更新现有配置"""
        updated_configs = []
        
        # 更新OpenAI配置
        try:
            openai_config = APIConfig.objects.get(user=user, provider='openai')
            if options.get('openai_key'):
                openai_config.api_key = options['openai_key']
                openai_config.save()
                updated_configs.append(openai_config)
        except APIConfig.DoesNotExist:
            pass
        
        return updated_configs
