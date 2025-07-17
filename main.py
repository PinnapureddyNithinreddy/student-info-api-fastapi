from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import sqlite3
import json

app = FastAPI()

# Database setup
conn = sqlite3.connect("students.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT,
    branch TEXT,
    year TEXT,
    attendance INTEGER,
    subjects TEXT,
    fees_paid BOOLEAN
)
""")
conn.commit()

# Pydantic model
class SubjectMarks(BaseModel):
    Maths: int
    Physics: int
    English: int

class Student(BaseModel):
    id: int
    name: str
    branch: str
    year: str
    attendance: int
    subjects: SubjectMarks
    fees_paid: bool

@app.post("/students")
def add_students(students: List[Student]):
    for student in students:
        cursor.execute("INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?, ?, ?, ?)", (
            student.id,
            student.name,
            student.branch,
            student.year,
            student.attendance,
            json.dumps(student.subjects.dict()),
            student.fees_paid
        ))
    conn.commit()
    return {"message": "Students added successfully"}

@app.get("/students")
def get_all_students():
    cursor.execute("SELECT * FROM students")
    records = cursor.fetchall()
    result = []
    for r in records:
        result.append({
            "id": r[0],
            "name": r[1],
            "branch": r[2],
            "year": r[3],
            "attendance": r[4],
            "subjects": json.loads(r[5]),
            "fees_paid": bool(r[6])
        })
    return result

@app.get("/students/{student_id}")
def get_student(student_id: int):
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    record = cursor.fetchone()
    if not record:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "id": record[0],
        "name": record[1],
        "branch": record[2],
        "year": record[3],
        "attendance": record[4],
        "subjects": json.loads(record[5]),
        "fees_paid": bool(record[6])
    }

@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    cursor.execute("UPDATE students SET name=?, branch=?, year=?, attendance=?, subjects=?, fees_paid=? WHERE id=?", (
        student.name,
        student.branch,
        student.year,
        student.attendance,
        json.dumps(student.subjects.dict()),
        student.fees_paid,
        student_id
    ))
    conn.commit()
    return {"message": "Student updated successfully"}

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    return {"message": "Student deleted successfully"}
