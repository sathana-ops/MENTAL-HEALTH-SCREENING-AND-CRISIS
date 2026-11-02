import csv
import hashlib
import hmac
import secrets
from datetime import date, datetime, timedelta
from pathlib import Path
from getpass import getpass

# In-memory Python lists replace the database.
users = []
journal_entries = []
questionnaire_records = []
next_user_id = 1
next_entry_id = 1
next_questionnaire_id = 1
ADMIN_PASSWORD = "admin123"


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"),
        bytes.fromhex(salt), 200_000
    ).hex()


def ask_int(prompt, minimum=None, maximum=None):
    while True:
        try:
            value = int(input(prompt).strip())
            if minimum is not None and value < minimum:
                print(f"Enter {minimum} or higher.")
                continue
            if maximum is not None and value > maximum:
                print(f"Enter {maximum} or lower.")
                continue
            return value
        except ValueError:
            print("Please enter a whole number.")


# -------------------- ACCOUNT SYSTEM --------------------

def sign_up():
    global next_user_id
    print("\n--- CREATE ACCOUNT ---")
    username = input("Username: ").strip()
    email = input("Email (optional): ").strip()
    password = getpass("Password: ")

    if not username or not password:
        print("Username and password are required.")
        return

    if any(u["username"].lower() == username.lower() for u in users):
        print("That username already exists.")
        return

    salt = secrets.token_hex(16)
    users.append({
        "user_id": next_user_id,
        "username": username,
        "email": email,
        "password_hash": hash_password(password, salt),
        "salt": salt,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    next_user_id += 1
    print("Account created successfully!")


def login():
    print("\n--- LOGIN ---")
    username = input("Username: ").strip()
    password = getpass("Password: ")

    for user in users:
        if user["username"].lower() == username.lower():
            entered_hash = hash_password(password, user["salt"])
            if hmac.compare_digest(entered_hash, user["password_hash"]):
                print(f"\nWelcome, {user['username']}!")
                return user["user_id"]

    print("Invalid username or password.")
    return None


def find_user(user_id):
    return next(
        (user for user in users if user["user_id"] == user_id),
        None
    )


# -------------------- JOURNAL AND MOOD --------------------

def journal_module(user_id):
    global next_entry_id
    print("\n--- DAILY MOOD JOURNAL ---")
    mood = ask_int("Rate your mood from 1 (low) to 10 (great): ", 1, 10)
    journal_text = input("Write a few lines about your day: ").strip()

    journal_entries.append({
        "entry_id": next_entry_id,
        "user_id": user_id,
        "entry_date": date.today().isoformat(),
        "mood_rating": mood,
        "journal_text": journal_text,
    })
    next_entry_id += 1
    print("Your journal entry has been saved in memory.")
    recommendation_for_mood(mood)


def recommendation_for_mood(mood):
    print("\n--- WELLBEING SUGGESTION ---")

    if mood <= 3:
        print("Consider talking with someone you trust.")
    elif mood <= 6:
        print("Try a short walk or a creative activity.")
    else:
        print("Keep doing the healthy things that support you.")

    print("These suggestions are not a medical diagnosis.")


def recommendation_module(user_id):
    entries = [
        e for e in journal_entries if e["user_id"] == user_id
    ]

    if not entries:
        print("No journal entries yet. Write one first.")
        return

    latest = max(
        entries,
        key=lambda e: (e["entry_date"], e["entry_id"])
    )
    recommendation_for_mood(latest["mood_rating"])


def seven_day_report(user_id):
    print("\n--- SEVEN-DAY WELLBEING REPORT ---")
    start_date = (date.today() - timedelta(days=6)).isoformat()

    entries = [
        e for e in journal_entries
        if e["user_id"] == user_id
        and e["entry_date"] >= start_date
    ]
    entries.sort(key=lambda e: (e["entry_date"], e["entry_id"]))

    if not entries:
        print("No journal entries found in the last seven days.")
        return

    average = sum(e["mood_rating"] for e in entries) / len(entries)
    print(f"Check-ins: {len(entries)}")
    print(f"Average mood: {average:.1f}/10")

    for entry in entries:
        note = entry["journal_text"].replace("\n", " ")
        if len(note) > 60:
            note = note[:57] + "..."
        print(
            f"{entry['entry_date']} | "
            f"Mood {entry['mood_rating']}/10 | {note}"
        )


# -------------------- CHATBOT AND ACTIVITIES --------------------

def ai_chatbot():
    print("\n--- MINDCARE SUPPORT CHATBOT ---")
    print("Type 'exit' to return to the menu.")

    while True:
        message = input("You: ").lower().strip()

        if message in {"exit", "quit", "bye"}:
            print("MindCare AI: Take care of yourself.")
            return
        elif "stress" in message or "overwhelmed" in message:
            answer = "Pause and take a comfortable breath."
        elif "sleep" in message or "tired" in message:
            answer = "A regular sleep schedule may help."
        elif "sad" in message or "lonely" in message:
            answer = "Consider speaking with someone you trust."
        elif "anxious" in message or "worry" in message:
            answer = "Notice five things you can see around you."
        elif "study" in message or "exam" in message:
            answer = "Break your work into small tasks."
        elif "happy" in message or "good" in message:
            answer = "Notice what helped you feel this way."
        else:
            answer = "Thank you for sharing. What small thing might help now?"

        print("MindCare AI:", answer)
        print("(This chatbot is not a therapist or emergency service.)")


def stress_relief():
    print("\n--- STRESS-RELIEF ACTIVITIES ---")
    print("1. Comfortable breathing pause")
    print("2. Grounding activity")
    print("3. Listen to calming music")
    print("4. Take a short break")

    tips = {
        "1": "Breathe naturally and relax your shoulders.",
        "2": "Notice five things you can see around you.",
        "3": "Listen to music that makes you feel comfortable.",
        "4": "Take a short break and return when ready.",
    }

    choice = input("Choose an activity (1-4): ").strip()
    print(tips.get(choice, "Please choose a number from 1 to 4."))


def mini_game():
    print("\n--- MINDFUL MINI-GAME ---")
    print("Find the missing number: 2, 4, 6, 8, ?")

    if input("Your answer: ").strip() == "10":
        print("Correct! The pattern adds 2 each time.")
    else:
        print("The answer is 10 because the pattern adds 2 each time.")
        # -------------------- CSV EXPORT --------------------

def export_csv(user_id):
    entries = sorted(
        [e for e in journal_entries if e["user_id"] == user_id],
        key=lambda e: (e["entry_date"], e["entry_id"])
    )

    output_path = Path("mindcare_export.csv")

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Entry ID", "User ID", "Date", "Mood", "Journal Text"
        ])

        for entry in entries:
            writer.writerow([
                entry["entry_id"],
                entry["user_id"],
                entry["entry_date"],
                entry["mood_rating"],
                entry["journal_text"]
            ])

    print(f"Exported {len(entries)} entries to: {output_path}")


# -------------------- WELLBEING QUESTIONNAIRE --------------------

def wellbeing_questionnaire(user_id):
    global next_questionnaire_id
    user = find_user(user_id)

    if user is None:
        print("User not found.")
        return

    print("\n--- WELLBEING QUESTIONNAIRE ---")
    print("Answer only what you feel comfortable sharing.")

    record = {
        "record_id": next_questionnaire_id,
        "user_id": user_id,
        "user_name": user["username"],
        "cur_mood": input("How have you been feeling lately? ").strip(),
        "stress": input(
            "Have you been feeling stressed or overwhelmed? "
        ).strip(),
        "sleep_appetite": input(
            "Any changes in sleep, appetite, or energy? "
        ).strip(),
        "emotions_coping": input(
            "What do you do when worried or sad? "
        ).strip(),
        "support_network": input(
            "Is there someone you trust whom you can talk to? "
        ).strip(),
        "safety": input(
            "Do you feel safe and supported right now? "
        ).strip(),
        "joy_resilience": input(
            "What activities help you feel better? "
        ).strip(),
        "need_professional_help": input(
            "Would you like professional support? (Yes/No/Unsure): "
        ).strip(),
        "response_date": date.today().isoformat(),
    }

    questionnaire_records.append(record)
    next_questionnaire_id += 1
    print("Your answers are saved in memory. This is not a diagnosis.")
    print(
        "If you feel unsafe or need urgent help, contact a trusted adult "
        "or local emergency service."
    )


# -------------------- OPTIONAL CAMERA CHECK --------------------

def camera_check():
    print("\n--- OPTIONAL CAMERA FACE-PRESENCE CHECK ---")
    print("This checks for a visible face. It does not identify you or infer emotions.")

    choice = input("Open your camera? (yes/no): ").strip().lower()

    if choice != "yes":
        print("Camera check cancelled.")
        return

    try:
        import cv2
    except ImportError:
        print("OpenCV is optional. Install it with:")
        print("!pip install opencv-python")
        return

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Could not open the camera.")
        camera.release()
        return

    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    try:
        print("Press Q in the camera window to close.")

        while True:
            ok, frame = camera.read()

            if not ok:
                print("Could not read from camera.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=4
            )

            label = "Face visible" if len(faces) else "No face detected"

            cv2.putText(
                frame, label, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (0, 200, 0), 2
            )

            for x, y, w, h in faces:
                cv2.rectangle(
                    frame, (x, y), (x + w, y + h),
                    (0, 200, 0), 2
                )

            cv2.imshow("MindCare Camera Check", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()


# -------------------- ADMIN SYSTEM --------------------

def admin_login():
    entered_password = getpass("Admin password: ")

    if hmac.compare_digest(entered_password, ADMIN_PASSWORD):
        admin_menu()
    else:
        print("Incorrect admin password.")


def admin_menu():
    while True:
        print("""
--- ADMIN MENU ---
1. View users
2. View journal entries
3. View questionnaire records
4. Export all journal entries to CSV
5. Delete a user
6. Return to main menu
""")

        choice = input("Choose (1-6): ").strip()

        if choice == "1":
            for user in users:
                print({
                    key: user[key]
                    for key in (
                        "user_id", "username", "email", "created_at"
                    )
                })

            if not users:
                print("No users found.")

        elif choice == "2":
            for entry in journal_entries:
                print(entry)

            if not journal_entries:
                print("No journal entries found.")

        elif choice == "3":
            for record in questionnaire_records:
                print(record)

            if not questionnaire_records:
                print("No questionnaire records found.")

        elif choice == "4":
            path = Path("mindcare_all_journals.csv")

            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Entry ID", "User ID", "Date", "Mood", "Journal Text"
                ])

                for entry in journal_entries:
                    writer.writerow([
                        entry["entry_id"],
                        entry["user_id"],
                        entry["entry_date"],
                        entry["mood_rating"],
                        entry["journal_text"]
                    ])

            print(f"Exported all entries to: {path}")

        elif choice == "5":
            try:
                user_id = int(input("User ID to delete: ").strip())
            except ValueError:
                print("Please enter a valid numeric user ID.")
                continue

            confirm = input(
                f"Delete user {user_id} and linked records? (yes/no): "
            ).strip().lower()

            if confirm == "yes":
                if find_user(user_id):
                    users[:] = [
                        u for u in users if u["user_id"] != user_id
                    ]
                    journal_entries[:] = [
                        e for e in journal_entries
                        if e["user_id"] != user_id
                    ]
                    questionnaire_records[:] = [
                        r for r in questionnaire_records
                        if r["user_id"] != user_id
                    ]
                    print("User deleted.")
                else:
                    print("User ID not found.")
            else:
                print("Deletion cancelled.")

        elif choice == "6":
            return

        else:
            print("Please choose a number from 1 to 6.")
            # -------------------- TEAMWORK FEATURES --------------------

def teamwork_module(user_id):
    teamwork_history = []

    while True:
        print("""
========== TEAMWORK WELLBEING MENU ==========
1. Wellbeing Assessment
2. AI Support Chatbot
3. Daily Mood Tracker
4. Stress Relief Tips
5. Mini Games
6. Wellbeing Report
7. Return to MindCare menu
""")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            print("\n--- WELLBEING ASSESSMENT ---")
            mood = input("How are you feeling today? ").strip()

            try:
                stress = int(input("Rate your stress level (1-10): "))
                sleep = float(input("How many hours did you sleep? "))
                energy = int(input("Rate your energy level (1-10): "))

                if not 1 <= stress <= 10 or not 1 <= energy <= 10:
                    print("Stress and energy must be from 1 to 10.")
                    continue

                if not 0 <= sleep <= 24:
                    print("Sleep must be between 0 and 24 hours.")
                    continue

            except ValueError:
                print("Please enter valid numbers.")
                continue

            record = {
                "mood": mood,
                "stress": stress,
                "sleep": sleep,
                "energy": energy,
                "date": date.today().isoformat()
            }

            teamwork_history.append(record)

            print("\nYour Assessment:")
            print("Mood:", mood)
            print("Stress Level:", stress)
            print("Sleep Hours:", sleep)
            print("Energy Level:", energy)

            if stress >= 8:
                print("Suggestion: Take a relaxing break.")
            elif stress >= 5:
                print("Suggestion: Try a calming activity.")
            else:
                print("Suggestion: Keep following healthy routines.")

            print("This is general wellbeing support, not a diagnosis.")

        elif choice == "2":
            print("\n--- MINDCARE SUPPORT CHATBOT ---")
            message = input("How can I help you? ").lower().strip()

            if "stress" in message or "overwhelmed" in message:
                print("MindCare AI: Take a comfortable pause and relax.")
            elif "sleep" in message or "tired" in message:
                print("MindCare AI: Try a regular sleep routine.")
            elif "sad" in message or "lonely" in message:
                print("MindCare AI: Talk with someone you trust.")
            elif "study" in message or "exam" in message:
                print("MindCare AI: Divide your work into smaller tasks.")
            elif "happy" in message or "good" in message:
                print("MindCare AI: Enjoy your positive moment.")
            else:
                print("MindCare AI: Thank you for sharing. Take care!")

            print("This chatbot is not a therapist or emergency service.")

        elif choice == "3":
            print("\n--- DAILY MOOD TRACKER ---")
            mood = input("Enter your current mood: ").strip()

            teamwork_history.append({
                "mood": mood,
                "stress": "Not recorded",
                "sleep": "Not recorded",
                "energy": "Not recorded",
                "date": date.today().isoformat()
            })

            print("Your mood has been recorded!")

        elif choice == "4":
            print("\n--- STRESS RELIEF ASSISTANT ---")
            print("1. Comfortable breathing pause")
            print("2. Grounding activity")
            print("3. Listen to calming music")
            print("4. Take a short break")

            activity = input("Choose an activity (1-4): ").strip()

            tips = {
                "1": "Breathe naturally and relax your shoulders.",
                "2": "Notice five things you can see around you.",
                "3": "Listen to music that makes you feel comfortable.",
                "4": "Take a short break and return when ready."
            }

            print(tips.get(activity, "Please select a valid activity."))

        elif choice == "5":
            print("\n--- MINDFUL MINI-GAME ---")
            answer = input("Find the missing number: 2, 4, 6, 8, ? ")

            if answer.strip() == "10":
                print("Correct! The pattern adds 2 each time.")
            else:
                print("Good try! The answer is 10.")

        elif choice == "6":
            print("\n--- WELLBEING REPORT ---")

            if not teamwork_history:
                print("No records available yet.")
            else:
                print("Total Check-ins:", len(teamwork_history))

                for index, record in enumerate(teamwork_history, 1):
                    print("\nRecord", index)
                    print("Date:", record["date"])
                    print("Mood:", record["mood"])
                    print("Stress:", record["stress"])
                    print("Sleep:", record["sleep"])
                    print("Energy:", record["energy"])

        elif choice == "7":
            return

        else:
            print("Invalid choice. Please try again.")


# -------------------- USER MENU --------------------

def user_menu(user_id):
    while True:
        print("""
========== MINDCARE USER MENU ==========
1. Write journal / mood check-in
2. Get mood recommendation
3. Seven-day wellbeing report
4. Support chatbot
5. Stress-relief activities
6. Mini-game
7. Export my journal to CSV
8. Wellbeing questionnaire
9. Optional camera face-presence check
10. Teamwork wellbeing features
11. Logout
""")

        choice = input("Choose (1-11): ").strip()

        actions = {
            "1": lambda: journal_module(user_id),
            "2": lambda: recommendation_module(user_id),
            "3": lambda: seven_day_report(user_id),
            "4": ai_chatbot,
            "5": stress_relief,
            "6": mini_game,
            "7": lambda: export_csv(user_id),
            "8": lambda: wellbeing_questionnaire(user_id),
            "9": camera_check,
            "10": lambda: teamwork_module(user_id)
        }

        if choice == "11":
            print("Logged out.")
            return

        action = actions.get(choice)

        if action:
            action()
        else:
            print("Please choose a number from 1 to 11.")


# -------------------- MAIN PROGRAM --------------------

def main():
    print("=" * 42)
    print("       WELCOME TO MINDCARE AI")
    print("       Your personal wellbeing helper")
    print("=" * 42)
    print("Admin demo password: admin123")
    print("Data is cleared when the program closes.")

    while True:
        print("""
========== MAIN MENU ==========
1. Sign up
2. Log in
3. Admin login
4. Exit
""")

        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            sign_up()

        elif choice == "2":
            user_id = login()

            if user_id is not None:
                user_menu(user_id)

        elif choice == "3":
            admin_login()

        elif choice == "4":
            print("Thank you for using MindCare AI. Take care!")
            break

        else:
            print("Please choose a number from 1 to 4.")


if __name__ == "__main__":
    main()