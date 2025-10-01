#!/bin/bash

echo "🚀 PropellerAds SDK - Автоматическая Установка"
echo "=============================================="

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+ и попробуйте снова."
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"

# Установка зависимостей
echo "📦 Устанавливаю зависимости..."
pip3 install -r requirements.txt

# Создание .env файла если его нет
if [ ! -f .env ]; then
    echo "📝 Создаю файл конфигурации..."
    cat > .env << EOF
# PropellerAds API Key
MainAPI=your_propellerads_api_key_here

# Claude API Key  
ANTHROPIC_API_KEY=your_claude_api_key_here
EOF
    echo "⚠️  ВАЖНО: Отредактируйте файл .env и добавьте ваши API ключи!"
fi

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте файл .env и добавьте ваши API ключи"
echo "2. Запустите: python3 claude_natural_interface_v2.py"
echo "3. Начинайте говорить с AI естественным языком!"
echo ""
echo "📖 Полный гайд: USER_GUIDE_FOR_NON_DEVELOPERS.md"
