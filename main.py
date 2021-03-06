import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
import requests
import _datetime
from forex_python.converter import CurrencyRates
from datetimerange import DateTimeRange
import pyqtgraph


def convert_from_unix_to_datetime(unix_time):
    datetime = _datetime.datetime.fromtimestamp(unix_time)
    return datetime


def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"


class WeatherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('weather_window.ui', self)

        # Вставляяем в виджеты на окне информацию по умолчанию, чтобы окно не было пустым
        self.city_edit.setText('Москва')
        self.country_edit.setText('Россия')
        self.paste_data()
        self.update_button.clicked.connect(self.paste_data)

    def paste_data(self):
        request = f'https://api.openweathermap.org/data/2.5/forecast?q={self.city_edit.text()},' \
                  f'{self.country_edit.text()}&appi' \
                  'd=942a25426a3b21ff180cfa7b0b01a248&units=metric'
        response = requests.get(request).json()
        if int(response['cod']) in range(400, 500):
            QMessageBox.critical(self, "Ошибка ",
                                 "Что-то пошло не так. Проверьте верность данных.",
                                 QMessageBox.Ok)
            return None

        sunrise_time, sunset_time = convert_from_unix_to_datetime(response['city']['sunrise']), \
                                    convert_from_unix_to_datetime(response['city']['sunset'])
        self.sunrise_time_label.setText(str(sunrise_time).split()[1])
        self.sunset_time_label.setText(str(sunset_time).split()[1])

        self.latitude_label.setText(str(response['city']['coord']['lat']) + '°')
        self.longitude_label.setText(str(response['city']['coord']['lon']) + '°')

        self.temperature_label.setText(str(response['list'][0]['main']['temp']) + '°C')
        self.feels_like_label.setText(str(response['list'][0]['main']['feels_like']) + '°C')
        self.visibility_label.setText(str(response['list'][0]['visibility']) + ' м')
        self.pop_label.setText(str(response['list'][0]['pop'] * 100) + ' %')

        self.grn_pres_label.setText(str(response['list'][0]['main']['grnd_level']) + ' гПа')
        self.sea_pres_label.setText(str(response['list'][0]['main']['sea_level']) + ' гПа')
        self.hmd_label.setText(str(response['list'][0]['main']['humidity']) + ' %')

        self.sow_label.setText(str(response['list'][0]['wind']['speed']) + ' м/с')
        self.direction_label.setText(str(response['list'][0]['wind']['deg']) + '°')
        self.gust_label.setText(str(response['list'][0]['wind']['gust']) + ' м/с')

        self.static_label_16.setText(f'Данные актуальны на {str(_datetime.datetime.now()).split(".")[0]}. '
                                     f'Источник: OpenWeatherMap ')

        weather_list = response['list'][4:36:4]
        weather_flist = []

        for weather in weather_list:
            weather_flist.append([weather['dt_txt'].split()[0].split('-')[-1] + '.'
                                  + weather['dt_txt'].split()[0].split('-')[-2],
                                  weather['weather'][0]['icon'],
                                  str(weather['main']['temp']) + '°C'])
        for lbl_date, lbl_icon, lbl_temp, weather in zip([self.date_label_1, self.date_label_2, self.date_label_3,
                                                          self.date_label_4, self.date_label_5, self.date_label_6,
                                                          self.date_label_7, self.date_label_8], [self.icon_label_1,
                                                                                                  self.icon_label_2,
                                                                                                  self.icon_label_3,
                                                                                                  self.icon_label_4,
                                                                                                  self.icon_label_5,
                                                                                                  self.icon_label_6,
                                                                                                  self.icon_label_7,
                                                                                                  self.icon_label_8],
                                                         [self.temp_label_1,
                                                          self.temp_label_2, self.temp_label_3, self.temp_label_4,
                                                          self.temp_label_5, self.temp_label_6, self.temp_label_7,
                                                          self.temp_label_8], weather_flist):
            lbl_date.setText(weather[0])
            lbl_icon.setPixmap(QPixmap(f'images/{weather[1]}.png'))
            lbl_temp.setText(weather[2])

    def closeEvent(self, event):
        self.close()
        main_window.show()


class MoneyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.second_cur_ok = None
        self.second_cur = None
        self.first_cur_ok = None
        self.first_cur = None
        uic.loadUi('money_window.ui', self)
        self.choose_cur_first_button.clicked.connect(self.choose_first_cur)
        self.choose_cur_second_button.clicked.connect(self.choose_second_cur)
        self.graphicsView.setXRange(0, 7, padding=0)
        color = self.palette().color(QtGui.QPalette.Window)  # Get the default window background,
        self.graphicsView.setBackground((255, 255, 255))

    def choose_first_cur(self):
        cur_rates = CurrencyRates()
        curs = cur_rates.get_rates('USD').keys()
        self.first_cur, self.first_cur_ok = QInputDialog.getItem(
            self, "UtApp - валюта", "Выберите валюту:",
            tuple(curs), 1, False)
        if self.first_cur_ok:
            self.label.setText(self.first_cur)
        if self.first_cur_ok and self.second_cur_ok:
            self.label_2.setText(self.second_cur)
            cur_rates = CurrencyRates()
            self.second_cur_edit.setText(str(toFixed(cur_rates.convert(self.first_cur,
                                                                       self.second_cur,
                                                                       float(self.first_cur_edit.text())), 2)))
            time_range = DateTimeRange(_datetime.date.today() - _datetime.timedelta(days=7), _datetime.date.today())
            cur_list = []
            for date in time_range.range(_datetime.timedelta(days=1)):
                cur_list.append(cur_rates.convert(self.first_cur, self.second_cur, amount=1, date_obj=date))
            day_list = [abs(0 - day) for day in range(0, 8)]
            pen = pyqtgraph.mkPen(color=(0, 0, 0))
            self.graphicsView.setTitle(f"Курс {self.first_cur} к {self.second_cur} за последние 7 дней.",
                                       color=(0, 0, 0), size='9pt')
            styles = {'color': (0, 0, 0), 'font-size': '9pt'}
            self.graphicsView.setLabel('left', f'Курс {self.first_cur} к {self.second_cur} в у.е.', **styles)
            self.graphicsView.setLabel('bottom', 'Время', **styles)
            self.graphicsView.plot(day_list, cur_list, pen=pen)

    def choose_second_cur(self):
        cur_rates = CurrencyRates()
        curs = cur_rates.get_rates('USD').keys()
        self.second_cur, self.second_cur_ok = QInputDialog.getItem(
            self, "UtApp - валюта", "Выберите валюту:",
            tuple(curs), 1, False)
        if self.first_cur_ok and self.second_cur_ok:
            self.label_2.setText(self.second_cur)
            cur_rates = CurrencyRates()
            self.second_cur_edit.setText(str(toFixed(cur_rates.convert(self.first_cur,
                                                                       self.second_cur,
                                                                       float(self.first_cur_edit.text())), 2)))
            time_range = DateTimeRange(_datetime.date.today() - _datetime.timedelta(days=7), _datetime.date.today())
            cur_list = []
            for date in time_range.range(_datetime.timedelta(days=1)):
                cur_list.append(cur_rates.convert(self.first_cur, self.second_cur, amount=1, date_obj=date))
            day_list = [abs(0 - day) for day in range(0, 8)]
            pen = pyqtgraph.mkPen(color=(0, 0, 0))
            self.graphicsView.setTitle(f"Курс {self.first_cur} к {self.second_cur} за последние 7 дней.",
                                       color=(0, 0, 0), size='9pt')
            styles = {'color': (0, 0, 0), 'font-size': '9pt'}
            self.graphicsView.setLabel('left', f'Курс {self.first_cur} к {self.second_cur} в у.е.', **styles)
            self.graphicsView.setLabel('bottom', 'Время', **styles)
            self.graphicsView.plot(day_list, cur_list, pen=pen)

    def closeEvent(self, event):
        self.close()
        main_window.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.wnd = None
        uic.loadUi('main_window.ui', self)
        self.weather.clicked.connect(self.show_weather)
        self.money.clicked.connect(self.show_money)

    def show_weather(self):
        self.wnd = WeatherWindow()
        self.wnd.show()
        self.hide()

    def show_money(self):
        self.wnd = MoneyWindow()
        self.wnd.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
