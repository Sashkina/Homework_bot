# Бот-ассистент для проверки статуса домашней работы в Yandex Praktikum

### Описание:

**Telegram-bot позволяет отслеживать ход проверки домашней работы: взята ли работа на ревью,  
проверена ли она, и каков результат этой проверки**

### Бот должен:
<li> раз в 10 минут обращаться к API сервису Практикума и проверять статус отправленной на ревью работы;
<li> при обновлении статуса отправлять соответствующее уведомление в Telegram;
<li> логировать свою работу и сообщать о проблемах в Telegram.

### Технологии:
<li> Python 3.9

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Sashkina/homework_bot.git
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Запустить проект:

```
python homework.py
```

### Автор  
Сашкина Кристина
