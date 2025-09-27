from db import engine, SessionLocal
from models import Base, School, Teacher, Student, Class, Lesson, LearningTarget, LessonTarget

def create_schema():
    Base.metadata.create_all(bind=engine)

def seed_minimal():
    from sqlalchemy import select
    with SessionLocal() as s:
        if not s.execute(select(School)).first():
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

if __name__ == "__main__":
    create_schema()
    seed_minimal()
    print("✅ Schema created and sample data seeded.")
