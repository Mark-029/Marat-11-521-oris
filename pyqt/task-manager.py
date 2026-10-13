import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QTextEdit,
                             QRadioButton, QCheckBox, QPushButton)

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("Task Manager")
window.resize(600, 700)

central_widget = QWidget()
window.setCentralWidget(central_widget)

main_layout = QVBoxLayout()

#Строка статуса и счетчик задач
status_layout = QHBoxLayout()
status_label = QLabel("Status: Ready")
counter_label = QLabel("Created tasks: 0")
status_layout.addWidget(status_label)
status_layout.addWidget(counter_label)
main_layout.addLayout(status_layout)

#Название задачи
main_layout.addWidget(QLabel("Task:"))
task_input = QLineEdit()
main_layout.addWidget(task_input)

#Описание
main_layout.addWidget(QLabel("Description:"))
desc_input = QTextEdit()
main_layout.addWidget(desc_input)

#Приоритет
main_layout.addWidget(QLabel("Priority:"))
priority_layout = QHBoxLayout()
radio_low = QRadioButton("Low")
radio_med = QRadioButton("Medium")
radio_high = QRadioButton("High")
radio_low.setChecked(True)

priority_layout.addWidget(radio_low)
priority_layout.addWidget(radio_med)
priority_layout.addWidget(radio_high)
main_layout.addLayout(priority_layout)

#Дополнительные настройки
main_layout.addWidget(QLabel("Settings:"))
settings_layout = QVBoxLayout()
cb_important = QCheckBox("Important")
cb_notify = QCheckBox("Send notification")
settings_layout.addWidget(cb_important)
settings_layout.addWidget(cb_notify)
main_layout.addLayout(settings_layout)

#Кнопки
buttons_layout = QHBoxLayout()
btn_create = QPushButton("Create task")
btn_clear = QPushButton("Clear")
btn_delete = QPushButton("Delete last task")

buttons_layout.addWidget(btn_create)
buttons_layout.addWidget(btn_clear)
buttons_layout.addWidget(btn_delete)
main_layout.addLayout(buttons_layout)

#Список задач
main_layout.addWidget(QLabel("Tasks list:"))
result_display = QTextEdit()
result_display.setReadOnly(True)
main_layout.addWidget(result_display)

central_widget.setLayout(main_layout)

tasks_list = []


def update_display():
    counter_label.setText(f"Created tasks: {len(tasks_list)}")

    all_tasks_text = ""
    for i, task in enumerate(tasks_list, 1):
        all_tasks_text += f"     Task {i}: {task['name']}\n"
        all_tasks_text += f"Priority: {task['priority']}\nImportant: {task['important']}\nNotify: {task['notify']}\n"
        all_tasks_text += f"Description: {task['desc']}\n\n"

    result_display.setText(all_tasks_text)


def create_task():
    name = task_input.text()
    desc = desc_input.toPlainText()

    if radio_low.isChecked():
        priority = "Low"
    elif radio_med.isChecked():
        priority = "Medium"
    else:
        priority = "High"

    important = "Yes" if cb_important.isChecked() else "No"
    notify = "Yes" if cb_notify.isChecked() else "No"

    tasks_list.append({
        "name": name,
        "desc": desc,
        "priority": priority,
        "important": important,
        "notify": notify
    })

    status_label.setText("Status: Task created")
    update_display()


def clear_form():
    task_input.clear()
    desc_input.clear()
    radio_low.setChecked(True)
    cb_important.setChecked(False)
    cb_notify.setChecked(False)
    status_label.setText("Status: Ready")


def delete_last_task():
    if tasks_list:
        tasks_list.pop()
        status_label.setText("Status: Last task deleted")
        update_display()
    else:
        status_label.setText("Status: No tasks to delete")


btn_create.clicked.connect(create_task)
btn_clear.clicked.connect(clear_form)
btn_delete.clicked.connect(delete_last_task)

window.show()
sys.exit(app.exec())