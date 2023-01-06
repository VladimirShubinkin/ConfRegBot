import sqlite3


def db_insert(data: dict):  # заносим данные, введённые пользователем в БД
    try:
        conn = sqlite3.connect('conference.sqlite')
        cur = conn.cursor()
        t = ('surname', 'name', 'patronym', 'surname2', 'name2', 'patronym2', 'student_class', 'oo',
             'teacher_surname', 'teacher_name', 'teacher_patronym', 'teacher_position', 'teacher_workplace',
             'section_id', 'work_name', 'email', 'annotation_file_name')
        t1 = ['?']*len(t)
        to_insert = [data[i] for i in t]
        sql = f'''INSERT INTO students({', '.join(t)})
                  VALUES({', '.join(t1)})'''
        cur.execute(sql, to_insert)
        conn.commit()
    except Exception as e:
        print(e)


def db_select(section_id: int):  # запрос данных из БД для отображения списка зарегистрированных на секцию
    section = ''
    data = []
    try:
        conn = sqlite3.connect('conference.sqlite')
        cur = conn.cursor()
        section = cur.execute('''SELECT section FROM sections
                              WHERE section_id = ?''', (section_id,)).fetchone()
        t = ('surname', 'name', 'patronym', 'surname2', 'name2', 'patronym2', 'student_class',
             'teacher_surname', 'teacher_name', 'teacher_patronym', 'work_name')
        sql = f'''SELECT {', '.join(t)} FROM students WHERE section_id = {section_id}'''
        data = cur.execute(sql).fetchall()
    except Exception as e:
        print(e)
    return section[0], data


def data_to_text(data: list):  # перевод данных из БД в удобную для отображения форму
    text = ''
    for i, el in enumerate(data, 1):
        text += f'{i}. {el[0]} {el[1][0]}.'
        if el[2] != 'NULL':
            text += f' {el[2][0]}., '
        else:
            text += ', '
        if el[3] != 'NULL':
            text += f'{el[3]} {el[4][0]}.'
            if el[5] != 'NULL':
                text += f' {el[5][0]}., '
            else:
                text += ', '
        text += f'{el[6]} кл., н.р. {el[7]} {el[8][0]}.'
        if el[9] != 'NULL':
            text += f' {el[9][0]}.'
        text += ', '
        text += el[10] + '\n'
    return text
