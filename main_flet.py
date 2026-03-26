import flet as ft
import requests
from datetime import datetime
import re

API_URL = "http://127.0.0.1:8000"


def validate_password(password: str) -> tuple[bool, str]:
    """ตรวจสอบรหัสผ่าน: ต้องมี 8 ตัว, อักษรพิเศษ, และตัวเลข"""
    if len(password) < 8:
        return False, "รหัสผ่านต้องมีอย่างน้อย 8 ตัว"
    if not re.search(r"[0-9]", password):
        return False, "รหัสผ่านต้องมีตัวเลข"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "รหัสผ่านต้องมีอักษรพิเศษ (!@#$%^&* เป็นต้น)"
    return True, "ตกลง"


def main(page: ft.Page):
    page.title = "Car Log - บันทึกเลขไมล์"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 420
    page.window.height = 800
    page.bgcolor = "#F5F7FA"
    page.padding = 0

    PRIMARY         = "#1A73E8"
    PRIMARY_VARIANT = "#0D47A1"

    current_user_id = [None]
    fuel_records    = [[]]

    def show_snack(message, is_error=True):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400,
        )
        page.snack_bar.open = True
        page.update()

    # ──────────── หน้า Login ────────────
    def show_login_page():
        username = ft.TextField(
            label="Username",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            width=320,
        )
        password = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            width=320,
        )

        def do_login(e):
            try:
                res = requests.post(
                    f"{API_URL}/login",
                    json={"username": username.value, "password": password.value},
                    timeout=5,
                )
                if res.status_code == 200:
                    current_user_id[0] = res.json()["user_id"]
                    show_list_page()
                else:
                    show_snack("เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่", is_error=True)
            except Exception:
                show_snack("ไม่สามารถเชื่อมต่อ Server ได้", is_error=True)

        page.clean()
        page.add(
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.Alignment(0, -1),
                    end=ft.alignment.Alignment(0, 1),
                    colors=[PRIMARY, PRIMARY_VARIANT],
                ),
                content=ft.Column(
                    [
                        ft.Container(height=60),
                        ft.Icon(ft.Icons.DIRECTIONS_CAR_ROUNDED, size=100, color="white"),
                        ft.Text("CAR LOG", size=32, weight="bold", color="white"),
                        ft.Text("บันทึกการเติมน้ำมันและเลขไมล์", color="white70"),
                        ft.Container(height=40),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("ยินดีต้อนรับ", size=20, weight="bold", color=PRIMARY),
                                    username,
                                    password,
                                    ft.Container(height=10),
                                    ft.Button(
                                        content=ft.Text("LOG IN"),
                                        on_click=do_login,
                                        width=320,
                                        height=50,
                                        style=ft.ButtonStyle(
                                            bgcolor=PRIMARY,
                                            color="white",
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                        ),
                                    ),
                                    ft.Container(height=15),
                                    ft.Row([
                                        ft.Text("ยังไม่มีบัญชี?", color="gray"),
                                        ft.TextButton(
                                            content=ft.Text("สมัครสมาชิก"),
                                            on_click=lambda _: show_register_page(),
                                        ),
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            bgcolor="white",
                            padding=30,
                            border_radius=30,
                            shadow=ft.BoxShadow(blur_radius=20, color="black26"),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        )
        page.update()

    # ──────────── หน้า Register ────────────
    def show_register_page():
        username = ft.TextField(
            label="Username",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            width=320,
        )
        password = ft.TextField(
            label="Password (ต้องมี 8+ ตัว, ตัวเลข, อักษรพิเศษ)",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            width=320,
        )
        confirm_password = ft.TextField(
            label="ยืนยันรหัสผ่าน",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            width=320,
        )

        def do_register(e):
            try:
                # ตรวจสอบการกรอก
                if not username.value or not password.value or not confirm_password.value:
                    show_snack("กรุณากรอกข้อมูลให้ครบถ้วน", is_error=True)
                    return

                # ตรวจสอบรหัสผ่านตรงกัน
                if password.value != confirm_password.value:
                    show_snack("รหัสผ่านไม่ตรงกัน", is_error=True)
                    return

                # ตรวจสอบความแข็งแกร่งของรหัสผ่าน
                is_valid, message = validate_password(password.value)
                if not is_valid:
                    show_snack(message, is_error=True)
                    return

                # ส่งคำขอ register ไปยัง API
                res = requests.post(
                    f"{API_URL}/register",
                    json={"username": username.value, "password": password.value},
                    timeout=5,
                )

                if res.status_code == 200:
                    show_snack("สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ", is_error=False)
                    page.clean()
                    show_login_page()
                elif res.status_code == 400:
                    show_snack(res.json().get("detail", "สมัครสมาชิกไม่สำเร็จ"), is_error=True)
                else:
                    show_snack("สมัครสมาชิกไม่สำเร็จ กรุณาลองใหม่", is_error=True)
            except Exception as ex:
                show_snack("ไม่สามารถเชื่อมต่อ Server ได้", is_error=True)

        page.clean()
        page.add(
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.Alignment(0, -1),
                    end=ft.alignment.Alignment(0, 1),
                    colors=[PRIMARY, PRIMARY_VARIANT],
                ),
                content=ft.Column(
                    [
                        ft.Container(height=40),
                        ft.Icon(ft.Icons.DIRECTIONS_CAR_ROUNDED, size=80, color="white"),
                        ft.Text("สมัครสมาชิก", size=28, weight="bold", color="white"),
                        ft.Container(height=30),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("สร้างบัญชีใหม่", size=18, weight="bold", color=PRIMARY),
                                    username,
                                    password,
                                    confirm_password,
                                    ft.Container(height=10),
                                    ft.Button(
                                        content=ft.Text("สมัครสมาชิก"),
                                        on_click=do_register,
                                        width=320,
                                        height=50,
                                        style=ft.ButtonStyle(
                                            bgcolor=PRIMARY,
                                            color="white",
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                        ),
                                    ),
                                    ft.Container(height=15),
                                    ft.Row([
                                        ft.Text("มีบัญชีแล้ว?", color="gray"),
                                        ft.TextButton(
                                            content=ft.Text("เข้าสู่ระบบ"),
                                            on_click=lambda _: show_login_page(),
                                        ),
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            bgcolor="white",
                            padding=30,
                            border_radius=30,
                            shadow=ft.BoxShadow(blur_radius=20, color="black26"),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        )
        page.update()

    # ──────────── หน้า Dashboard ────────────
    def show_list_page():
        list_view           = ft.ListView(expand=True, spacing=12, padding=20)
        status_card_content = ft.Column(spacing=5)

        def load_data():
            try:
                list_view.controls.clear()
                status_res = requests.get(
                    f"{API_URL}/fuel/status/{current_user_id[0]}", timeout=5
                )
                if status_res.status_code == 200:
                    st = status_res.json()
                    
                    # กำหนดสีสำหรับการแจ้งเตือน
                    alert_color = "white"
                    if "ถึงเวลา" in st.get('alert', ''):
                        alert_color = "#FF5252"
                    elif "ควรตรวจเช็ค" in st.get('alert', ''):
                        alert_color = "#FFC107"
                    
                    status_card_content.controls = [
                        ft.Row([
                            ft.Icon(ft.Icons.SPEED, color="white70", size=20),
                            ft.Text(
                                f"เลขไมล์ล่าสุด: {st.get('last_odometer', 0):,} km",
                                color="white", size=16, weight="w600",
                            ),
                        ]),
                        ft.Row([
                            ft.Icon(ft.Icons.BUILD_CIRCLE_OUTLINED, color="white70", size=20),
                            ft.Text(
                                f"เช็คระยะถัดไป: {st.get('next_service_at', 0):,} km",
                                color="white", size=14,
                            ),
                        ]),
                        ft.Row([
                            ft.Icon(ft.Icons.DIRECTIONS_RUN, color="white70", size=20),
                            ft.Text(
                                f"ระยะที่เหลือ: {st.get('km_remaining', 0):,} km",
                                color="white", size=14,
                            ),
                        ]),
                        ft.Container(
                            padding=10,
                            bgcolor=alert_color,
                            border_radius=8,
                            content=ft.Row([
                                ft.Icon(ft.Icons.WARNING if "ถึงเวลา" in st.get('alert', '') else ft.Icons.INFO, color="white", size=18),
                                ft.Text(
                                    f"สถานะ: {st.get('alert', 'ปกติ')}",
                                    color="white", weight="bold", size=12,
                                ),
                            ]),
                        ),
                    ]

                res = requests.get(f"{API_URL}/fuel/{current_user_id[0]}", timeout=5)
                if res.status_code == 200:
                    fuel_records[0] = res.json()
                    for f in fuel_records[0]:
                        eff = f.get("efficiency")
                        eff_display = f"{eff} km/L" if eff else "ยังไม่"
                        
                        # กำหนดสี efficiency
                        eff_color = PRIMARY
                        if eff and eff > 0:
                            if eff >= 10:
                                eff_color = "#4CAF50"  # สีเขียว - ดี
                            elif eff >= 8:
                                eff_color = "#FFC107"  # สีเหลือง - พอใจ
                            else:
                                eff_color = "#FF5252"  # สีแดง - ต้องปรับปรุง
                        
                        list_view.controls.append(
                            ft.Container(
                                content=ft.ListTile(
                                    leading=ft.Container(
                                        content=ft.Icon(ft.Icons.LOCAL_GAS_STATION, color=PRIMARY),
                                        bgcolor="#E3F2FD",
                                        padding=10,
                                        border_radius=10,
                                    ),
                                    title=ft.Text(f"{f['odometer']:,.0f} km", weight="bold"),
                                    subtitle=ft.Column([
                                        ft.Text(
                                            f"{f['fill_date']} • {f['liters']} ลิตร • {f['total_cost']:,.0f} บาท",
                                            size=12,
                                        ),
                                        ft.Container(
                                            padding=ft.padding.only(top=5, bottom=5),
                                            content=ft.Text(
                                                f"อัตราสิ้นเปลือง: {eff_display}",
                                                color=eff_color,
                                                weight="bold",
                                                size=11,
                                            ),
                                        ),
                                    ]),
                                    trailing=ft.PopupMenuButton(
                                        items=[
                                            ft.PopupMenuItem(
                                                content=ft.Text("แก้ไข"),
                                                icon=ft.Icons.EDIT,
                                                on_click=lambda e, fid=f["id"]: show_form_page(fid),
                                            ),
                                            ft.PopupMenuItem(
                                                content=ft.Text("ลบ"),
                                                icon=ft.Icons.DELETE,
                                                on_click=lambda e, fid=f["id"]: delete_data(fid),
                                            ),
                                        ]
                                    ),
                                ),
                                bgcolor="white",
                                border_radius=15,
                                shadow=ft.BoxShadow(blur_radius=10, color="#DEE3ED"),
                            )
                        )
                page.update()
            except Exception as err:
                print(f"Error loading data: {err}")
                import traceback
                traceback.print_exc()
                status_card_content.controls = [
                    ft.Text("เชื่อมต่อข้อมูลไม่ได้", color="white")
                ]
                page.update()

        def delete_data(fuel_id):
            try:
                r = requests.delete(f"{API_URL}/fuel/{fuel_id}", timeout=5)
                if r.status_code == 200:
                    show_snack("ลบข้อมูลเรียบร้อย", is_error=False)
                    load_data()
                else:
                    show_snack("ลบไม่สำเร็จ กรุณาลองใหม่", is_error=True)
            except Exception as ex:
                show_snack(f"ลบไม่สำเร็จ: {str(ex)}", is_error=True)

        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Container(
                        padding=ft.padding.only(left=20, top=50, right=20, bottom=20),
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.Alignment(0, -1),
                            end=ft.alignment.Alignment(0, 1),
                            colors=[PRIMARY, PRIMARY_VARIANT],
                        ),
                        content=ft.Column([
                            ft.Row(
                                [
                                    ft.Text("Dashboard", color="white", size=24, weight="bold"),
                                    ft.IconButton(
                                        ft.Icons.LOGOUT,
                                        icon_color="white",
                                        on_click=lambda _: show_login_page(),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Container(
                                padding=20,
                                bgcolor="#1AFFFFFF",
                                border_radius=20,
                                content=status_card_content,
                                border=ft.border.all(1, "#3DFFFFFF"),
                            ),
                        ]),
                    ),
                    ft.Container(
                        expand=True,
                        margin=ft.margin.only(top=-20),
                        bgcolor=page.bgcolor,
                        border_radius=ft.border_radius.only(top_left=30, top_right=30),
                        content=ft.Stack(
                            [
                                list_view,
                                ft.FloatingActionButton(
                                    icon=ft.Icons.ADD,
                                    on_click=lambda _: show_form_page(None),
                                    bottom=30,
                                    right=20,
                                    bgcolor=PRIMARY,
                                    foreground_color="white",
                                ),
                            ]
                        ),
                    ),
                ],
                expand=True,
                spacing=0,
            )
        )
        page.update()
        load_data()

    # ──────────── หน้าฟอร์ม เพิ่ม/แก้ไข ────────────
    def show_form_page(edit_id):
        odo    = ft.TextField(
            label="เลขไมล์ปัจจุบัน (km)",
            border_radius=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SPEED,
        )
        liters = ft.TextField(
            label="จำนวนลิตร",
            border_radius=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.LOCAL_GAS_STATION,
        )
        price  = ft.TextField(
            label="ราคาต่อลิตร",
            border_radius=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.ATTACH_MONEY,
        )
        date   = ft.TextField(
            label="วันที่ (YYYY-MM-DD)",
            border_radius=12,
            value=datetime.now().strftime("%Y-%m-%d"),
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
        )
        
        total_cost_display = ft.Container(
            padding=15,
            bgcolor="#E3F2FD",
            border_radius=15,
            content=ft.Column([
                ft.Text("ราคารวม", size=12, color="gray"),
                ft.Text("0.00 บาท", size=20, weight="bold", color=PRIMARY),
            ]),
        )

        def update_total_cost(e):
            try:
                l = float(liters.value) if liters.value else 0
                p = float(price.value) if price.value else 0
                total = l * p
                total_cost_display.content.controls[1].value = f"{total:,.2f} บาท"
                page.update()
            except:
                pass

        liters.on_change = update_total_cost
        price.on_change = update_total_cost

        if edit_id:
            entry = next((i for i in fuel_records[0] if i["id"] == edit_id), None)
            if entry:
                odo.value    = str(entry["odometer"])
                liters.value = str(entry["liters"])
                price.value  = str(entry["price_per_liter"])
                date.value   = entry["fill_date"]
                update_total_cost(None)

        def save(e):
            try:
                if not odo.value or not liters.value or not price.value or not date.value:
                    show_snack("กรุณากรอกข้อมูลให้ครบถ้วน", is_error=True)
                    return
                
                payload = {
                    "odometer":        float(odo.value),
                    "liters":          float(liters.value),
                    "price_per_liter": float(price.value),
                    "fill_date":       date.value,
                }
                if edit_id:
                    res = requests.put(f"{API_URL}/fuel/{edit_id}", json=payload, timeout=5)
                else:
                    payload["user_id"] = current_user_id[0]
                    res = requests.post(f"{API_URL}/fuel/", json=payload, timeout=5)

                if res.status_code in (200, 201):
                    show_snack("บันทึกสำเร็จ", is_error=False)
                    show_list_page()
                else:
                    show_snack("เซิร์ฟเวอร์ปฏิเสธการบันทึก", is_error=True)
            except ValueError:
                show_snack("กรุณากรอกตัวเลขให้ถูกต้อง", is_error=True)
            except Exception as ex:
                show_snack(f"กรุณาตรวจสอบข้อมูล: {str(ex)}", is_error=True)

        page.clean()
        page.add(
            ft.Column([
                ft.Container(
                    padding=ft.padding.only(left=20, top=50, right=20, bottom=20),
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.Alignment(0, -1),
                        end=ft.alignment.Alignment(0, 1),
                        colors=[PRIMARY, PRIMARY_VARIANT],
                    ),
                    content=ft.Row([
                        ft.IconButton(
                            ft.Icons.ARROW_BACK_IOS_NEW,
                            icon_color="white",
                            on_click=lambda _: show_list_page(),
                        ),
                        ft.Text("บันทึกข้อมูล", size=24, weight="bold", color="white"),
                    ]),
                ),
                ft.Container(
                    expand=True,
                    margin=ft.margin.only(top=-20),
                    bgcolor=page.bgcolor,
                    border_radius=ft.border_radius.only(top_left=30, top_right=30),
                    content=ft.ListView([
                        ft.Container(height=20),
                        ft.Container(
                            padding=25,
                            content=ft.Column(
                                [
                                    ft.Container(
                                        padding=15,
                                        bgcolor="white",
                                        border_radius=15,
                                        shadow=ft.BoxShadow(blur_radius=10, color="#DEE3ED"),
                                        content=odo,
                                    ),
                                    ft.Container(
                                        padding=15,
                                        bgcolor="white",
                                        border_radius=15,
                                        shadow=ft.BoxShadow(blur_radius=10, color="#DEE3ED"),
                                        content=liters,
                                    ),
                                    ft.Container(
                                        padding=15,
                                        bgcolor="white",
                                        border_radius=15,
                                        shadow=ft.BoxShadow(blur_radius=10, color="#DEE3ED"),
                                        content=price,
                                    ),
                                    ft.Container(
                                        padding=15,
                                        bgcolor="white",
                                        border_radius=15,
                                        shadow=ft.BoxShadow(blur_radius=10, color="#DEE3ED"),
                                        content=date,
                                    ),
                                    total_cost_display,
                                    ft.Container(height=20),
                                    ft.Button(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.SAVE_ROUNDED, color="white"),
                                            ft.Text("บันทึกข้อมูล", color="white", weight="bold"),
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        on_click=save,
                                        width=400,
                                        height=55,
                                        style=ft.ButtonStyle(
                                            bgcolor=PRIMARY,
                                            shape=ft.RoundedRectangleBorder(radius=15),
                                        ),
                                    ),
                                    ft.Container(height=20),
                                ],
                                spacing=15,
                            ),
                        ),
                    ]),
                ),
            ], expand=True, spacing=0)
        )
        page.update()

    show_login_page()


if __name__ == "__main__":
    ft.run(main)