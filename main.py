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
        self.user_input = ft.TextField(label="Enter User Name")
        self.add_user_button = ft.ElevatedButton("Add User", on_click=self.add_user)
        self.user_list = ft.Row(spacing=10)  # Dynamic row for user names

        # Create the weekly scheduler grid
        self.grid = ft.Column(spacing=0)

        # Add day headers
        header_row = ft.Row(spacing=0)
        header_row.controls.append(ft.Container(width=50, height=50))  # Blank corner for alignment
        for i, day in enumerate(self.days):
            header_row.controls.append(
                ft.Container(
                    content=ft.Text(f"{day}\n{self.dates[i]}", size=10, weight="bold"),
                    bgcolor="gray",
                    width=100,
                    height=50,
                    alignment=ft.alignment.center,
                )
            )
        self.grid.controls.append(header_row)

        # Add time rows and slots
        self.times = [f"{hour}:00" for hour in range(24)]
        for time in self.times:
            time_row = ft.Row(spacing=0)
            # Add time labels on the left
            time_row.controls.append(
                ft.Container(
                    content=ft.Text(time, size=10),
                    bgcolor="white",
                    width=50,
                    height=50,
                    alignment=ft.alignment.center,
                )
            )
            # Add slots for each day
            for day in self.days:
                slot = ft.Container(
                    bgcolor="white",
                    border=ft.border.all(1, "lightgray"),
                    width=100,
                    height=50,
                    on_hover=self.on_hover,
                    on_click=self.on_click,
                    data=(day, time),  # Attach slot info
                )
                time_row.controls.append(slot)
            self.grid.controls.append(time_row)

        return ft.Column(
            [
                ft.Text("Weekly Scheduler", size=20, weight="bold"),
                ft.Row([self.user_input, self.add_user_button], spacing=10),
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
            logging.info(f"Assigning color {user_color} to user {user_name}")
            
            self.users.append(user_name)
            self.user_colors[user_name] = user_color
            self.selected_slots[user_name] = []  # Initialize selection storage

            # Update the UI with the new user
            self.user_list.controls.append(
                ft.TextButton(
                    text=user_name,
                    on_click=self.set_current_user,
                    bgcolor=user_color,
                    color="white",
                    data=user_name
                )
            )
            self.user_list.update()
            self.user_input.value = ""  # Clear the input field after adding user
            self.user_input.update()  # Ensure the field visually updates

            # Automatically set the first user as the current user
            if len(self.users) == 1:
                self.current_user = user_name
                logging.info(f"Current user set to: {self.current_user}")
        else:
            logging.warning("Invalid user name or user already exists")

    def set_current_user(self, e: ft.ControlEvent):
        """Set the current user for slot selection."""
        self.current_user = e.control.data
        logging.info(f"User switched to: {self.current_user}")

    def on_hover(self, e: ft.HoverEvent):
        """Handle hover events for drag-selecting slots."""
        if self.is_dragging and self.current_user:
            self.update_slot(e)

    def on_click(self, e: ft.TapEvent):
        """Toggle drag state and select slots on click."""
        if not self.current_user:  # Prevent selection if no user is set
            logging.warning("No user selected!")
            return
        self.is_dragging = not self.is_dragging  # Toggle dragging state
        logging.info(f"Dragging state set to: {self.is_dragging}")
        if e.control.data:
            self.update_slot(e)

    def update_slot(self, e):
        """Update the slot for selection."""
        slot = e.control.data
        if slot not in self.selected_slots[self.current_user]:
            self.selected_slots[self.current_user].append(slot)
            self.update_slot_visual(e.control, self.current_user)
            logging.info(f"Slot {slot} selected for user {self.current_user}")

    def update_slot_visual(self, slot_container, user):
        """Update the visual representation of a slot based on user selection."""
        user_color = self.user_colors[user]
        slot_container.bgcolor = user_color
        slot_container.update()


def main(page: ft.Page):
    page.title = "Weekly Scheduler with User Overlap"
    scheduler = SchedulerApp()
    page.add(scheduler)


logging.basicConfig(level=logging.INFO)

ft.app(target=main, view=None, port=int(os.getenv("PORT", 8502)))
