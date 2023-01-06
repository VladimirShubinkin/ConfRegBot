import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import (InputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
                           InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message)
import urllib.request
from db import db_insert, db_select, data_to_text
import requests
from random import choice

# Секции конференции. Номер соответствует id секции в БД
SECTIONS = {'math': 1,
            'phys': 2,
            'inf': 3,
            'chem': 4,
            'rus': 5,
            'lit': 6,
            'art': 7,
            'eng': 8,
            'hist': 9,
            'soc': 10,
            'geo': 11,
            'bio': 12,
            'health': 13}
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
# получаем имя бота и токен из файла Bot.txt
with open('Bot.txt') as f:
    bot_name, TOKEN = map(lambda s: s.split('=')[1].strip(), f.readlines()[:2])
logger = logging.getLogger(bot_name)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def rkbm():  # "постоянная" клавиатура с командами (скрывается после команды /reg)
    reply_keyboard_markup = ReplyKeyboardMarkup()
    b_start = KeyboardButton('/start')
    b_help = KeyboardButton('/help')
    b_address = KeyboardButton('/address')
    b_site = KeyboardButton('/site')
    b_email = KeyboardButton('/email')
    b_reg = KeyboardButton('/reg')
    b_show = KeyboardButton('/show')
    reply_keyboard_markup.add(b_start, b_help)
    reply_keyboard_markup.add(b_reg, b_show)
    reply_keyboard_markup.add(b_address, b_email, b_site)
    return reply_keyboard_markup


async def start(message: Message, state: FSMContext):  # приветствие от бота, вызывается командой /start
    await state.finish()
    text = 'Привет! Я помогу Вам зарегистрироваться на конференцию '
    text += '"Название конференции скрыто в связи с требованием анонимности".\n'
    text += 'Узнать доступные команды и данные, необходимые для регистрации, можно по команде /help\n'
    text += 'Для удобства набора команд используйте клавиатуру внизу\n'
    text += 'Эта клавиатура скроется, когда Вы начнёте регистрацию (команда /reg), и появится снова по команде /start'
    await message.reply(text, reply_markup=keyboard_markup)  # активируем "постоянную" клавиатуру


@dp.message_handler(commands='help')
async def help(message: Message):  # обработчик команды /help
    await message.answer('''Для успешной регистрации Вам понадобятся следующие данные:
ФИО участника
название оразовательной организации
ФИО руководителя
должность руководителя
место работы руководителя
название работы
текстовый файл (.pdf/.docx/.odt/.txt) с аннотацией работы.
Доступные команды:
/start - приветствие от бота
/help - Вы уже здесь
/address - адрес проведения конференции
/site - сайт о конференции
/email - электронный адрес конференции
/reg - начать регистрацию
/show - показать список зарегистрировавшихся на секцию''')


@dp.message_handler(commands='address')
async def get_address(message: Message):  # обработчик команды /address
    '''По команде /address пользователь может получить адрес места проведения конференции, а также карту.
    В связи с требованием анонимности будут показаны данные одной из трёх случайно выбранных мною школ'''
    schools = ['Калининград, ул. Новый вал, 23',
               'Краснодар, Красноармейская ул., 2',
               'Владивосток, улица Адмирала Кузнецова, 40а']
    school = choice(schools)
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": school,
        "format": "json"}
    response = requests.get(geocoder_api_server, params=geocoder_params)
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    delta = "0.005"
    ll = ",".join([toponym_longitude, toponym_lattitude])
    spn = ",".join([delta, delta])
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map"
    await message.answer_photo(static_api_request, f'{school}\nРеальный адрес скрыт в связи с требованием анонимности')


@dp.message_handler(commands='site')
async def get_site(message: Message):
    '''по команде /site пользователь получал бы ссылку на страницу конференции на сайте школы'''
    await message.answer('Доступ к сайту конференции закрыт в связи с требованием анонимности')


@dp.message_handler(commands='email')
async def get_email(message: Message):
    '''по команде /email пользователь получал бы e-mail оргкомитета конференции'''
    await message.answer('Адрес скрыт в связи с требованием анонимности')


@dp.message_handler(commands='show')
async def choise_section_to_show(message: Message):
    '''по команде /show с помощью "временной" клавиатуры, встроенной в сообщение,
    пользователю предлагается выбрать секцию, со списком участников которой он хотел бы ознакомиться.'''
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Математика", callback_data="section:math"))
    keyboard.add(InlineKeyboardButton(text="Физика", callback_data="section:phys"))
    keyboard.add(InlineKeyboardButton(text="Информатика", callback_data="section:inf"))
    keyboard.add(InlineKeyboardButton(text="Химия", callback_data="section:chem"))
    keyboard.add(InlineKeyboardButton(text="Русский язык", callback_data="section:rus"))
    keyboard.add(InlineKeyboardButton(text="Литература", callback_data="section:lit"))
    keyboard.add(InlineKeyboardButton(text="Искусство", callback_data="section:art"))
    keyboard.add(InlineKeyboardButton(text="Иностранные языки", callback_data="section:eng"))
    keyboard.add(InlineKeyboardButton(text="История", callback_data="section:hist"))
    keyboard.add(InlineKeyboardButton(text="Обществознание", callback_data="section:soc"))
    keyboard.add(InlineKeyboardButton(text="География", callback_data="section:geo"))
    keyboard.add(InlineKeyboardButton(text="Биология", callback_data="section:bio"))
    keyboard.add(InlineKeyboardButton(text="ОБЖ, физкультура", callback_data="section:health"))
    await message.answer('Выберите секцию', reply_markup=keyboard)


@dp.callback_query_handler(lambda callback: callback.data.startswith('section:'))
async def show_section_info(callback: CallbackQuery):
    '''Когда пользователь определился, со списком участников какой секции он хочет ознакомиться, делаем запрос БД.
    Информация предлагается пользователю в двух видах: сообщение со списком и файл .txt, содержащий тот же список'''
    section_id = SECTIONS[callback.data.split(':')[1]]
    section, data = db_select(section_id)
    if data:
        text = f'Список зарегистрировавшихся на секцию "{section}":\n'
        text += data_to_text(data)
        with open(f'{section}.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        text += '\nДля Вашего удобства список доступен для скачивания в формате .txt'
        await callback.message.answer(text)
        file = InputFile(f'{section}.txt')
        await callback.message.reply_document(file)
    else:
        text = f'На секцию {section} пока нет заявок'
        await callback.message.answer(text)
    await callback.answer()


class OrderQuestions(StatesGroup):  # вводим состояния диалога (FSM)
    waiting_for_ans_2 = State()
    waiting_for_ans_3 = State()
    waiting_for_ans_4 = State()
    ans_4 = State()
    waiting_for_ans_5 = State()
    waiting_for_ans_6 = State()
    waiting_for_ans_7 = State()
    waiting_for_ans_8 = State()
    ans_8 = State()
    waiting_for_ans_9 = State()
    waiting_for_ans_10 = State()
    waiting_for_ans_11 = State()
    waiting_for_ans_12 = State()
    waiting_for_ans_13 = State()
    ans_13 = State()
    waiting_for_ans_14 = State()
    waiting_for_ans_15 = State()
    waiting_for_ans_16 = State()
    ans_16 = State()


async def resp_1(message: Message, state: FSMContext):  # запрос фамилии автора
    await state.finish()  # завершаем предыдущий сценарий диалога, если пользователь ввёл команду /reg
    text = "Введите фамилию автора работы (возможности ввести данные второго автора Вам предоставится позже)"
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderQuestions.waiting_for_ans_2.state)


async def resp_2(message: Message, state: FSMContext):  # запрос имени автора
    await state.update_data(surname=message.text)
    await message.answer("Введите имя автора работы")
    await state.set_state(OrderQuestions.waiting_for_ans_3.state)


async def resp_3(message: Message, state: FSMContext):  # запрос отчества автора
    await state.update_data(name=message.text)
    await message.answer('Введите отчество автора работы (при отсутствии введите "нет")')
    await state.set_state(OrderQuestions.waiting_for_ans_4.state)


async def resp_4(message: Message, state: FSMContext):
    '''Задаём пользователю вопрос о наличии второго автора с помощью "временной" клавиатуры, встроенной в сообщение'''
    patr = message.text
    if len(patr) < 5:
        patr = 'NULL'
    await state.update_data(patronym=patr)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Да", callback_data="second_author_yes"),
                 InlineKeyboardButton(text="Нет", callback_data="second_author_no"))
    await message.answer("Есть ли второй автор?", reply_markup=keyboard)
    await state.set_state(OrderQuestions.ans_4.state)


async def ans_4(callback: CallbackQuery, state: FSMContext):
    if callback.data.endswith('yes'):  # если второй автор присутствует, переводим диалог в состояние 5...
        await callback.message.answer('Введите фамилию второго автора работы')
        await state.set_state(OrderQuestions.waiting_for_ans_5.state)
    else:  # ...иначе присваиваем ФИО второго автора значения "NULL"
        await state.update_data(surname2='NULL')
        await state.update_data(name2='NULL')
        await state.update_data(patronym2='NULL')
        await callback.message.answer('Введите название работы')
        await state.set_state(OrderQuestions.waiting_for_ans_8.state)
    await callback.answer()


async def resp_5(message: Message, state: FSMContext):
    await state.update_data(surname2=message.text)
    await message.answer("Введите имя второго автора работы")
    await state.set_state(OrderQuestions.waiting_for_ans_6.state)


async def resp_6(message: Message, state: FSMContext):
    await state.update_data(name2=message.text)
    await message.answer('Введите отчество второго автора работы (при отсутствии введите "нет")')
    await state.set_state(OrderQuestions.waiting_for_ans_7.state)


async def resp_7(message: Message, state: FSMContext):  # запрос названия работы
    patr = message.text
    if len(patr) < 5:
        patr = 'NULL'
    await state.update_data(patronym2=patr)
    await message.answer('Введите название работы')
    await state.set_state(OrderQuestions.waiting_for_ans_8.state)


async def resp_8(message: Message, state: FSMContext):  # выбор секции с помощью inline-клавиатуры
    await state.update_data(work_name=message.text)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Математика", callback_data="math"))
    keyboard.add(InlineKeyboardButton(text="Физика", callback_data="phys"))
    keyboard.add(InlineKeyboardButton(text="Информатика", callback_data="inf"))
    keyboard.add(InlineKeyboardButton(text="Химия", callback_data="chem"))
    keyboard.add(InlineKeyboardButton(text="Русский язык", callback_data="rus"))
    keyboard.add(InlineKeyboardButton(text="Литература", callback_data="lit"))
    keyboard.add(InlineKeyboardButton(text="Искусство", callback_data="art"))
    keyboard.add(InlineKeyboardButton(text="Иностранные языки", callback_data="eng"))
    keyboard.add(InlineKeyboardButton(text="История", callback_data="hist"))
    keyboard.add(InlineKeyboardButton(text="Обществознание", callback_data="soc"))
    keyboard.add(InlineKeyboardButton(text="География", callback_data="geo"))
    keyboard.add(InlineKeyboardButton(text="Биология", callback_data="bio"))
    keyboard.add(InlineKeyboardButton(text="ОБЖ, физкультура", callback_data="health"))
    await message.answer('Выберите секцию', reply_markup=keyboard)
    await state.set_state(OrderQuestions.ans_8.state)


async def ans_8(callback: CallbackQuery, state: FSMContext):  # запрос фамилии научного руководителя
    await state.update_data(section_id=SECTIONS[callback.data])
    await callback.message.answer('Введите фамилию научного руководителя')
    await state.set_state(OrderQuestions.waiting_for_ans_9.state)
    await callback.answer()


async def resp_9(message: Message, state: FSMContext):  # запрос имени научного руководителя
    await state.update_data(teacher_surname=message.text)
    await message.answer('Введите имя научного руководителя')
    await state.set_state(OrderQuestions.waiting_for_ans_10.state)


async def resp_10(message: Message, state: FSMContext):  # запрос отчества научного руководителя
    await state.update_data(teacher_name=message.text)
    await message.answer('Введите отчество научного руководителя (при отсутствии введите "нет")')
    await state.set_state(OrderQuestions.waiting_for_ans_11.state)


async def resp_11(message: Message, state: FSMContext):  # запрос должности научного руководителя
    await state.update_data(teacher_patronym=message.text)
    text = 'Введите должность научного руководителя. Примеры: учитель физики, доцент кафедры нанотехнологий'
    await message.answer(text)
    await state.set_state(OrderQuestions.waiting_for_ans_12.state)


async def resp_12(message: Message, state: FSMContext):  # запрос места работы научного руководителя
    await state.update_data(teacher_position=message.text)
    text = 'Введите место работы научного руководителя. Примеры: Гимназия №56, ДВФУ'
    await message.answer(text)
    await state.set_state(OrderQuestions.waiting_for_ans_13.state)


async def resp_13(message: Message, state: FSMContext):  # запрос параллели, в которой обучается автор
    await state.update_data(teacher_workplace=message.text)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="6", callback_data="6"),
                 InlineKeyboardButton(text="7", callback_data="7"),
                 InlineKeyboardButton(text="8", callback_data="8"))
    keyboard.add(InlineKeyboardButton(text="9", callback_data="9"),
                 InlineKeyboardButton(text="10", callback_data="10"),
                 InlineKeyboardButton(text="11", callback_data="11"))
    text = 'Выберите класс обучения автора (авторов) работы'
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(OrderQuestions.ans_13.state)


async def ans_13(callback: CallbackQuery, state: FSMContext):  # запрос школы автора
    await state.update_data(student_class=callback.data)
    text = 'Введите образовательное учреждение автора работы. Пример: Гимназия №56'
    await callback.message.answer(text)
    await state.set_state(OrderQuestions.waiting_for_ans_14.state)
    await callback.answer()


async def resp_14(message: Message, state: FSMContext):  # запрос электронной почты автора
    await state.update_data(oo=message.text)
    await message.answer('Введите адрес электронной почты для связи')
    await state.set_state(OrderQuestions.waiting_for_ans_15.state)


async def resp_15(message: Message, state: FSMContext):  # просим загрузить файл с аннотацией работы
    # минимальная проверка на корректность адреса электронной почты
    # если адрес некорректен, снова переводим диалог в состояние 15
    email = message.text
    if email.count('@') != 1:
        await message.answer('Вы ввели некорректный адрес электронной почты. Пожалуйста, введите правильно')
        await state.set_state(OrderQuestions.waiting_for_ans_15.state)
    else:
        dom = email.split('@')[1]
        if '.' not in dom:
            await state.set_state(OrderQuestions.waiting_for_ans_15.state)
        else:
            await state.update_data(email=email)
            await message.answer('Загрузите аннотацию работы в одном из следующих форматов: docx, odt, pdf, txt')
            await state.set_state(OrderQuestions.waiting_for_ans_16.state)


async def resp_16(message: Message, state: FSMContext):
    '''сохраняем файл, полученный от пользователя, и просим согласие на обработку персональных данных'''
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    if file_path.endswith(('.docx', '.odt', '.pdf', '.txt')):
        file_name = 'Аннотация ' + (await state.get_data())['surname'] + '.' + file_path.split('.')[-1]
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{file_path}', f'./{file_name}')
        await state.update_data(annotation_file_name=file_name)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="Да", callback_data="pers_yes"))
        text1 = 'Согласны ли Вы на обработку персональных данных? '
        text2 = 'Если не согласны, мы не сможем пригласить Вас для участия в конференции.'
        await message.answer(text1 + text2, reply_markup=keyboard)
        await state.set_state(OrderQuestions.ans_16.state)
    else:
        text = 'Неверный формат файла. Загрузите аннотацию работы в одном из следующих форматов: docx, odt, pdf, txt'
        await message.answer(text)
        await state.set_state(OrderQuestions.waiting_for_ans_16.state)


async def ans_16(callback: CallbackQuery, state: FSMContext):  # благодарим пользователя за регистрацию
    pers = callback.data
    if pers == "pers_yes":
        await state.update_data(pers='True')
    db_insert(await state.get_data())  # запись в БД
    text = 'Регистрация завершена успешно. Благодарим за интерес к нашей конференции!'
    await callback.message.answer(text)
    await callback.answer()
    await state.finish()


def handlers():  # регистрируем handler`ы, относящиеся к сценарию диалога (FSM)
    dp.register_message_handler(start, commands='start', state='*')
    dp.register_message_handler(resp_1, commands='reg', state='*')
    dp.register_message_handler(resp_2, state=OrderQuestions.waiting_for_ans_2)
    dp.register_message_handler(resp_3, state=OrderQuestions.waiting_for_ans_3)
    dp.register_message_handler(resp_4, state=OrderQuestions.waiting_for_ans_4)
    dp.register_callback_query_handler(ans_4, state=OrderQuestions.ans_4)
    dp.register_message_handler(resp_5, state=OrderQuestions.waiting_for_ans_5)
    dp.register_message_handler(resp_6, state=OrderQuestions.waiting_for_ans_6)
    dp.register_message_handler(resp_7, state=OrderQuestions.waiting_for_ans_7)
    dp.register_message_handler(resp_8, state=OrderQuestions.waiting_for_ans_8)
    dp.register_callback_query_handler(ans_8, state=OrderQuestions.ans_8)
    dp.register_message_handler(resp_9, state=OrderQuestions.waiting_for_ans_9)
    dp.register_message_handler(resp_10, state=OrderQuestions.waiting_for_ans_10)
    dp.register_message_handler(resp_11, state=OrderQuestions.waiting_for_ans_11)
    dp.register_message_handler(resp_12, state=OrderQuestions.waiting_for_ans_12)
    dp.register_message_handler(resp_13, state=OrderQuestions.waiting_for_ans_13)
    dp.register_callback_query_handler(ans_13, state=OrderQuestions.ans_13)
    dp.register_message_handler(resp_14, state=OrderQuestions.waiting_for_ans_14)
    dp.register_message_handler(resp_15, state=OrderQuestions.waiting_for_ans_15)
    dp.register_message_handler(resp_16, state=OrderQuestions.waiting_for_ans_16, content_types=['document'])
    dp.register_callback_query_handler(ans_16, state=OrderQuestions.ans_16)


if __name__ == '__main__':
    handlers()
    keyboard_markup = rkbm()
    executor.start_polling(dp, skip_updates=True)
