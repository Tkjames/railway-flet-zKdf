import logging
import flet as ft
import os

class SchedulerApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.selected_slots = set()  # Store selected slots as (day, time) tuples
        self.is_dragging = False  # Track drag state

    def build(self):
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.times = [f"{hour}:00" for hour in range(24)]  # 24-hour format
        
        # Create a grid layout
        calendar_grid = ft.Column()
        for time in self.times:
            row = ft.Row(spacing=1)
            for day in self.days:
                slot = ft.Container(
                    content=ft.Text(f"{day[:3]} {time}"),
                    bgcolor="white",
                    border=ft.border.all(1, "lightgray"),
                    width=100,
                    height=50,
                    padding=5,
                    on_hover=self.on_hover,
                    on_click=self.on_click,
                    data=(day, time)  # Tag the slot with its coordinates
                )
                row.controls.append(slot)
            calendar_grid.controls.append(row)
        
        return ft.Column([ft.Text("Weekly Scheduler"), calendar_grid])

    def on_hover(self, e: ft.HoverEvent):
        """Handle hover events for drag-selecting slots."""
        if self.is_dragging and e.control.data not in self.selected_slots:
            e.control.bgcolor = "lightblue"
            self.selected_slots.add(e.control.data)
            e.control.update()

    def on_click(self, e: ft.TapEvent):
        """Toggle drag state and select slots on click."""
        self.is_dragging = not self.is_dragging
        slot = e.control.data
        if self.is_dragging:  # Starting selection
            e.control.bgcolor = "lightblue"
            self.selected_slots.add(slot)
        else:  # Ending selection
            pass  # Dragging logic ends here
        e.control.update()


def main(page: ft.Page):
    page.title = "Weekly Scheduler"
    scheduler = SchedulerApp()
    page.add(scheduler)

logging.basicConfig(level=logging.INFO)

ft.app(target=main, view=None, port=int(os.getenv("PORT", 8502)))
