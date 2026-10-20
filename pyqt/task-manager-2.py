import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QTextEdit,
                             QCheckBox, QPushButton, QMessageBox, QComboBox, QInputDialog, QDialog)


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.resize(150, 100)

        layout = QVBoxLayout()

        info_label = QLabel("Task Manager App\nVersion: 2.0")
        layout.addWidget(info_label)

        close_btn = QPushButton("OK")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)


class TaskManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.resize(600, 700)

        self.editing_task_index = None
        self.load_tasks()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Ready")
        self.counter_label = QLabel("Created tasks: 0")
        self.btn_about = QPushButton("About")

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.counter_label)
        status_layout.addWidget(self.btn_about)
        main_layout.addLayout(status_layout)

        main_layout.addWidget(QLabel("Task:"))

        task_layout = QHBoxLayout()

        self.task_input = QLineEdit()
        task_layout.addWidget(self.task_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        task_layout.addWidget(self.priority_combo)

        main_layout.addLayout(task_layout)

        self.char_count_label = QLabel("Characters: 0")
        main_layout.addWidget(self.char_count_label)

        main_layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        main_layout.addWidget(self.desc_input)

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
        self.btn_delete_spec = QPushButton("Delete specific task")
        self.btn_delete_all = QPushButton("Delete all tasks")
        self.btn_edit = QPushButton("Edit specific task")

        buttons_layout.addWidget(self.btn_create)
        buttons_layout.addWidget(self.btn_clear)
        buttons_layout.addWidget(self.btn_delete)
        buttons_layout.addWidget(self.btn_delete_spec)
        buttons_layout.addWidget(self.btn_delete_all)
        buttons_layout.addWidget(self.btn_edit)
        main_layout.addLayout(buttons_layout)

        main_layout.addWidget(QLabel("Tasks list:"))
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        main_layout.addWidget(self.result_display)

        central_widget.setLayout(main_layout)

        self.btn_create.clicked.connect(self.create_task)
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_delete.clicked.connect(self.delete_last_task)
        self.btn_delete_spec.clicked.connect(self.delete_specific_task)
        self.btn_delete_all.clicked.connect(self.delete_all_tasks)

        self.task_input.textChanged.connect(self.update_char_count)

        self.btn_about.clicked.connect(self.show_about_dialog)

        self.btn_edit.clicked.connect(self.load_task_for_editing)

        self.update_display()

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
        priority = self.priority_combo.currentText()
        important = "Yes" if self.cb_important.isChecked() else "No"
        notify = "Yes" if self.cb_notify.isChecked() else "No"

        new_task = {
            "name": name,
            "desc": desc,
            "priority": priority,
            "important": important,
            "notify": notify
        }

        if self.editing_task_index is not None:
            self.tasks_list[self.editing_task_index] = new_task
            self.status_label.setText(f"Status: Task {self.editing_task_index + 1} updated")

            self.editing_task_index = None
            self.btn_create.setText("Create task")
        else:
            self.tasks_list.append(new_task)
            self.status_label.setText("Status: Task created")

        self.save_tasks()
        self.clear_form()
        self.update_display()

    def clear_form(self):
        self.task_input.clear()
        self.desc_input.clear()
        self.priority_combo.setCurrentIndex(0)
        self.cb_important.setChecked(False)
        self.cb_notify.setChecked(False)
        self.status_label.setText("Status: Ready")

        self.editing_task_index = None
        self.btn_create.setText("Create task")

    def delete_last_task(self):
        if self.tasks_list:
            self.tasks_list.pop()

            self.save_tasks()

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

            self.save_tasks()

            self.status_label.setText("Status: All tasks deleted")
            self.update_display()
        else:
            self.status_label.setText("Status: Deletion cancelled")

    def update_char_count(self, text):
        self.char_count_label.setText(f"Characters: {len(text)}")

    def delete_specific_task(self):
        if not self.tasks_list:
            QMessageBox.information(self, "Info", "No tasks to delete.")
            return

        task_num, ok = QInputDialog.getInt(
            self,
            "Delete Task",
            f"Enter task number to delete (1 - {len(self.tasks_list)}):",
            1,
            1,
            len(self.tasks_list),
            1
        )

        if ok:
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete Task {task_num}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.tasks_list.pop(task_num - 1)

                self.save_tasks()

                self.status_label.setText(f"Status: Task {task_num} deleted")
                self.update_display()
            else:
                self.status_label.setText("Status: Deletion cancelled")
        else:
            self.status_label.setText("Status: Deletion cancelled")

    @staticmethod
    def show_about_dialog():
        dialog = AboutDialog()
        dialog.exec()

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r", encoding="utf-8") as file:
                self.tasks_list = json.load(file)
        else:
            self.tasks_list = []

    def save_tasks(self):
        with open("tasks.json", "w", encoding="utf-8") as file:
            json.dump(self.tasks_list, file, indent=4, ensure_ascii=False)

    def load_task_for_editing(self):
        if not self.tasks_list:
            QMessageBox.information(self, "Info", "No tasks to edit.")
            return

        task_num, ok = QInputDialog.getInt(
            self, "Edit Task", f"Enter task number to edit (1 - {len(self.tasks_list)}):",
            1, 1, len(self.tasks_list), 1
        )

        if ok:
            self.editing_task_index = task_num - 1
            task = self.tasks_list[self.editing_task_index]

            self.task_input.setText(task['name'])
            self.desc_input.setPlainText(task['desc'])

            self.priority_combo.setCurrentText(task['priority'])

            self.cb_important.setChecked(task['important'] == "Yes")
            self.cb_notify.setChecked(task['notify'] == "Yes")

            self.btn_create.setText("Save changes")
            self.status_label.setText(f"Status: Editing Task {task_num}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskManagerApp()
    window.show()
    sys.exit(app.exec())