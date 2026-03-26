from fastapi import FastAPI, HTTPException
import re
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import database as db
import schemas
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize database tables
db.create_tables()

# สร้าง User ตัวอย่างให้ทดสอบระบบ (รันตอนเปิด Server)
@app.on_event("startup")
def create_dummy_user():
    connection = db.get_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", ("testuser",))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    ("testuser", "123")
                )
                connection.commit()
        except Exception as ex:
            print(f"Error creating dummy user: {ex}")
        finally:
            cursor.close()
            connection.close()

def validate_password(password: str) -> tuple[bool, str]:
    """ตรวจสอบรหัสผ่าน: ต้องมี 8 ตัว, อักษรพิเศษ, และตัวเลข"""
    import re
    if len(password) < 8:
        return False, "รหัสผ่านต้องมีอย่างน้อย 8 ตัว"
    if not re.search(r"[0-9]", password):
        return False, "รหัสผ่านต้องมีตัวเลข"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "รหัสผ่านต้องมีอักษรพิเศษ (!@#$%^&* เป็นต้น)"
    return True, "ตกลง"

# 1. Register
@app.post("/register")
def register(user: schemas.UserLogin):
    connection = db.get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        # ตรวจสอบรหัสผ่าน
        is_valid, message = validate_password(user.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        cursor = connection.cursor()
        
        # ตรวจสอบ username ซ้ำ
        cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username นี้ถูกใช้แล้ว")
        
        # บันทึก user ใหม่
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (user.username, user.password)
        )
        connection.commit()
        user_id = cursor.lastrowid
        
        return {"user_id": user_id, "message": "สมัครสมาชิกสำเร็จ"}
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        connection.close()

# 2. Login
@app.post("/login")
def login(user: schemas.UserLogin):
    connection = db.get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE username = %s AND password = %s",
            (user.username, user.password)
        )
        db_user = cursor.fetchone()
        
        if not db_user:
            raise HTTPException(status_code=401, detail="Username หรือ Password ไม่ถูกต้อง")
        
        return {"user_id": db_user[0], "message": "Login successful"}
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        connection.close()

# --- CRUD Operations สำหรับหน้าแอป ---

# [C] CREATE: บันทึกเลขไมล์และเติมน้ำมัน
@app.post("/fuel/", response_model=schemas.FuelResponse)
def create_fuel(fuel: schemas.FuelCreate):
    connection = db.get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO fuel_oil (user_id, odometer, liters, price_per_liter, total_cost, fill_date) VALUES (%s, %s, %s, %s, %s, %s)",
            (fuel.user_id, fuel.odometer, fuel.liters, fuel.price_per_liter, fuel.liters * fuel.price_per_liter, fuel.fill_date)
        )
        connection.commit()
        fuel_id = cursor.lastrowid
        total_cost = fuel.liters * fuel.price_per_liter

        return {
            "id": fuel_id,
            "user_id": fuel.user_id,
            "odometer": fuel.odometer,
            "liters": fuel.liters,
            "price_per_liter": fuel.price_per_liter,
            "total_cost": total_cost,
            "fill_date": fuel.fill_date,
            "efficiency": None
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        connection.close()

# [R] READ: แสดงประวัติเติมน้ำมัน ผู้ใช้
@app.get("/fuel/{user_id}", response_model=List[schemas.FuelResponse])
def read_fuel(user_id: int):
    connection = db.get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, user_id, odometer, liters, price_per_liter, total_cost, fill_date FROM fuel_oil WHERE user_id = %s ORDER BY fill_date DESC",
            (user_id,)
        )

        rows = cursor.fetchall()
        fuels = []
        prev_odometer = None

        for row in reversed(rows):  # คำนวณ efficiency จากย้อนหลัง
            if prev_odometer is not None:
                distance = row[2] - prev_odometer
                efficiency = (distance / row[3]) if row[3] > 0 and distance > 0 else None
            else:
                efficiency = None
            prev_odometer = row[2]

            fuels.append({
                "id": row[0],
                "user_id": row[1],
                "odometer": row[2],
                "liters": row[3],
                "price_per_liter": row[4],
                "total_cost": float(row[5]),
                "fill_date": row[6],
                "efficiency": round(efficiency, 2) if efficiency is not None else None
            })

        return list(reversed(fuels))  # ไฟล์ล่าสุดก่อน
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        connection.close()

# [U] UPDATE: แก้ไขข้อมูลบันทึกเติมน้ำมัน
@app.put("/fuel/{fuel_id}", response_model=schemas.FuelResponse)
def update_fuel(fuel_id: int, fuel_data: schemas.FuelUpdate):
    connection = db.get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, user_id, odometer, liters, price_per_liter, fill_date FROM fuel_oil WHERE id = %s", (fuel_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Fuel record not found")

        odometer = fuel_data.odometer if fuel_data.odometer is not None else row[2]
        liters = fuel_data.liters if fuel_data.liters is not None else row[3]
        price_per_liter = fuel_data.price_per_liter if fuel_data.price_per_liter is not None else row[4]

        cursor.execute(
            "UPDATE fuel_oil SET odometer = %s, liters = %s, price_per_liter = %s, total_cost = %s WHERE id = %s",
            (odometer, liters, price_per_liter, liters * price_per_liter, fuel_id)
        )
        connection.commit()

        total_cost = odometer and liters and price_per_liter and (liters * price_per_liter)

        return {
            "id": row[0],
            "user_id": row[1],
            "odometer": odometer,
            "liters": liters,
            "price_per_liter": price_per_liter,
            "total_cost": float(liters * price_per_liter),
            "fill_date": row[5],
            "efficiency": None
        }
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        connection.close()

# [D] DELETE: ลบรายการเติมน้ำมัน
@app.delete("/fuel/{fuel_id}")
def delete_fuel(fuel_id: int):
    connection = db.get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM fuel_oil WHERE id = %s", (fuel_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Fuel record not found")

        cursor.execute("DELETE FROM fuel_oil WHERE id = %s", (fuel_id,))
        connection.commit()

        return {"status": "Deleted successfully"}
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        connection.close()

# [S] Service Alert
@app.get("/fuel/status/{user_id}")
def fuel_status(user_id: int):
    connection = db.get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT odometer FROM fuel_oil WHERE user_id = %s ORDER BY fill_date DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        if not row:
            return {"last_odometer": None, "next_service_at": None, "km_remaining": None, "alert": "ไม่มีข้อมูลเติมน้ำมัน"}

        last_odometer = row[0]
        service_interval = 10000
        next_service = ((last_odometer // service_interval) + 1) * service_interval
        remaining = max(0, next_service - last_odometer)

        alert = "ปกติ" if remaining > 500 else "ควรตรวจเช็คระยะ" if remaining > 0 else "ถึงเวลาตรวจเช็คแล้ว"

        return {
            "last_odometer": last_odometer,
            "next_service_at": next_service,
            "km_remaining": remaining,
            "alert": alert
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        connection.close()