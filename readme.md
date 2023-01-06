# Бот, регистрирующий на конференцию
## Описание проекта
### Введение
Здравствуйте, коллега! В нашей школе ежегодно проводится конференция городского уровня. Название конференции
указать не могу в связи с требованием анонимности. Для регистрации на эту конференцию
мы использовали сначала Google-, а затем Яндекс-Формы. В этом проекте я попробовал
создать альтернативу - регистрацию с помощью Telegram-бота.
### Что умеет бот?
У бота есть следующие команды:
* /start - вывод приветствия от бота. Также по этой команде пользователю становится доступна клавиатура в нижней части экрана, содержащая все доступные боту команды
* /help - получение информации о том, какие данные потребуются пользователю для регистрации, а также описание команд, поддерживаемых ботом
* /site - по задумке выдаёт ссылку на страницу конференции на сайте школы, но согласно требованию анонимности выводит просто текст
* /email - по задумке выдаёт e-mail оргкомитета конференции, но согласно требованию анонимности выводит просто текст
* /address - выдает адрес места проведения конференции, а также выводит карту местности, полученную от Яндекс.Карт и преобразованную в картинку. Для демонстрации возможностей выдаёт информацию об одной из трёх случайно выбранных мною школ
* /show - просмотр списка зарегистрированных на секцию, выбранную пользователем. Этот список также доступен пользователю для скачивания в формате .txt
* /reg - запуск сценария диалога. Так называемый FSM или Конечный автомат. Бот задаёт пользователю вопросы в определённой последовательности и обрабатывает ответы. В зависимости от ответа, диалог переходит к тому или иному состоянию, а иногда и повторяет состояние при вводе некорректной информации. Иногда пользователю для ответа нужно нажать на одну из кнопок, встроенных в сообщение
### Как запустить проект?
1. Найти в Телеграме бота BotFather

![BotFather](/info/1.png)
2. Дать BotFather команду /newbot

![Запрос на создание бота](/info/2.png)
3. Ответить на пару вопросов от BotFather: как будет подписан бот в чате и имя бота (username), которое должно заканчиваться символами "bot"
4. После ответов на вопросы Вам будет выдан **токен**

![Получаем токен](/info/3.png)
5. Записываем имя бота (username) и токен в файл Bot.txt
![Login_Password](/info/4.png)
6. Сохраняем текстовый файл
7. Если не установлены необходимые библиотеки,
устанавливаем совместимые версии aiogram и requests (см. файл requirements.txt)
8. Запускаем программу (файл conf_reg_bot.py)
9. Находим в Телеграм нашего бота (например, набрав в строке поиска @username),
где username - придуманное Вами имя бота
10. Ура! Можно начинать общение.
### Содержание проекта
* файл Bot.txt, в котором записаны имя и токен
* файл conf_reg_bot.py, содержащий основную часть кода (~400 строк)
* файл db.py, отвечающий за взаимодействие с БД (~55 строк)
* файл conference.sqlite, содержащий информацию об успешно зарегистрированных участниках
(для тестирования зарегистрированы 3 участника на секцию истории)
* файл readme.md, который Вы сейчас читаете
* файл requirements.txt
* папка info, содержащая снимки экрана для файла readme.md
### Дополнительная информация
Подгруженные пользователем файлы на этапе загрузки аннотации сохраняются в папке проекта
под именем "Аннотация <Фамилия автора>.<расширение файла, загруженного пользователем>".

При запросе пользователем списка зарегистрировавшихся на выбранную секцию конференции,
формируется файл "<Название секции>.txt", содержащий список зарегистрированных.
Пользователю отправляется сообщение с этим списком и сам файл на случай, если пользователь
захочет его скачать.

К сожалению, Heroku прекратил поддержку бесплатных аккаунтов и вообще не принимает
новые заявки из России.
![Heroku](/info/5.png)
### Успехов, коллега!