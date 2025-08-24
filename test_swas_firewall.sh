#!/bin/bash

# 轻量应用服务器防火墙测试脚本
# 替换YOUR_SERVER_IP为你的实际服务器IP

SERVER_IP="YOUR_SERVER_IP"

echo "🔍 轻量应用服务器防火墙测试开始..."
echo "服务器IP: $SERVER_IP"
echo ""

# 测试SSH端口
echo "1. 测试SSH连接 (22端口)"
if timeout 5 bash -c "echo >/dev/tcp/$SERVER_IP/22" 2>/dev/null; then
    echo "✅ SSH端口(22)可访问"
else
    echo "❌ SSH端口(22)不可访问 - 请检查防火墙规则"
fi

echo ""

# 测试HTTP端口  
echo "2. 测试HTTP连接 (80端口)"
if timeout 5 bash -c "echo >/dev/tcp/$SERVER_IP/80" 2>/dev/null; then
    echo "✅ HTTP端口(80)可访问"
else
    echo "❌ HTTP端口(80)不可访问 - 请检查防火墙规则"
fi

echo ""

# 测试HTTPS端口
echo "3. 测试HTTPS连接 (443端口)" 
if timeout 5 bash -c "echo >/dev/tcp/$SERVER_IP/443" 2>/dev/null; then
    echo "✅ HTTPS端口(443)可访问"
else
    echo "❌ HTTPS端口(443)不可访问 - 请检查防火墙规则"
fi

echo ""

# 测试不应该开放的端口
echo "4. 安全检查 - 以下端口应该不可访问："

if timeout 3 bash -c "echo >/dev/tcp/$SERVER_IP/3306" 2>/dev/null; then
    echo "⚠️  MySQL端口(3306)可访问 - 存在安全风险!"
else
    echo "✅ MySQL端口(3306)正确屏蔽"
fi

if timeout 3 bash -c "echo >/dev/tcp/$SERVER_IP/6379" 2>/dev/null; then
    echo "⚠️  Redis端口(6379)可访问 - 存在安全风险!"
else
    echo "✅ Redis端口(6379)正确屏蔽"
fi

echo ""
echo "🎯 测试完成!"
echo ""
echo "📋 防火墙配置检查清单:"
echo "□ SSH(22)端口已开放且可访问"
echo "□ HTTP(80)端口已开放且可访问"  
echo "□ HTTPS(443)端口已开放且可访问"
echo "□ MySQL(3306)端口未开放"
echo "□ Redis(6379)端口未开放"
echo ""
echo "如果以上都显示 ✅，防火墙配置正确！"
