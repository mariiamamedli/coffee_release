import sqlite3
import sys

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QDialog, QApplication

from main_ui import Ui_MainWindow
from addEditCoffeeForm import Ui_Dialog


class DBSample(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect("data/coffee.sqlite")
        self.pushButton.clicked.connect(self.add_elem)
        self.pushButton_2.clicked.connect(self.edit_elem)
        self.update_data()

    def update_data(self):
        res = self.connection.cursor().execute("""SELECT coffee.ID, coffee.Название_сорта,
        roasting.Степень_обжарки, types.Вид_зерен, coffee.Описание_вкуса, coffee.Цена_р, coffee.Объем_упаковки_г
        FROM coffee
        JOIN roasting
        ON coffee.Степень_обжарки = roasting.ID
        JOIN types
        ON coffee.Вид_зерен = types.ID""").fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Название сорта', 'Степень обжарки', 'Вид зерен',
                                                    'Описание вкуса', 'Цена (р)', 'Объем упаковки (г)'])
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def closeEvent(self, event):
        self.connection.close()

    def add_elem(self):
        self.dialog = Dialog_add(self)
        self.dialog.show()
        self.dialog.exec_()

    def edit_elem(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        if len(rows) != 1:
            self.statusBar.showMessage('Выберите один элемент')
        else:
            id = self.tableWidget.item(rows[0], 0).text()
            self.dialog = Dialog_edit(self, id)
            self.dialog.show()
            self.dialog.exec_()


class Dialog_add(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.setWindowTitle('Добавить элемент')
        self.comboBox.addItems(list(map(lambda x: x[0], self.parent.connection.cursor().execute("""SELECT
         Степень_обжарки FROM roasting"""))))
        self.comboBox_2.addItems(list(map(lambda x: x[0], self.parent.connection.cursor().execute("""SELECT
         Вид_зерен FROM types"""))))
        self.label_5.setHidden(True)
        self.setModal(True)
        self.pushButton.clicked.connect(self.add_elem)

    def add_elem(self):
        try:
            self.label_5.setHidden(True)
            assert self.lineEdit.text() != ''
            assert self.lineEdit_2.text() != ''
            roasting = int(list(self.parent.connection.cursor().execute("""SELECT
             ID FROM roasting WHERE Степень_обжарки == ?""", (self.comboBox.currentText(), )))[0][0])
            type = int(list(self.parent.connection.cursor().execute("""SELECT ID FROM types WHERE Вид_зерен == ?""",
                                                         (self.comboBox_2.currentText(), )))[0][0])
            self.parent.connection.cursor().execute("""INSERT INTO coffee(Название_сорта, Степень_обжарки, Вид_зерен,
            Описание_вкуса, Цена_р, Объем_упаковки_г) VALUES(?, ?, ?, ?, ?, ?)""",
                                                    (self.lineEdit.text(), roasting, type, self.lineEdit_2.text(),
                                                     float(self.doubleSpinBox.value()), int(self.spinBox.value())))
            self.parent.connection.commit()
            self.parent.update_data()
            self.close()
        except Exception:
            self.label_5.setHidden(False)


class Dialog_edit(QDialog, Ui_Dialog):
    def __init__(self, parent, id):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.id = id
        self.parent.statusBar.showMessage('')
        self.setWindowTitle('Редактировать элемент')
        r = list(map(lambda x: x[0], self.parent.connection.cursor().execute("""SELECT
         Степень_обжарки FROM roasting""")))
        self.comboBox.addItems(r)
        g = list(self.parent.connection.cursor().execute("""SELECT Степень_обжарки FROM roasting WHERE ID in
         (SELECT Степень_обжарки FROM coffee WHERE ID = ?)""", (id, )))[0][0]
        self.comboBox.setCurrentIndex(r.index(g))
        r = list(map(lambda x: x[0], self.parent.connection.cursor().execute("""SELECT
                 Вид_зерен FROM types""")))
        self.comboBox_2.addItems(r)
        g = list(self.parent.connection.cursor().execute("""SELECT Вид_зерен FROM types WHERE ID in
                 (SELECT Вид_зерен FROM coffee WHERE ID = ?)""", (id,)))[0][0]
        self.comboBox_2.setCurrentIndex(r.index(g))
        t = list(self.parent.connection.cursor().execute("""SELECT Название_сорта FROM coffee WHERE ID = ?""", (id,)))[0][0]
        self.lineEdit.setText(t)
        t = list(self.parent.connection.cursor().execute("""SELECT Описание_вкуса FROM coffee WHERE ID = ?""", (id,)))[0][0]
        self.lineEdit_2.setText(t)
        t = float(list(self.parent.connection.cursor().execute("""SELECT Цена_р FROM coffee WHERE ID = ?""", (id,)))[0][0])
        self.doubleSpinBox.setValue(t)
        t = int(list(self.parent.connection.cursor().execute("""SELECT Объем_упаковки_г FROM coffee WHERE ID = ?""", (id,)))[0][0])
        self.spinBox.setValue(t)
        self.label_5.setHidden(True)
        self.setModal(True)
        self.pushButton.clicked.connect(self.edit_elem)

    def edit_elem(self):
        try:
            id = int(self.id)
            self.label_5.setHidden(True)
            assert self.lineEdit.text() != ''
            assert self.lineEdit_2.text() != ''
            roasting = int(list(self.parent.connection.cursor().execute("""SELECT
                         ID FROM roasting WHERE Степень_обжарки == ?""", (self.comboBox.currentText(),)))[0][0])
            type = int(list(self.parent.connection.cursor().execute("""SELECT ID FROM types WHERE Вид_зерен == ?""",
                                                                    (self.comboBox_2.currentText(),)))[0][0])
            self.parent.connection.cursor().execute("UPDATE coffee SET Название_сорта = ? WHERE ID = ?",
                                             (self.lineEdit.text(), id))
            self.parent.connection.cursor().execute("UPDATE coffee SET Степень_обжарки = ? WHERE ID = ?", (roasting, id))
            self.parent.connection.cursor().execute("UPDATE coffee SET Вид_зерен = ? WHERE ID = ?", (type, id))
            self.parent.connection.cursor().execute("UPDATE coffee SET Описание_вкуса = ? WHERE ID = ?",
                                             (self.lineEdit_2.text(), id))
            self.parent.connection.cursor().execute("UPDATE coffee SET Цена_р = ? WHERE ID = ?",
                                             (float(self.doubleSpinBox.value()), id))
            self.parent.connection.cursor().execute("UPDATE coffee SET Объем_упаковки_г = ? WHERE ID = ?",
                                             (int(self.spinBox.value()), id))
            self.parent.connection.commit()
            self.parent.update_data()
            self.close()
        except Exception:
            self.label_5.setHidden(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(app.exec())
