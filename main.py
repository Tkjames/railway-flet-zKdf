import logging
import flet as ft
import os

from datetime import datetime, timedelta
import random


class SchedulerApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.selected_slots = {}  # Store slots as {user: [(day, time), ...]}
        self.users = []  # List of user names
        self.user_colors = {}  # Map user names to colors
        self.is_dragging = False  # Track drag state
        self.current_user = None  # User currently making a selection

    def build(self):
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today = datetime.today()
        self.dates = [(today + timedelta(days=i)).strftime("%b %d") for i in range(7)]  # Next 7 days

        # Input area for new users
        self.user_input = ft.TextField(label="Enter User Name", on_submit=self.add_user)
        self.user_list = ft.Row(spacing=10)  # Dynamic row for user names

        # Create the weekly scheduler grid
        self.grid = ft.Column(spacing=0)

        # Add the time labels column and day headers
        time_labels_col = ft.Column(spacing=1, width=50)  # Fixed width for time labels
        header_row = ft.Row(spacing=1, height=50)

        # Add a placeholder for the top-left corner
        time_labels_col.controls.append(ft.Container(width=50, height=50, bgcolor="white"))

        # Add day and date headers
        for i, day in enumerate(self.days):
            header_row.controls.append(
                ft.Container(
                    content=ft.Text(f"{day}\n{self.dates[i]}", size=10),
                    bgcolor="lightgray",
                    width=80,
                    height=50,
                    alignment=ft.alignment.center,
                )
            )

        self.grid.controls.append(ft.Row([time_labels_col, header_row]))

        # Add time rows
        self.times = [f"{hour}:00" for hour in range(24)]
        for time in self.times:
            time_row = ft.Row(spacing=1, height=30)
            time_labels_col.controls.append(
                ft.Container(
                    content=ft.Text(time, size=10),
                    bgcolor="white",
                    width=50,
                    height=30,
                    alignment=ft.alignment.center,
                )
            )

            for day in self.days:
                slot = ft.Container(
                    content=ft.Row([], spacing=0),
                    bgcolor="white",
                    border=ft.border.all(1, "lightgray"),
                    width=80,
                    height=30,
                    padding=1,
                    on_hover=self.on_hover,
                    on_click=self.on_click,
                    data=(day, time)  # Tag slot with coordinates
                )
                time_row.controls.append(slot)
            self.grid.controls.append(ft.Row([time_labels_col.controls[-1], time_row]))

        return ft.Column(
            [
                ft.Text("Weekly Scheduler", size=20, weight="bold"),
                self.user_input,
                self.user_list,
                self.grid,
            ]
        )

    def add_user(self, e: ft.ControlEvent):
        """Add a new user with a unique color."""
        user_name = self.user_input.value.strip()
        if user_name and user_name not in self.users:
            # Assign a unique random color
            user_color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            self.users.append(user_name)
            self.user_colors[user_name] = user_color
            self.selected_slots[user_name] = []  # Initialize selection storage

            # Update the UI with the new user
            self.user_list.controls.append(
                ft.TextButton(
                    text=f"{user_name} (color)",
                    on_click=self.set_current_user,
                    bgcolor=user_color,
                    color="white",
                    data=user_name
                )
            )
            self.user_list.update()
            self.user_input.value = ""  # Clear the input field
            self.user_input.update()  # Ensure the field visually updates

            # Automatically set the first user as the current user
            if len(self.users) == 1:
                self.current_user = user_name

    def set_current_user(self, e: ft.ControlEvent):
        """Set the current user for slot selection."""
        self.current_user = e.control.data

    def on_hover(self, e: ft.HoverEvent):
        """Handle hover events for drag-selecting slots."""
        if self.is_dragging and self.current_user:
            self.update_slot(e)

    def on_click(self, e: ft.TapEvent):
        """Toggle drag state and select slots on click."""
        if not self.current_user:  # Prevent selection if no user is set
            return
        self.is_dragging = not self.is_dragging  # Toggle dragging state
        if e.control.data:
            self.update_slot(e)

    def update_slot(self, e):
        """Update the slot for selection."""
        slot = e.control.data
        if slot not in self.selected_slots[self.current_user]:
            self.selected_slots[self.current_user].append(slot)
            self.update_slot_visual(e.control, self.current_user)

    def update_slot_visual(self, slot_container, user):
        """Update the visual representation of a slot based on user selection."""
        user_color = self.user_colors[user]
        slot_content = slot_container.content

        # Add a sub-cell with the user's color
        slot_content.controls.append(
            ft.Container(
                bgcolor=user_color,
                width=slot_container.width / len(self.users),
                height=slot_container.height,
                alignment=ft.alignment.center,
            )
        )
        slot_content.update()


def main(page: ft.Page):
    page.title = "Weekly Scheduler with User Overlap"
    scheduler = SchedulerApp()
    page.add(scheduler)


logging.basicConfig(level=logging.INFO)

ft.app(target=main, view=None, port=int(os.getenv("PORT", 8502)))
