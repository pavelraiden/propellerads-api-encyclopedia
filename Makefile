# Makefile для PropellerAds API Encyclopedia

.PHONY: help install test test-unit test-integration test-all lint format clean docs

# Змінні
PYTHON := python3
PIP := pip3
PYTEST := pytest
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs

# Кольори для виводу
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

help: ## Показати це повідомлення
	@echo "$(BLUE)PropellerAds API Encyclopedia - Команди$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

install: ## Встановити залежності
	@echo "$(YELLOW)Встановлення залежностей...$(RESET)"
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio pytest-mock

test: test-unit ## Запустити unit тести (за замовчуванням)

test-unit: ## Запустити тільки unit тести
	@echo "$(YELLOW)Запуск unit тестів...$(RESET)"
	$(PYTEST) $(TEST_DIR) -m "not integration" -v

test-integration: ## Запустити інтеграційні тести (потребують API токен)
	@echo "$(YELLOW)Запуск інтеграційних тестів...$(RESET)"
	@if [ -z "$$MainAPI" ]; then \
		echo "$(RED)Помилка: MainAPI токен не встановлено$(RESET)"; \
		echo "Встановіть: export MainAPI='your_token'"; \
		exit 1; \
	fi
	$(PYTEST) $(TEST_DIR) -m "integration" -v

test-all: ## Запустити всі тести
	@echo "$(YELLOW)Запуск всіх тестів...$(RESET)"
	$(PYTEST) $(TEST_DIR) -v

test-coverage: ## Запустити тести з покриттям коду
	@echo "$(YELLOW)Запуск тестів з покриттям...$(RESET)"
	$(PYTEST) $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term

test-quick: ## Швидкий тест основного функціоналу
	@echo "$(YELLOW)Швидкий тест клієнта...$(RESET)"
	$(PYTHON) $(SRC_DIR)/examples/quick_start.py

demo: ## Запустити демо enhanced клієнта
	@echo "$(YELLOW)Запуск демо enhanced клієнта...$(RESET)"
	$(PYTHON) $(SRC_DIR)/examples/enhanced_client_demo.py

lint: ## Перевірити код на помилки
	@echo "$(YELLOW)Перевірка коду...$(RESET)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 $(SRC_DIR) $(TEST_DIR) --max-line-length=100; \
	else \
		echo "$(RED)flake8 не встановлено. Встановіть: pip install flake8$(RESET)"; \
	fi

format: ## Форматувати код
	@echo "$(YELLOW)Форматування коду...$(RESET)"
	@if command -v black >/dev/null 2>&1; then \
		black $(SRC_DIR) $(TEST_DIR) --line-length=100; \
	else \
		echo "$(RED)black не встановлено. Встановіть: pip install black$(RESET)"; \
	fi

clean: ## Очистити тимчасові файли
	@echo "$(YELLOW)Очищення тимчасових файлів...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

docs: ## Генерувати документацію
	@echo "$(YELLOW)Генерація документації...$(RESET)"
	@echo "Документація вже створена в папці $(DOCS_DIR)/"
	@ls -la $(DOCS_DIR)/

health-check: ## Перевірити здоров'я API
	@echo "$(YELLOW)Перевірка здоров'я API...$(RESET)"
	@$(PYTHON) -c "
import sys; sys.path.append('$(SRC_DIR)')
from propellerads_client import PropellerAdsUltimateClient
client = PropellerAdsUltimateClient()
health = client.health_check()
print('✅ API Health:', health['overall_health'])
print('💰 Balance: $$' + health.get('balance', 'N/A'))
"

validate: ## Валідувати структуру проекту
	@echo "$(YELLOW)Валідація структуру проекту...$(RESET)"
	@echo "Перевірка основних файлів:"
	@for file in README.md requirements.txt $(SRC_DIR)/propellerads_client.py $(TEST_DIR)/test_client.py; do \
		if [ -f "$$file" ]; then \
			echo "✅ $$file"; \
		else \
			echo "❌ $$file"; \
		fi; \
	done

benchmark: ## Запустити бенчмарк API
	@echo "$(YELLOW)Бенчмарк API продуктивності...$(RESET)"
	@$(PYTHON) -c "
import time, sys; sys.path.append('$(SRC_DIR)')
from propellerads_client import PropellerAdsUltimateClient
client = PropellerAdsUltimateClient()
start = time.time()
for i in range(5):
    client.get_balance()
end = time.time()
print(f'⚡ 5 запитів за {end-start:.2f}s ({5/(end-start):.1f} req/s)')
"

# Комбіновані команди
dev-setup: install ## Повне налаштування для розробки
	@echo "$(GREEN)Розробницьке середовище готове!$(RESET)"

ci: test lint ## CI pipeline (тести + лінтинг)
	@echo "$(GREEN)CI pipeline завершено успішно!$(RESET)"

release-check: test-all lint docs validate ## Перевірка готовності до релізу
	@echo "$(GREEN)Проект готовий до релізу!$(RESET)"
