# Загружаем все необходимые библиотеки
import urllib.request
import datetime
import requests
from urllib.parse import urlencode
import concurrent.futures
from bs4 import BeautifulSoup
import re
import subprocess
from tabulate import tabulate
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
username = os.getlogin()# берем логин пк, так как они совпадают с почтовым адресом 


# tablfm='pretty'
def webtest(tablfm='', enabled_features=['date', 'http', 'ping', 'skycontrol', 'email']):
    if enabled_features is None:
        enabled_features = []

    header = '\nСистема автоматизированного тестирования сервисов '
    author = "Вы вошли как " + username
    version = 'Версия 1.5.2023'

    if 'date' in enabled_features:

        def date():
            return str(datetime.datetime.now())

        print(header, version,author, date(), sep='\n')
    if 'http' in enabled_features:# Тут получаем HTTP-коды чтобы проверить доступность сайтов 
        print("\nПроверка веб-сервисов\n")
    sites = {
        'https://ya.ru/': 'Яндекс',
        'https://google.com/': 'Google',
        '******************************': '',
        '******************************': '******************************',
        '******************************': '******************************',
        '******************************': '******************************',
        '******************************': '******************************',
        '******************************': '******************************',
        '******************************': '******************************',
        '*****************************': '******************************'
    }

    def get_status(code):
        if code in range(200, 299):
            return 'Успешно'
        elif code in range(400, 499):
            return 'Ошибка клиента'
        elif code in range(500, 599):
            return 'Ошибка сервера'
        else:
            return 'Неизвестный статус'

    def get_code(site):
        try:
            response = urllib.request.urlopen(site)
            return site, response.code
        except Exception as e:
            return site, str(e).split('] ')[0][:48].replace("<", "")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:# Пускаем получение кода http в многопотоке, чтобы забустить скорость проверки без потери качества проверки
        results = list(executor.map(get_code, sites.keys()))

    table = []# собираем табличку
    for (site, name), code in zip(sites.items(), [result[1] for result in results]):
        if isinstance(code, int):
            status = get_status(code)
            status = ' ' * (8 - len(status)) + status
            table.append((name, site, code, status))
        else:
            table.append((name, site, 'н/д', str(code)[:50]))# ограничиваем вывод code до 50 символов, чтобы не ломать табличку в случае ошибки

    headers = ['Имя', 'Адрес', 'Код HTTP', 'Статус']
    print(tabulate(table, headers=headers, tablefmt=tablfm))

    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)# Отключаем предупреждения 
    print('Получаем состояние сайта...')
    r = requests.get("********************", verify=False).text# получаем данные о работе сайта
    cccbtest = re.sub('<[^<]+?>', '', r)# Тут подключились к веб-интерфейсу и получили с него строку состяния
    print(cccbtest.split('Web-service - ')[1])

    print('Проверка IP\n')# Ниже словарь -  ip:название
    list1 = {'8.8.8.8': 'Google IP', '77.88.55.60': 'Yandex IP'}
    columns = ['Название', 'IP', 'отправлено', 'получено',
               'потеряно', '% потерь', 'Мин.мсек', 'Макс.мсек', 'Сред.мсек']
    png_it_res = []

    def ping_ip(ip, name):# Тут проверяем все предыдущие сервисы на досупность через утилиту ping в windows, 
        try:
            ping_output = subprocess.check_output(
                ["ping", "-n", "10", ip]).decode('cp866')#Вызываем виндовый ping из под питона с 10 пингами и декодируем ответ, чтобы читалось норм
            ping_lines = ping_output.split('\n')
            sent, received, lost, loss_pct, min_time, max_time, avg_time = None, None, None, None, None, None, None
            for line in ping_lines:
                sent = ping_output.split(': отправлено')[# форматируем то, что вернул пинг
                    1].split(' = ')[1].split(',')[0]
                received = ping_output.split(' = ')[1].split(',')[0]
                lost = ping_output.split('потеряно = ')[1].split('\r\n ')[0]
                loss_pct = ping_output.split('%')[0].split('\n    (')[1]+'%'
                min_time = ping_output.split('Минимальное = ')[
                    1].split('мсек')[0]
                max_time = ping_output.split('Максимальное = ')[
                    1].split('мсек')[0]
                avg_time = ping_output.split('Среднее = ')[1].split('мсек')[0]
            png_it_res.append(
                (name[:50], ip[:50], sent, received, lost, loss_pct, min_time, max_time, avg_time))
        except subprocess.CalledProcessError:
            row = (name[:50], ip[:50], '-', '-', '-', '-', '-',
                   '-', '-')  # заполняем пустые "столбцы" этими значениями
            png_it_res.append(row)

    with concurrent.futures.ThreadPoolExecutor() as executor:# Многопоток
        results = [executor.submit(ping_ip, ip, name)
                   for ip, name in list1.items()]
    print('\n', tabulate(png_it_res, headers=columns,
          stralign='center', tablefmt=tablfm), '\n')

    # SkyControl Auth
    if 'skycontrol' in enabled_features:
        def skycontrol(password="****************"):# подключаемся к веб-интерфейсу системы контроля за температурой и парсим с нее нужные значения

            # URL страницы авторизации
            url = "*************************"

            try:
                # Параметры POST-запроса
                data = {"pwd": password}

                # Отправляем POST-запрос на страницу авторизации
                response = requests.post(url + "?show=loginok", data=data)

                # Проверяем, успешна ли авторизация
                if response.status_code == 200 and "You should authorize to view/modify this content" not in response.text:# читаем ответ и проверяем код 
                    print("Sky Control Monitoring System:\nАвторизация выполнена\n")
                else:
                    raise Exception(
                        "\nSky Control Monitoring System: Ошибка авторизации")

                # Используем BeautifulSoup для парсинга HTML-ответа
                soup = BeautifulSoup(response.text, 'html.parser')

                def get_value(str, par_header, val_q):# парсим веб-морду
                    par_value = soup.find('td', string=str).find_next_sibling(
                        'td').find_next_sibling('td').find_next_sibling('td').text
                    par_state = soup.find('td', string=str).find_next_sibling(
                        'td').find_next_sibling('td').text
                    par_name = soup.find(
                        'td', string=str).find_next_sibling('td').text
                    return (par_header, par_name.lower(), par_state, par_value + f" {val_q}")

                skyctrl = [get_value('Humidity-fd7c0603', 'Датчик влажности воздуха (fd7c0603):', '%'),#получаем нужные значения, наводим красоту 
                           get_value('Humidity-6af7401',
                                     'Датчик влажности воздуха (6af7401):', '%'),
                           get_value('Ð¨ÐºÐ°Ñ â2',
                                     'Датчик температуры: Шкаф 2', 'Cº'),
                           get_value('Ð¨ÐºÐ°Ñ â3',
                                     'Датчик температуры: Шкаф 3', 'Cº'),
                           get_value('ÐÐ¾ÑÐ¾Ð»Ð¾Ðº',
                                     'Датчик температуры: Потолок', 'Cº'),
                           get_value('Voltage-COD', 'Датчик напряжения', 'V')]

                headers = ['Наименование', 'Тип данных', 'Статус', 'Значение']
                # тут можно задать красоту tablefmt='pretty'
                table = tabulate(skyctrl, headers=headers, tablefmt=tablfm)
                print(table)

            except requests.exceptions.RequestException as e:
                print(
                    f"\nSky Control Monitoring System: Ошибка при выполнении запроса\n{str(e)[:48]}")

            except Exception as e:
                print(
                    f"\nSky Control Monitoring System: Получена ошибка\n{str(e)[:48]}")

        # Call the function
        skycontrol()
        print('-'*73)
        if 'email' in enabled_features:
            def email_sender(email='justmail@mail.ru', password='********************', recipient=username+'@domen.ru'):# отправляем письмо с внешнего ящика для проверки досупности почтового сервиса
                print(
                    f"Проверка работы почтового сервиса {email} -> {recipient}")
                # данные для письма
                subject = 'Система автоматизированного тестирования'
                body = (f"Отправьте ответное письмо на {email}.")

                # создаем сообщение
                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = recipient
                msg['Subject'] = subject

                # добавляем текст письма
                msg.attach(MIMEText(body, 'plain'))

                # подключаемся к серверу Mail.ru
                server = smtplib.SMTP_SSL('smtp.mail.ru', 465)

                # авторизуемся
                server.login(email, password)

                # отправляем сообщение
                server.sendmail(email, recipient, msg.as_string())

                # отключаемся от сервера
                server.quit()

                print('Письмо отправлено\n')
            email_sender()


webtest()
