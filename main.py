import flet as ft
import datetime
import os

def main(page: ft.Page):
    page.title = "Positivity Roadmap App"
    page.theme_mode = "light"
    
    # --- Dark Mode Toggle ---
    def toggle_dark_mode(e):
        page.theme_mode = "dark" if dark_mode_switch.value else "light"
        page.update()

    dark_mode_switch = ft.Switch(
        label="Dark Mode",
        value=False,
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
        value=roadmap_steps[0],
        width=350,
    )
    progress_text = ft.Text(roadmap_steps[0], size=18, weight="bold")

    def update_progress(e):
        progress_text.value = progress_dropdown.value
        page.update()

    progress_button = ft.ElevatedButton("Update Progress", on_click=update_progress)

    # --- Daily Gratitude Log ---
    gratitude_input = ft.TextField(label="Enter something positive today", width=350)
    gratitude_list = ft.Column()

    def add_gratitude(e):
        if gratitude_input.value:
            entry_text = gratitude_input.value
            gratitude_list.controls.append(
                ft.Text(f"- {entry_text} ({datetime.date.today().isoformat()})")
            )
            gratitude_input.value = ""
            page.update()

    gratitude_button = ft.ElevatedButton("Add Gratitude", on_click=add_gratitude)

    # --- Daily Reminder using Timer ---
    # For demonstration purposes, the timer is set to trigger every 60 seconds.
    # For daily reminders, change the interval to 86400 seconds (24 hours).
    def send_daily_reminder(e):
        page.snack_bar = ft.SnackBar(ft.Text("Don't forget to log your gratitude for today!"))
        page.snack_bar.open = True
        page.update()

    daily_timer = ft.Timer(interval=60, on_tick=send_daily_reminder)
    page.add_timer(daily_timer)

    # --- Main App Layout ---
    main_view = ft.Column(
        [
            ft.Text("Positivity Roadmap", size=28, weight="bold"),
            dark_mode_switch,
            ft.Divider(),
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
    page.add(main_view)
    page.update()

ft.app(target=main, port=8550)
