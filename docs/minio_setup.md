# Установка и настройка MinIO для Art Gallery Management System

## Введение

MinIO - это высокопроизводительное объектное хранилище, совместимое с Amazon S3 API. В этом документе описаны шаги по установке и настройке MinIO для использования в Art Gallery Management System.

## Системные требования

- Windows 10 или выше
- Минимум 4 ГБ оперативной памяти
- Минимум 1 ГБ свободного места на диске
- Доступ к порту 9000 (для API) и 9001 (для веб-интерфейса)

## Шаг 1: Загрузка MinIO

1. Перейдите на [официальный сайт MinIO](https://min.io/download) или скачайте бинарный файл напрямую с GitHub:
   ```
   https://dl.min.io/server/minio/release/windows-amd64/minio.exe
   ```

2. Сохраните файл `minio.exe` в удобном месте, например, `C:\minio\minio.exe`

## Шаг 2: Создание директории для данных

1. Создайте директорию для хранения данных MinIO:
   ```
   mkdir C:\minio\data
   ```

## Шаг 3: Настройка MinIO как сервиса Windows

### Вариант 1: Использование NSSM (рекомендуется)

1. Скачайте NSSM (Non-Sucking Service Manager) с [официального сайта](https://nssm.cc/download)
2. Распакуйте архив и запустите командную строку от имени администратора
3. Перейдите в директорию с NSSM и выполните:
   ```
   nssm.exe install MinIO
   ```
4. В открывшемся окне настройте параметры:
   - Path: `C:\minio\minio.exe`
   - Startup directory: `C:\minio`
   - Arguments: `server C:\minio\data --console-address :9001`
   - В разделе Environment добавьте:
     ```
     MINIO_ROOT_USER=minioadmin
     MINIO_ROOT_PASSWORD=minioadmin
     ```
5. Нажмите "Install service"

### Вариант 2: Запуск вручную (для разработки)

1. Откройте командную строку
2. Выполните следующие команды:
   ```
   set MINIO_ROOT_USER=minioadmin
   set MINIO_ROOT_PASSWORD=minioadmin
   C:\minio\minio.exe server C:\minio\data --console-address :9001
   ```

## Шаг 4: Проверка работоспособности

1. Откройте веб-браузер и перейдите по адресу: http://localhost:9001
2. Войдите, используя следующие учетные данные:
   - Username: minioadmin
   - Password: minioadmin
3. Вы должны увидеть веб-интерфейс MinIO Console

## Шаг 5: Создание структуры хранилища для Art Gallery Management System

После входа в MinIO Console:

1. Создайте bucket `art-gallery-data`:
   - Нажмите кнопку "Create Bucket"
   - Введите имя "art-gallery-data"
   - Нажмите "Create Bucket"

2. Создайте bucket `art-gallery-media`:
   - Нажмите кнопку "Create Bucket"
   - Введите имя "art-gallery-media"
   - Нажмите "Create Bucket"

## Шаг 6: Настройка доступа

Для безопасности рекомендуется создать отдельного пользователя для приложения:

1. В MinIO Console перейдите в раздел "Identity" -> "Users"
2. Нажмите "Create User"
3. Заполните форму:
   - Name: artgallery
   - Password: (придумайте надежный пароль)
4. Нажмите "Create"
5. Выберите созданного пользователя и назначьте ему политику доступа через "Assign Policies"

## Настройка для разработки

Для локальной разработки можно использовать следующие настройки в конфигурационном файле приложения:

```python
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"  # или созданный вами пользователь
MINIO_SECRET_KEY = "minioadmin"  # или пароль созданного пользователя
MINIO_DATA_BUCKET = "art-gallery-data"
MINIO_MEDIA_BUCKET = "art-gallery-media"
MINIO_SECURE = False  # для локальной разработки без SSL
```

## Устранение неполадок

### Проблема: Не удается подключиться к MinIO

1. Проверьте, запущен ли сервис MinIO:
   ```
   sc query MinIO
   ```
2. Проверьте, что порты 9000 и 9001 не заняты другими приложениями:
   ```
   netstat -ano | findstr :9000
   netstat -ano | findstr :9001
   ```
3. Проверьте наличие файрвола или антивируса, блокирующего доступ

### Проблема: Ошибка аутентификации

1. Убедитесь, что вы используете правильные учетные данные
2. Проверьте переменные окружения:
   ```
   echo %MINIO_ROOT_USER%
   echo %MINIO_ROOT_PASSWORD%
   ```

## Дополнительные ресурсы

- [Официальная документация MinIO](https://docs.min.io/)
- [MinIO Client (mc) для управления через командную строку](https://docs.min.io/docs/minio-client-quickstart-guide.html)
- [Python SDK для MinIO](https://docs.min.io/docs/python-client-quickstart-guide.html)
