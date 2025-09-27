from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, ForeignKey,
    Text, Float, UniqueConstraint, Index, func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import event
from sqlalchemy.engine import Engine

Base = declarative_base()

# Database-agnostic JSON column type
def JSONColumn():
    """Returns JSONB for PostgreSQL, JSON for SQLite"""
    from db import engine
    if engine.dialect.name == 'postgresql':
        return JSONB
    else:
        return SQLiteJSON

class TimeStamped:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class School(Base, TimeStamped):
    __tablename__ = "schools"
    school_id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True)
    address = Column(String(300))
    active = Column(Boolean, default=True, nullable=False)

class Teacher(Base, TimeStamped):
    __tablename__ = "teachers"
    teacher_id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey("schools.school_id", ondelete="RESTRICT"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name  = Column(String(100), nullable=False)
    email      = Column(String(200), unique=True)
    active     = Column(Boolean, default=True, nullable=False)
    school = relationship("School")
    __table_args__ = (Index("ix_teachers_school_last", "school_id", "last_name"),)

class Student(Base, TimeStamped):
    __tablename__ = "students"
    student_id = Column(Integer, primary_key=True)
    school_id  = Column(Integer, ForeignKey("schools.school_id", ondelete="RESTRICT"), nullable=False, index=True)
    sis_id     = Column(String(100), unique=True)
    first_name = Column(String(100), nullable=False)
    last_name  = Column(String(100), nullable=False)
    grad_year  = Column(Integer)
    email      = Column(String(200))
    active     = Column(Boolean, default=True, nullable=False)
    school = relationship("School")

class Class(Base, TimeStamped):
    __tablename__ = "classes"
    class_id   = Column(Integer, primary_key=True)
    school_id  = Column(Integer, ForeignKey("schools.school_id", ondelete="RESTRICT"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id", ondelete="RESTRICT"), nullable=False, index=True)
    course_code = Column(String(50), nullable=False)  # e.g., CSE, CYBER, UNITY
    term        = Column(String(50))
    period      = Column(String(50))
    title       = Column(String(200))
    active      = Column(Boolean, default=True, nullable=False)
    school  = relationship("School")
    teacher = relationship("Teacher")
    __table_args__ = (UniqueConstraint("teacher_id", "course_code", "term", "period", name="uq_class_unique_slot"),)

class Enrollment(Base, TimeStamped):
    __tablename__ = "enrollments"
    enrollment_id = Column(Integer, primary_key=True)
    class_id      = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False, index=True)
    student_id    = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    start_date    = Column(Date)
    end_date      = Column(Date)
    status        = Column(String(20), default="active")  # active, dropped, completed
    __table_args__ = (UniqueConstraint("class_id", "student_id", name="uq_enrollment"),)

class Lesson(Base, TimeStamped):
    __tablename__ = "lessons"
    lesson_id     = Column(Integer, primary_key=True)
    class_id      = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_number = Column(Integer, nullable=False)
    title         = Column(String(300), nullable=False)
    date_planned  = Column(Date)
    date_delivered= Column(Date)
    status        = Column(String(20), default="planned")  # planned, delivered, skipped
    notes         = Column(Text)
    __table_args__ = (UniqueConstraint("class_id", "lesson_number", name="uq_lesson_number_per_class"),)

class LearningTarget(Base, TimeStamped):
    __tablename__ = "learning_targets"
    target_id    = Column(Integer, primary_key=True)
    code         = Column(String(50), unique=True)
    short_name   = Column(String(200), nullable=False)
    description  = Column(Text)
    domain       = Column(String(100))     # e.g., CS, Cyber
    bloom_level  = Column(String(20))
    tags         = Column(JSONColumn())    # list/obj as JSON
    ai_model_version = Column(String(50))
    rubric_json  = Column(JSONColumn())

class LessonTarget(Base, TimeStamped):
    __tablename__ = "lesson_targets"
    lesson_target_id = Column(Integer, primary_key=True)
    lesson_id  = Column(Integer, ForeignKey("lessons.lesson_id", ondelete="CASCADE"), nullable=False, index=True)
    target_id  = Column(Integer, ForeignKey("learning_targets.target_id", ondelete="RESTRICT"), nullable=False, index=True)
    weight     = Column(Float, default=1.0)
    required   = Column(Boolean, default=True, nullable=False)
    __table_args__ = (UniqueConstraint("lesson_id", "target_id", name="uq_lesson_target"),)

class Assessment(Base, TimeStamped):
    __tablename__ = "assessments"
    assessment_id = Column(Integer, primary_key=True)
    class_id      = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id     = Column(Integer, ForeignKey("lessons.lesson_id", ondelete="SET NULL"))
    title         = Column(String(300), nullable=False)
    type          = Column(String(50), nullable=False)  # google_form, project, quiz
    google_form_url = Column(Text)
    google_form_id  = Column(String(200))
    max_points    = Column(Float)

class AssessmentItem(Base, TimeStamped):
    __tablename__ = "assessment_items"
    item_id       = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="CASCADE"), nullable=False, index=True)
    item_number   = Column(Integer, nullable=False)
    prompt        = Column(Text)
    max_points    = Column(Float)
    target_id     = Column(Integer, ForeignKey("learning_targets.target_id", ondelete="SET NULL"))
    tags          = Column(JSONColumn())
    __table_args__ = (UniqueConstraint("assessment_id", "item_number", name="uq_item_number_per_assessment"),)

class StudentSubmission(Base, TimeStamped):
    __tablename__ = "student_submissions"
    submission_id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="CASCADE"), nullable=False, index=True)
    student_id    = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    submitted_at  = Column(DateTime(timezone=True))
    score_total   = Column(Float)
    percent       = Column(Float)
    external_response_id = Column(String(200))
    __table_args__ = (UniqueConstraint("assessment_id", "student_id", name="uq_submission_one_attempt"),)

class SubmissionItem(Base, TimeStamped):
    __tablename__ = "submission_items"
    submission_item_id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("student_submissions.submission_id", ondelete="CASCADE"), nullable=False, index=True)
    item_id       = Column(Integer, ForeignKey("assessment_items.item_id", ondelete="CASCADE"), nullable=False, index=True)
    score         = Column(Float)
    response_text = Column(Text)
    correct       = Column(Boolean)
    __table_args__ = (Index("ix_submission_item_pair", "submission_id", "item_id"),)

class StudentTargetProgress(Base, TimeStamped):
    __tablename__ = "student_target_progress"
    progress_id  = Column(Integer, primary_key=True)
    student_id   = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    class_id     = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False, index=True)
    target_id    = Column(Integer, ForeignKey("learning_targets.target_id", ondelete="RESTRICT"), nullable=False, index=True)
    date         = Column(Date, nullable=False)
    evidence_type= Column(String(50))  # assessment_item, observation, project
    evidence_ref = Column(String(100)) # e.g., submission_item_id
    score        = Column(Float)
    max_score    = Column(Float)
    proficiency_level = Column(String(10))  # BEG, DEV, PROF, ADV
    notes        = Column(Text)
    __table_args__ = (
        Index("ix_progress_class_target", "class_id", "target_id"),
        Index("ix_progress_student_target_date", "student_id", "target_id", "date"),
    )
