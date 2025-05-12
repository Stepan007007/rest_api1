import requests
from pprint import pprint

BASE_URL = 'http://127.0.0.1:8080/api/jobs'  # Базовый URL без слеша на конце


def test_api():
    # Тест 1: Получение всех работ
    print('\n=== GET ALL JOBS ===')
    response = requests.get(BASE_URL)
    print(f'Status: {response.status_code}')
    pprint(response.json())

    # Тест 2: Неправильный параметр
    print('\n=== WRONG PARAM ===')
    response = requests.get(f'{BASE_URL}/gg')
    print(f'Status: {response.status_code}')
    pprint(response.json())

    # Тест 3: Получение одной работы
    print('\n=== GET ONE JOB ===')
    response = requests.get(f'{BASE_URL}/1')
    print(f'Status: {response.status_code}')
    pprint(response.json())

    # Тест 4: Несуществующий ID
    print('\n=== WRONG ID ===')
    response = requests.get(f'{BASE_URL}/1290')
    print(f'Status: {response.status_code}')
    pprint(response.json())

    # Тест 5: Создание работы
    print('\n=== CREATE JOB ===')
    job_data = {
        "job": "Обновить документацию",
        "work_size": 8,  # Число, а не строка
        "team_leader": 42,
        "collaborators": "3",  # Строка, а не массив
        "start_date": "2025-04-12",
        "end_date": "2025-04-13",
        "is_finished": True
    }
    response = requests.post(BASE_URL, json=job_data)
    print(f'Status: {response.status_code}')
    pprint(response.json())

    # Тест 6: Создание с неправильным is_finished
    print('\n=== CREATE WITH WRONG is_finished ===')
    job_data = {
        "job": "Обновить документацию",
        "work_size": '8',  # Теперь передаём строку
        "team_leader": 42,
        "collaborators": "3",
        "start_date": "2025-04-12",
        "end_date": "2025-04-13",
        "is_finished": 'NotBull'
    }
    response = requests.post(BASE_URL, json=job_data)
    print(f'Status: {response.status_code}')
    pprint(response.json())

    print('\n EDIT CORRECT')
    # Тест 8 редакитирование  работы корректное
    job_data = {
        "job": " Удалите документацию",
        "work_size": 290,  # Теперь передаём строку
        "team_leader": 42,
        "collaborators": 3,
        "start_date": "2025-04-12",
        "end_date": "2025-04-13",
        "is_finished": True
    }
    response = requests.put(BASE_URL + '/8', json=job_data)
    print(response.text)
    print(f'Status: {response.status_code}')
    pprint(response.json())

    print('\n  NO EDIT CORRECT error data')
    # Тест 9 редакитирование  работы не корректное ошибка в запросе
    job_data = {
        "job": " Удалите документацию",
        "work_size": 290,  # Теперь передаём строку
        "team_leader": 42,
        "collaborators": ['2'],
        "start_date": "2025-04-12",
        "end_date": "2025-04-13",
        "is_finished": 'True'  # Передае строку
    }
    response = requests.put(BASE_URL + '/8', json=job_data)
    print(f'Status: {response.status_code}')
    pprint(response.json())

    print('\n  NO EDIT CORRECT error id')
    # Тест 10 редакитирование  работы  не корректное не верный id
    job_data = {
        "job": " Удалите документацию",
        "work_size": 290,  # Теперь передаём строку
        "team_leader": 42,
        "collaborators": ['2'],
        "start_date": "2025-04-12",
        "end_date": "2025-04-13",
        "is_finished": True
    }
    response = requests.put(BASE_URL + '/322323', json=job_data)
    print(f'Status: {response.status_code}')
    pprint(response.json())

    # тест 11 удаление верноеное
    print('\n DELETE ')
    response = requests.delete(BASE_URL + '/8', json=job_data)
    print(f'Status: {response.status_code}')
    pprint(response.json())

    # тест 11 удаление  не верноеное ошибка в id

    print('\n ERROR DELETE ')
    response = requests.delete(BASE_URL + '/88989898989', json=job_data)
    print(f'Status: {response.status_code}')
    pprint(response.json())


if __name__ == '__main__':
    test_api()