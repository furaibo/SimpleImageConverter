import time
import flet as ft
from pathlib import Path
from flet.core.file_picker import FilePickerFileType
from flet.core.textfield import NumbersOnlyInputFilter

from image import convert_image_file


# main関数
def main(page: ft.Page):
    # タイトル設定
    page.title = "シンプル画像変換"
    page.appbar = ft.AppBar(title=ft.Text("シンプル画像変換"))

    # サイズ指定
    page.window.width = 1000
    page.window.height = 800
    page.window.min_width = 500
    page.window.min_height = 400

    # デフォルト保存パスの設定
    home_path = Path.home()
    folder_name = "SimpleImageConverter"
    save_dir_path = home_path.joinpath("Pictures", folder_name)

    # 保存先フォルダの作成
    if not save_dir_path.exists():
        save_dir_path.mkdir(parents=True)

    # 画像形式
    allowed_extensions_list = ["jpg", "png", "svg", "gif", "bmp", "tiff"]

    #
    # 各種イベントの定義
    #

    def event_switch_size_limit_disabled(value: bool):
        text_field_size_limit_width.disabled = value
        text_field_size_limit_height.disabled = value
        text_field_size_limit_width.update()
        text_field_size_limit_height.update()

    def event_switch_convert_ext_disabled(value: bool):
        drop_down_image_ext.disabled = value
        drop_down_image_ext.update()
        event_check_start_button_enabled()

    def event_switch_file_name_prefix_disabled(value: bool):
        text_field_file_name_prefix.disabled = value
        text_field_file_name_prefix.update()

    def event_remove_input_file(e):
        target_key = e.control.data

        # 該当データ行の検索と削除
        for i, row in enumerate(data_table_input_files.rows):
            if row.data == target_key:
                # 行の削除とボタンの不活化処理
                data_table_input_files.rows.pop(i)
                data_table_input_files.update()
                if len(data_table_input_files.rows) == 0:
                    button_image_conversion_start.disabled = True
                    button_image_conversion_start.update()
                break

    def event_get_directory_result(e: ft.FilePickerResultEvent):
        if e.path:
            text_field_save_path.value = e.path
            text_field_save_path.update()
        else:
            print("get directory canceled!")

    def event_get_input_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                # データテーブルへの行追加
                row = ft.DataRow(
                    data=f.path,
                    cells=[
                        ft.DataCell(ft.Text(f.name)),
                        ft.DataCell(ft.Text(Path(f.path).suffix)),
                        ft.DataCell(ft.Text(f.size)),
                        ft.DataCell(ft.OutlinedButton(
                            text="削除",
                            data=f.path,    # ファイルパスを値として保持
                            on_click=lambda e2:
                                event_remove_input_file(e2)))
                    ]
                )
                data_table_input_files.rows.append(row)
                data_table_input_files.update()

                # ボタンの有効化判定
                event_check_start_button_enabled()

        else:
            print("get files canceled!")

    def event_check_start_button_enabled():
        # 各入力の状態チェック
        selected_ext = drop_down_image_ext.value
        ext_disabled = checkbox_cancel_ext_convert.value
        ext_allowed = selected_ext in allowed_extensions_list
        file_not_empty = len(data_table_input_files.rows) > 0

        # 論理計算
        button_enabled = (
                (ext_disabled or ext_allowed) and file_not_empty)
        button_image_conversion_start.disabled = not button_enabled
        button_image_conversion_start.update()

    def event_exec_image_conversion():
        # 入力済みファイルパスを取得
        input_files = []
        for row in data_table_input_files.rows:
            input_files.append(row.data)

        # ファイル数の取得
        input_files_count = len(input_files)

        # 保存時の拡張子を取得
        save_ext = drop_down_image_ext.value

        # プログレスバーの初期化
        progress_bar_conversion_status.value = 0
        progress_bar_conversion_status.visible = True

        # 変換処理の実行およびプログレスバーの更新
        for i, path in enumerate(input_files):
            # ファイル名の取得(接頭辞処理含む)
            input_path = Path(path)
            file_name = input_path.name
            if not checkbox_cancel_file_name_prefix.value:
                prefix = text_field_file_name_prefix.value
                file_name = prefix + file_name

            # ファイル保存パスの取得
            save_path = (save_dir_path.joinpath(file_name).
                         with_suffix("." + save_ext))

            # リサイズ時のリミットを取得
            size_limit = (
                int(text_field_size_limit_width.value),
                int(text_field_size_limit_height.value)
            )

            # 変換処理の実行
            convert_image_file(input_path, save_path, size_limit)

            # プログレスバーの更新
            progress_bar_conversion_status.value = i / input_files_count
            progress_bar_conversion_status.update()

        # プログレスバーを完了状態に変更
        progress_bar_conversion_status.value = 1
        progress_bar_conversion_status.update()

        # プログレスバーの不可視への変更
        time.sleep(1)
        progress_bar_conversion_status.visible = False
        progress_bar_conversion_status.update()

        # 入力済みファイルパスの消去
        data_table_input_files.rows.clear()
        data_table_input_files.update()

    #
    # 各種UIの定義
    #

    # FilePicker定義
    # Note: appendによるpage追加がないとエラー発生
    get_directory_dialog = ft.FilePicker(
        on_result=event_get_directory_result)
    get_input_files_dialog = ft.FilePicker(
        on_result=event_get_input_files_result)
    page.overlay.append(get_directory_dialog)
    page.overlay.append(get_input_files_dialog)

    # テキストフィールド定義
    text_field_save_path = ft.TextField(
        label="保存パス",
        width=500,
        value=str(save_dir_path),
        read_only=True
    )
    text_field_size_limit_width = ft.TextField(
        label="幅", width=120, value="1280",
        input_filter=NumbersOnlyInputFilter()
    )
    text_field_size_limit_height = ft.TextField(
        label="高さ",
        width=120,
        value="800",
        input_filter=NumbersOnlyInputFilter()
    )
    text_field_file_name_prefix = ft.TextField(
        label="接頭辞の文字列",
        width=270,
        value="s_"
    )

    # チェックボックス
    checkbox_cancel_ext_convert = ft.Checkbox(
        label="画像の拡張子変換をしない",
        value=False,
        on_change=lambda e:
            event_switch_convert_ext_disabled(e.control.value)
    )
    checkbox_cancel_size_convert = ft.Checkbox(
        label="画像サイズの制限をしない",
        value=False,
        on_change=lambda e:
            event_switch_size_limit_disabled(e.control.value)
    )
    checkbox_cancel_file_name_prefix = ft.Checkbox(
        label="ファイル名に接頭辞を追加しない",
        value=False,
        on_change=lambda e:
            event_switch_file_name_prefix_disabled(e.control.value)
    )

    # フォルダ選択ボタン
    button_select_save_path = ft.FilledButton(
        text="フォルダ選択",
        width=120,
        icon=ft.Icons.FOLDER,
        disabled=page.web,
        on_click=lambda _:
            get_directory_dialog.get_directory_path(
                initial_directory=str(save_dir_path))
    )
    button_add_input_files = ft.FilledButton(
        text="入力ファイル追加",
        width=150,
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _:
            get_input_files_dialog.pick_files(
                file_type=FilePickerFileType.CUSTOM,
                allowed_extensions=allowed_extensions_list,
                allow_multiple=True)
    )
    button_image_conversion_start = ft.CupertinoFilledButton(
        text="画像変換処理開始",
        width=800,
        disabled=True,
        on_click=lambda _: event_exec_image_conversion()
    )

    # ドロップダウンメニュー
    dropdown_options = []
    for ext in allowed_extensions_list:
        option_item = ft.DropdownOption(
            key=ext,
            content=ft.Text(value=ext),
        )
        dropdown_options.append(option_item)

    drop_down_image_ext = ft.Dropdown(
        label="拡張子選択",
        width=270,
        value="jpg",
        editable=False,
        options=dropdown_options,
        on_change=lambda _: event_check_start_button_enabled()
    )

    # DataTable/ListView定義
    data_table_input_files = ft.DataTable(
        width=850,
        divider_thickness=1,
        columns=[
            ft.DataColumn(ft.Text("名称")),
            ft.DataColumn(ft.Text("拡張子")),
            ft.DataColumn(ft.Text("サイズ")),
            ft.DataColumn(ft.Text("削除"))
        ],
    )
    list_view_input_files = ft.ListView(
        [data_table_input_files],
        expand=1, spacing=10, padding=20
    )

    # プログレスバー定義
    progress_bar_conversion_status = ft.ProgressBar(
        width=400, value=0, visible=False
    )

    #
    # 行の定義
    #

    row_spacer_large = ft.Row(controls=[ft.Divider(height=20)])
    row_spacer_small = ft.Row(controls=[ft.Divider(height=10)])

    row_save_path = ft.Row(
        controls=[
            ft.Text("保存パス", width=80),
            text_field_save_path,
            button_select_save_path
        ]
    )
    row_image_ext = ft.Row(
        controls=[
            ft.Text("画像形式", width=80),
            drop_down_image_ext,
            checkbox_cancel_ext_convert
        ]
    )
    row_image_size = ft.Row(
        controls=[
            ft.Text("上限サイズ", width=80),
            text_field_size_limit_width,
            ft.Text("x", width=10),
            text_field_size_limit_height,
            checkbox_cancel_size_convert
        ]
    )
    row_file_name_prefix = ft.Row(
        controls=[
            ft.Text("接頭辞", width=80),
            text_field_file_name_prefix,
            checkbox_cancel_file_name_prefix
        ]
    )
    row_input_files_selector = ft.Row(
        controls=[
            ft.Text("ファイル選択", width=80),
            button_add_input_files,
            progress_bar_conversion_status
        ]
    )
    row_input_files_list = ft.Row(
        controls=[
            ft.Container(
                content=list_view_input_files,
                height=360,
                width=900
            ),
        ]
    )
    row_image_conversion_start_button = ft.Row(
        controls=[button_image_conversion_start]
    )

    # ページへのタブ定義追加
    page.add(
        row_spacer_large,
        row_save_path,
        row_image_ext,
        row_image_size,
        row_file_name_prefix,
        row_spacer_small,
        row_input_files_selector,
        row_spacer_small,
        row_input_files_list,
        row_spacer_small,
        row_image_conversion_start_button
    )


if __name__ == "__main__":
    ft.app(target=main)
