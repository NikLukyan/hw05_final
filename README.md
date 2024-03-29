# Yatube - платформа для блогов (с авторизацией, персональными лентами, с комментариями и подпиской на авторов).
Реализована классическая архитектура Django MVT, используется пагинация постов, кэширование, валидация данных при регистрации, смена и восстановление пароля через почту. Написаны тесты. Деплой в облаке.
1. С помощью sorl-thumbnail выведены иллюстрации к постам:
в шаблон главной страницы,
в шаблон профайла автора,
в шаблон страницы группы,
на отдельную страницу поста.
Написаны тесты, которые проверяют:
при выводе поста с картинкой изображение передаётся в словаре context
на главную страницу,
на страницу профайла,
на страницу группы,
на отдельную страницу поста;
при отправке поста с картинкой через форму PostForm создаётся запись в базе данных;
2. Создана система комментариев
Написана система комментирования записей. На странице поста под текстом записи выводится форма для отправки комментария, а ниже — список комментариев. Комментировать могут только авторизованные пользователи. 
Работоспособность модуля протестирована.
3. Кеширование главной страницы
Список постов на главной странице сайта хранится в кэше и обновляется раз в 20 секунд.
4. Тестирование кэша
Написан тест для проверки кеширования главной страницы. Логика теста: при удалении записи из базы, она остаётся в response.content главной страницы до тех пор, пока кэш не будет очищен принудительно.
5. Реализована система подписки на авторов и создана лента их постов.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/NikLukyan/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Перейти в папку yatube и выполнить миграции:

```
cd yatube
```

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
