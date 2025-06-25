import flet as ft
import os
import json
import flet
import shutil
from datetime import datetime

def load_projects_metadata(projects_dir):
    projects = []
    for project_name in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, project_name)
        metadata_path = os.path.join(project_path, "metadata.mfe")
        if os.path.isdir(project_path) and os.path.isfile(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                try:
                    metadata = json.load(f)
                    metadata["__folder"] = project_name  # フォルダ名も保持
                    projects.append(metadata)
                except Exception as e:
                    print(f"Error reading {metadata_path}: {e}")
    return projects

def save_metadata(project_dir, metadata):
    metadata_path = os.path.join(project_dir, "metadata.mfe")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def main(page: ft.Page):
    page.title = "MidFall Exproler"
    page.theme_mode = ft.ThemeMode.DARK

    projects_dir = os.path.join(os.getcwd(), "Projects")
    author = "finou"

    # プロジェクト一覧を表示するColumnを作成
    projects_column = ft.Column(
        controls=[],
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.START,
    )

    def make_project_row(project):
        return ft.Container(
            content=ft.Row([
                ft.Text(project.get('name', ''), size=18, weight=ft.FontWeight.BOLD),
                ft.Text(project.get('updated_at', ''), size=14, color=ft.Colors.GREY_400),
                ft.IconButton(ft.Icons.EDIT, tooltip="リネーム", on_click=lambda e: rename_project_dialog(project)),
                ft.IconButton(ft.Icons.DELETE, tooltip="削除", on_click=lambda e: delete_project(project)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            bgcolor=ft.Colors.BLUE_800,
            border_radius=8,
            margin=ft.margin.only(right=12),
            width=page.width - 230 if page.width else 400,
            height=48,
        )

    def refresh_projects():
        projects = load_projects_metadata(projects_dir)
        projects_column.controls.clear()
        for project in projects:
            projects_column.controls.append(make_project_row(project))
        update_project_width()
        page.update()

    def add_project_dialog(e):
        tags = load_tags()
        name_field = ft.TextField(label="プロジェクト名")
        desc_field = ft.TextField(label="説明")
        tag_checks = [ft.Checkbox(label=tag) for tag in tags]
        error_text = ft.Text("", color=ft.Colors.RED)
        def on_create(_):
            name = name_field.value.strip()
            desc = desc_field.value.strip()
            selected_tags = [cb.label for cb in tag_checks if cb.value]
            if not name:
                error_text.value = "プロジェクト名を入力してください"
                page.update()
                return
            project_path = os.path.join(projects_dir, name)
            if os.path.exists(project_path):
                error_text.value = "同じ名前のプロジェクトが既に存在します"
                page.update()
                return
            now = datetime.now().strftime("%Y-%m-%d")
            os.makedirs(project_path)
            metadata = {
                "name": name,
                "description": desc,
                "created_at": now,
                "updated_at": now,
                "author": author,
                "tags": selected_tags,
            }
            save_metadata(project_path, metadata)
            dlg.open = False
            page.update()
            refresh_projects()
        dlg = ft.AlertDialog(
            title=ft.Text("新規プロジェクト作成"),
            content=ft.Column([name_field, desc_field, ft.Text("タグ"), *tag_checks, error_text]),
            actions=[
                ft.TextButton("作成", on_click=on_create),
                ft.TextButton("キャンセル", on_click=lambda e: close_dialog(dlg))
            ]
        )
        dlg.open = True
        page.open(dlg)
        page.update()

    def close_dialog(dlg):
        dlg.open = False
        page.update()

    def create_project(name, desc, dlg):
        # 使わない（add_project_dialog内で完結）

        pass

    def delete_project(project):
        project_path = os.path.join(projects_dir, project["__folder"])
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        refresh_projects()

    def rename_project_dialog(project):
        tags = load_tags()
        name_field = ft.TextField(label="新しいプロジェクト名", value=project["name"])
        tag_checks = [ft.Checkbox(label=tag, value=tag in project.get("tags", [])) for tag in tags]
        error_text = ft.Text("", color=ft.Colors.RED)
        def on_rename(_):
            new_name = name_field.value.strip()
            selected_tags = [cb.label for cb in tag_checks if cb.value]
            if not new_name or new_name == project["name"]:
                error_text.value = "新しい名前を入力してください"
                page.update()
                return
            new_path = os.path.join(projects_dir, new_name)
            if os.path.exists(new_path):
                error_text.value = "同じ名前のプロジェクトが既に存在します"
                page.update()
                return
            old_path = os.path.join(projects_dir, project["__folder"])
            now = datetime.now().strftime("%Y-%m-%d")
            os.rename(old_path, new_path)
            metadata_path = os.path.join(new_path, "metadata.mfe")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    data["name"] = new_name
                    data["updated_at"] = now
                    data["tags"] = selected_tags
                    f.seek(0)
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    f.truncate()
            dlg.open = False
            page.update()
            refresh_projects()
        dlg = ft.AlertDialog(
            title=ft.Text("プロジェクト名変更"),
            content=ft.Column([name_field, ft.Text("タグ"), *tag_checks, error_text]),
            actions=[
                ft.TextButton("変更", on_click=on_rename),
                ft.TextButton("キャンセル", on_click=lambda e: close_dialog(dlg))
            ]
        )
        dlg.open = True
        page.open(dlg)
        page.update()

    def rename_project(project, new_name, dlg):
        # 使わない（rename_project_dialog内で完結）
        pass

    def update_project_width(e=None):
        width = page.width - 230 if page.width else 400
        for row in projects_column.controls:
            row.width = width
        page.update()

    def tag_manage_dialog(e):
        tags = load_tags()
        tag_field = ft.TextField(label="新しいタグ名")
        error_text = ft.Text("", color=ft.Colors.RED)
        tag_list = ft.Column()

        def refresh_tag_list():
            tag_list.controls.clear()
            for t in tags:
                tag_name = ft.Text(t)
                rename_field = ft.TextField(value=t, visible=False)
                def show_rename(tf=rename_field, tn=tag_name):
                    tf.visible = True
                    tn.visible = False
                    page.update()
                def do_rename(tf=rename_field, tn=tag_name, old=t):
                    new_tag = tf.value.strip()
                    if not new_tag or new_tag in tags:
                        error_text.value = "タグ名が空か重複しています"
                        page.update()
                        return
                    idx = tags.index(old)
                    tags[idx] = new_tag
                    save_tags(tags)
                    refresh_tag_list()
                    error_text.value = ""
                    page.update()
                tag_row = ft.Row([
                    tag_name,
                    rename_field,
                    ft.IconButton(ft.Icons.EDIT, tooltip="リネーム", on_click=lambda e, tf=rename_field, tn=tag_name: show_rename(tf, tn)),
                    ft.IconButton(ft.Icons.DELETE, tooltip="削除", on_click=lambda e, tag=t: remove_tag(tag)),
                    ft.TextButton("OK", visible=False, on_click=lambda e, tf=rename_field, tn=tag_name, old=t: do_rename(tf, tn, old))
                ])
                # rename_fieldのon_submitでdo_renameを呼ぶ
                rename_field.on_submit = lambda e, tf=rename_field, tn=tag_name, old=t: do_rename(tf, tn, old)
                tag_list.controls.append(tag_row)
            page.update()

        def add_tag(_):
            new_tag = tag_field.value.strip()
            if not new_tag or new_tag in tags:
                error_text.value = "タグ名が空か重複しています"
                page.update()
                return
            tags.append(new_tag)
            save_tags(tags)
            tag_field.value = ""
            error_text.value = ""
            refresh_tag_list()
            page.update()

        def remove_tag(tag):
            tags.remove(tag)
            save_tags(tags)
            refresh_tag_list()
            page.update()

        refresh_tag_list()

        dlg = ft.AlertDialog(
            title=ft.Text("タグ管理"),
            content=ft.Column([tag_field, ft.TextButton("追加", on_click=add_tag), error_text, tag_list]),
            actions=[ft.TextButton("閉じる", on_click=lambda e: close_dialog(dlg))]
        )
        page.open(dlg)
        dlg.open = True
        page.update()

    def load_tags():
        tags_path = os.path.join(projects_dir, "tags.json")
        if os.path.exists(tags_path):
            with open(tags_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_tags(tags):
        tags_path = os.path.join(projects_dir, "tags.json")
        with open(tags_path, "w", encoding="utf-8") as f:
            json.dump(tags, f, ensure_ascii=False, indent=2)

    # サイドバー
    sidebar = ft.Container(
        width=200,
        bgcolor=ft.Colors.BLUE_900,
        padding=20,
        content=ft.Column([
            ft.Text("サイドバー", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Divider(),
            ft.TextButton("新規プロジェクト作成", icon=ft.Icons.ADD, on_click=add_project_dialog),
            ft.TextButton("タグ管理", icon=ft.Icons.LABEL, on_click=tag_manage_dialog),  # ←追加
            ft.Text("メニュー1", color=ft.Colors.WHITE),
            ft.Text("メニュー2", color=ft.Colors.WHITE),
        ])
    )

    # メニューバー
    menu_bar = ft.AppBar(
        title=ft.Text("MidFall Exproler"),
        bgcolor=ft.Colors.BLUE_900,
        actions=[
            ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: refresh_projects()),
            ft.IconButton(ft.Icons.SETTINGS),
        ]
    )

    # 初期表示
    refresh_projects()

    # ウィンドウサイズ変更時に幅を更新
    page.on_resize = update_project_width

    page.add(
        menu_bar,
        ft.Row([
            sidebar,
            ft.Container(
                content=projects_column,
                padding=20,
                expand=True,
            )
        ])
    )

ft.app(target=main)