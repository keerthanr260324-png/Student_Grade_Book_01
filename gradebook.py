"""
Student Grade Book
BCA (Data Science) - Semester 1
Python Project 
A console application to store student marks, calculate totals, averages,
grades and results, rank the class and export a report.

Data is stored in a JSON file so it is not lost when the program is closed.
"""

import csv
import json
import statistics

DATA_FILE = "gradebook.json"
REPORT_FILE = "grade_report.csv"
CHART_FILE = "subject_averages.png"

SUBJECTS = ["Python", "Maths", "Statistics", "English", "Computer Fundamentals"]
PASS_MARK = 40          # a student must score at least this in EVERY subject

# (minimum average, grade) - checked from top to bottom
GRADE_SCALE = [(90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D"), (0, "F")]


# ------------------------------------------------------------------
# Part 1 : data handling (load / save)
# ------------------------------------------------------------------
def load_data(filename=DATA_FILE):
    """Read the students dictionary from a JSON file.
    If the file is missing or damaged an empty dictionary is returned."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("Warning: data file is damaged, starting with empty grade book.")
        return {}


def save_data(students, filename=DATA_FILE):
    """Write the students dictionary to a JSON file."""
    with open(filename, "w") as f:
        json.dump(students, f, indent=4)


# ------------------------------------------------------------------
# Part 2 : calculation functions (no input / print here, so they can be tested)
# ------------------------------------------------------------------
def is_valid_name(name):
    """A name must have at least one letter and contain only letters and spaces."""
    if name.strip() == "":
        return False
    for ch in name:
        if not (ch.isalpha() or ch == " "):
            return False
    return True


def calculate_total_average(marks):
    """marks is a dictionary {subject: mark}. Returns (total, average)."""
    total = sum(marks.values())
    average = total / len(marks)
    return total, average


def calculate_grade(average):
    """Return the grade letter for an average."""
    for minimum, grade in GRADE_SCALE:
        if average >= minimum:
            return grade
    return "F"


def get_result(marks):
    """PASS only if every subject is at or above the pass mark."""
    if all(m >= PASS_MARK for m in marks.values()):
        return "PASS"
    return "FAIL"


def rank_students(students):
    """Return a list of dictionaries sorted from highest to lowest total.
    Students with the same total get the same rank."""
    rows = []
    for roll, data in students.items():
        total, average = calculate_total_average(data["marks"])
        rows.append({
            "roll": roll,
            "name": data["name"],
            "total": total,
            "average": average,
            "grade": calculate_grade(average),
            "result": get_result(data["marks"]),
        })

    rows.sort(key=lambda r: r["total"], reverse=True)

    previous_total = None
    previous_rank = 0
    for position, row in enumerate(rows, start=1):
        if row["total"] == previous_total:
            row["rank"] = previous_rank
        else:
            row["rank"] = position
            previous_rank = position
            previous_total = row["total"]
    return rows


def subject_stats(students):
    """Average, highest and lowest mark for every subject."""
    stats = {}
    for subject in SUBJECTS:
        marks_list = [d["marks"][subject] for d in students.values()]
        stats[subject] = {
            "average": sum(marks_list) / len(marks_list),
            "highest": max(marks_list),
            "lowest": min(marks_list),
        }
    return stats


def class_summary(students):
    """Overall statistics of the class. Returns None if there are no students."""
    if not students:
        return None

    ranked = rank_students(students)
    averages = [r["average"] for r in ranked]
    passed = len([r for r in ranked if r["result"] == "PASS"])

    try:
        spread = statistics.stdev(averages)
    except statistics.StatisticsError:      # only one student, stdev not defined
        spread = 0.0

    return {
        "count": len(ranked),
        "mean": statistics.mean(averages),
        "median": statistics.median(averages),
        "std_dev": spread,
        "topper": ranked[0],
        "lowest": ranked[-1],
        "passed": passed,
        "pass_percent": passed / len(ranked) * 100,
    }


# ------------------------------------------------------------------
# Part 3 : input helpers
# ------------------------------------------------------------------
def ask_marks(subject):
    """Keep asking until a number between 0 and 100 is entered."""
    while True:
        text = input("   Marks in " + subject + " (0-100): ").strip()
        try:
            mark = float(text)
        except ValueError:
            print("   Please enter a number.")
            continue
        if 0 <= mark <= 100:
            return mark
        print("   Marks must be between 0 and 100.")


def ask_roll(students, must_exist):
    """Ask for a roll number. Returns None (with a message) if it is not usable."""
    roll = input("Enter roll number: ").strip()
    if not roll.isdigit():
        print("Roll number should contain digits only.")
        return None
    if must_exist and roll not in students:
        print("No student found with roll number", roll)
        return None
    if not must_exist and roll in students:
        print("Roll number", roll, "already exists.")
        return None
    return roll


# ------------------------------------------------------------------
# Part 4 : menu options
# ------------------------------------------------------------------
def add_student(students):
    roll = ask_roll(students, must_exist=False)
    if roll is None:
        return

    name = input("Enter student name: ").strip()
    if not is_valid_name(name):
        print("Name should contain only letters and spaces.")
        return

    marks = {}
    for subject in SUBJECTS:
        marks[subject] = ask_marks(subject)

    students[roll] = {"name": name.title(), "marks": marks}
    print("Student", name.title(), "added.")


def view_all(students):
    if not students:
        print("The grade book is empty.")
        return

    print()
    print("{:<5} {:<6} {:<18} {:>7} {:>7} {:>6} {:>7}".format(
        "Rank", "Roll", "Name", "Total", "Avg", "Grade", "Result"))
    print("-" * 62)
    for r in rank_students(students):
        print("{:<5} {:<6} {:<18} {:>7.1f} {:>7.2f} {:>6} {:>7}".format(
            r["rank"], r["roll"], r["name"], r["total"],
            r["average"], r["grade"], r["result"]))


def search_student(students):
    roll = ask_roll(students, must_exist=True)
    if roll is None:
        return

    data = students[roll]
    total, average = calculate_total_average(data["marks"])
    print("\nName   :", data["name"])
    print("Roll   :", roll)
    for subject, mark in data["marks"].items():
        flag = "" if mark >= PASS_MARK else "   <-- below pass mark"
        print("   {:<24}{:>6.1f}{}".format(subject, mark, flag))
    print("Total  : {:.1f} / {}".format(total, len(SUBJECTS) * 100))
    print("Average: {:.2f}".format(average))
    print("Grade  :", calculate_grade(average))
    print("Result :", get_result(data["marks"]))


def update_marks(students):
    roll = ask_roll(students, must_exist=True)
    if roll is None:
        return

    print("Choose subject:")
    for number, subject in enumerate(SUBJECTS, start=1):
        print("  ", number, "-", subject)

    try:
        choice = int(input("Enter number: "))
    except ValueError:
        print("Please enter a number.")
        return
    if choice < 1 or choice > len(SUBJECTS):
        print("Invalid subject number.")
        return
    subject = SUBJECTS[choice - 1]

    old = students[roll]["marks"][subject]
    new = ask_marks(subject)
    students[roll]["marks"][subject] = new
    print("{} marks changed from {} to {}.".format(subject, old, new))


def delete_student(students):
    roll = ask_roll(students, must_exist=True)
    if roll is None:
        return

    sure = input("Delete " + students[roll]["name"] + "? (y/n): ").strip().lower()
    if sure == "y":
        del students[roll]
        print("Student deleted.")
    else:
        print("Delete cancelled.")


def show_statistics(students):
    summary = class_summary(students)
    if summary is None:
        print("No data available for statistics.")
        return

    print("\n========== CLASS STATISTICS ==========")
    print("Number of students : ", summary["count"])
    print("Class mean         :  {:.2f}".format(summary["mean"]))
    print("Class median       :  {:.2f}".format(summary["median"]))
    print("Standard deviation :  {:.2f}".format(summary["std_dev"]))
    print("Topper             : ", summary["topper"]["name"],
          "({:.2f})".format(summary["topper"]["average"]))
    print("Lowest             : ", summary["lowest"]["name"],
          "({:.2f})".format(summary["lowest"]["average"]))
    print("Passed             :  {} of {} ({:.1f}%)".format(
        summary["passed"], summary["count"], summary["pass_percent"]))

    print("\nSubject-wise report")
    print("{:<24}{:>9}{:>9}{:>9}".format("Subject", "Average", "Highest", "Lowest"))
    print("-" * 51)
    for subject, s in subject_stats(students).items():
        print("{:<24}{:>9.2f}{:>9.1f}{:>9.1f}".format(
            subject, s["average"], s["highest"], s["lowest"]))

    # simple text bar chart of the grades
    grade_count = {}
    for r in rank_students(students):
        grade_count[r["grade"]] = grade_count.get(r["grade"], 0) + 1

    print("\nGrade distribution")
    for _, grade in GRADE_SCALE:
        print("  {:<3} {}".format(grade, "#" * grade_count.get(grade, 0)))

    weak = [r["name"] for r in rank_students(students) if r["result"] == "FAIL"]
    if weak:
        print("\nStudents who failed at least one subject:", ", ".join(weak))


def export_report(students, filename=REPORT_FILE):
    if not students:
        print("Nothing to export.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Roll", "Name"] + SUBJECTS +
                        ["Total", "Average", "Grade", "Result"])
        for r in rank_students(students):
            marks = students[r["roll"]]["marks"]
            writer.writerow([r["rank"], r["roll"], r["name"]] +
                            [marks[s] for s in SUBJECTS] +
                            [r["total"], round(r["average"], 2), r["grade"], r["result"]])
    print("Report saved as", filename)


def show_chart(students):
    """Bar chart of subject averages. Needs matplotlib (optional)."""
    if not students:
        print("No data to plot.")
        return
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed. Install it with: pip install matplotlib")
        return

    stats = subject_stats(students)
    names = list(stats.keys())
    averages = [stats[n]["average"] for n in names]

    plt.figure(figsize=(8, 4.5))
    plt.bar(names, averages, color="steelblue")
    plt.axhline(PASS_MARK, color="red", linestyle="--", label="Pass mark")
    plt.title("Subject-wise Class Average")
    plt.ylabel("Average marks")
    plt.ylim(0, 100)
    plt.xticks(rotation=20)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close()
    print("Chart saved as", CHART_FILE)


# ------------------------------------------------------------------
# Part 5 : main program
# ------------------------------------------------------------------
def show_menu():
    print("\n========== STUDENT GRADE BOOK ==========")
    print(" 1. Add student")
    print(" 2. View all students (ranked)")
    print(" 3. Search student")
    print(" 4. Update marks")
    print(" 5. Delete student")
    print(" 6. Class statistics")
    print(" 7. Export report to CSV")
    print(" 8. Subject average chart")
    print(" 9. Save and exit")


def main():
    students = load_data()
    print("Welcome! {} student(s) loaded.".format(len(students)))

    # menu choice -> function to call
    actions = {
        "1": add_student,
        "2": view_all,
        "3": search_student,
        "4": update_marks,
        "5": delete_student,
        "6": show_statistics,
        "7": export_report,
        "8": show_chart,
    }

    try:
        while True:
            show_menu()
            choice = input("Enter choice (1-9): ").strip()

            if choice == "9":
                break
            elif choice in actions:
                actions[choice](students)
            else:
                print("Invalid choice, please enter a number from 1 to 9.")
    except (KeyboardInterrupt, EOFError):
        print("\swapfile.sys")

    save_data(students)
    print("Data saved. Goodbye!")


if __name__ == "__main__":
    main()
