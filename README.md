# GRADUATE_DIARY_PROJECT
## Описание
Данный проект - это реализация дипломного проекта **Веб-приложение для ведения личного дневника** от *SkyPro*.
  
## Инструкция по установке
Для того, чтобы проверить код из данного репозитория вам понадобятся **Python**, **Poetry** и **Pycharm**, так что перед началом убедитесь, что они установлены на ваш ПК (проект пишется на версии Python 3.12.7).
Если хотите использовать Python версии ниже, чем 3.12, необходимо отредактировать файл **pyproject.toml**.  
Найдите в нем строчки и вместо **3.12** впишите версию Python, которую хотите использовать:  
```
[tool.poetry.dependencies]  
python = "^3.12"  
```

После чего скачайте все файлы проекта одним архивом:  
```
<> Code -> Download ZIP  
```

Разархивируйте скачанный файл в любое удобное для Вас место.  
Откройте папку проекта **GRADUATE_DIARY_PROJECT** с помощью **PyCharm**. 

Для работы приложения пропишите в терминале
~~~
poetry install
~~~

## Альтернативная инструкция по установке
Можете клонировать данный проект к себе на компьютер. Запустите командную строку из папки, в которую хотите клонировать данный проект

~~~
git clone git@github.com:your-username/GRADUATE_DIARY_PROJECT.git -b your_branch
git pull
~~~

Для работы приложения пропишите в терминале
~~~
poetry install
~~~

## Инструкция по использованию
Запустите в терминале
~~~
python manage.py runserver
~~~

Имейте в виду, что для работы на вашем компьютере, необходимо в .env файле прописать все необходимые переменные

~~~
SECRET_KEY=your_secret_key
DEBUG=True

POSTGRES_DB=your_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

TEST_EMAIL=example@sky.pro
TEST_PASSWORD=example
~~~

В браузере в адресной строке, перейдите на

~~~
http://127.0.0.1:8000/
~~~

Зарегистрируйтесь и войдите с помощью своего email.

Enjoy :)

## Кастомные команды
1. Для создания суперпользователя в .env файле пропишите email и пароль
~~~
TEST_EMAIL=example@sky.pro
TEST_PASSWORD=example
~~~

Затем в терминале наберите

~~~
python manage.py csu
~~~

2. Для заполнения БД тестовыми записями и тегами наберите в терминале

~~~
python manage.py load_initial_data
~~~

ВАЖНО: для работы данной команды, также как и для команды **csu** необходимо прописать в .env файле

~~~
TEST_EMAIL=example@sky.pro
TEST_PASSWORD=example
~~~

## Инструкция Docker
**Запуск приложения**

Для запуска всех сервисов, определенных в файле 
docker-compose.yml
, используйте команду:

~~~
docker-compose up -d --build
~~~

**Рассмотрим основные команды управления Docker Compose:**
~~~
docker-compose up
~~~
 — запускает все сервисы, определенные в файле 
docker-compose.yml
. Если образы для сервисов еще не созданы, они будут собраны перед запуском.
Флаг 
-d
 позволяет запустить контейнеры в фоновом режиме (Detach):
~~~
docker-compose up -d
~~~
~~~
docker-compose down
~~~
 — останавливает все работающие контейнеры и удаляет контейнеры, сети, тома и образы, созданные командой 
docker-compose up
.
~~~
docker-compose build
~~~
 — собирает образы для всех сервисов, используя Dockerfile, определенный в конфигурации.
~~~
docker-compose logs
~~~
 — позволяет просматривать логи всех контейнеров. Это полезно для отладки и мониторинга работы контейнеров.
~~~
docker-compose ps
~~~
 — выводит список всех контейнеров, созданных Docker Compose, и их текущее состояние.
~~~
docker-compose exec
~~~
 — позволяет выполнять команды внутри работающего контейнера. Это полезно для выполнения административных задач или отладки.
docker-compose exec service_name command
Где:

service_name
 — это имя контейнера, которое можно узнать с помощью команды 
docker ps
.
 
command
 — команда, которую нужно выполнить внутри контейнера.
Пример выполнения команды 
bash
 внутри контейнера 
web
:

docker-compose exec web bash

**Остановка и удаление контейнеров**

Чтобы остановить все работающие контейнеры и удалить контейнеры, сети, тома и образы, созданные командой 
docker-compose up
, используйте команду:

~~~
docker-compose down
~~~

**Просмотр логов**

Для просмотра логов всех контейнеров используйте команду:

~~~
docker-compose logs
~~~

## Настройка для виртуальной машины

Подключитесь к виртуальной машине с помощью команды, отображаемой в вашей личном кабинете yandex cloud:

~~~
ssh -l your_VM_login your_VM_public_IP
~~~

Обновите систему и установите Docker и Nginx:

~~~
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose -y
sudo apt install nginx
sudo systemctl enable docker
sudo systemctl start docker
~~~

Добавьте пользователя в группу docker:

~~~
sudo usermod -aG docker $USER
newgrp docker
~~~

**!!! НЕ ЗАКРЫВАЙТЕ ТЕРМИНАЛ, ОН ПОНАДОБИТСЯ ЧУТЬ ПОЗЖЕ !!!**

Перейдите в вашем репозитории GitHub в Settings → Secrets and variables → Actions. Добавьте следующие secrets:

| First Header            | Second Header                                                                  |
|-------------------------|--------------------------------------------------------------------------------|
| SSH_KEY                 | Приватный SSH ключ для доступа к серверу                                       |
| SSH_USER                | SSH пользователь (например: ubuntu)                                            |
| SERVER_IP               | IP адрес вашего сервера                                                        |
| DOCKER_HUB_ACCESS_TOKEN | Docker Hub Access Token                                                        |
| DOCKER_HUB_USERNAME     | Docker Hub username                                                            |
| SECRET_KEY              | Django SECRET_KEY                                                              |
| DEBUG                   | Django DEBUG (False для production)                                            |
| TEST_EMAIL              | Email для создания суперпользователя и загрузки в БД тестовых записей и тегов  |
| TEST_PASSWORD           | Пароль для создания суперпользователя и загрузки в БД тестовых записей и тегов |
| POSTGRES_DB             | Имя БД                                                                         |
| POSTGRES_USER           | Имя пользователя БД                                                            |
| POSTGRES_PASSWORD       | Пароль пользователя БД                                                         |
| POSTGRES_HOST           | Хост БД (для работы на сервере должен быть = db)                               |
| POSTGRES_PORT           | Порт БД (по стандарту должен быть = 5432)                                      |

Создайте репозиторий на Docker Hub
Сгенерируйте Access Token:
- Зайдите в Docker Hub → Account Settings → Security → New Access Token
- Сохраните токен в GitHub Secrets как DOCKER_HUB_ACCESS_TOKEN

Сделайте fork проекта в свой github и клонируйте проект на сервер и к себе локально на компьютер (сделайте это из терминала открытом на первых шагах, вы должны быть подключены к виртуальной машине и находиться в корневом каталоге сервера):

~~~
git clone git@github.com:your-username/GRADUATE_DIARY_PROJECT.git -b your_branch
~~~

Перейдите в папку **GRADUATE_DIARY_PROJECT**:

~~~
cd GRADUATE_DIARY_PROJECT/
~~~

Закоммитьте изменения в вашу ветку:

~~~
git add .
git commit -m "Deploy preparation"
git push origin your_branch
~~~

GitHub Actions автоматически запустит workflow:
- Сборка Docker образа
- Запуск тестов
- Пуш образа в Docker Hub
- Деплой на сервер

Проверьте работу приложения.

Создайте superuser с помощью команды:

~~~
sudo docker compose -f docker-compose.yml --env-file .env exec web python manage.py csu
~~~

Логин суперпользователя (из .env файла):

~~~
TEST_EMAIL=example@sky.pro
~~~

Пароль суперпользователя (из .env файла):

~~~
TEST_PASSWORD=example
~~~

Перейдите по публичному ip вашего сервера в браузере, вы должны увидеть главную страницу личного дневника:

Команды для управления на сервере:

~~~
# Просмотр запущенных контейнеров
docker ps

# Просмотр логов
docker logs <container_name>

# Остановка и удаление контейнеров
docker compose down

# Перезапуск контейнеров
docker compose restart

# Просмотр системных логов
journalctl -u docker --since "1 hour ago"
~~~

❌ Устранение неполадок

Если деплой не удался:
1. Проверьте логи GitHub Actions в соответствующем workflow
2. Проверьте подключение к серверу:
~~~
ssh -v your-user@your-server-ip
~~~
3. Проверьте Docker на сервере:
~~~
ssh your-user@your-server-ip
docker info
docker ps -a
~~~
4. Проверьте наличие .env файла на сервере:
~~~
cat ~/GRADUATE_DIARY_PROJECT/.env
~~~

## Готовое развернутое приложение доступно по адресу
~~~
158.160.184.104
~~~