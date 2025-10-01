# 🚀 Подробное Руководство по Установке PropellerAds SDK

Это руководство поможет вам установить и настроить PropellerAds SDK на Windows, macOS и Linux.



## 🖥️ Установка на Windows

### Шаг 1: Установка Git

Git - это система контроля версий, которая нужна для скачивания проекта. Если у вас еще не установлен Git, скачайте его с официального сайта:

[https://git-scm.com/download/win](https://git-scm.com/download/win)

При установке оставьте все настройки по умолчанию.

### Шаг 2: Установка Python

Python - это язык программирования, на котором написан SDK. Скачайте последнюю версию Python с официального сайта:

[https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

**Важно:** Во время установки обязательно поставьте галочку `Add Python to PATH`.

![Add Python to PATH](https://i.imgur.com/f3sJsgn.png)

### Шаг 3: Скачивание и Установка SDK

1.  **Откройте Командную строку:**
    *   Нажмите `Win + R`, введите `cmd` и нажмите `Enter`.

2.  **Создайте папку для проекта:**
    ```bash
    mkdir propeller_project
    cd propeller_project
    ```

3.  **Скачайте проект с GitHub:**
    ```bash
    git clone https://github.com/pavelraiden/propellerads-api-encyclopedia.git
    cd propellerads-api-encyclopedia
    ```

4.  **Запустите автоматическую установку:**
    ```bash
    INSTALL.bat
    ```
    *Если `INSTALL.bat` не существует, выполните команду:*
    ```bash
    pip install -r requirements.txt
    ```



## 🍎 Установка на macOS

### Шаг 1: Установка Homebrew

Homebrew - это менеджер пакетов для macOS, который упрощает установку программ. Если у вас еще не установлен Homebrew, откройте **Терминал** и выполните команду:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Шаг 2: Установка Git и Python

1.  **Откройте Терминал:**
    *   `Command + Пробел`, введите `Терминал` и нажмите `Enter`.

2.  **Установите Git и Python с помощью Homebrew:**
    ```bash
    brew install git python
    ```

### Шаг 3: Скачивание и Установка SDK

1.  **Создайте папку для проекта:**
    ```bash
    mkdir propeller_project
    cd propeller_project
    ```

2.  **Скачайте проект с GitHub:**
    ```bash
    git clone https://github.com/pavelraiden/propellerads-api-encyclopedia.git
    cd propellerads-api-encyclopedia
    ```

3.  **Запустите автоматическую установку:**
    ```bash
    ./INSTALL.sh
    ```



## 🐧 Установка на Linux (Ubuntu/Debian)

### Шаг 1: Установка Git и Python

1.  **Откройте Терминал:**
    *   `Ctrl + Alt + T`

2.  **Установите Git и Python с помощью apt:**
    ```bash
    sudo apt update
    sudo apt install git python3 python3-pip -y
    ```

### Шаг 2: Скачивание и Установка SDK

1.  **Создайте папку для проекта:**
    ```bash
    mkdir propeller_project
    cd propeller_project
    ```

2.  **Скачайте проект с GitHub:**
    ```bash
    git clone https://github.com/pavelraiden/propellerads-api-encyclopedia.git
    cd propellerads-api-encyclopedia
    ```

3.  **Запустите автоматическую установку:**
    ```bash
    ./INSTALL.sh
    ```

