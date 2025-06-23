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
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            on_primary=ft.Colors.WHITE,
            secondary=ft.Colors.GREEN,
            on_secondary=ft.Colors.BLACK
        )
    )

    projects_dir = os.path.join(os.getcwd(), "Projects")
    projects = load_projects_metadata(projects_dir)

    project_cards = []
    for project in projects:
        card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"名前: {project.get('name', '')}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"説明: {project.get('description', '')}"),
                    ft.Text(f"作成日: {project.get('created_at', '')}"),
                    ft.Text(f"更新日: {project.get('updated_at', '')}"),
                    ft.Text(f"作者: {project.get('author', '')}"),
                ]),
                padding=20,
            ),
            elevation=4,
            margin=10,
        )
        project_cards.append(card)

    page.add(
        ft.Column(
            controls=project_cards,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

ft.app(target=main)