import flet as ft
import os
import json

def load_projects_metadata(projects_dir):
    projects = []
    for project_name in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, project_name)
        metadata_path = os.path.join(project_path, "metadata.json")
        if os.path.isdir(project_path) and os.path.isfile(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                try:
                    metadata = json.load(f)
                    projects.append(metadata)
                except Exception as e:
                    print(f"Error reading {metadata_path}: {e}")
    return projects

def main(page: ft.Page):
    page.title = "MidFall Exproler"
    page.theme_mode = ft.ThemeMode.DARK

    # メニューバー
    menu_bar = ft.AppBar(
        title=ft.Text("MidFall Exproler"),
        bgcolor=ft.Colors.BLUE_900,
        actions=[
            ft.IconButton(ft.Icons.REFRESH),
            ft.IconButton(ft.Icons.SETTINGS),
        ]
    )

    projects_dir = os.path.join(os.getcwd(), "Projects")
    projects = load_projects_metadata(projects_dir)

    # Finder風 横並びリスト（1行で横スクロール）
    project_rows = []
    for project in projects:
        row = ft.Container(
            content=ft.Row([
                ft.Text(project.get('name', ''), size=18, weight=ft.FontWeight.BOLD),
                ft.Text(project.get('updated_at', ''), size=14, color=ft.Colors.GREY_400),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            bgcolor=ft.Colors.BLUE_800,
            border_radius=8,
            margin=ft.margin.only(right=12),
            width=280,
            height=48,
        )
        project_rows.append(row)

    page.add(
        menu_bar,
        ft.Container(
            content=ft.Row(
                controls=project_rows,
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=20,
            expand=True,
        )
    )

ft.app(target=main)