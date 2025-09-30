from db import engine, SessionLocal
from models import Base, School, Teacher, Student, Class, Lesson, LearningTarget, LessonTarget
import time

def create_schema():
    """Create database schema - safe to run multiple times"""
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Schema checked/created")
    except Exception as e:
        print(f"⚠️  Schema creation skipped (may already exist): {e}")

def seed_minimal():
    """Seed minimal data if database is empty"""
    from sqlalchemy import select
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            with SessionLocal() as s:
                # Check if data already exists
                existing_school = s.execute(select(School)).first()
                if existing_school:
                    print("✅ Database already has data, skipping seed")
                    return
                
                # Seed data
                hs = School(name="Centennial High", code="CENT", address="123 Main St")
                s.add(hs); s.flush()

                t = Teacher(school_id=hs.school_id, first_name="Alex", last_name="Rivera", email="arivera@cent.example")
                s.add(t); s.flush()

                st = Student(school_id=hs.school_id, first_name="Jamie", last_name="Lee", grad_year=2027, email="jlee@example.com")
                s.add(st); s.flush()

                cse = Class(school_id=hs.school_id, teacher_id=t.teacher_id, course_code="CSE", term="2025-Fall", period="P2", title="PLTW CSE")
                s.add(cse); s.flush()

                l1 = Lesson(class_id=cse.class_id, lesson_number=1, title="Intro to Algorithms")
                s.add(l1); s.flush()

                tgt = LearningTarget(code="CSE.ALG.1", short_name="Design simple algorithms",
                                     description="Students design and explain simple algorithms.", domain="CS", bloom_level="Apply")
                s.add(tgt); s.flush()

                lt = LessonTarget(lesson_id=l1.lesson_id, target_id=tgt.target_id, weight=1.0, required=True)
                s.add(lt)
                s.commit()
                print("✅ Sample data seeded")
                return
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️  Attempt {attempt + 1} failed, retrying in {retry_delay}s: {e}")
                time.sleep(retry_delay)
            else:
                print(f"⚠️  Database seeding skipped after {max_retries} attempts: {e}")

if __name__ == "__main__":
    create_schema()
    seed_minimal()
    print("✅ Database initialization complete")
