import sys
import random
import string
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSlider, QCheckBox, QPushButton, QLineEdit, QMessageBox,
    QProgressBar, QListWidget, QComboBox, QStackedLayout
)
from PySide6.QtCore import Qt, QTimer
from plyer import notification
import json
import os
import requests
import zipfile
import io


class PasswordGenerator(QWidget):
    def __init__(self, lang_code="fr"):
        super().__init__()
        self.lang_code = lang_code
        self.translations = self.load_language(lang_code)
        self.setWindowTitle(self.translations["window_title"])
        self.setFixedSize(450, 450)
        self.history = []

        # Timer d’expiration
        self.expire_timer = QTimer()
        self.expire_timer.setInterval(30_000)
        self.expire_timer.timeout.connect(self.clear_password)

        # Création des deux pages
        self.home_widget = self.create_home_page()
        self.about_widget = self.create_about_page()

        # Layout avec switch entre les deux
        self.stack = QStackedLayout()
        self.stack.addWidget(self.home_widget)
        self.stack.addWidget(self.about_widget)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.stack)
        self.setLayout(main_layout)

    def updater(main_window):
        # Exemple avec GitHub API pour release la plus récente
        url = "https://api.github.com/repos/TON_COMPTE/TON_REPO/releases/latest"
        try:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            zip_url = data['zipball_url']

            # Téléchargement du zip
            zip_resp = requests.get(zip_url)
            zip_resp.raise_for_status()

            # Extraction dans un dossier temporaire
            z = zipfile.ZipFile(io.BytesIO(zip_resp.content))

            # Extraire tout dans un dossier temporaire
            tmp_dir = "update_tmp"
            if not os.path.exists(tmp_dir):
                os.mkdir(tmp_dir)
            z.extractall(tmp_dir)

            QMessageBox.information(main_window, "Update",
                                    "Mise à jour téléchargée, merci de redémarrer l'application.")

        except Exception as e:
            QMessageBox.warning(main_window, "Erreur update", str(e))


    def create_home_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Sélecteur de langue
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["fr", "en"])
        self.lang_selector.setCurrentText(self.lang_code)
        self.lang_selector.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(QLabel("Langue :"))
        lang_layout.addWidget(self.lang_selector)
        layout.addLayout(lang_layout)

        # Profils
        profile_layout = QHBoxLayout()
        profile_label = QLabel(self.translations["profile_label"])
        self.profile_combo = QComboBox()
        self.profile_combo.addItems([
            self.translations["profile_custom"],
            self.translations["profile_simple"],
            self.translations["profile_secure"],
            self.translations["profile_ultrasecure"]
        ])
        self.profile_combo.currentTextChanged.connect(self.apply_profile)
        profile_layout.addWidget(profile_label)
        profile_layout.addWidget(self.profile_combo)

        # Longueur
        length_layout = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(4, 64)
        self.slider.setValue(12)
        self.slider.valueChanged.connect(self.update_length_label)
        self.length_label = QLabel(f"{self.translations['length_label']} : {self.slider.value()}")
        length_layout.addWidget(self.length_label)
        length_layout.addWidget(self.slider)

        # Options
        self.checkbox_lower = QCheckBox(self.translations["lowercase"])
        self.checkbox_upper = QCheckBox(self.translations["uppercase"])
        self.checkbox_digits = QCheckBox(self.translations["digits"])
        self.checkbox_symbols = QCheckBox(self.translations["symbols"])
        self.checkbox_lower.setChecked(True)
        self.checkbox_digits.setChecked(True)

        # Générer
        self.generate_button = QPushButton(self.translations["generate_button"])
        self.generate_button.clicked.connect(self.generate_password)

        # Output + bouton afficher
        self.output = QLineEdit()
        self.output.setReadOnly(True)
        self.output.setEchoMode(QLineEdit.Password)
        self.toggle_button = QPushButton(self.translations["show_button"])
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(lambda: self.output.setEchoMode(
            QLineEdit.Normal if self.toggle_button.isChecked() else QLineEdit.Password)
        )

        # Copie
        self.copy_button = QPushButton(self.translations["copy_button"])
        self.copy_button.clicked.connect(self.copy_password)

        # Force
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 5)
        self.strength_bar.setFormat(self.translations["strength_format"])

        # Historique
        self.history_widget = QListWidget()
        self.history_widget.setMaximumHeight(80)

        # Ajout à layout
        layout.addLayout(profile_layout)
        layout.addLayout(length_layout)
        layout.addWidget(self.checkbox_lower)
        layout.addWidget(self.checkbox_upper)
        layout.addWidget(self.checkbox_digits)
        layout.addWidget(self.checkbox_symbols)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.output)

        btns = QHBoxLayout()
        btns.addWidget(self.toggle_button)
        btns.addWidget(self.copy_button)
        layout.addLayout(btns)

        layout.addWidget(self.strength_bar)
        layout.addWidget(QLabel(self.translations["history_label"]))
        layout.addWidget(self.history_widget)

        # Bouton vers la page à propos
        about_button = QPushButton("About GenPass")
        about_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.about_widget))
        layout.addWidget(about_button)

        widget.setLayout(layout)
        return widget

    def create_about_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel("GenPass - Safe password generator\n\n"
                       "Version : 1.0\nAuthor : bowser-2077\n\n"
                       "This project is open-source and fully customisable\n"
                       "Contact : hostinfire@gmail.com")
        label.setAlignment(Qt.AlignCenter)

        back_button = QPushButton("⬅ Retour")
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.home_widget))

        update_button = QPushButton("Update GenPass")
        update_button.clicked.connect(self.updater)

        layout.addWidget(label)
        layout.addWidget(update_button)
        layout.addWidget(back_button)
        widget.setLayout(layout)
        return widget

    def update_length_label(self, value):
        self.length_label.setText(f"{self.translations['length_label']} : {value}")

    def apply_profile(self, profile):
        if profile == self.translations["profile_simple"]:
            self.slider.setValue(8)
            self.checkbox_lower.setChecked(True)
            self.checkbox_upper.setChecked(False)
            self.checkbox_digits.setChecked(True)
            self.checkbox_symbols.setChecked(False)
        elif profile == self.translations["profile_secure"]:
            self.slider.setValue(14)
            self.checkbox_lower.setChecked(True)
            self.checkbox_upper.setChecked(True)
            self.checkbox_digits.setChecked(True)
            self.checkbox_symbols.setChecked(True)
        elif profile == self.translations["profile_ultrasecure"]:
            self.slider.setValue(24)
            self.checkbox_lower.setChecked(True)
            self.checkbox_upper.setChecked(True)
            self.checkbox_digits.setChecked(True)
            self.checkbox_symbols.setChecked(True)

    def generate_password(self):
        length = self.slider.value()
        chars = ""
        if self.checkbox_lower.isChecked(): chars += string.ascii_lowercase
        if self.checkbox_upper.isChecked(): chars += string.ascii_uppercase
        if self.checkbox_digits.isChecked(): chars += string.digits
        if self.checkbox_symbols.isChecked(): chars += "!@#$%&*+-=?"

        if not chars:
            QMessageBox.warning(self, self.translations["error_title"], self.translations["error_no_chars"])
            return

        pwd = ''.join(random.choice(chars) for _ in range(length))
        self.output.setText(pwd)
        self.update_strength(pwd)
        self.add_to_history(pwd)
        self.expire_timer.start()

    def update_strength(self, pwd):
        score = 0
        if len(pwd) >= 8: score += 1
        if any(c.islower() for c in pwd): score += 1
        if any(c.isupper() for c in pwd): score += 1
        if any(c.isdigit() for c in pwd): score += 1
        if any(c in "!@#$%&*+-=?" for c in pwd): score += 1
        self.strength_bar.setValue(score)

    def add_to_history(self, pwd):
        self.history.insert(0, pwd)
        self.history = self.history[:5]
        self.history_widget.clear()
        self.history_widget.addItems(self.history)

    def copy_password(self):
        QApplication.clipboard().setText(self.output.text())
        QMessageBox.information(self, self.translations["info_title"], self.translations["copied_message"])
        self.show_notification(self.translations["window_title"], self.translations["copied_message"])

    def clear_password(self):
        self.output.setText("")
        self.expire_timer.stop()
        QMessageBox.information(self, self.translations["info_title"], self.translations["expired_message"])

    def show_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            app_name="GenPass",
            timeout=5
        )

    def load_language(self, lang_code="fr"):
        path = os.path.join("lang", f"{lang_code}.json")
        if not os.path.exists(path):
            print(f"Langue {lang_code} Unavailable, falling back to default.")
            path = os.path.join("lang", "fr.json")
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def change_language(self, lang_code):
        self.lang_code = lang_code
        self.translations = self.load_language(lang_code)
        self.refresh_ui()


    def refresh_ui(self):
        self.setWindowTitle(self.translations["window_title"])
        self.length_label.setText(f"{self.translations['length_label']} : {self.slider.value()}")
        self.checkbox_lower.setText(self.translations["lowercase"])
        self.checkbox_upper.setText(self.translations["uppercase"])
        self.checkbox_digits.setText(self.translations["digits"])
        self.checkbox_symbols.setText(self.translations["symbols"])
        self.generate_button.setText(self.translations["generate_button"])
        self.strength_bar.setFormat(self.translations["strength_format"])
        self.profile_combo.setItemText(0, self.translations["profile_custom"])
        self.profile_combo.setItemText(1, self.translations["profile_simple"])
        self.profile_combo.setItemText(2, self.translations["profile_secure"])
        self.profile_combo.setItemText(3, self.translations["profile_ultrasecure"])
        self.history_widget.setToolTip(self.translations["history_label"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordGenerator(lang_code="fr")
    window.show()
    sys.exit(app.exec())
