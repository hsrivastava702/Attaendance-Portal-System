import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import cv2
from PIL import Image
import os

# Function to establish MySQL database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",    # Replace with your MySQL host
            user="root",         # Replace with your MySQL username
            password="Amity",    # Replace with your MySQL password
            database="attendance_db"  # Replace with your database name
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error: {e}")
        return None

# Function to mark attendance and save to MySQL
def mark_attendance(enrollment_number, first_name, last_name):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO attendance_records (enrollment_number, first_name, last_name, timestamp) VALUES (%s, %s, %s, %s)",
                (enrollment_number, first_name, last_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            connection.commit()
            st.success(f"Attendance marked for {first_name} {last_name} (Enrollment: {enrollment_number})")
        except Error as e:
            st.error(f"Error inserting data: {e}")
        finally:
            cursor.close()
            connection.close()

# Function to view attendance records from MySQL
def view_attendance():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM attendance_records")
            data = cursor.fetchall()
            connection.close()
            return data
        except Error as e:
            st.error(f"Error retrieving data: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

# Function to capture image from webcam and save
def capture_image():
    st.header("Capture Image from Webcam")
    
    cap = cv2.VideoCapture(0)
    
    if st.button("Capture Image", key='capture_button'):
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                st.image(pil_image, caption='Captured Image', use_column_width=True)
                image_path = f"captured_image_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                pil_image.save(image_path)
                st.success(f"Image captured and saved as {image_path}")
                
                delete_option = st.checkbox("Delete Image")
                modify_option = st.checkbox("Modify Image")
                
                if delete_option:
                    os.remove(image_path)
                    st.warning("Image deleted.")
                
                if modify_option:
                    rotation_angle = st.slider("Rotation Angle", -180, 180, 0)
                    if st.button("Apply Rotation"):
                        modified_image = pil_image.rotate(rotation_angle)
                        st.image(modified_image, caption='Modified Image', use_column_width=True)
                        modified_image.save(image_path)
    
    cap.release()

# Streamlit UI code
def main():
    st.set_page_config(page_title="Amity University Attendance Portal", page_icon=":bar_chart:", layout='wide')

    st.title("Amity University Attendance Portal")
    st.sidebar.header("Navigation")
    menu = ["Mark Attendance", "View Attendance", "Capture Image"]
    choice = st.sidebar.selectbox("Menu", menu)

    st.sidebar.markdown("---")

    if choice == "Mark Attendance":
        st.header("Mark Attendance")
        st.info("Enter student details to mark attendance.")
        enrollment_number = st.text_input("Enter Enrollment Number")
        first_name = st.text_input("Enter First Name")
        last_name = st.text_input("Enter Last Name")
        if st.button("Mark Attendance"):
            mark_attendance(enrollment_number, first_name, last_name)
    
    elif choice == "View Attendance":
        st.header("View Attendance")
        data = view_attendance()
        if data:
            st.write("### Attendance Records")
            for record in data:
                st.write(f"ID: {record[0]}, Enrollment: {record[1]}, Name: {record[2]} {record[3]}, Date & Time: {record[4]}")
        else:
            st.write("No attendance records found.")
    
    elif choice == "Capture Image":
        capture_image()

if __name__ == '__main__':
    main()
