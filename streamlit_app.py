import streamlit as st
import pandas as pd
from sqlalchemy import text, select
from db import SessionLocal, engine
from models import School, Teacher, Student, Class, Lesson, LearningTarget, LessonTarget, StudentTargetProgress

st.set_page_config(page_title="EdTrack", layout="wide")
st.title("EdTrack — Classes, Lessons, Targets & Progress")


def df_sql(sql: str, params: dict | None = None) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})

@st.cache_data(ttl=60)
def load_dims():
    with SessionLocal() as s:
        schools = pd.read_sql(select(School).order_by(School.name), s.bind)
        teachers = pd.read_sql(select(Teacher), s.bind)
        students = pd.read_sql(select(Student), s.bind)
        classes  = pd.read_sql(select(Class), s.bind)
        lessons  = pd.read_sql(select(Lesson), s.bind)
        targets  = pd.read_sql(select(LearningTarget), s.bind)
    return schools, teachers, students, classes, lessons, targets

def refresh():
    load_dims.clear()

page = st.sidebar.radio("Go to", ["Dashboard", "Add Data", "Lessons & Targets", "Progress & Reports"])

if page == "Dashboard":
    schools, teachers, students, classes, lessons, targets = load_dims()
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Schools", len(schools)); col2.metric("Teachers", len(teachers))
    col3.metric("Students", len(students)); col4.metric("Classes", len(classes))
    col5.metric("Lessons", len(lessons)); col6.metric("Targets", len(targets))

    st.subheader("Classes by School/Teacher")
    sql = """
    SELECT c.class_id, s.name AS school, t.last_name || ', ' || t.first_name AS teacher,
           c.course_code, c.term, c.period, c.title
    FROM classes c
    JOIN schools s ON s.school_id=c.school_id
    JOIN teachers t ON t.teacher_id=c.teacher_id
    ORDER BY s.name, teacher, c.term, c.period;"""
    st.dataframe(df_sql(sql), use_container_width=True)

elif page == "Add Data":
    st.subheader("Quick Add")

    with st.expander("➕ School"):
        name = st.text_input("Name"); code = st.text_input("Code")
        if st.button("Add School", use_container_width=True, key="add_school"):
            with SessionLocal() as s:
                s.add(School(name=name, code=code)); s.commit()
            refresh(); st.success("Added school.")

    schools, teachers, students, classes, lessons, targets = load_dims()

    with st.expander("➕ Teacher"):
        if schools.empty:
            st.info("Add a school first.")
        else:
            school_map = dict(zip(schools["name"], schools["school_id"]))
            sch = st.selectbox("School", list(school_map))
            fn = st.text_input("First name"); ln = st.text_input("Last name"); em = st.text_input("Email")
            if st.button("Add Teacher", use_container_width=True):
                with SessionLocal() as s:
                    s.add(Teacher(school_id=school_map[sch], first_name=fn, last_name=ln, email=em)); s.commit()
                refresh(); st.success("Added teacher.")

    with st.expander("➕ Student"):
        if schools.empty:
            st.info("Add a school first.")
        else:
            school_map = dict(zip(schools["name"], schools["school_id"]))
            sch = st.selectbox("School ", list(school_map), key="stud_school")
            fn = st.text_input("First name ", key="stud_fn"); ln = st.text_input("Last name ", key="stud_ln")
            grad = st.number_input("Grad year", value=2027, step=1)
            if st.button("Add Student", use_container_width=True):
                with SessionLocal() as s:
                    s.add(Student(school_id=school_map[sch], first_name=fn, last_name=ln, grad_year=grad)); s.commit()
                refresh(); st.success("Added student.")

    with st.expander("➕ Class"):
        if teachers.empty:
            st.info("Add a teacher first.")
        else:
            tmap = dict(zip(teachers["last_name"] + ", " + teachers["first_name"], teachers["teacher_id"]))
            teacher_label = st.selectbox("Teacher", list(tmap))
            course = st.selectbox("Course code", ["CSE", "CYBER", "UNITY", "OTHER"])
            term = st.text_input("Term (e.g., 2025-Fall)", value="2025-Fall")
            period = st.text_input("Period", value="P1")
            title = st.text_input("Title", value=f"Course {course}")
            if st.button("Add Class", use_container_width=True):
                with SessionLocal() as s:
                    tid = tmap[teacher_label]
                    sch_id = s.get(Teacher, tid).school_id
                    s.add(Class(teacher_id=tid, school_id=sch_id, course_code=course, term=term, period=period, title=title))
                    s.commit()
                refresh(); st.success("Added class.")

elif page == "Lessons & Targets":
    st.subheader("Lessons & Target Mapping")
    schools, teachers, students, classes, lessons, targets = load_dims()

    if classes.empty:
        st.info("Add a class first on 'Add Data'.")
    else:
        cmap = dict(zip(classes["title"] + " • " + classes["term"] + " • " + classes["period"], classes["class_id"]))
        csel = st.selectbox("Class", list(cmap)); class_id = cmap[csel]

        with st.form("add_lesson"):
            st.markdown("**Add a Lesson**")
            num = st.number_input("Lesson number", min_value=1, step=1)
            ltitle = st.text_input("Lesson title")
            submitted = st.form_submit_button("Add Lesson")
            if submitted:
                from models import Lesson
                with SessionLocal() as s:
                    s.add(Lesson(class_id=class_id, lesson_number=int(num), title=ltitle)); s.commit()
                refresh(); st.success("Lesson added.")

        st.divider()

        with st.form("add_target"):
            st.markdown("**Add / Map Learning Target**")
            tgt_code = st.text_input("Target code (optional)")
            tgt_name = st.text_input("Short name", value="Describe algorithms")
            tgt_desc = st.text_area("Description", value="")
            weight = st.number_input("Weight", value=1.0)
            required = st.checkbox("Required", value=True)

            class_lessons = df_sql(
                "SELECT lesson_id, lesson_number, title FROM lessons WHERE class_id=:cid ORDER BY lesson_number",
                {"cid": class_id})
            if class_lessons.empty:
                st.info("Add a lesson first.")
            else:
                lmap = dict(zip(class_lessons["lesson_number"].astype(str) + " • " + class_lessons["title"], class_lessons["lesson_id"]))
                lsel = st.selectbox("Map to Lesson", list(lmap))
                btn = st.form_submit_button("Create Target (if needed) & Map")
                if btn:
                    from sqlalchemy import select
                    with SessionLocal() as s:
                        target = None
                        if tgt_code:
                            target = s.execute(select(LearningTarget).where(LearningTarget.code==tgt_code)).scalar_one_or_none()
                        if not target:
                            target = LearningTarget(code=tgt_code or None, short_name=tgt_name, description=tgt_desc)
                            s.add(target); s.flush()
                        s.add(LessonTarget(lesson_id=lmap[lsel], target_id=target.target_id, weight=weight, required=required))
                        s.commit()
                    refresh(); st.success("Target mapped to lesson.")

    st.subheader("Lesson • Target Coverage")
    sql = """
    SELECT l.class_id, l.lesson_number, l.title AS lesson_title, t.code, t.short_name, lt.weight, lt.required
    FROM lesson_targets lt
    JOIN lessons l ON l.lesson_id=lt.lesson_id
    JOIN learning_targets t ON t.target_id=lt.target_id
    ORDER BY l.class_id, l.lesson_number, t.short_name;"""
    st.dataframe(df_sql(sql), use_container_width=True)

elif page == "Progress & Reports":
    st.subheader("Record Student Target Progress")
    schools, teachers, students, classes, lessons, targets = load_dims()

    if classes.empty or students.empty or targets.empty:
        st.info("Need at least one class, student, and target.")
    else:
        cmap = dict(zip(classes["title"] + " • " + classes["term"] + " • " + classes["period"], classes["class_id"]))
        csel = st.selectbox("Class", list(cmap)); class_id = cmap[csel]

        smap = dict(zip(students["last_name"] + ", " + students["first_name"], students["student_id"]))
        ssel = st.selectbox("Student", list(smap))
        tmap = dict(zip(targets["short_name"], targets["target_id"]))
        tsel = st.selectbox("Target", list(tmap))

        date = st.date_input("Evidence date")
        p_level = st.selectbox("Proficiency", ["BEG","DEV","PROF","ADV"])
        score   = st.number_input("Score", value=1.0)
        max_sc  = st.number_input("Max score", value=1.0)
        notes   = st.text_input("Notes (optional)")
        if st.button("Save Progress"):
            with SessionLocal() as s:
                s.add(StudentTargetProgress(student_id=smap[ssel], class_id=class_id,
                                            target_id=tmap[tsel], date=date,
                                            evidence_type="observation", evidence_ref=None,
                                            score=score, max_score=max_sc, proficiency_level=p_level, notes=notes))
                s.commit()
            st.success("Saved progress.")

    st.subheader("Mastery by Class & Target (latest record)")
    sql_latest = """
    WITH ranked AS (
      SELECT progress_id, student_id, class_id, target_id, date, proficiency_level,
             ROW_NUMBER() OVER (PARTITION BY student_id, target_id ORDER BY date DESC, progress_id DESC) AS rn
      FROM student_target_progress
    )
    SELECT r.class_id, r.target_id, COUNT(*) FILTER (WHERE r.rn=1) AS students,
           SUM(CASE WHEN r.rn=1 AND r.proficiency_level IN ('PROF','ADV') THEN 1 ELSE 0 END) AS mastered
    FROM ranked r
    WHERE r.rn=1
    GROUP BY r.class_id, r.target_id
    ORDER BY r.class_id, r.target_id;"""
    df = df_sql(sql_latest)
    if not df.empty:
        df["mastery_rate"] = (df["mastered"] / df["students"]).round(3)
    st.dataframe(df, use_container_width=True)

    st.subheader("Per-Student Target Timeline")
    sql_timeline = """
    SELECT stp.student_id, stp.class_id, stp.target_id, stp.date, stp.proficiency_level, stp.score, stp.max_score
    FROM student_target_progress stp
    ORDER BY stp.student_id, stp.target_id, stp.date;"""
    st.dataframe(df_sql(sql_timeline), use_container_width=True)
