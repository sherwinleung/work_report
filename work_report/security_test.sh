#!/bin/bash

# 安全组配置验证脚本
# 在本地运行，测试服务器安全组配置

echo "🔍 安全组配置验证开始..."

# 替换为你的服务器IP
SERVER_IP="your-server-ip"

echo ""
echo "1. 测试SSH连接 (22端口)"
timeout 5 telnet $SERVER_IP 22 2>/dev/null && echo "✅ SSH端口可访问" || echo "❌ SSH端口不可访问"

echo ""
echo "2. 测试HTTP连接 (80端口)" 
timeout 5 telnet $SERVER_IP 80 2>/dev/null && echo "✅ HTTP端口可访问" || echo "❌ HTTP端口不可访问"

echo ""
echo "3. 测试HTTPS连接 (443端口)"
timeout 5 telnet $SERVER_IP 443 2>/dev/null && echo "✅ HTTPS端口可访问" || echo "❌ HTTPS端口不可访问"

echo ""
echo "4. 测试MySQL端口 (3306端口 - 应该不可访问)"
timeout 5 telnet $SERVER_IP 3306 2>/dev/null && echo "⚠️  MySQL端口可访问 - 安全风险!" || echo "✅ MySQL端口正确屏蔽"

echo ""
echo "5. 测试Redis端口 (6379端口 - 应该不可访问)"
timeout 5 telnet $SERVER_IP 6379 2>/dev/null && echo "⚠️  Redis端口可访问 - 安全风险!" || echo "✅ Redis端口正确屏蔽"

echo ""
echo "6. 测试应用端口 (8000端口 - 应该不可访问)"
timeout 5 telnet $SERVER_IP 8000 2>/dev/null && echo "⚠️  应用端口可访问 - 建议通过Nginx代理" || echo "✅ 应用端口正确屏蔽"

echo ""
echo "🎯 安全检查完成!"
echo "如果所有测试都显示 ✅，说明安全组配置正确"
