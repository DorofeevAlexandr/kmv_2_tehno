    sudo docker compose down
    sudo docker compose build
    sudo docker compose up -d
    sudo docker ps -a
    
    sudo docker logs --tail 100 kmv_2-app-1
    sudo docker logs --tail 100 kmv_2-db-1
    sudo docker logs --tail 100 kmv_2-web-1

    
    sudo docker compose logs -f

---
Удалит тома вместе с контейнерами:

    docker compose down -v
---
Запустить миграцию:

    $ docker compose exec web python manage.py migrate --noinput
---
Создайте суперпользователя командой:

    $ sudo docker compose exec web python manage.py createsuperuser 
---
    sudo docker compose down
    sudo docker compose -f docker-compose.prod.yml down
    sudo docker compose -f docker-compose.prod.yml up -d --build
---
    sudo docker compose -f docker-compose.prod.yml up -d --build
    sudo docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
    sudo docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
---
Запуск psql

    docker exec -it kmv_2-db-1 psql -U username lines_database 
---
Вход в терминал контейнера

    sudo docker compose -f docker-compose.prod.yml exec -it ftp sh
---


