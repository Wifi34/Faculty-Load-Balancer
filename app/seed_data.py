import datetime
from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models import (
    User, FacultyProfile, Subject, AcademicClass, Classroom, Schedule,
    Notification, ReminderPreference, AuditLog
)
from app.auth import hash_password

def init_db():
    Base.metadata.create_all(bind=engine)

def seed_sample_data(db: Session):
    # Check if database already has users
    if db.query(User).count() > 0:
        return

    print("[Seed Data] Populating realistic engineering college faculty database...")

    # 1. Classrooms
    rooms = [
        Classroom(room_no="LH-301", building="Aryabhata Academic Block", capacity=75, room_type="Lecture Hall"),
        Classroom(room_no="LH-302", building="Aryabhata Academic Block", capacity=75, room_type="Lecture Hall"),
        Classroom(room_no="LH-303", building="Aryabhata Academic Block", capacity=60, room_type="Lecture Hall"),
        Classroom(room_no="Lab-1", building="Computing Center", capacity=40, room_type="Computer Systems Lab"),
        Classroom(room_no="Lab-2", building="Computing Center", capacity=40, room_type="AI & Data Science Lab"),
        Classroom(room_no="Lab-3", building="Computing Center", capacity=40, room_type="Networking & Security Lab"),
        Classroom(room_no="Seminar-Hall-A", building="Main Block", capacity=150, room_type="Seminar Hall"),
    ]
    db.add_all(rooms)
    db.commit()

    # 2. Classes
    classes = [
        AcademicClass(name="B.Tech CSE - 5th Sem - Sec A", department="Computer Science & Engineering", semester=5, section="A", academic_year="2026-2027"),
        AcademicClass(name="B.Tech CSE - 5th Sem - Sec B", department="Computer Science & Engineering", semester=5, section="B", academic_year="2026-2027"),
        AcademicClass(name="B.Tech CSE - 7th Sem - Sec A", department="Computer Science & Engineering", semester=7, section="A", academic_year="2026-2027"),
        AcademicClass(name="B.Tech CSE - 3rd Sem - Sec A", department="Computer Science & Engineering", semester=3, section="A", academic_year="2026-2027"),
    ]
    db.add_all(classes)
    db.commit()

    # 3. Subjects
    subjects = [
        Subject(code="CS501", name="Data Structures & Algorithms", department="Computer Science & Engineering", semester=5, credits=4, lecture_hours_per_week=4),
        Subject(code="CS502", name="Database Management Systems", department="Computer Science & Engineering", semester=5, credits=4, lecture_hours_per_week=4),
        Subject(code="CS503", name="Operating Systems & Architecture", department="Computer Science & Engineering", semester=5, credits=4, lecture_hours_per_week=4),
        Subject(code="CS504", name="Computer Networks & Protocols", department="Computer Science & Engineering", semester=5, credits=4, lecture_hours_per_week=4),
        Subject(code="CS505", name="Artificial Intelligence & ML", department="Computer Science & Engineering", semester=5, credits=3, lecture_hours_per_week=3),
        Subject(code="CS506", name="Software Engineering & Agile", department="Computer Science & Engineering", semester=5, credits=3, lecture_hours_per_week=3),
        Subject(code="CS507", name="Data Structures Practical Lab", department="Computer Science & Engineering", semester=5, credits=2, lecture_hours_per_week=2),
        Subject(code="CS508", name="DBMS & SQL Query Lab", department="Computer Science & Engineering", semester=5, credits=2, lecture_hours_per_week=2),
    ]
    db.add_all(subjects)
    db.commit()

    # 4. Faculty Profiles
    faculty_members = [
        FacultyProfile(
            faculty_code="FAC-CS-001",
            name="Dr. Amit Verma",
            department="Computer Science & Engineering",
            designation="Associate Professor",
            email="amit.verma@college.edu",
            phone="+91 98765 43210",
            cabin_room="Cabin 304-A, CS Block",
            subjects_taught="Data Structures & Algorithms, Design Analysis of Algorithms, DS Lab",
            weekly_lecture_limit=16,
            max_duties_limit=6,
            is_active=True
        ),
        FacultyProfile(
            faculty_code="FAC-CS-002",
            name="Prof. Priya Patel",
            department="Computer Science & Engineering",
            designation="Assistant Professor",
            email="priya.patel@college.edu",
            phone="+91 98765 43211",
            cabin_room="Cabin 305-B, CS Block",
            subjects_taught="Database Management Systems, DBMS & SQL Lab",
            weekly_lecture_limit=16,
            max_duties_limit=6,
            is_active=True
        ),
        FacultyProfile(
            faculty_code="FAC-CS-003",
            name="Dr. Rohit Gupta",
            department="Computer Science & Engineering",
            designation="Assistant Professor",
            email="rohit.gupta@college.edu",
            phone="+91 98765 43212",
            cabin_room="Cabin 306-A, CS Block",
            subjects_taught="Operating Systems & Architecture, Computer Networks",
            weekly_lecture_limit=16,
            max_duties_limit=6,
            is_active=True
        ),
        FacultyProfile(
            faculty_code="FAC-CS-004",
            name="Prof. Sneha Kulkarni",
            department="Computer Science & Engineering",
            designation="Assistant Professor",
            email="sneha.kulkarni@college.edu",
            phone="+91 98765 43213",
            cabin_room="Cabin 307-B, CS Block",
            subjects_taught="Artificial Intelligence & ML, Neural Networks",
            weekly_lecture_limit=16,
            max_duties_limit=6,
            is_active=True
        ),
        FacultyProfile(
            faculty_code="FAC-CS-005",
            name="Prof. Vikram Singh",
            department="Computer Science & Engineering",
            designation="Lecturer",
            email="vikram.singh@college.edu",
            phone="+91 98765 43214",
            cabin_room="Cabin 308-A, CS Block",
            subjects_taught="Software Engineering & Agile, Object Oriented Programming",
            weekly_lecture_limit=16,
            max_duties_limit=6,
            is_active=True
        ),
        FacultyProfile(
            faculty_code="FAC-CS-006",
            name="Prof. Anita Desai",
            department="Computer Science & Engineering",
            designation="Assistant Professor",
            email="anita.desai@college.edu",
            phone="+91 98765 43215",
            cabin_room="Cabin 309-C, CS Block",
            subjects_taught="Web Technologies, Mobile App Development",
            weekly_lecture_limit=16,
            max_duties_limit=6,
            is_active=True
        ),
    ]
    db.add_all(faculty_members)
    db.commit()

    # 5. User Accounts
    # HOD User Account
    hod_user = User(
        username="hod_cs",
        password_hash=hash_password("admin123"),
        role="hod",
        email="hod.cse@college.edu",
        full_name="Dr. Rajesh Sharma (HOD CSE)",
        faculty_id=None
    )
    db.add(hod_user)
    db.commit()

    # Reminder preference for HOD
    db.add(ReminderPreference(user_id=hod_user.id, lead_time_minutes=15, browser_enabled=True, email_enabled=True))
    db.commit()

    # Faculty User Accounts
    faculty_user_map = {}
    usernames = ["prof_amit", "prof_priya", "prof_rohit", "prof_sneha", "prof_vikram", "prof_anita"]
    for i, fac in enumerate(faculty_members):
        uname = usernames[i]
        u = User(
            username=uname,
            password_hash=hash_password("faculty123"),
            role="faculty",
            email=fac.email,
            full_name=fac.name,
            faculty_id=fac.id
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        faculty_user_map[fac.id] = u
        db.add(ReminderPreference(user_id=u.id, lead_time_minutes=15, browser_enabled=True, email_enabled=True))
    db.commit()

    # 6. Schedules (Monday to Saturday)
    # Calculate dates for the current week
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    dates_by_day = {
        "Monday": (monday + datetime.timedelta(days=0)).strftime("%Y-%m-%d"),
        "Tuesday": (monday + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
        "Wednesday": (monday + datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
        "Thursday": (monday + datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
        "Friday": (monday + datetime.timedelta(days=4)).strftime("%Y-%m-%d"),
        "Saturday": (monday + datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
    }

    fac1 = faculty_members[0] # Dr. Amit Verma (Will have High Load: 18 hrs)
    fac2 = faculty_members[1] # Prof. Priya Patel (Balanced: 14 hrs)
    fac3 = faculty_members[2] # Dr. Rohit Gupta (Balanced: 13 hrs)
    fac4 = faculty_members[3] # Prof. Sneha Kulkarni (Balanced: 11 hrs)
    fac5 = faculty_members[4] # Prof. Vikram Singh (Low: 8 hrs) -> Available for extra duties!
    fac6 = faculty_members[5] # Prof. Anita Desai (Low: 7 hrs) -> Available for extra duties!

    schedules_data = [
        # --- Dr. Amit Verma (High Workload ~ 18 hours) ---
        Schedule(schedule_type="regular_lecture", faculty_id=fac1.id, subject_id=subjects[0].id, class_id=classes[0].id, classroom_id=rooms[0].id,
                 day_of_week="Monday", date=dates_by_day["Monday"], start_time="09:00", end_time="10:00", duration_hours=1.0, academic_week=1,
                 duty_title="Data Structures: Trees & Graphs", instructions="Review Binary Search Tree balancing"),
        Schedule(schedule_type="lab_duty", faculty_id=fac1.id, subject_id=subjects[6].id, class_id=classes[0].id, classroom_id=rooms[3].id,
                 day_of_week="Monday", date=dates_by_day["Monday"], start_time="10:00", end_time="12:00", duration_hours=2.0, academic_week=1,
                 duty_title="Data Structures Practical Lab Batch A", instructions="Conduct Lab Assessment #3"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac1.id, subject_id=subjects[0].id, class_id=classes[1].id, classroom_id=rooms[1].id,
                 day_of_week="Tuesday", date=dates_by_day["Tuesday"], start_time="09:00", end_time="10:00", duration_hours=1.0, academic_week=1,
                 duty_title="Data Structures: Graph Traversals"),
        Schedule(schedule_type="substitute_lecture", faculty_id=fac1.id, subject_id=subjects[2].id, class_id=classes[0].id, classroom_id=rooms[0].id,
                 day_of_week="Tuesday", date=dates_by_day["Tuesday"], start_time="11:00", end_time="12:00", duration_hours=1.0, academic_week=1,
                 duty_title="Substitute Lecture: Operating Systems", instructions="Covering for Dr. Rohit (Medical Leave)"),
        Schedule(schedule_type="lab_duty", faculty_id=fac1.id, subject_id=subjects[6].id, class_id=classes[1].id, classroom_id=rooms[3].id,
                 day_of_week="Wednesday", date=dates_by_day["Wednesday"], start_time="14:00", end_time="16:00", duration_hours=2.0, academic_week=1,
                 duty_title="Data Structures Practical Lab Batch B"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac1.id, subject_id=subjects[0].id, class_id=classes[0].id, classroom_id=rooms[0].id,
                 day_of_week="Thursday", date=dates_by_day["Thursday"], start_time="10:00", end_time="11:00", duration_hours=1.0, academic_week=1,
                 duty_title="Data Structures: Dynamic Programming"),
        Schedule(schedule_type="exam_duty", faculty_id=fac1.id, subject_id=None, class_id=classes[0].id, classroom_id=rooms[6].id,
                 day_of_week="Thursday", date=dates_by_day["Thursday"], start_time="14:00", end_time="17:00", duration_hours=3.0, academic_week=1,
                 duty_title="Mid-Term Exam Chief Invigilator", instructions="Collect question papers from Exam Cell by 1:30 PM"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac1.id, subject_id=subjects[0].id, class_id=classes[1].id, classroom_id=rooms[1].id,
                 day_of_week="Friday", date=dates_by_day["Friday"], start_time="11:00", end_time="12:00", duration_hours=1.0, academic_week=1,
                 duty_title="Data Structures: Hashing Techniques"),
        Schedule(schedule_type="college_duty", faculty_id=fac1.id, subject_id=None, class_id=None, classroom_id=rooms[6].id,
                 day_of_week="Friday", date=dates_by_day["Friday"], start_time="14:00", end_time="17:00", duration_hours=3.0, academic_week=1,
                 duty_title="NAAC Accreditation Documentation Committee", instructions="Verify Criterion 2 course files"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac1.id, subject_id=subjects[0].id, class_id=classes[0].id, classroom_id=rooms[0].id,
                 day_of_week="Saturday", date=dates_by_day["Saturday"], start_time="09:00", end_time="12:00", duration_hours=3.0, academic_week=1,
                 duty_title="Remedial Lecture & Doubt Clearing Session"),

        # --- Prof. Priya Patel (Balanced ~ 14 hours) ---
        Schedule(schedule_type="regular_lecture", faculty_id=fac2.id, subject_id=subjects[1].id, class_id=classes[0].id, classroom_id=rooms[1].id,
                 day_of_week="Monday", date=dates_by_day["Monday"], start_time="11:00", end_time="12:00", duration_hours=1.0, academic_week=1,
                 duty_title="DBMS: Relational Algebra & Normalization"),
        Schedule(schedule_type="lab_duty", faculty_id=fac2.id, subject_id=subjects[7].id, class_id=classes[0].id, classroom_id=rooms[4].id,
                 day_of_week="Monday", date=dates_by_day["Monday"], start_time="14:00", end_time="16:00", duration_hours=2.0, academic_week=1,
                 duty_title="DBMS & SQL Query Lab Batch A"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac2.id, subject_id=subjects[1].id, class_id=classes[1].id, classroom_id=rooms[2].id,
                 day_of_week="Tuesday", date=dates_by_day["Tuesday"], start_time="10:00", end_time="11:00", duration_hours=1.0, academic_week=1,
                 duty_title="DBMS: Transaction Management & ACID"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac2.id, subject_id=subjects[1].id, class_id=classes[0].id, classroom_id=rooms[1].id,
                 day_of_week="Wednesday", date=dates_by_day["Wednesday"], start_time="09:00", end_time="10:00", duration_hours=1.0, academic_week=1,
                 duty_title="DBMS: Indexing and B-Trees"),
        Schedule(schedule_type="lab_duty", faculty_id=fac2.id, subject_id=subjects[7].id, class_id=classes[1].id, classroom_id=rooms[4].id,
                 day_of_week="Wednesday", date=dates_by_day["Wednesday"], start_time="10:00", end_time="12:00", duration_hours=2.0, academic_week=1,
                 duty_title="DBMS & SQL Query Lab Batch B"),
        Schedule(schedule_type="exam_duty", faculty_id=fac2.id, subject_id=None, class_id=classes[1].id, classroom_id=rooms[1].id,
                 day_of_week="Thursday", date=dates_by_day["Thursday"], start_time="14:00", end_time="17:00", duration_hours=3.0, academic_week=1,
                 duty_title="Mid-Term Exam Room Invigilation Room LH-302"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac2.id, subject_id=subjects[1].id, class_id=classes[1].id, classroom_id=rooms[2].id,
                 day_of_week="Friday", date=dates_by_day["Friday"], start_time="10:00", end_time="11:00", duration_hours=1.0, academic_week=1,
                 duty_title="DBMS: Concurrency Control Protocols"),
        Schedule(schedule_type="college_duty", faculty_id=fac2.id, subject_id=None, class_id=None, classroom_id=rooms[6].id,
                 day_of_week="Saturday", date=dates_by_day["Saturday"], start_time="10:00", end_time="13:00", duration_hours=3.0, academic_week=1,
                 duty_title="Internal Quality Assurance Cell (IQAC) Audit"),

        # --- Dr. Rohit Gupta (Balanced ~ 13 hours) ---
        Schedule(schedule_type="regular_lecture", faculty_id=fac3.id, subject_id=subjects[2].id, class_id=classes[0].id, classroom_id=rooms[0].id,
                 day_of_week="Monday", date=dates_by_day["Monday"], start_time="14:00", end_time="15:00", duration_hours=1.0, academic_week=1,
                 duty_title="Operating Systems: Memory Management"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac3.id, subject_id=subjects[3].id, class_id=classes[0].id, classroom_id=rooms[0].id,
                 day_of_week="Wednesday", date=dates_by_day["Wednesday"], start_time="11:00", end_time="12:00", duration_hours=1.0, academic_week=1,
                 duty_title="Computer Networks: TCP/IP Stack"),
        Schedule(schedule_type="lab_duty", faculty_id=fac3.id, subject_id=subjects[3].id, class_id=classes[0].id, classroom_id=rooms[5].id,
                 day_of_week="Thursday", date=dates_by_day["Thursday"], start_time="09:00", end_time="11:00", duration_hours=2.0, academic_week=1,
                 duty_title="Networks Packet Tracer Practical Lab"),
        Schedule(schedule_type="exam_duty", faculty_id=fac3.id, subject_id=None, class_id=classes[0].id, classroom_id=rooms[0].id,
                 day_of_week="Thursday", date=dates_by_day["Thursday"], start_time="14:00", end_time="17:00", duration_hours=3.0, academic_week=1,
                 duty_title="Exam Invigilation Duty LH-301"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac3.id, subject_id=subjects[2].id, class_id=classes[1].id, classroom_id=rooms[1].id,
                 day_of_week="Friday", date=dates_by_day["Friday"], start_time="09:00", end_time="10:00", duration_hours=1.0, academic_week=1,
                 duty_title="Operating Systems: Virtual Memory & Page Replacement"),
        Schedule(schedule_type="college_duty", faculty_id=fac3.id, subject_id=None, class_id=None, classroom_id=rooms[6].id,
                 day_of_week="Friday", date=dates_by_day["Friday"], start_time="14:00", end_time="18:00", duration_hours=4.0, academic_week=1,
                 duty_title="Campus Placement Drive Technical Evaluator"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac3.id, subject_id=subjects[3].id, class_id=classes[1].id, classroom_id=rooms[2].id,
                 day_of_week="Saturday", date=dates_by_day["Saturday"], start_time="10:00", end_time="11:00", duration_hours=1.0, academic_week=1,
                 duty_title="Computer Networks: Subnetting & Routing Protocols"),

        # --- Prof. Sneha Kulkarni (Balanced ~ 11 hours) ---
        Schedule(schedule_type="regular_lecture", faculty_id=fac4.id, subject_id=subjects[4].id, class_id=classes[0].id, classroom_id=rooms[2].id,
                 day_of_week="Monday", date=dates_by_day["Monday"], start_time="10:00", end_time="11:00", duration_hours=1.0, academic_week=1,
                 duty_title="AI: Search Strategies & A* Search"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac4.id, subject_id=subjects[4].id, class_id=classes[1].id, classroom_id=rooms[2].id,
                 day_of_week="Tuesday", date=dates_by_day["Tuesday"], start_time="14:00", end_time="15:00", duration_hours=1.0, academic_week=1,
                 duty_title="AI: Heuristic Functions & Game Trees"),
        Schedule(schedule_type="lab_duty", faculty_id=fac4.id, subject_id=subjects[4].id, class_id=classes[0].id, classroom_id=rooms[4].id,
                 day_of_week="Wednesday", date=dates_by_day["Wednesday"], start_time="14:00", end_time="16:00", duration_hours=2.0, academic_week=1,
                 duty_title="Machine Learning Python Lab"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac4.id, subject_id=subjects[4].id, class_id=classes[0].id, classroom_id=rooms[2].id,
                 day_of_week="Thursday", date=dates_by_day["Thursday"], start_time="11:00", end_time="12:00", duration_hours=1.0, academic_week=1,
                 duty_title="AI: Supervised Learning & SVMs"),
        Schedule(schedule_type="exam_duty", faculty_id=fac4.id, subject_id=None, class_id=classes[1].id, classroom_id=rooms[2].id,
                 day_of_week="Friday", date=dates_by_day["Friday"], start_time="14:00", end_time="17:00", duration_hours=3.0, academic_week=1,
                 duty_title="Mid-Term Exam Invigilation LH-303"),
        Schedule(schedule_type="college_duty", faculty_id=fac4.id, subject_id=None, class_id=None, classroom_id=rooms[6].id,
                 day_of_week="Saturday", date=dates_by_day["Saturday"], start_time="11:00", end_time="14:00", duration_hours=3.0, academic_week=1,
                 duty_title="Women in Tech Engineering Chapter Faculty Advisor"),

        # --- Prof. Vikram Singh (Low Workload ~ 8 hours -> Available for extra lectures/duties!) ---
        Schedule(schedule_type="regular_lecture", faculty_id=fac5.id, subject_id=subjects[5].id, class_id=classes[0].id, classroom_id=rooms[1].id,
                 day_of_week="Tuesday", date=dates_by_day["Tuesday"], start_time="15:00", end_time="16:00", duration_hours=1.0, academic_week=1,
                 duty_title="Software Engineering: Agile & Scrum"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac5.id, subject_id=subjects[5].id, class_id=classes[1].id, classroom_id=rooms[1].id,
                 day_of_week="Wednesday", date=dates_by_day["Wednesday"], start_time="15:00", end_time="16:00", duration_hours=1.0, academic_week=1,
                 duty_title="Software Engineering: UML & Architecture Diagrams"),
        Schedule(schedule_type="exam_duty", faculty_id=fac5.id, subject_id=None, class_id=classes[0].id, classroom_id=rooms[0].id,
                 day_of_week="Thursday", date=dates_by_day["Thursday"], start_time="14:00", end_time="17:00", duration_hours=3.0, academic_week=1,
                 duty_title="Mid-Term Exam Flying Squad Duty"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac5.id, subject_id=subjects[5].id, class_id=classes[0].id, classroom_id=rooms[1].id,
                 day_of_week="Friday", date=dates_by_day["Friday"], start_time="15:00", end_time="16:00", duration_hours=1.0, academic_week=1,
                 duty_title="Software Engineering: Software Testing & QA"),
        Schedule(schedule_type="college_duty", faculty_id=fac5.id, subject_id=None, class_id=None, classroom_id=rooms[6].id,
                 day_of_week="Saturday", date=dates_by_day["Saturday"], start_time="14:00", end_time="16:00", duration_hours=2.0, academic_week=1,
                 duty_title="Student Sports Committee Coordinator"),

        # --- Prof. Anita Desai (Low Workload ~ 7 hours -> Available for extra duties!) ---
        Schedule(schedule_type="regular_lecture", faculty_id=fac6.id, subject_id=subjects[1].id, class_id=classes[2].id, classroom_id=rooms[0].id,
                 day_of_week="Monday", date=dates_by_day["Monday"], start_time="15:00", end_time="16:00", duration_hours=1.0, academic_week=1,
                 duty_title="Web Engineering: Modern Frontend Architecture"),
        Schedule(schedule_type="regular_lecture", faculty_id=fac6.id, subject_id=subjects[1].id, class_id=classes[2].id, classroom_id=rooms[0].id,
                 day_of_week="Wednesday", date=dates_by_day["Wednesday"], start_time="16:00", end_time="17:00", duration_hours=1.0, academic_week=1,
                 duty_title="Web Engineering: RESTful API Design"),
        Schedule(schedule_type="lab_duty", faculty_id=fac6.id, subject_id=subjects[7].id, class_id=classes[2].id, classroom_id=rooms[3].id,
                 day_of_week="Thursday", date=dates_by_day["Thursday"], start_time="11:00", end_time="13:00", duration_hours=2.0, academic_week=1,
                 duty_title="Full Stack Web Dev Project Lab"),
        Schedule(schedule_type="exam_duty", faculty_id=fac6.id, subject_id=None, class_id=classes[2].id, classroom_id=rooms[0].id,
                 day_of_week="Friday", date=dates_by_day["Friday"], start_time="14:00", end_time="17:00", duration_hours=3.0, academic_week=1,
                 duty_title="Examination Invigilation LH-301"),
    ]
    db.add_all(schedules_data)
    db.commit()

    # 7. Seed Initial Notifications for Faculty
    for u in faculty_user_map.values():
        fac_obj = db.query(FacultyProfile).filter(FacultyProfile.id == u.faculty_id).first()
        n1 = Notification(
            user_id=u.id,
            title="Weekly Timetable Published",
            message=f"Welcome {fac_obj.name}. Your official weekly teaching schedule and college duties have been published by the HOD.",
            notification_type="assignment",
            channel="in_app, email",
            is_read=True,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
        )
        n2 = Notification(
            user_id=u.id,
            title="⏰ Upcoming Duty Reminder",
            message=f"Reminder: You have scheduled departmental duties this week. Check your timetable for classroom and lab locations.",
            notification_type="reminder",
            channel="in_app, browser",
            reminder_minutes=15,
            is_read=False,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=3)
        )
        db.add_all([n1, n2])
    db.commit()

    # 8. Seed Audit Log entries
    log1 = AuditLog(
        user_id=hod_user.id,
        username=hod_user.username,
        action="SEMESTER_INITIALIZATION",
        entity_type="System",
        details="Initial academic timetable and faculty workload distribution loaded for CSE Department.",
        timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=3)
    )
    db.add(log1)
    db.commit()

    print("[Seed Data] Database initialization and seed completed successfully!")
