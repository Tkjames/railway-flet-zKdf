import logging
import flet as ft
from datetime import datetime, timedelta
import random


class SchedulerApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.selected_slots = {}  # Store slots as {(day, time): [users, ...]}
        self.users = []  # List of user names
        self.user_colors = {}  # Map user names to colors
        self.filling_enabled = False  # Track whether filling on hover is enabled
        self.current_user = None  # User currently making a selection

    def build(self):
        today = datetime.today()

        # Get the start day (current weekday) using weekday() function (0=Monday, 6=Sunday)
        start_day = today.weekday()  # Monday = 0, Sunday = 6

        # Days of the week (ordered to match the typical calendar week)
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Calculate the dates for the next 14 days based on today's date (2 weeks view)
        self.dates = [(today + timedelta(days=(i - start_day))).strftime("%b %d") for i in range(14)]

        # Input area for new users
        self.user_input = ft.TextField(label="Enter User Name")
        self.add_user_button = ft.ElevatedButton("Add User", on_click=self.add_user)
        self.user_list = ft.Row(spacing=10)  # Dynamic row for user names

        # Create the weekly scheduler grid
        self.grid = ft.Column(spacing=0)

        # Add day headers with scrolling
        header_row = ft.Row(spacing=0, scroll="horizontal")  # Allow horizontal scrolling
        header_row.controls.append(ft.Container(width=50, height=50))  # Blank corner for alignment

        # Update day headers to align with the correct starting day
        for i, day in enumerate(self.days):
            header_row.controls.append(
                ft.Container(
                    content=ft.Text(f"{day}\n{self.dates[i]}", size=10, weight="bold"),
                    bgcolor="gray" if self.is_past_date(self.dates[i]) else "lightblue",
                    width=100,
                    height=50,
                    alignment=ft.alignment.center,
                )
            )

        # Make header row scrollable horizontally
        self.grid.controls.append(header_row)

        # Add time rows and slots with scrolling for both directions
        self.times = [f"{hour}:00" for hour in range(24)]
        grid_container = ft.Column()  # Container for the grid rows (with scroll)

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
            for i, day in enumerate(self.days):
                slot = ft.Container(
                    bgcolor="white",
                    border=ft.border.all(1, "lightgray"),
                    width=100,
                    height=50,
                    on_hover=self.on_hover,
                    on_click=self.on_click,
                    data=(self.dates[i], time),  # Attach slot info
                )
                time_row.controls.append(slot)

            grid_container.controls.append(time_row)

        # Make the grid container scrollable vertically using Column with scroll="vertical"
        grid_container = ft.Column(
            controls=grid_container.controls,
            scroll="vertical"  # Allow vertical scrolling
        )
        self.grid.controls.append(grid_container)

        return ft.Column(
            [
                ft.Text("Weekly Scheduler", size=20, weight="bold"),
                ft.Row([self.user_input, self.add_user_button], spacing=10),
                self.user_list,
                self.grid,
            ]
        )

    def is_past_date(self, date_str):
        """Return True if the given date is in the past."""
        today = datetime.today()
        date = datetime.strptime(date_str, "%b %d")
        if date < today:
            return True
        return False

    def add_user(self, e: ft.ControlEvent):
        """Add a new user with a unique color and auto switch to them."""
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
                    style=ft.ButtonStyle(
                        bgcolor=user_color,  # Set background color
                        color="white"  # Set text color
                    ),
                    data=user_name
                )
            )
            self.user_list.update()
            self.user_input.value = ""  # Clear the input field after adding user
            self.user_input.update()  # Ensure the field visually updates

            # **Automatically set the new user as the current user**
            self.current_user = user_name
            logging.info(f"Current user set to: {self.current_user}")

        else:
            logging.warning("Invalid user name or user already exists")

    def set_current_user(self, e: ft.ControlEvent):
        """Set the current user for slot selection."""
        self.current_user = e.control.data
        logging.info(f"User switched to: {self.current_user}")

    def on_hover(self, e: ft.HoverEvent):
        """Handle hover events for slot selection, only if filling is enabled."""
        if self.filling_enabled and self.current_user:  # Only fill if filling is enabled
            self.update_slot(e)

    def on_click(self, e: ft.TapEvent):
        """Toggle filling behavior on second click."""
        if not self.current_user:  # Prevent filling if no user is set
            logging.warning("No user selected!")
            return

        # Toggle the filling behavior on each click
        self.filling_enabled = not self.filling_enabled
        if self.filling_enabled:
            logging.info("Filling started on hover.")
            self.update_slot(e)  # Immediately update the clicked slot
        else:
            logging.info("Filling stopped on hover.")

    def update_slot(self, e):
        """Update the slot for selection."""
        slot = e.control.data
        if slot not in self.selected_slots.get(self.current_user, []):  # Avoid duplicate selection
            self.selected_slots[self.current_user].append(slot)
            self.update_slot_visual(e.control, self.current_user)
            logging.info(f"Slot {slot} selected for user {self.current_user}")

    def update_slot_visual(self, slot_container, user):
        """Update the visual representation of a slot based on user selection."""
        day, time = slot_container.data  # Extract the day and time from slot data
        selected_users = self.get_users_for_slot(day, time)
        num_users = len(selected_users)

        # Remove any existing content in the slot container
        slot_container.bgcolor = "white"  # Reset slot background color

        # Ensure that the colors are not clipped and are evenly distributed across the slot
        overlapping_width = 100 / num_users  # Calculate the width each color segment should take

        # Prepare a list of colors for the overlapping users
        user_colors = [self.user_colors[user] for user in selected_users]
        color_segments = []

        # Create overlapping segments without any margin or space
        for idx, color in enumerate(user_colors):
            color_segments.append(
                ft.Container(
                    bgcolor=color,
                    width=overlapping_width,  # Each color takes up equal width
                    height=50,
                    alignment=ft.alignment.center,
                    content=ft.Text(selected_users[idx][0], size=10, color="white")  # Use the first letter as a label
                )
            )

        # Set the content of the slot container to hold all overlapping color segments
        slot_container.content = ft.Row(
            color_segments,
            alignment=ft.alignment.center,  # Ensure segments are centered, no extra space
            spacing=0,  # No space between segments
        )
        slot_container.update()

    def get_users_for_slot(self, day, time):
        """Return the list of users that have selected a given slot."""
        users_in_slot = []
        for user, slots in self.selected_slots.items():
            if (day, time) in slots:
                users_in_slot.append(user)
        return users_in_slot


# Run the app
def main(page: ft.Page):
    page.add(SchedulerApp())


logging.basicConfig(level=logging.INFO)

ft.app(target=main, view=None, port=int(os.getenv("PORT", 8502)))
