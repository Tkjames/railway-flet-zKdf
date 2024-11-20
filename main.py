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
        self.user_list = ft.Row()  # Dynamic row for user names

        # Create the weekly scheduler grid
        self.grid = ft.Column()

        # Add day and date headers
        header_row = ft.Row(spacing=1)
        for i, day in enumerate(self.days):
            header_row.controls.append(
                ft.Container(
                    content=ft.Text(f"{day}\n{self.dates[i]}"),
                    bgcolor="lightgray",
                    width=100,
                    height=50,
                    padding=5,
                    alignment=ft.alignment.center,
                )
            )
        self.grid.controls.append(header_row)

        # Add time rows
        self.times = [f"{hour}:00" for hour in range(24)]
        for time in self.times:
            time_row = ft.Row(spacing=1)
            for day in self.days:
                slot = ft.Container(
                    content=ft.Column([ft.Text(time, size=10)], spacing=0),
                    bgcolor="white",
                    border=ft.border.all(1, "lightgray"),
                    width=100,
                    height=50,
                    padding=5,
                    on_hover=self.on_hover,
                    on_click=self.on_click,
                    data=(day, time)  # Tag slot with coordinates
                )
                time_row.controls.append(slot)
            self.grid.controls.append(time_row)

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
                ft.Text(f"{user_name} (color)", color=user_color)
            )
            self.user_list.update()
            self.user_input.value = ""  # Clear the input field
            self.user_input.update()  # Ensure the field visually updates

            # Automatically set the first user as the current user
            if len(self.users) == 1:
                self.current_user = user_name

    def on_hover(self, e: ft.HoverEvent):
        """Handle hover events for drag-selecting slots."""
        if self.is_dragging and self.current_user:
            slot = e.control.data
            if slot not in self.selected_slots[self.current_user]:
                self.selected_slots[self.current_user].append(slot)
                self.update_slot_visual(e.control, self.current_user)

    def on_click(self, e: ft.TapEvent):
        """Toggle drag state and select slots on click."""
        if not self.current_user:  # Prevent selection if no user is set
            return
        if e.control.data:
            self.is_dragging = not self.is_dragging  # Toggle dragging state
            slot = e.control.data
            if self.is_dragging:  # Starting selection
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
