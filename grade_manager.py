import streamlit as st
import pandas as pd

# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------
st.set_page_config(
    page_title="Student Grade Manager",
    page_icon="🎓",
    layout="wide"
)

# -------------------------------------------------
# FUNCTIONS
# -------------------------------------------------

def calculate_grade(marks):
    """Calculate grade based on marks."""
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "F"


def calculate_status(marks_list):
    """Calculate Pass or Fail status."""
    if any(mark < 40 for mark in marks_list):
        return "Fail"
    return "Pass"


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "students" not in st.session_state:
    st.session_state.students = []


# -------------------------------------------------
# TITLE
# -------------------------------------------------

st.title("🎓 Student Grade Manager")
st.markdown("### Manage student information, multiple subjects, marks, and grades")

st.divider()


# -------------------------------------------------
# SIDEBAR - STUDENT DETAILS
# -------------------------------------------------

st.sidebar.header("👨‍🎓 Student Information")

student_id = st.sidebar.text_input("Student ID")
student_name = st.sidebar.text_input("Student Name")
student_class = st.sidebar.text_input("Class / Section")

st.sidebar.divider()

st.sidebar.header("📚 Subject Details")

number_of_subjects = st.sidebar.number_input(
    "Number of Subjects",
    min_value=1,
    max_value=10,
    value=5,
    step=1
)

subjects = []
marks_list = []

for i in range(number_of_subjects):
    st.sidebar.markdown(f"### Subject {i + 1}")

    subject = st.sidebar.text_input(
        f"Subject Name {i + 1}",
        key=f"subject_{i}"
    )

    marks = st.sidebar.number_input(
        f"Marks {i + 1}",
        min_value=0,
        max_value=100,
        value=0,
        key=f"marks_{i}"
    )

    subjects.append(subject)
    marks_list.append(marks)


# -------------------------------------------------
# ADD STUDENT BUTTON
# -------------------------------------------------

if st.sidebar.button("➕ Add Student", use_container_width=True):

    if student_id and student_name and student_class:

        # Check if all subject names are entered
        if all(subject.strip() != "" for subject in subjects):

            subject_details = {}

            for subject, marks in zip(subjects, marks_list):
                subject_details[subject] = {
                    "Marks": marks,
                    "Grade": calculate_grade(marks)
                }

            total_marks = sum(marks_list)
            average_marks = total_marks / len(marks_list)
            overall_grade = calculate_grade(average_marks)
            status = calculate_status(marks_list)

            student_data = {
                "Student ID": student_id,
                "Student Name": student_name,
                "Class": student_class,
                "Subjects": subject_details,
                "Total Marks": total_marks,
                "Average Marks": round(average_marks, 2),
                "Overall Grade": overall_grade,
                "Status": status
            }

            st.session_state.students.append(student_data)

            st.sidebar.success("Student added successfully!")

        else:
            st.sidebar.error("Please enter all subject names.")

    else:
        st.sidebar.error("Please fill in all student details.")


# -------------------------------------------------
# DISPLAY STUDENTS
# -------------------------------------------------

st.header("📋 Student Records")

if st.session_state.students:

    # Create summary table
    summary_data = []

    for student in st.session_state.students:

        summary_data.append({
            "Student ID": student["Student ID"],
            "Student Name": student["Student Name"],
            "Class": student["Class"],
            "Total Marks": student["Total Marks"],
            "Average": student["Average Marks"],
            "Overall Grade": student["Overall Grade"],
            "Status": student["Status"]
        })

    summary_df = pd.DataFrame(summary_data)

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()


    # -------------------------------------------------
    # STATISTICS
    # -------------------------------------------------

    st.header("📊 Overall Statistics")

    total_students = len(summary_df)
    average_class_marks = summary_df["Average"].mean()
    highest_average = summary_df["Average"].max()
    lowest_average = summary_df["Average"].min()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👨‍🎓 Total Students", total_students)
    col2.metric("📊 Class Average", f"{average_class_marks:.2f}")
    col3.metric("🏆 Highest Average", f"{highest_average:.2f}")
    col4.metric("📉 Lowest Average", f"{lowest_average:.2f}")


    # -------------------------------------------------
    # GRADE DISTRIBUTION
    # -------------------------------------------------

    st.header("📈 Grade Distribution")

    grade_counts = summary_df["Overall Grade"].value_counts()

    st.bar_chart(grade_counts)


    # -------------------------------------------------
    # STUDENT DETAILED REPORT
    # -------------------------------------------------

    st.divider()

    st.header("🔍 Detailed Student Report")

    student_names = [
        f"{student['Student ID']} - {student['Student Name']}"
        for student in st.session_state.students
    ]

    selected_student_name = st.selectbox(
        "Select a Student",
        student_names
    )

    selected_index = student_names.index(selected_student_name)

    selected_student = st.session_state.students[selected_index]

    # Student information
    st.subheader("👤 Student Information")

    info_col1, info_col2, info_col3 = st.columns(3)

    info_col1.info(f"**Student ID:** {selected_student['Student ID']}")
    info_col2.info(f"**Name:** {selected_student['Student Name']}")
    info_col3.info(f"**Class:** {selected_student['Class']}")


    # Subject marks table
    st.subheader("📚 Subject-wise Performance")

    subject_data = []

    for subject, details in selected_student["Subjects"].items():

        subject_data.append({
            "Subject": subject,
            "Marks": details["Marks"],
            "Grade": details["Grade"]
        })

    subject_df = pd.DataFrame(subject_data)

    st.dataframe(
        subject_df,
        use_container_width=True,
        hide_index=True
    )


    # -------------------------------------------------
    # PERFORMANCE SUMMARY
    # -------------------------------------------------

    st.subheader("🏆 Performance Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Marks",
        selected_student["Total Marks"]
    )

    col2.metric(
        "Average Marks",
        selected_student["Average Marks"]
    )

    col3.metric(
        "Overall Grade",
        selected_student["Overall Grade"]
    )

    col4.metric(
        "Status",
        selected_student["Status"]
    )


    # -------------------------------------------------
    # SUBJECT PERFORMANCE CHART
    # -------------------------------------------------

    st.subheader("📊 Subject Performance")

    chart_data = subject_df.set_index("Subject")["Marks"]

    st.bar_chart(chart_data)


    # -------------------------------------------------
    # DELETE STUDENT
    # -------------------------------------------------

    st.divider()

    st.header("🗑️ Delete Student")

    delete_student = st.selectbox(
        "Select Student to Delete",
        student_names,
        key="delete_student"
    )

    if st.button("🗑️ Delete Selected Student"):

        delete_index = student_names.index(delete_student)

        st.session_state.students.pop(delete_index)

        st.success("Student deleted successfully!")

        st.rerun()


    # -------------------------------------------------
    # DOWNLOAD REPORT
    # -------------------------------------------------

    st.divider()

    st.header("⬇️ Download Student Summary")

    csv = summary_df.to_csv(index=False)

    st.download_button(
        label="📥 Download Student Report as CSV",
        data=csv,
        file_name="student_grade_report.csv",
        mime="text/csv",
        use_container_width=True
    )


else:

    st.info(
        "👋 No student records available yet. "
        "Add student details using the sidebar."
    )


# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.divider()

st.caption(
    "🎓 Student Grade Manager | Built with Python and Streamlit"
)
