import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QTextEdit,
                             QRadioButton, QCheckBox, QPushButton, QMessageBox)


class TaskManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.resize(600, 700)

        self.tasks_list = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Ready")
        self.counter_label = QLabel("Created tasks: 0")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.counter_label)
        main_layout.addLayout(status_layout)

        main_layout.addWidget(QLabel("Task:"))
        self.task_input = QLineEdit()
        main_layout.addWidget(self.task_input)
        self.char_count_label = QLabel("Characters: 0")
        main_layout.addWidget(self.char_count_label)

        main_layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        main_layout.addWidget(self.desc_input)

        main_layout.addWidget(QLabel("Priority:"))
        priority_layout = QHBoxLayout()
        self.radio_low = QRadioButton("Low")
        self.radio_med = QRadioButton("Medium")
        self.radio_high = QRadioButton("High")
        self.radio_low.setChecked(True)

        priority_layout.addWidget(self.radio_low)
        priority_layout.addWidget(self.radio_med)
        priority_layout.addWidget(self.radio_high)
        main_layout.addLayout(priority_layout)

        main_layout.addWidget(QLabel("Settings:"))
        settings_layout = QVBoxLayout()
        self.cb_important = QCheckBox("Important")
        self.cb_notify = QCheckBox("Send notification")
        settings_layout.addWidget(self.cb_important)
        settings_layout.addWidget(self.cb_notify)
        main_layout.addLayout(settings_layout)

        buttons_layout = QHBoxLayout()
        self.btn_create = QPushButton("Create task")
        self.btn_clear = QPushButton("Clear")
        self.btn_delete = QPushButton("Delete last task")
        self.btn_delete_all = QPushButton("Delete all tasks")

        buttons_layout.addWidget(self.btn_create)
        buttons_layout.addWidget(self.btn_clear)
        buttons_layout.addWidget(self.btn_delete)
        buttons_layout.addWidget(self.btn_delete_all)
        main_layout.addLayout(buttons_layout)

        main_layout.addWidget(QLabel("Tasks list:"))
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        main_layout.addWidget(self.result_display)

        central_widget.setLayout(main_layout)

        self.btn_create.clicked.connect(self.create_task)
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_delete.clicked.connect(self.delete_last_task)
        self.btn_delete_all.clicked.connect(self.delete_all_tasks)

        self.task_input.textChanged.connect(self.update_char_count)

    def update_display(self):
        self.counter_label.setText(f"Created tasks: {len(self.tasks_list)}")

        all_tasks_text = ""
        for i, task in enumerate(self.tasks_list, 1):
            all_tasks_text += f"     Task {i}: {task['name']}\n"
            all_tasks_text += f"Priority: {task['priority']}\nImportant: {task['important']}\nNotify: {task['notify']}\n"
            all_tasks_text += f"Description: {task['desc']}\n\n"

        self.result_display.setText(all_tasks_text)

    def create_task(self):
        name = self.task_input.text()

        if not name.strip():
            QMessageBox.warning(self, "Warning", "Task name cannot be empty!")
            return

        desc = self.desc_input.toPlainText()

        if self.radio_low.isChecked():
            priority = "Low"
        elif self.radio_med.isChecked():
            priority = "Medium"
        else:
            priority = "High"

        important = "Yes" if self.cb_important.isChecked() else "No"
        notify = "Yes" if self.cb_notify.isChecked() else "No"

        self.tasks_list.append({
            "name": name,
            "desc": desc,
            "priority": priority,
            "important": important,
            "notify": notify
        })

        self.clear_form()

        self.status_label.setText("Status: Task created")
        self.update_display()

    def clear_form(self):
        self.task_input.clear()
        self.desc_input.clear()
        self.radio_low.setChecked(True)
        self.cb_important.setChecked(False)
        self.cb_notify.setChecked(False)
        self.status_label.setText("Status: Ready")

    def delete_last_task(self):
        if self.tasks_list:
            self.tasks_list.pop()
            self.status_label.setText("Status: Last task deleted")
            self.update_display()
        else:
            self.status_label.setText("Status: No tasks to delete")

    def delete_all_tasks(self):
        if not self.tasks_list:
            QMessageBox.information(self, "Info", "The task list is already empty.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete all tasks?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.tasks_list.clear()
            self.status_label.setText("Status: All tasks deleted")
            self.update_display()
        else:
            self.status_label.setText("Status: Deletion cancelled")

    def update_char_count(self, text):
        self.char_count_label.setText(f"Characters: {len(text)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskManagerApp()
    window.show()
    sys.exit(app.exec())