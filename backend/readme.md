# Команды управления проектом

Для начала создадим основу для конфигурации проекта при помощи команды:

    django-admin startproject config . 

Точка в конце команды обязательна: она нужна, чтобы проект создался в текущей папке

---
Запуск сервера в режиме разработки 

    python manage.py runserver 
---
Создать все служебные таблицы можно одной командой: 

    python manage.py migrate 
---
Создайте суперпользователя командой:

    python manage.py createsuperuser 
---
Создайте каркас приложения

    python manage.py startapp lines
---
Выгрузка models.py из существующей БД

    python manage.py inspectdb > models.py

---


