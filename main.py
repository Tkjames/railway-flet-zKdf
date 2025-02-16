import logging
import flet as ft
from datetime import datetime, timedelta
import random
import os

import flet as ft
import datetime

# Global in-memory storage for user accounts.
# (In production you’d use a persistent database.)
users = {}

def main(page: ft.Page):
    page.title = "Positivity Roadmap App"
    # Set default theme mode; this will be updated based on user preference.
    page.theme_mode = "light"
    
    # -------------------------------
    # Login / Register Screen
    # -------------------------------
    def show_login():
        login_username = ft.TextField(label="Username", width=300)
        login_password = ft.TextField(label="Password", password=True, width=300)
        login_message = ft.Text("", color="red")

        def login_clicked(e):
            username = login_username.value.strip()
            password = login_password.value.strip()
            if not username or not password:
                login_message.value = "Please enter both username and password."
                page.update()
                return

            # Create account if new, or check password if exists.
            if username not in users:
                users[username] = {
                    "password": password,
                    "gratitude": [],   # List of dicts: {"text": ..., "date": ...}
                    "progress": "Week 1-2: Catch Negative Thoughts & Reframe",
                    "dark_mode": False,
                }
            else:
                if users[username]["password"] != password:
                    login_message.value = "Incorrect password."
                    page.update()
                    return

            # Successful login; switch to main app view.
            show_main_app(username)

        login_button = ft.ElevatedButton("Login / Register", on_click=login_clicked)
        login_view = ft.Column(
            [
                ft.Text("Login or Register", size=28, weight="bold"),
                login_username,
                login_password,
                login_button,
                login_message,
            ],
            alignment="center",
            horizontal_alignment="center",
            spacing=20,
        )
        page.controls.clear()
        page.add(login_view)
        page.update()

    # -------------------------------
    # Main App Screen
    # -------------------------------
    def show_main_app(username: str):
        user_data = users[username]

        # --- Dark Mode Toggle ---
        def toggle_dark_mode(e):
            user_data["dark_mode"] = dark_mode_switch.value
            page.theme_mode = "dark" if dark_mode_switch.value else "light"
            page.update()

        dark_mode_switch = ft.Switch(
            label="Dark Mode",
            value=user_data["dark_mode"],
            on_change=toggle_dark_mode,
        )

        # --- Roadmap Progress ---
        roadmap_steps = [
            "Week 1-2: Catch Negative Thoughts & Reframe",
            "Week 3-4: Build Gratitude & Positive Replacements",
            "Week 5-6: Surround Yourself with Positivity",
            "Week 7-8: Automate & Reinforce",
        ]
        progress_dropdown = ft.Dropdown(
            label="Select Your Current Step",
            options=[ft.dropdown.Option(step) for step in roadmap_steps],
            value=user_data["progress"],
            width=350,
        )
        progress_text = ft.Text(user_data["progress"], size=18, weight="bold")

        def update_progress(e):
            user_data["progress"] = progress_dropdown.value
            progress_text.value = progress_dropdown.value
            page.update()

        progress_button = ft.ElevatedButton("Update Progress", on_click=update_progress)

        # --- Daily Gratitude Log ---
        gratitude_input = ft.TextField(label="Enter something positive today", width=350)
        gratitude_list = ft.Column()

        # Populate gratitude list from stored data
        for entry in user_data["gratitude"]:
            gratitude_list.controls.append(
                ft.Text(f"- {entry['text']} ({entry['date']})")
            )

        def add_gratitude(e):
            if gratitude_input.value:
                entry = {
                    "text": gratitude_input.value,
                    "date": datetime.date.today().isoformat(),
                }
                user_data["gratitude"].append(entry)
                gratitude_list.controls.append(
                    ft.Text(f"- {entry['text']} ({entry['date']})")
                )
                gratitude_input.value = ""
                page.update()

        gratitude_button = ft.ElevatedButton("Add Gratitude", on_click=add_gratitude)

        # --- Daily Reminder using Timer ---
        # For demo purposes, this timer is set to trigger every 60 seconds.
        # Change interval to 86400 (seconds) for daily reminders.
        def send_daily_reminder(e):
            page.snack_bar = ft.SnackBar(ft.Text("Don't forget to log your gratitude for today!"))
            page.snack_bar.open = True
            page.update()

        daily_timer = ft.Timer(interval=60, on_tick=send_daily_reminder)
        page.add_timer(daily_timer)

        # --- Logout ---
        def logout(e):
            show_login()
        logout_button = ft.ElevatedButton("Logout", on_click=logout)

        # --- Main App Layout ---
        main_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(f"Welcome, {username}!", size=28, weight="bold"),
                        logout_button,
                    ],
                    alignment="spaceBetween",
                ),
                dark_mode_switch,
                ft.Divider(),
                ft.Text("Positivity Roadmap", size=24, weight="bold"),
                progress_text,
                progress_dropdown,
                progress_button,
                ft.Divider(),
                ft.Text("Daily Gratitude Log", size=22, weight="bold"),
                gratitude_input,
                gratitude_button,
                gratitude_list,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
        page.controls.clear()
        page.add(main_view)
        page.update()

    # Start with the login view.
    show_login()

# Run the Flet app.
# The port number is set for local testing.
#ft.app(target=main, port=8550)


ft.app(target=main, view=None, port=int(os.getenv("PORT", 8502)))
