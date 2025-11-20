import flet as ft
import os, csv, json, shutil, webbrowser, sys
from pathlib import Path
from datetime import datetime, date

# --------- Smart folder locations (AppData) ---------
def get_app_paths():
    app_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "SmartStudy"
    data = base / "data"
    uploads = base / "uploads"
    books = uploads / "books"
    notes = uploads / "notes"
    for p in (base, data, uploads, books, notes):
        p.mkdir(parents=True, exist_ok=True)
    return app_dir, data, uploads, books, notes

APP_DIR, DATA_DIR, UPLOADS_DIR, BOOKS_DIR, NOTES_DIR = get_app_paths()
USERS_CSV = str(DATA_DIR / "users.csv")
COURSES_CSV = str(DATA_DIR / "courses.csv")
NOTES_CSV = str(DATA_DIR / "notes.csv")
PROGRESS_CSV = str(DATA_DIR / "progress.csv")
THEME_JSON = str(DATA_DIR / "theme.json")

USER_HEADERS = ["username", "password", "first_time", "class", "board", "stream", "goal"]
COURSE_HEADERS = ["username", "class", "stream", "subject", "chapters"]
NOTES_HEADERS = ["username", "title", "filepath", "date"]
PROGRESS_HEADERS = ["username", "subject", "chapter", "done"]

def ensure_csv(path, headers):
    if (not os.path.exists(path)) or (os.path.getsize(path) == 0):
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

def read_csv_dicts(path, headers):
    ensure_csv(path, headers)
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k: r.get(k, "") for k in headers})
    return rows

def write_csv_dicts(path, headers, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in headers})

def append_csv_row(path, headers, row_dict):
    exists = os.path.exists(path) and os.path.getsize(path) > 0
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not exists:
            writer.writeheader()
        writer.writerow({k: row_dict.get(k, "") for k in headers})

def read_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

ensure_csv(USERS_CSV, USER_HEADERS)
ensure_csv(COURSES_CSV, COURSE_HEADERS)
ensure_csv(NOTES_CSV, NOTES_HEADERS)
ensure_csv(PROGRESS_CSV, PROGRESS_HEADERS)

STREAM_SUBJECTS = {
    "Class 6": ["Mathematics", "Science", "English", "Social Science"],
    "Class 7": ["Mathematics", "Science", "English", "Social Science"],
    "Class 8": ["Mathematics", "Science", "English", "Social Science"],
    "Class 9": ["Mathematics", "Science", "English", "Social Science"],
    "Class 10": ["Mathematics", "Science", "English", "Social Science"],
    "Class 11 - Science (Maths)": ["Physics", "Chemistry", "Mathematics", "English"],
    "Class 11 - Science (Biology)": ["Physics", "Chemistry", "Biology", "English"],
    "Class 11 - Commerce": ["Accountancy", "Business Studies", "Economics", "English"],
    "Class 11 - Humanities": ["History", "Political Science", "Geography", "English"],
    "Class 12 - Science (Maths)": ["Physics", "Chemistry", "Mathematics", "English"],
    "Class 12 - Science (Biology)": ["Physics", "Chemistry", "Biology", "English"],
    "Class 12 - Commerce": ["Accountancy", "Business Studies", "Economics", "English"],
    "Class 12 - Humanities": ["History", "Political Science", "Geography", "English"],
    "JEE (PCM)": ["Physics", "Chemistry", "Mathematics"],
    "NEET (PCB)": ["Physics", "Chemistry", "Biology"]
}

PRELOADED_CHAPTERS = {
    "Mathematics": ["Number System", "Algebra Basics", "Geometry Basics", "Mensuration", "Data Handling"],
    "Science": ["Matter in Our Surroundings", "Is Matter Around Us Pure?", "Atoms and Molecules", "Motion and Measurement of Distances"],
    "English": ["Prose: Stories & Poems", "Writing Skills", "Grammar"],
    "Social Science": ["History: Ancient to Medieval", "Geography: Our Environment", "Civics: Democracy & Government"],
    "Physics": [
        "Physical World and Measurement", "Kinematics", "Laws of Motion", "Work, Energy and Power",
        "System of Particles and Rotational Motion", "Gravitation", "Mechanical Properties of Solids",
        "Mechanical Properties of Fluids", "Thermal Properties of Matter", "Thermodynamics", "Kinetic Theory",
        "Oscillations", "Waves"
    ],
    "Chemistry": [
        "Some Basic Concepts of Chemistry", "Structure of Atom", "Classification of Elements & Periodicity",
        "Chemical Bonding", "States of Matter", "Thermodynamics (Basics)", "Equilibrium (Basic)"
    ],
    "Mathematics (11)": [
        "Sets and Functions", "Relations and Functions", "Trigonometric Functions",
        "Principle of Mathematical Induction", "Complex Numbers", "Linear Inequalities",
        "Permutations and Combinations", "Binomial Theorem", "Sequences and Series"
    ],
    "Biology": [
        "Diversity in the Living World", "Structural Organisation in Animals and Plants",
        "Cell Structure and Function", "Plant Kingdom", "Human Physiology (Intro)"
    ],
    "Physics (12)": [
        "Electrostatics", "Current Electricity", "Magnetic Effects of Current and Magnetism",
        "Electromagnetic Induction", "Alternating Current", "Electromagnetic Waves",
        "Optics", "Dual Nature of Matter", "Atoms and Nuclei", "Electronic Devices"
    ],
    "Chemistry (12)": [
        "Solid State", "Solutions", "Electrochemistry", "Chemical Kinetics", "Surface Chemistry",
        "Coordination Compounds", "Haloalkanes and Haloarenes", "Alcohols, Phenols and Ethers",
        "Aldehydes, Ketones and Carboxylic Acids", "Amines", "Biomolecules"
    ],
    "Mathematics (12)": [
        "Relations and Functions", "Inverse Trigonometric Functions", "Matrices and Determinants",
        "Continuity and Differentiability", "Application of Derivatives", "Integrals",
        "Differential Equations", "Probability"
    ]
}

def chapters_for(subject):
    if subject in PRELOADED_CHAPTERS:
        return PRELOADED_CHAPTERS[subject]
    if "Math" in subject or (subject == "Mathematics"):
        return PRELOADED_CHAPTERS.get("Mathematics (11)", PRELOADED_CHAPTERS.get("Mathematics", ["Chapter 1", "Chapter 2"]))
    if subject == "Chemistry":
        return PRELOADED_CHAPTERS.get("Chemistry", PRELOADED_CHAPTERS.get("Chemistry (12)", ["Chapter 1", "Chapter 2"]))
    if subject == "Biology":
        return PRELOADED_CHAPTERS.get("Biology", ["Chapter 1", "Chapter 2"])
    return PRELOADED_CHAPTERS.get(subject, ["Chapter 1", "Chapter 2"])

def load_users():
    return read_csv_dicts(USERS_CSV, USER_HEADERS)

def save_users(rows):
    write_csv_dicts(USERS_CSV, USER_HEADERS, rows)

def user_exists(username):
    return any(u["username"] == username for u in load_users())

def add_user(username, password):
    append_csv_row(USERS_CSV, USER_HEADERS, {
        "username": username, "password": password, "first_time": "yes",
        "class": "", "board": "", "stream": "", "goal": ""
    })

def validate_login(username, password):
    for u in load_users():
        if u["username"] == username and u["password"] == password:
            return u
    return None

def load_courses():
    return read_csv_dicts(COURSES_CSV, COURSE_HEADERS)

def save_courses(rows):
    write_csv_dicts(COURSES_CSV, COURSE_HEADERS, rows)

def ensure_user_courses(username, class_name, stream_name):
    rows = load_courses()
    subjects = STREAM_SUBJECTS.get(stream_name) or STREAM_SUBJECTS.get(f"Class {class_name}") or ["Mathematics", "Science"]
    existing = {(r["username"], r["subject"]) for r in rows}
    changed = False
    for s in subjects:
        if (username, s) not in existing:
            chs = chapters_for(s)
            rows.append({"username": username, "class": class_name, "stream": stream_name, "subject": s, "chapters": "||".join(chs)})
            changed = True
    if changed:
        save_courses(rows)

def get_user_courses(username):
    return [r for r in load_courses() if r["username"] == username]

def update_course_chapters(username, subject, new_chapters):
    rows = load_courses()
    for r in rows:
        if r["username"] == username and r["subject"] == subject:
            r["chapters"] = "||".join(new_chapters)
    save_courses(rows)

def load_notes():
    return read_csv_dicts(NOTES_CSV, NOTES_HEADERS)

def save_notes(rows):
    write_csv_dicts(NOTES_CSV, NOTES_HEADERS, rows)

def add_note(username, title, filepath):
    append_csv_row(NOTES_CSV, NOTES_HEADERS, {"username": username, "title": title, "filepath": filepath, "date": date.today().isoformat()})

def load_progress():
    return read_csv_dicts(PROGRESS_CSV, PROGRESS_HEADERS)

def save_progress(rows):
    write_csv_dicts(PROGRESS_CSV, PROGRESS_HEADERS, rows)

def set_progress(username, subject, chapter, done=True):
    rows = load_progress()
    found = False
    for r in rows:
        if r["username"] == username and r["subject"] == subject and r["chapter"] == chapter:
            r["done"] = "yes" if done else "no"
            found = True
            break
    if not found:
        rows.append({"username": username, "subject": subject, "chapter": chapter, "done": "yes" if done else "no"})
    save_progress(rows)

def is_done(username, subject, chapter):
    for r in load_progress():
        if r["username"] == username and r["subject"] == subject and r["chapter"] == chapter:
            return r.get("done","no") == "yes"
    return False

def subject_progress_percent(username, subject):
    chs = chapters_for(subject)
    total = len(chs)
    if total == 0:
        return 0
    done = sum(1 for r in load_progress() if r["username"]==username and r["subject"]==subject and r.get("done","no")=="yes")
    return int((done/total)*100)

def main(page: ft.Page):
    page.title = "SmartStudy Companion"
    page.window_width = 1150
    page.window_height = 720

    theme = read_json(THEME_JSON, {"mode":"dark"}).get("mode","dark")
    page.theme_mode = ft.ThemeMode.DARK if theme=="dark" else ft.ThemeMode.LIGHT

    state = {"user": None, "record": None}

    file_picker = ft.FilePicker(on_result=lambda e: None)
    page.overlay.append(file_picker)
    state["file_picker"] = file_picker

    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_btn.icon = ft.Icons.WB_SUNNY
            write_json(THEME_JSON, {"mode":"light"})
        else:
            page.theme_mode = ft.ThemeMode.DARK
            theme_btn.icon = ft.Icons.DARK_MODE
            write_json(THEME_JSON, {"mode":"dark"})
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.WB_SUNNY,
        on_click=toggle_theme,
        tooltip="Toggle theme"
    )

    username_input = ft.TextField(label="Username", width=320)
    password_input = ft.TextField(label="Password", password=True, can_reveal_password=True, width=320)
    login_msg = ft.Text("", color=ft.Colors.RED_700)

    footer = ft.Container(
        content=ft.Text("By Diptanshu Kumar", size=13, color=ft.colors.GREY_400, italic=True),
        alignment=ft.alignment.center,
        padding=10
    )
    ROOT_COL = ft.Column([], expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    def show_layout(*body_widgets):
        ROOT_COL.controls.clear()
        ROOT_COL.controls.extend([
            *body_widgets,
            footer
        ])
        page.clean()
        page.add(ROOT_COL)
        page.update()

    def build_login_view():
        header = ft.Row([ft.Text("SmartStudy", size=24, weight=ft.FontWeight.W_700), ft.Container(expand=True), theme_btn])
        card = ft.Card(content=ft.Container(ft.Column([
            ft.Text("Login", size=20, weight=ft.FontWeight.W_600),
            username_input,
            password_input,
            ft.Row([ft.ElevatedButton("Login", on_click=on_login, width=140), ft.Container(width=12), ft.ElevatedButton("Register", on_click=build_register_view, width=140)]),
            login_msg
        ]), padding=16), width=560, elevation=4)
        show_layout(
            ft.Container(header, padding=10),
            ft.Container(card, alignment=ft.alignment.center, expand=True)
        )

    def build_register_view(e=None):
        username_input.value = ""
        password_input.value = ""
        login_msg.value = ""
        header = ft.Row([ft.Text("SmartStudy - Register", size=24, weight=ft.FontWeight.W_700), ft.Container(expand=True), theme_btn])
        card = ft.Card(content=ft.Container(ft.Column([
            ft.Text("Create Account", size=20, weight=ft.FontWeight.W_600),
            username_input,
            password_input,
            ft.Row([ft.ElevatedButton("Create", on_click=on_register, width=140), ft.Container(width=12), ft.TextButton("Back", on_click=lambda e: build_login_view())]),
            login_msg
        ]), padding=16), width=560, elevation=4)
        show_layout(
            ft.Container(header, padding=10),
            ft.Container(card, alignment=ft.alignment.center, expand=True)
        )

    def on_register(e):
        uname = (username_input.value or "").strip()
        pwd = (password_input.value or "")
        if not uname or not pwd:
            login_msg.value = "Username & password required"
            page.update()
            return
        if user_exists(uname):
            login_msg.value = "Username exists"
            page.update()
            return
        add_user(uname, pwd)
        login_msg.value = "Registered. Login now."
        page.update()
        build_login_view()

    def on_login(e):
        uname = (username_input.value or "").strip()
        pwd = (password_input.value or "")
        if not uname or not pwd:
            login_msg.value = "Enter username & password"
            page.update()
            return
        rec = validate_login(uname, pwd)
        if not rec:
            login_msg.value = "Invalid credentials"
            page.update()
            return
        state["user"] = uname
        state["record"] = rec
        if rec.get("first_time","yes") == "yes":
            build_onboarding_view()
        else:
            build_main_shell()

    cb_class = ft.Dropdown(label="Class", options=[ft.dropdown.Option(x) for x in ["6","7","8","9","10","11","12","Dropper"]], width=200)
    cb_board = ft.Dropdown(label="Board", options=[ft.dropdown.Option(x) for x in ["CBSE","ICSE","State Board","Other"]], width=200)
    cb_stream = ft.Dropdown(label="Stream", options=[ft.dropdown.Option(s) for s in STREAM_SUBJECTS.keys()], width=480)
    cb_goal = ft.Dropdown(label="Goal", options=[ft.dropdown.Option(x) for x in ["Boards/CBSE","IIT-JEE","NEET","Other"]], width=260)
    onb_msg = ft.Text("", color=ft.Colors.RED_700)

    def build_onboarding_view(e=None):
        header = ft.Row([ft.Text("First-time Setup", size=24, weight=ft.FontWeight.W_700), ft.Container(expand=True), theme_btn])
        card = ft.Card(content=ft.Container(ft.Column([
            ft.Text("Tell us about your class & stream", size=18, weight=ft.FontWeight.W_600),
            ft.Row([cb_class, cb_board]),
            ft.Row([cb_stream, cb_goal]),
            ft.ElevatedButton("Save & Create Course", on_click=on_save_onboarding),
            onb_msg
        ]), padding=16), width=820, elevation=4)
        show_layout(
            ft.Container(header, padding=10),
            ft.Container(card, alignment=ft.alignment.center, expand=True)
        )

    def on_save_onboarding(e):
        if not (cb_class.value and cb_board.value and cb_stream.value and cb_goal.value):
            onb_msg.value = "Fill all fields"
            page.update()
            return
        users = load_users()
        for u in users:
            if u["username"] == state["user"]:
                u["class"] = cb_class.value
                u["board"] = cb_board.value
                u["stream"] = cb_stream.value
                u["goal"] = cb_goal.value
                u["first_time"] = "no"
        save_users(users)
        ensure_user_courses(state["user"], cb_class.value, cb_stream.value)
        build_main_shell()

    nav = None
    main_content = ft.Container(expand=True)

    def build_main_shell():
        header = ft.Row([
            ft.Text(f"SmartStudy — {state['user']}", size=22, weight=ft.FontWeight.W_700),
            ft.Container(expand=True), theme_btn, ft.TextButton("Logout", on_click=on_logout)
        ])
        nonlocal nav
        nav = ft.NavigationRail(
            selected_index=0,
            extended=True,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Home"),
                ft.NavigationRailDestination(icon=ft.Icons.SCHOOL_OUTLINED, selected_icon=ft.Icons.SCHOOL, label="My Courses"),
                ft.NavigationRailDestination(icon=ft.Icons.MENU_BOOK_OUTLINED, selected_icon=ft.Icons.MENU_BOOK, label="Study Material"),
                ft.NavigationRailDestination(icon=ft.Icons.LIBRARY_BOOKS_OUTLINED, selected_icon=ft.Icons.LIBRARY_BOOKS, label="Books"),
                ft.NavigationRailDestination(icon=ft.Icons.NOTE_OUTLINED, selected_icon=ft.Icons.NOTE, label="Notes"),
                ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Settings"),
            ],
            on_change=on_nav_change,
            min_width=72,
            min_extended_width=180
        )
        nonlocal main_content
        main_content = ft.Container(expand=True)
        layout = ft.Row([nav, ft.VerticalDivider(width=1), main_content], expand=True)
        show_layout(
            ft.Container(header, padding=10),
            ft.Container(ft.Divider(), padding=0),
            layout
        )
        show_home()

    def on_nav_change(e):
        idx = e.control.selected_index
        if idx == 0:
            show_home()
        elif idx == 1:
            show_courses()
        elif idx == 2:
            show_study_material()
        elif idx == 3:
            show_books_view()
        elif idx == 4:
            show_notes()
        elif idx == 5:
            show_settings()

    def on_logout(e):
        state["user"] = None
        state["record"] = None
        username_input.value = ""
        password_input.value = ""
        build_login_view()

    def show_home():
        main_content.content = ft.Container(ft.Column([
            ft.Text(f"Welcome, {state['user']}!", size=24, weight=ft.FontWeight.W_700),
            ft.Text("Manage and access your study material, notes and video lectures.", size=14),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton("My Courses", on_click=lambda e: show_courses()),
                ft.Container(width=12),
                ft.ElevatedButton("Study Material", on_click=lambda e: show_study_material())
            ])
        ], spacing=12), padding=16)
        page.update()

    def show_courses():
        courses = get_user_courses(state["user"])
        if not courses:
            main_content.content = ft.Container(ft.Text("No courses found. Please set your stream in Settings or run onboarding."), padding=16)
            page.update()
            return
        cards = []
        for c in courses:
            subj = c["subject"]
            chs = [x for x in c.get("chapters","").split("||") if x]
            pct = subject_progress_percent(state["user"], subj)
            progress = ft.ProgressBar(width=300, value=pct/100)
            ch_controls = []
            def make_cb(s, chapter):
                def on_change_cb(ev):
                    set_progress(state["user"], s, chapter, done=ev.control.value)
                    show_courses()
                return ft.Checkbox(label=chapter, value=is_done(state["user"], s, chapter), on_change=on_change_cb)
            for ch in chs:
                ch_controls.append(make_cb(subj, ch))
            new_field = ft.TextField(label=f"Add chapter to {subj}", width=300)
            def make_add_handler(s, field, record):
                def h(e):
                    txt = (field.value or "").strip()
                    if not txt:
                        return
                    existing = [x for x in record.get("chapters","").split("||") if x]
                    update_course_chapters(state["user"], s, existing + [txt])
                    show_courses()
                return h
            add_btn = ft.ElevatedButton("Add Chapter", on_click=make_add_handler(subj, new_field, c))
            card = ft.Card(content=ft.Container(ft.Column([
                ft.Row([ft.Text(subj, size=18, weight=ft.FontWeight.W_600), ft.Container(expand=True), ft.Text(f"{pct}%")]),
                progress,
                ft.Divider(),
                *ch_controls,
                ft.Row([new_field, add_btn])
            ]), padding=12), elevation=2)
            cards.append(card)
        main_content.content = ft.Container(ft.Column(cards, scroll=ft.ScrollMode.AUTO), padding=12)
        page.update()

    def show_study_material():
        tab_books = build_books_tab()
        tab_videos = build_videos_tab()
        tabs = ft.Tabs(tabs=[ft.Tab(text="Books", content=tab_books), ft.Tab(text="Videos", content=tab_videos)], selected_index=0, expand=True)
        main_content.content = ft.Container(tabs, padding=12)
        page.update()

    def build_books_tab():
        search_field = ft.TextField(label="Search books / folders", width=420)
        book_list_col = ft.Column(scroll=ft.ScrollMode.AUTO)
        def refresh_list(_=None):
            book_list_col.controls.clear()
            try:
                entries = sorted(os.listdir(BOOKS_DIR))
            except FileNotFoundError:
                entries = []
            q = (search_field.value or "").lower()
            if not entries:
                book_list_col.controls.append(ft.Text("No books uploaded yet."))
            else:
                for name in entries:
                    if q and q not in name.lower():
                        continue
                    full = os.path.join(BOOKS_DIR, name)
                    if os.path.isdir(full):
                        pdfs = sorted([f for f in os.listdir(full) if f.lower().endswith(".pdf")])
                        inner = []
                        for p in pdfs:
                            pathp = os.path.join(full, p)
                            inner.append(ft.Row([ft.Text(p), ft.Container(expand=True), ft.ElevatedButton("Open", on_click=lambda e, x=pathp: open_file(x))]))
                        book_list_col.controls.append(ft.Card(content=ft.Container(ft.Column([ft.Text(f"[Folder] {name}", weight=ft.FontWeight.W_600), *inner]), padding=8), elevation=2))
                    elif name.lower().endswith(".pdf"):
                        fp = os.path.join(BOOKS_DIR, name)
                        book_list_col.controls.append(ft.Card(content=ft.Container(ft.Row([ft.Text(name), ft.Container(expand=True), ft.ElevatedButton("Open", on_click=lambda e, x=fp: open_file(x))]), padding=8), elevation=2))
            page.update()

        folder_field = ft.TextField(label="Book folder name (optional)", width=320)
        def create_folder(e):
            nm = (folder_field.value or "").strip()
            if not nm:
                page.snack_bar = ft.SnackBar(ft.Text("Provide a folder name"), open=True)
                page.update()
                return
            os.makedirs(os.path.join(BOOKS_DIR, nm), exist_ok=True)
            refresh_list()
        def on_upload_chapter(ev):
            def on_result(event):
                if event.files:
                    src = event.files[0].path
                    dest_dir = os.path.join(BOOKS_DIR, (folder_field.value or "").strip() or "")
                    os.makedirs(dest_dir, exist_ok=True)
                    dest = os.path.join(dest_dir, os.path.basename(src))
                    shutil.copy(src, dest)
                    refresh_list()
            state["file_picker"].on_result = on_result
            state["file_picker"].pick_files()
        def on_upload_full(ev):
            def on_result(event):
                if event.files:
                    src = event.files[0].path
                    dest = os.path.join(BOOKS_DIR, os.path.basename(src))
                    shutil.copy(src, dest)
                    refresh_list()
            state["file_picker"].on_result = on_result
            state["file_picker"].pick_files()
        refresh_list()
        controls = ft.Column([
            ft.Row([search_field, ft.ElevatedButton("Refresh", on_click=refresh_list)]),
            ft.Divider(),
            book_list_col,
            ft.Divider(),
            ft.Row([folder_field, ft.ElevatedButton("Create Folder", on_click=create_folder), ft.Container(width=8), ft.ElevatedButton("Upload Chapter into Book", on_click=on_upload_chapter), ft.Container(width=8), ft.ElevatedButton("Upload Full Book (PDF)", on_click=on_upload_full)])
        ], spacing=8)
        return ft.Container(controls, padding=12)

    def build_videos_tab():
        search_field = ft.TextField(label="Search YouTube", width=420)
        def on_search(ev):
            q = (search_field.value or "").strip()
            if not q:
                page.snack_bar = ft.SnackBar(ft.Text("Type something to search"), open=True)
                page.update()
                return
            webbrowser.open("https://www.youtube.com/results?search_query="+q.replace(" ", "+"))
        courses = get_user_courses(state["user"])
        subjects = [c["subject"] for c in courses]
        dd_subject = ft.Dropdown(label="Subject", options=[ft.dropdown.Option(s) for s in subjects], width=240)
        dd_chapter = ft.Dropdown(label="Chapter", width=420)
        def on_subj_change(ev):
            sel = dd_subject.value
            for c in courses:
                if c["subject"] == sel:
                    chs = [x for x in c.get("chapters","").split("||") if x]
                    dd_chapter.options = [ft.dropdown.Option(x) for x in chs]
                    dd_chapter.value = chs[0] if chs else None
                    break
            page.update()
        dd_subject.on_change = on_subj_change
        def open_lecture(ev):
            s = dd_subject.value
            ch = dd_chapter.value
            if not s or not ch:
                page.snack_bar = ft.SnackBar(ft.Text("Select subject and chapter"), open=True)
                page.update()
                return
            cls = state["record"].get("class","")
            q = f"Class {cls} {s} {ch} video lecture"
            webbrowser.open("https://www.youtube.com/results?search_query="+q.replace(" ", "+"))
        controls = ft.Column([
            ft.Row([search_field, ft.ElevatedButton("Search", on_click=on_search)]),
            ft.Divider(),
            ft.Text("Open lecture by chapter", weight=ft.FontWeight.W_600),
            ft.Row([dd_subject, dd_chapter, ft.ElevatedButton("Open Lecture", on_click=open_lecture)])
        ], spacing=8)
        return ft.Container(controls, padding=12)

    def show_books_view():
        main_content.content = build_books_tab()
        page.update()

    def show_notes():
        notes_all = load_notes()
        my = [n for n in notes_all if n["username"] == state["user"]]
        search_field = ft.TextField(label="Search notes by title", width=420)
        list_col = ft.Column(scroll=ft.ScrollMode.AUTO)
        def refresh_list(_=None):
            nonlocal my
            my = [n for n in load_notes() if n["username"] == state["user"]]
            list_col.controls.clear()
            q = (search_field.value or "").lower()
            if not my:
                list_col.controls.append(ft.Text("No notes yet. Upload one below."))
            else:
                for n in reversed(my):
                    if q and q not in n["title"].lower():
                        continue
                    p = n["filepath"]
                    rec = n
                    list_col.controls.append(ft.Card(content=ft.Container(ft.Column([
                        ft.Text(n["title"], weight=ft.FontWeight.W_600),
                        ft.Text(n["date"], size=11),
                        ft.Row([ft.ElevatedButton("Open", on_click=lambda e, x=p: open_file(x)),
                                ft.ElevatedButton("Save As", on_click=lambda e, x=p: save_as(x)),
                                ft.ElevatedButton("Delete", on_click=lambda e, r=rec: delete_note(r))])
                    ]), padding=8), elevation=2))
            page.update()
        def upload_note(ev):
            def on_result(event):
                if event.files:
                    src = event.files[0].path
                    dest_name = f"{state['user']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(src)}"
                    dest = os.path.join(NOTES_DIR, dest_name)
                    shutil.copy(src, dest)
                    add_note(state['user'], os.path.basename(src), dest)
                    page.snack_bar = ft.SnackBar(ft.Text("Note uploaded"), open=True)
                    page.update()
                    refresh_list()
            state["file_picker"].on_result = on_result
            state["file_picker"].pick_files()
        def save_as(src):
            page.snack_bar = ft.SnackBar(ft.Text(f"Open file location: {src}"), open=True)
            page.update()
            open_file(os.path.dirname(src))
        def delete_note(rec):
            alln = load_notes()
            new = [x for x in alln if not (x["username"]==rec["username"] and x["filepath"]==rec["filepath"])]
            save_notes(new)
            try:
                if os.path.exists(rec["filepath"]):
                    os.remove(rec["filepath"])
            except Exception:
                pass
            page.snack_bar = ft.SnackBar(ft.Text("Deleted"), open=True)
            page.update()
            refresh_list()
        refresh_list()
        main_content.content = ft.Container(ft.Column([ft.Row([search_field, ft.ElevatedButton("Search", on_click=refresh_list), ft.Container(expand=True), ft.ElevatedButton("Upload Note (PDF)", on_click=upload_note)]), ft.Divider(), list_col], spacing=8), padding=12)
        page.update()

    def show_settings():
        users = load_users()
        user = [u for u in users if u["username"]==state["user"]][0]
        class_dd = ft.Dropdown(label="Class", options=[ft.dropdown.Option(x) for x in ["6","7","8","9","10","11","12","Dropper"]], value=user.get("class") or "11", width=240)
        board_dd = ft.Dropdown(label="Board", options=[ft.dropdown.Option(x) for x in ["CBSE","ICSE","State Board","Other"]], value=user.get("board") or "CBSE", width=240)
        stream_dd = ft.Dropdown(label="Stream", options=[ft.dropdown.Option(x) for x in STREAM_SUBJECTS.keys()], value=user.get("stream") or list(STREAM_SUBJECTS.keys())[0], width=480)
        goal_dd = ft.Dropdown(label="Goal", options=[ft.dropdown.Option(x) for x in ["Boards/CBSE","IIT-JEE","NEET","Other"]], value=user.get("goal") or "Boards/CBSE", width=240)
        msg = ft.Text("", color=ft.Colors.GREEN_700)
        def save(e):
            users2 = load_users()
            for u in users2:
                if u["username"] == state["user"]:
                    u["class"] = class_dd.value or ""
                    u["board"] = board_dd.value or ""
                    u["stream"] = stream_dd.value or ""
                    u["goal"] = goal_dd.value or ""
            save_users(users2)
            ensure_user_courses(state["user"], class_dd.value, stream_dd.value)
            msg.value = "Saved"
            page.update()
        main_content.content = ft.Container(ft.Column([ft.Text("Settings", size=18, weight=ft.FontWeight.W_700), class_dd, board_dd, stream_dd, goal_dd, ft.ElevatedButton("Save", on_click=save), msg], spacing=8), padding=12)
        page.update()

    def open_file(path):
        if os.path.exists(path):
            try:
                if os.name == "nt":
                    os.startfile(path)
                else:
                    webbrowser.open("file://"+os.path.abspath(path))
            except Exception as e:
                page.snack_bar = ft.SnackBar(ft.Text(str(e)), open=True)
                page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("File missing"), open=True)
            page.update()

    build_login_view()

if __name__ == "__main__":
    ft.app(target=main)
