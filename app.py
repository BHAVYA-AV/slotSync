import streamlit as st
from streamlit_oauth import OAuth2Component
import json
import gspread
import pandas as pd
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests
from google.oauth2.service_account import Credentials
from datetime import time, datetime, timedelta
import time as pytime

# =========================
# PAGE CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(layout="wide")

# =========================
# GOOGLE OAUTH SETUP
# =========================
with open("client_secret.json") as f:
    google_secrets = json.load(f)

CLIENT_ID = google_secrets["web"]["client_id"]
CLIENT_SECRET = google_secrets["web"]["client_secret"]

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REFRESH_TOKEN_URL = "https://oauth2.googleapis.com/token"

oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL,
    REFRESH_TOKEN_URL,
)

st.title("🔐 Login Required")

# =========================
# LOGIN FLOW (FIXED)
# =========================
if "token" not in st.session_state:

    result = oauth2.authorize_button(
        name="Login with Work Email",
        redirect_uri="http://localhost:8501",
        scope="openid email profile",
        key="google",
    )

    with st.expander("📖 How to use this booking system", expanded=False):
        st.markdown("""
### 👋 Welcome to the Course Slot Booking System

This tool allows instructors to **view availability, book slots, and delete their own bookings** safely.

You must log in using your **@study.iitm.ac.in email** to access the system.

---

# 📅 1. Viewing the Schedule

Open **“View Schedule”** to see the full weekly timetable.

### 🧭 How the timetable is arranged
- **Rows → Days**
- **Columns → Time slots (30-min each)**

### 🎨 Color meaning
- 🟢 **Free** → No levels running
- 🟡 **Partial** → Some levels busy, some free
- 🔴 **Full** → All levels busy

💡 Hover over any cell to see:
- Busy levels
- Free levels
- Courses running in that slot

This view shows **overall centre availability**, not course-specific availability.

---

# 📝 2. Booking Slots

Open **“Book Slots”** to schedule your course.

## Step 1 — Select your course
Only courses assigned to your email will appear.

---

## Step 2 — Check availability table

A **course-specific availability table** appears before booking.

Color meaning:
- 🟢 **Available** → You can book this slot
- 🔵 **Booked** → This course already runs here
- ⚪ **Busy / Conflict** → Cannot book due to clash

The system automatically checks:
- Same level conflicts  
- Prerequisite relationships  
- Existing bookings  

💡 This table prevents trial-and-error booking.

---

## Step 3 — Choose day and time range

Booking is done using a **time range picker**.

### ⏰ Time rules
- Booking happens in **30-minute blocks**
- Start time must be **before** end time
- End time is **exclusive** (like Google Calendar)
- Last slot of the day cannot be a start time

Example  
Start: 17:00  
End: 18:30  
→ Books: 17:00, 17:30, 18:00

---

## Step 4 — Click **Book Selected Slots**

The system will:
- Check all selected slots for conflicts
- Reject the booking if **any slot conflicts**
- Otherwise book the **entire range automatically**

You’ll see a success message and the timetable refreshes.

---

# 🗑️ 3. Deleting Booked Slots

Open **“Delete Booked Slots”**.

You will see a table showing **only your course bookings**.

Color meaning:
- 🔵 **Booked** → Can be deleted
- ⚪ **Empty** → Nothing to delete

### Steps to delete
1️⃣ Select your course  
2️⃣ Select day  
3️⃣ Select time range  
4️⃣ Click delete  

The system deletes the **entire selected range safely**.

---

# 🔒 Permissions & Safety

✔ Only college email login allowed  
✔ You see only your assigned courses  
✔ You can modify only your course bookings  
✔ Conflict detection prevents invalid scheduling  
✔ Range booking prevents partial mistakes  

---

# 💡 Tips for smooth scheduling

✔ Check availability table before booking  
✔ Book longer continuous blocks at once  
✔ Use hover tooltips to avoid clashes  
✔ Delete ranges to quickly free slots  

---

You're ready to use the scheduler 🎉
""")

    if result and "token" in result:
        st.session_state["token"] = result["token"]
        st.rerun()

    st.stop()

# =========================
# DECODE USER EMAIL SAFELY
# =========================
token = st.session_state["token"]
id_token_str = token["id_token"]

@st.cache_data(show_spinner=False)
def get_user_email_cached(id_token_str):
    idinfo = google_id_token.verify_oauth2_token(
        id_token_str,
        requests.Request(),
        CLIENT_ID
    )
    return idinfo["email"]

user_email = get_user_email_cached(id_token_str)

st.success(f"Logged in as {user_email}")

with st.expander("📖 How to use this booking system", expanded=False):
    st.markdown("""
### 👋 Welcome to the Course Slot Booking System

This tool allows instructors to **view availability, book slots, and delete their own bookings** safely.

You must log in using your **@study.iitm.ac.in email** to access the system.

---

# 📅 1. Viewing the Schedule

Open **“View Schedule”** to see the full weekly timetable.

### 🧭 How the timetable is arranged
- **Rows → Days**
- **Columns → Time slots (30-min each)**

### 🎨 Color meaning
- 🟢 **Free** → No levels running
- 🟡 **Partial** → Some levels busy, some free
- 🔴 **Full** → All levels busy

💡 Hover over any cell to see:
- Busy levels
- Free levels
- Courses running in that slot

This view shows **overall centre availability**, not course-specific availability.

---

# 📝 2. Booking Slots

Open **“Book Slots”** to schedule your course.

## Step 1 — Select your course
Only courses assigned to your email will appear.

---

## Step 2 — Check availability table

A **course-specific availability table** appears before booking.

Color meaning:
- 🟢 **Available** → You can book this slot
- 🔵 **Booked** → This course already runs here
- ⚪ **Busy / Conflict** → Cannot book due to clash

The system automatically checks:
- Same level conflicts  
- Prerequisite relationships  
- Existing bookings  

💡 This table prevents trial-and-error booking.

---

## Step 3 — Choose day and time range

Booking is done using a **time range picker**.

### ⏰ Time rules
- Booking happens in **30-minute blocks**
- Start time must be **before** end time
- End time is **exclusive** (like Google Calendar)
- Last slot of the day cannot be a start time

Example  
Start: 17:00  
End: 18:30  
→ Books: 17:00, 17:30, 18:00

---

## Step 4 — Click **Book Selected Slots**

The system will:
- Check all selected slots for conflicts
- Reject the booking if **any slot conflicts**
- Otherwise book the **entire range automatically**

You’ll see a success message and the timetable refreshes.

---

# 🗑️ 3. Deleting Booked Slots

Open **“Delete Booked Slots”**.

You will see a table showing **only your course bookings**.

Color meaning:
- 🔵 **Booked** → Can be deleted
- ⚪ **Empty** → Nothing to delete

### Steps to delete
1️⃣ Select your course  
2️⃣ Select day  
3️⃣ Select time range  
4️⃣ Click delete  

The system deletes the **entire selected range safely**.

---

# 🔒 Permissions & Safety

✔ Only college email login allowed  
✔ You see only your assigned courses  
✔ You can modify only your course bookings  
✔ Conflict detection prevents invalid scheduling  
✔ Range booking prevents partial mistakes  

---

# 💡 Tips for smooth scheduling

✔ Check availability table before booking  
✔ Book longer continuous blocks at once  
✔ Use hover tooltips to avoid clashes  
✔ Delete ranges to quickly free slots  

---

You're ready to use the scheduler 🎉
""")
    
ALLOWED_DOMAIN = "@study.iitm.ac.in"

if not user_email.endswith(ALLOWED_DOMAIN):
    st.error("Only college email allowed")
    st.stop()

# =========================
# GOOGLE SHEETS SETUP
# =========================
@st.cache_resource(show_spinner=False)
def connect_gsheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("key.json", scopes=scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=60, show_spinner="Loading timetable...")
def load_timetable():
    client = connect_gsheet()
    sheet = client.open("Course Slot Booking")
    timetable_ws = sheet.sheet1
    data = timetable_ws.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.fillna("").replace(" ", "").replace("  ", "")
    return df

df = load_timetable()

# we still need worksheet object for updates (not cached!)
client = connect_gsheet()
sheet = client.open("Course Slot Booking")
timetable_ws = sheet.sheet1

# ⭐ ADD THIS (needed for time-range booking)
time_slots = df["Time"].tolist()

@st.cache_data(ttl=300, show_spinner=False)
def load_courses_permissions():
    client = connect_gsheet()
    sheet = client.open("Course Slot Booking")

    courses_ws = sheet.worksheet("Courses")
    courses_data = courses_ws.get_all_values()
    courses_df = pd.DataFrame(courses_data[1:], columns=courses_data[0])

    perm_ws = sheet.worksheet("Permissions")
    perm_data = perm_ws.get_all_values()
    perm_df = pd.DataFrame(perm_data[1:], columns=perm_data[0])

    return courses_df, perm_df

courses_df, perm_df = load_courses_permissions()
levels = courses_df["Level"].unique().tolist()

allowed_courses = perm_df[perm_df["Email"] == user_email]["Course"].tolist()

if not allowed_courses:
    st.error("No courses assigned to this user.")
    st.stop()

# =========================
# HELPER FUNCTIONS
# =========================

def generate_slots_from_time_range(start_t, end_t):

    # convert sheet slot strings to datetime objects
    slot_times = [
        datetime.strptime(t, "%H:%M").time()
        for t in time_slots
    ]

    # find first slot >= start time
    start_candidates = [t for t in slot_times if t >= start_t]
    if not start_candidates:
        return []

    rounded_start = start_candidates[0]

    # find first slot >= end time  (END IS EXCLUSIVE)
    end_candidates = [t for t in slot_times if t >= end_t]
    if not end_candidates:
        end_idx = len(slot_times)
    else:
        end_idx = slot_times.index(end_candidates[0])

    start_idx = slot_times.index(rounded_start)

    return time_slots[start_idx:end_idx]

def get_course_info(course_name):

    if not course_name or str(course_name).strip() == "":
        return "Unknown", ""

    course_name = str(course_name).strip()

    match = courses_df[courses_df["Course"].str.strip() == course_name]

    if match.empty:
        return "Unknown", ""

    row = match.iloc[0]

    return row["Level"], row["Prerequisite"]

def get_all_prereqs(course, visited=None):
    if visited is None:
        visited = set()

    if course in visited:
        return visited

    visited.add(course)

    _, prereq = get_course_info(course)

    if prereq is None or str(prereq).strip() == "":
        return visited

    prereq_list = [p.strip() for p in str(prereq).split("|")]

    for p in prereq_list:
        if p not in visited:
            get_all_prereqs(p, visited)

    return visited

def is_prerequisite_pair(course1, course2):
    c1 = get_all_prereqs(course1)
    c2 = get_all_prereqs(course2)

    c1.discard(course1)
    c2.discard(course2)

    return course2 in c1 or course1 in c2

# def get_courses_in_same_slot(day, time):
#     row = df[df["Time"] == time].iloc[0]
#     cell = str(row[day]).strip()

#     if cell == "":
#         return []

#     return [c.strip() for c in cell.split("|")]


def get_courses_in_same_slot(day, time):
    row = df[df["Time"] == time].iloc[0]
    cell = str(row[day]).strip()

    if cell == "":
        return []

    return [
        c.strip().replace("\u00a0", "")
        for c in cell.split("|")
        if c.strip()
    ]

def has_conflict(selected_course, day, time):
    selected_level, _ = get_course_info(selected_course)
    booked_courses = get_courses_in_same_slot(day, time)

    for booked in booked_courses:
        booked_level, _ = get_course_info(booked)

        if selected_level == booked_level:
            if is_prerequisite_pair(selected_course, booked):
                continue
            return f"{booked} already running (same level & not prerequisite pair)."

    return None

def get_slot_status(day, time):
    row = df[df["Time"] == time].iloc[0]
    cell = str(row[day]).strip()

    status = {level: "free" for level in levels}

    if cell == "":
        return status

    booked_courses = [c.strip() for c in cell.split("|") if c.strip()]

    for course in booked_courses:
        level, _ = get_course_info(course)

        if level != "Unknown":
            status[level] = "busy"

    return status


def generate_half_hour_slots(start=time(16,0), end=time(23,30)):
    slots = []
    current = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)

    while current <= end_dt:
        slots.append(current.time())
        current += timedelta(minutes=30)

    return slots


# =========================
# UI - TIMETABLE
# =========================
with st.expander("📅 View Schedule", expanded=False):
    st.subheader("📊 Timetable Availability")
    st.markdown("""
    🟢 All levels are Free &nbsp;&nbsp; | &nbsp;&nbsp;
    🟡 Some levels are Busy &nbsp;&nbsp; | &nbsp;&nbsp;
    🔴 All levels are Busy
    """, unsafe_allow_html=True)

    days = df.columns[1:]
    times = df["Time"]

    html = """
    <style>
    table {border-collapse: collapse; width: 100%;}
    .cell {
        padding:8px;
        border:1px solid #ddd;
        text-align:center;
        font-size:13px;
        color:black;
        font-weight:600;
    }

    .green {background:#d4edda;}
    .red {background:#f8d7da;}
    .yellow {background:#fff3cd;}

    .header {
        background:#343a40;
        color:white;
        font-weight:bold;
    }
    </style>

    <table>
    <tr>
        <th class='header'>Time</th>
    """

    # 👉 TIMES AS COLUMN HEADERS
    for slot_time in times:
        html += f"<th class='header'>{slot_time}</th>"
    html += "</tr>"

    # 👉 DAYS AS ROWS
    for day in days:
        html += f"<tr><td class='header'>{day}</td>"

        for slot_time in times:

            status = get_slot_status(day, slot_time)
            busy_count = list(status.values()).count("busy")

            if busy_count == 0:
                color = "green"
                cell_html = "🟢 Free"
            elif busy_count == len(levels):
                color = "red"
                cell_html = "🔴 Full"
            else:
                color = "yellow"
                cell_html = "🟡 Partial"

            courses_here = get_courses_in_same_slot(day, slot_time)

            busy_levels = [lvl for lvl in levels if status[lvl] == "busy"]
            free_levels = [lvl for lvl in levels if status[lvl] == "free"]

            tooltip = (
                f"Busy: {', '.join(busy_levels) if busy_levels else 'None'}\n"
                f"Free: {', '.join(free_levels) if free_levels else 'None'}\n"
                f"Courses: {' | '.join(courses_here) if courses_here else 'None'}"
            )

            html += f"<td class='cell {color}' title='{tooltip}'>{cell_html}</td>"

        html += "</tr>"

    html += "</table>"

    st.components.v1.html(html, height=400, scrolling=True)

    st.divider()

# =========================
# BOOKING UI
# =========================
with st.expander("📝 Book Slots", expanded=False):


    course = st.selectbox("Select Course", allowed_courses).strip()

    st.markdown("### 🟢 Available slots for selected course")
    st.markdown(     "🟢 **Available** | 🔵 **Booked by this course** | ⚪ **Not available / conflict**")

    days = df.columns[1:]
    times = df["Time"]

    html = """
    <style>
    table {border-collapse: collapse; width: 100%;}
    .cell {
        padding:8px;
        border:1px solid #ddd;
        text-align:center;
        font-size:13px;
        color:black;
        font-weight:600;
    }
    .green {background:#c6f6c6;}
    .grey {background:#e6e6e6;}
    .blue {background:#cfe2ff;}

    .header {
        background:#343a40;
        color:white;
        font-weight:bold;
    }
    </style>

    <table>
    <tr>
        <th class='header'>Time</th>
    """

    # TIMES AS COLUMNS
    for slot_time in times:
        html += f"<th class='header'>{slot_time}</th>"
    html += "</tr>"

    # DAYS AS ROWS
    for day_i in days:
        html += f"<tr><td class='header'>{day_i}</td>"

        for slot_time in times:

            conflict_msg = has_conflict(course, day_i, slot_time)
            existing_courses = get_courses_in_same_slot(day_i, slot_time)

            if course in existing_courses:
                color = "blue"
                cell_html = "Booked"
                tooltip = "This course is already scheduled here"

            elif conflict_msg:
                color = "grey"
                cell_html = "Busy"
                tooltip = conflict_msg

            else:
                color = "green"
                cell_html = "Available"
                tooltip = "You can book this slot"

            html += f"<td class='cell {color}' title='{tooltip}'>{cell_html}</td>"

        html += "</tr>"

    html += "</table>"

    st.components.v1.html(html, height=280, scrolling=True)

    
    day = st.selectbox("Select Day", df.columns[1:])

    st.write("### Select Time Range")

    col3, col4 = st.columns(2)

    # =========================
    # HALF-HOUR SLOT PICKERS
    # =========================
    from datetime import datetime, timedelta, time


    half_hour_slots = generate_half_hour_slots()
    slot_strings = [t.strftime("%H:%M") for t in half_hour_slots]

    # ❗ REMOVE LAST SLOT FROM START TIME OPTIONS (prevents 23:00 start)
    start_slot_options = slot_strings[:-1]

    col3, col4 = st.columns(2)

    # --- START TIME ---
    with col3:
        start_slot_str = st.selectbox("Start Time", start_slot_options)
        start_time = datetime.strptime(start_slot_str, "%H:%M").time()

    # Safety guard (in case of cached session values)
    if start_slot_str == slot_strings[-1]:
        st.error("Start time cannot be the last slot of the day. Choose an earlier time.")
        st.stop()

    # --- END TIME (auto filtered) ---
    with col4:
        end_slot_strings = [
            s for s in slot_strings
            if datetime.strptime(s, "%H:%M").time() > start_time
        ]

        end_slot_str = st.selectbox("End Time", end_slot_strings)
        end_time = datetime.strptime(end_slot_str, "%H:%M").time()

    if st.button("Book Selected Slots"):


        # --- CONVERT TO SHEET SLOTS ---
        selected_times = generate_slots_from_time_range(start_time, end_time)

        if not selected_times:
            st.error("No valid 30-min slots fall inside this range")
            st.stop()

        # --- CHECK CONFLICTS ---
        conflicts = []

        for slot_time in selected_times:
            msg = has_conflict(course, day, slot_time)
            if msg:
                conflicts.append(f"{slot_time} → {msg}")

        if conflicts:
            st.error("Booking failed due to conflicts:")
            for c in conflicts:
                st.write("•", c)
        else:

            # --- WRITE TO SHEET ---
            for slot_time in selected_times:
                row_index = df.index[df["Time"] == slot_time][0] + 2
                col_index = list(df.columns).index(day) + 1

                existing = timetable_ws.cell(row_index, col_index).value

                if not existing:
                    new_value = course
                else:
                    courses = [c.strip() for c in existing.split("|")]
                    new_value = existing if course in courses else existing + " | " + course

                timetable_ws.update_cell(row_index, col_index, new_value)

            st.success("✅ Booking successful!")
            pytime.sleep(2)   # ← show message for 1 second
            st.cache_data.clear()
            st.rerun()

# =========================
# DELETE SLOTS (TIME RANGE VERSION)
# =========================
with st.expander("🗑️ Delete Booked Slots", expanded=False):

    del_course = st.selectbox("Select Course to Delete", allowed_courses)

    st.markdown("### 🗑️ Slots booked for selected course")

    st.markdown(
        "🔵 **Booked (can delete)** | ⚪ **No booking in this slot**"
    )

    days = df.columns[1:]
    times = df["Time"]

    html = """
    <style>
    table {border-collapse: collapse; width: 100%;}
    .cell {
        padding:8px;
        border:1px solid #ddd;
        text-align:center;
        font-size:13px;
        color:black;
        font-weight:600;
    }
    .blue {background:#cfe2ff;}
    .grey {background:#e6e6e6;}

    .header {
        background:#343a40;
        color:white;
        font-weight:bold;
    }
    </style>

    <table>
    <tr>
        <th class='header'>Time</th>
    """

    # times as columns
    for slot_time in times:
        html += f"<th class='header'>{slot_time}</th>"
    html += "</tr>"

    # days as rows
    for day_i in days:
        html += f"<tr><td class='header'>{day_i}</td>"

        for slot_time in times:
            existing_courses = get_courses_in_same_slot(day_i, slot_time)

            if del_course in existing_courses:
                color = "blue"
                text = "Booked"
                tooltip = "You can delete this slot"
            else:
                color = "grey"
                text = "-"
                tooltip = "No booking here"

            html += f"<td class='cell {color}' title='{tooltip}'>{text}</td>"

        html += "</tr>"

    html += "</table>"

    st.components.v1.html(html, height=280, scrolling=True)

    st.subheader("Delete your booked slots")

    del_day = st.selectbox("Select Day", df.columns[1:], key="del_day")

    st.write("### Select Time Range to Delete")

    # --- SAME HALF HOUR SLOT GENERATOR AS BOOKING ---

    half_hour_slots = generate_half_hour_slots()
    slot_strings = [t.strftime("%H:%M") for t in half_hour_slots]

    # ❗ REMOVE LAST SLOT FROM START TIME OPTIONS
    del_start_options = slot_strings[:-1]

    col3, col4 = st.columns(2)

    # --- START TIME ---
    with col3:
        del_start_str = st.selectbox("Start Time", del_start_options, key="del_start")
        del_start_time = datetime.strptime(del_start_str, "%H:%M").time()

    # Safety guard
    if del_start_str == slot_strings[-1]:
        st.error("Start time cannot be the last slot of the day. Choose an earlier time.")
        st.stop()

    # Safety guard (in case of cached session values)
    if start_slot_str == slot_strings[-1]:
        st.error("Start time cannot be the last slot of the day. Choose an earlier time.")
        st.stop()
    # --- END TIME (only after start) ---

    with col4:
        end_options = [
            s for s in slot_strings
            if datetime.strptime(s, "%H:%M").time() > del_start_time
        ]

        del_end_str = st.selectbox("End Time", end_options, key="del_end")
        del_end_time = datetime.strptime(del_end_str, "%H:%M").time()

    # =========================
    # DELETE BUTTON
    # =========================
    if st.button("Delete Selected Slots"):

        # convert range → sheet slots
        selected_times = generate_slots_from_time_range(del_start_time, del_end_time)

        if not selected_times:
            st.error("No valid 30-min slots fall inside this range")
            st.stop()

        del_course_clean = del_course.strip().replace("\u00a0", "")

        invalid_slots = []
        slot_data = []

        # --- VALIDATE ALL FIRST ---
        for slot_time in selected_times:

            row_match = df.index[df["Time"] == slot_time].tolist()
            if not row_match:
                invalid_slots.append(f"{slot_time} (invalid time)")
                continue

            row_index = row_match[0] + 2
            col_index = list(df.columns).index(del_day) + 1

            existing_value = timetable_ws.cell(row_index, col_index).value

            if not existing_value:
                invalid_slots.append(f"{slot_time} (empty slot)")
                continue

            courses = [
                c.strip().replace("\u00a0", "")
                for c in existing_value.split("|")
                if c and c.strip()
            ]

            if del_course_clean not in courses:
                invalid_slots.append(f"{slot_time} (course not present)")
                continue

            slot_data.append((row_index, col_index, courses))

        # ❌ If ANY invalid → STOP ALL deletion
        if invalid_slots:
            st.error("❌ Cannot delete because some slots are not yours:")
            for err in invalid_slots:
                st.write("•", err)
            st.stop()

        # ✅ ALL VALID → perform delete
        for row_index, col_index, courses in slot_data:
            courses.remove(del_course_clean)
            new_value = " | ".join(courses)
            timetable_ws.update_cell(row_index, col_index, new_value)

        st.success("🗑️ Slots deleted successfully!")
        pytime.sleep(2);
        st.cache_data.clear()
        st.rerun()