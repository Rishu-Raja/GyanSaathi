
import sqlite3

DATABASE_NAME = "learning_assistant.db"


def create_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level TEXT,
            goal TEXT,
            learning_style TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT,
            topic TEXT,
            prompt_type TEXT,
            prompt TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()


def save_student(name, level, goal, learning_style):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (name, level, goal, learning_style)
        VALUES (?, ?, ?, ?)
    """, (name, level, goal, learning_style))

    student_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return student_id


def save_learning_history(
    student_id, subject, topic, prompt_type, prompt, response
):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO learning_history
        (student_id, subject, topic, prompt_type, prompt, response)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        student_id, subject, topic, prompt_type, prompt, response
    ))

    conn.commit()
    conn.close()


def get_learning_history(student_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject, topic, prompt_type, created_at
        FROM learning_history
        WHERE student_id = ?
        ORDER BY id DESC
    """, (student_id,))

    records = cursor.fetchall()
    conn.close()

    return records
