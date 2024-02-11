import sys

from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QCalendarWidget, QLabel, QVBoxLayout, QDialog, QPushButton, QLineEdit, QHBoxLayout, QWidget
from PyQt5.QtCore import QDate, QLocale, Qt


class CalculateDaysDialog(QDialog):
    def __init__(self, holidays, parent=None):
        super().__init__(parent)
        self.holidays = holidays
        self.setWindowTitle("计算日期")

        self.result_label = QLabel(self)
        self.result_label.setAlignment(Qt.AlignCenter)

        self.date_edit = QLineEdit(self)

        self.calculate_button = QPushButton("计算", self)
        self.calculate_button.clicked.connect(self.calculateDays)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("请输入日期(yyyy-MM-dd)"))
        layout.addWidget(self.date_edit)
        layout.addWidget(self.calculate_button)
        layout.addWidget(self.result_label)

    def calculateDays(self):
        try:
            input_date = QDate.fromString(self.date_edit.text(), "yyyy-MM-dd")
            current_date = QDate.currentDate()

            # 计算相隔天数
            days_difference = current_date.daysTo(input_date)

            # 计算中间的节假日天数
            holidays_between_dates = 0
            date = current_date.addDays(1)  # 从明天开始检查
            while date <= input_date:
                if date.toString("yyyy-MM-dd") in self.holidays:
                    holidays_between_dates += 1
                date = date.addDays(1)

            # 从相隔天数中减去节假日天数
            effective_days_difference = days_difference - holidays_between_dates

            # 计算周数和剩余天数
            weeks_difference = (days_difference - (days_difference % 7)) / 7
            holidays_dates = 0

            temp_date = current_date.addDays(int(weeks_difference) * 7)
            temp = 0
            while temp_date <= input_date:
                if temp_date.toString("yyyy-MM-dd") in self.holidays:
                    if temp ==0:
                        temp += 1
                    elif temp!=0:
                        holidays_dates += 1
                temp_date = temp_date.addDays(1)
            weeks_difference_day = (days_difference % 7) - holidays_dates

            if effective_days_difference > 0:
                self.result_label.setText(
                    f"距离 {input_date.toString('yyyy-MM-dd')} 还有 {effective_days_difference} 天，或者说还有 {weeks_difference} 周,{weeks_difference_day} 天")
            elif effective_days_difference < 0:
                self.result_label.setText(
                    f"{input_date.toString('yyyy-MM-dd')} 已经过去 {abs(effective_days_difference)} 天，或者说已经 {abs(weeks_difference)} 周,{abs(weeks_difference_day)} 天")
            else:
                self.result_label.setText("今天就是这个日期！")
        except Exception as e:
            self.result_label.setText("错误：" + str(e))


class SelectHolidaysDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("选择节假日")

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)

        self.ok_button = QPushButton("确认", self)
        self.ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.calendar)
        layout.addWidget(self.ok_button)

    def selectedDates(self):
        return self.calendar.selectedDate()


class HolidayCalendar(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("倒数日")

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setDateRange(QDate(2024, 1, 1), QDate(2025, 12, 31))

        self.holidays = {}

        self.select_holidays_button = QPushButton("选择节假日", self)
        self.select_holidays_button.clicked.connect(self.selectHolidays)

        self.calculate_days_button = QPushButton("计算日期", self)
        self.calculate_days_button.clicked.connect(self.openCalculateDaysDialog)

        # 创建一个垂直布局
        layout = QVBoxLayout()
        # 添加控件到布局
        layout.addWidget(self.calendar)
        layout.addWidget(self.select_holidays_button)
        layout.addWidget(self.calculate_days_button)

        # 创建一个QWidget作为中心控件
        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        # 获取节假日数据
        self.load_holidays()

        self.load_holidays_from_file()
        # 显示节假日
        self.update_calendar()

    def openCalculateDaysDialog(self):
        dialog = CalculateDaysDialog(self.holidays, self)
        dialog.exec_()

    def load_holidays_from_file(self):
        try:
            with open("holidays.txt", "r") as file:
                for line in file:
                    date, holiday_name = line.strip().split(',')
                    self.holidays[date] = holiday_name
        except FileNotFoundError:
            print("未找到节假日文件。未加载任何节假日。")
        except Exception as e:
            print("加载节假日时出错:", e)

    def load_holidays(self):
        # 加载所有周末为节假日
        start_date = self.calendar.minimumDate()
        end_date = self.calendar.maximumDate()
        current_date = start_date
        while current_date <= end_date:
            if current_date.dayOfWeek() == Qt.Saturday or current_date.dayOfWeek() == Qt.Sunday:
                self.holidays[current_date.toString("yyyy-MM-dd")] = "周末"
            current_date = current_date.addDays(1)

    def update_calendar(self):
        date = self.calendar.selectedDate()
        current_year = date.year()

        # 更新日历的节假日显示
        for day, holiday in self.holidays.items():
            if day.startswith(f"{current_year}-"):
                day_qdate = QDate.fromString(day, "yyyy-MM-dd")
                text_format = QTextCharFormat()
                text_format.setForeground(Qt.red)
                self.calendar.setDateTextFormat(day_qdate, text_format)

        print(self.holidays)

    def showEvent(self, event):
        self.update_calendar()
        super().showEvent(event)

    def save_holidays_to_file(self):
        try:
            with open("holidays.txt", "w") as file:
                for date, holiday_name in self.holidays.items():
                    file.write(f"{date},{holiday_name}\n")
        except Exception as e:
            print("保存节假日时出错:", e)

    def selectHolidays(self):
        try:
            dialog = SelectHolidaysDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                selected_date = dialog.selectedDates()
                self.holidays[selected_date.toString("yyyy-MM-dd")] = "节假日"
                self.update_calendar()
                self.save_holidays_to_file()  # 保存节假日更新后的信息
        except Exception as e:
            print("错误:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = HolidayCalendar()
    window.show()

    sys.exit(app.exec_())
