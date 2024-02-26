import sys, sqlite3, datetime

from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from design import Ui_MainWindow


# Наследуемся от виджета из PyQt5.QtWidgets и от класса с интерфейсом
class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Вызываем метод для загрузки интерфейса из класса Ui_MainWindow,

        self.setupUi(self)
        # приветсвуем пользователя диалоговым окном
        hello_window = QMessageBox()
        hello_window.setWindowTitle("Домашняя Бухгалетрия")
        hello_window.setWindowIcon(QIcon("image/logo.png"))
        hello_window.setText("<p align='center'>Приветсвую в ""Домащней бухгалтерии""<br>"
                             "<p align='left'><br>"
                             "</p>")
        hello_window.setInformativeText("<p align='left'>))) </p>")

        hello_window.exec_()

        # подключаем БД
        self.connection = sqlite3.connect('data.db')
        self.select_data_checking()
        self.select_data_income()
        self.select_data_spent()
        self.balance()
        self.combo()

        # настраиваем кнопки
        self.btn_new_checking.clicked.connect(self.new_checking)
        self.btn_new_income.clicked.connect(self.new_income)
        self.btn_new_spent.clicked.connect(self.new_spent)
        self.btn_stat_spent.clicked.connect(self.spent_statistic)

        # настраиваем даты
        date_now = datetime.datetime.today()
        self.write_date_spent.setDateTime(date_now)
        self.write_date_income.setDateTime(date_now)
        self.date_stat_1.setDateTime(date_now)
        self.date_stat_2.setDateTime(date_now)

    def spent_statistic(self):
        # обновляем статстистику по расходам
        type_spent = self.comboBox.currentText()
        date_1 = tuple([int(i) for i in self.date_stat_1.text().split('.')][::-1])
        date_2 = tuple([int(i) for i in self.date_stat_2.text().split('.')][::-1])
        cur = self.connection.cursor()
        query = f"SELECT money, date FROM spent_table WHERE type = '{type_spent}'"
        money = cur.execute(query).fetchall()
        date_1 = datetime.datetime(*date_1)
        date_2 = datetime.datetime(*date_2)
        result = []
        for i in money:
            date_spent = tuple([int(j) for j in i[1].split('.')][::-1])
            date_spent = datetime.datetime(*date_spent)
            if date_1 <= date_spent <= date_2:
                result.append(i[0])
        self.label_report_stat_spent.setText(f'{sum(result)} руб')
        self.label_report_stat_spent.setAlignment(Qt.AlignCenter)

    def balance(self):
        # обновляем данные страницы статистики
        cur = self.connection.cursor()
        query_money = f"SELECT money FROM checking"
        money_checking = cur.execute(query_money).fetchall()
        res = sum([i[0] for i in money_checking])
        self.label_all_money_now.setText(f'{res} руб')
        self.label_all_money_now.setAlignment(Qt.AlignCenter)
        if res < 30000:
            self.label_quote.setText('Деньги - это не главное, возможно...')
        elif res < 60000:
            self.label_quote.setText('Время и деньги по большей части взаимозаменяемы...')
        elif res < 100000:
            self.label_quote.setText('Нельзя купить счастье за деньги, но можно арендовать...')
        else:
            self.label_quote.setText('Жизнь — игра, а деньги — способ вести счет...')
        self.label_quote.setAlignment(Qt.AlignCenter)
        self.label_quote.setFont(QFont('Monotype Corsiva', 15))
        query_money = f"SELECT money FROM income_table"
        money_income = cur.execute(query_money).fetchall()
        res = sum([i[0] for i in money_income])
        self.label_all_income.setText(f'{res} руб')
        self.label_all_income.setAlignment(Qt.AlignCenter)
        query_money = f"SELECT money FROM spent_table"
        money_income = cur.execute(query_money).fetchall()
        res = sum([i[0] for i in money_income])
        self.label_all_spent.setText(f'{res} руб')
        self.label_all_spent.setAlignment(Qt.AlignCenter)

    def new_spent(self):
        # Создаем новый расход
        money = float(self.write_money_spent.text().replace(',', '.'))
        other = self.write_other_spent.text()
        type_spent = self.write_checking_spent.currentText()
        type_checking = self.write_type_spent.currentText()
        date_income = self.write_date_spent.text()
        cur = self.connection.cursor()
        query = f"""INSERT INTO spent_table(date, money, type, checking, note)
                    VALUES(?, ?, ?, ?, ?)"""
        data_tuple = (date_income, money, type_spent, type_checking, other)
        cur.execute(query, data_tuple)
        query_money = f"SELECT money FROM checking where name='{type_checking}'"
        money_old = cur.execute(query_money).fetchall()[0][0]
        money_old -= money
        query = f"UPDATE checking set money = {money_old} WHERE name = '{type_checking}'"
        cur.execute(query)
        self.connection.commit()
        self.select_data_checking()
        self.select_data_spent()
        self.balance()

    def new_income(self):
        # Создаем новый доход
        money = float(self.write_money_income.text().replace(',', '.'))
        other = self.write_other_income.text()
        type_income = self.write_type_income.currentText()
        type_checking = self.write_checking_income.currentText()
        date_income = self.write_date_income.text()
        cur = self.connection.cursor()
        query = f"""INSERT INTO income_table(date, money, type_income, checking, note)
                    VALUES(?, ?, ?, ?, ?)"""
        data_tuple = (date_income, money, type_income, type_checking, other)
        cur.execute(query, data_tuple)
        query_money = f"SELECT money FROM checking where name='{type_checking}'"
        money_old = cur.execute(query_money).fetchall()[0][0]
        money += money_old
        query = f"UPDATE checking set money = {money} WHERE name = '{type_checking}'"
        cur.execute(query)
        self.connection.commit()
        self.select_data_checking()
        self.select_data_income()
        self.balance()

    def new_checking(self):
        # Создаем новый счет
        name1 = self.write_new_checking.text()
        cur = self.connection.cursor()
        query = f"""INSERT INTO checking(name) VALUES('{name1}')"""
        cur.execute(query)
        self.connection.commit()
        self.select_data_checking()
        self.combo()
        self.balance()

    def combo(self):
        # настраиваем все Combo box
        res = self.connection.cursor().execute("SELECT name FROM spent_type").fetchall()
        spent_type = [i[0] for i in res]
        self.write_checking_spent.addItems(spent_type)
        self.comboBox.clear()
        self.comboBox.addItems(spent_type)
        query = "SELECT name FROM checking"
        res = self.connection.cursor().execute(query).fetchall()
        checking_list = [i[0] for i in res]
        self.write_type_spent.clear()
        self.write_checking_income.clear()
        self.write_type_spent.addItems(checking_list)
        self.write_checking_income.addItems(checking_list)
        res = self.connection.cursor().execute("SELECT name FROM income_type").fetchall()
        income_type = [i[0] for i in res]
        self.write_type_income.clear()
        self.write_type_income.addItems(income_type)
        
    def select_data_spent(self):
        # Создаем или обновляем таблицу с раходами
        query = "SELECT * FROM spent_table"
        res = self.connection.cursor().execute(query).fetchall()
        self.tablespent.setColumnCount(6)
        self.tablespent.setRowCount(0)
        hed = ['№', 'Датa', 'Сумма' + ' ' * 20, 'Причина расхода',
               'Счёт списания', 'Примечание']
        self.tablespent.setHorizontalHeaderLabels(hed)
        for i, row in enumerate(res):
            self.tablespent.setRowCount(
                self.tablespent.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tablespent.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tablespent.resizeColumnsToContents()

    def select_data_income(self):
        # Создаем или обновляем таблицу с доходами
        query = "SELECT * FROM income_table"
        res = self.connection.cursor().execute(query).fetchall()
        self.table_income.setColumnCount(6)
        self.table_income.setRowCount(0)
        hed = ['№', 'Датa', 'Сумма' + ' ' * 20, 'Источник дохода',
               'Счёт поступления', 'Примечание']
        self.table_income.setHorizontalHeaderLabels(hed)
        for i, row in enumerate(res):
            self.table_income.setRowCount(
                self.table_income.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table_income.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.table_income.resizeColumnsToContents()

    def select_data_checking(self):
        # Создаем или обновляем таблицу со счетами
        query = "SELECT name, money FROM checking"
        res = self.connection.cursor().execute(query).fetchall()
        self.table_checking.setColumnCount(2)
        self.table_checking.setRowCount(0)
        self.table_checking.setHorizontalHeaderLabels(["Назавание счёта" + ' ' * 70, "Остаток" + ' ' * 100])
        for i, row in enumerate(res):
            self.table_checking.setRowCount(
                self.table_checking.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table_checking.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.table_checking.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
