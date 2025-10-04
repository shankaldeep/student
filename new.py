import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv, os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from PIL import ImageTk, Image

# ------------------ CONSTANTS ------------------
CSV_FILE = "registrations.csv"

UP_CITIES = ["Moradabad", "Lucknow", "Kanpur", "Varanasi", "Prayagraj", "Agra", "Meerut", "Noida", "Ghaziabad", "Bareilly"]
INDIA_STATES = ["Uttar Pradesh", "Maharashtra", "Delhi", "Punjab", "Haryana", "Madhya Pradesh", "Rajasthan", "Bihar"]
COURSES = ["Basic Computer course", "Adobe Photoshop", "Corealdraw", "MS Office", "Typing", "Tally", "Python", "C Programming", "C++", "Java", "Web Development"]

COLLEGE_NAME = "YUG COMPUTER CENTER"
COLLEGE_LOGO = "college_logo.png"  # <-- apna logo yahan rakhen

# ------------------ FUNCTIONS ------------------
def get_next_registration_number():
    """Generate sequential registration numbers"""
    if not os.path.exists(CSV_FILE):
        return "REG001"
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        if len(reader) <= 1:
            return "REG001"
        last_reg = reader[-1][0]
        num = int(last_reg.replace("REG", ""))
        return f"REG{num+1:03d}"

def generate_pdf(data, reg_no, photo):
    """Generate a colorful PDF with styled header, title, and table"""
    filename = f"registration_{reg_no}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # -------- COLLEGE HEADER --------
    college_name = Paragraph(f"<font color='darkgreen'><b>{COLLEGE_NAME}</b></font>", styles["Title"])

    if os.path.exists(COLLEGE_LOGO):
        header = Table([
            [RLImage(COLLEGE_LOGO, width=60, height=60), college_name, ""]
        ], colWidths=[80, 350, 80])
    else:
        header = Table([
            ["", college_name, ""]
        ], colWidths=[80, 350, 80])

    header.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.lightblue),
    ]))
    elements.append(header)
    elements.append(Spacer(1, 20))

    # -------- TITLE + PHOTO --------
    title = Paragraph("<font color='darkblue'><b>STUDENT REGISTRATION FORM</b></font>", styles["Heading2"])

    if photo and os.path.exists(photo):
        header_table = Table([
            [title, RLImage(photo, width=100, height=100)]
        ], colWidths=[350, 100])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('BACKGROUND', (0,0), (0,0), colors.whitesmoke),
        ]))
    else:
        header_table = Table([[title]], colWidths=[450])

    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # -------- STUDENT DETAILS TABLE --------
    table_data = [["Field", "Details"]]
    for key, value in data.items():
        if key == "Photo": continue
        table_data.append([key, value])

    table = Table(table_data, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.lightyellow),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 40))

    # -------- DECLARATION --------
    declaration_text = (
        "<font color='red'><b>Declaration:</b></font><br/>"
        "I hereby declare that the information provided above is true to the best of my knowledge.<br/>"
        "I understand that any false information may result in cancellation of my admission."
    )
    elements.append(Paragraph(declaration_text, styles["Normal"]))
    elements.append(Spacer(1, 60))

    # -------- SIGNATURE LINES --------
    sig_table = Table([
        ["____________________", "____________________"],
        ["Student Signature", "Guardian Signature"]
    ], colWidths=[250, 250])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.darkblue),
    ]))
    elements.append(sig_table)

    # Build PDF
    doc.build(elements)
    messagebox.showinfo("Success", f"PDF generated: {filename}")

def submit_form():
    """Submit form, save CSV, generate PDF"""
    reg_no = get_next_registration_number()

    data = {
        "Registration No": reg_no,
        "Name": entry_name.get(),
        "Father's Name": entry_father.get(),
        "Mother's Name": entry_mother.get(),
        "DOB": entry_dob.get(),
        "Mobile": entry_mobile.get(),
        "Aadhaar": entry_aadhaar.get(),
        "Address": entry_address.get("1.0", "end").strip(),
        "City": combo_city.get(),
        "State": combo_state.get(),
        "PIN": entry_pin.get(),
        "Course": combo_course.get(),
        "Photo": photo_path.get()
    }
    photo = photo_path.get()

    # Validation
    if not data["Name"] or not data["Mobile"] or not data["Aadhaar"]:
        messagebox.showerror("Error", "Please fill Name, Mobile and Aadhaar!")
        return

    # Save to CSV
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

    # Generate PDF
    generate_pdf(data, reg_no, photo)

def upload_photo():
    """Upload photo using file dialog"""
    file = filedialog.askopenfilename(filetypes=[("Image files","*.jpg *.png")])
    if file:
        photo_path.set(file)

def find_student():
    """Find student by Registration No or Mobile and show in new window with photo + PDF button"""
    search_value = entry_search.get().strip()
    if not search_value:
        messagebox.showerror("Error", "Please enter Registration No or Mobile!")
        return

    if not os.path.exists(CSV_FILE):
        messagebox.showerror("Error", "No data found!")
        return

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Registration No"] == search_value or row["Mobile"] == search_value:
                # New window
                win = tk.Toplevel(root)
                win.title("Student Details")
                win.geometry("500x650")

                # Heading
                tk.Label(win, text="Student Details", font=("Arial", 16, "bold")).pack(pady=10)

                # Show details
                frame = tk.Frame(win, padx=10, pady=10)
                frame.pack()

                for i, (k, v) in enumerate(row.items()):
                    if k == "Photo":
                        continue
                    tk.Label(frame, text=f"{k}:", font=("Arial", 10, "bold"), anchor="w", width=15).grid(row=i, column=0, sticky="w", pady=2)
                    tk.Label(frame, text=v, font=("Arial", 10), anchor="w", width=30).grid(row=i, column=1, sticky="w", pady=2)

                # Show photo
                photo_file = row.get("Photo", "")
                if photo_file and os.path.exists(photo_file):
                    img = Image.open(photo_file)
                    img = img.resize((120, 120))
                    photo_img = ImageTk.PhotoImage(img)
                    img_label = tk.Label(win, image=photo_img)
                    img_label.image = photo_img
                    img_label.pack(pady=10)
                else:
                    tk.Label(win, text="No Photo Available", fg="red").pack(pady=10)

                # PDF Button
                def generate_pdf_from_find():
                    generate_pdf(row, row["Registration No"], row.get("Photo", ""))

                tk.Button(win, text="Generate PDF", command=generate_pdf_from_find,
                          bg="green", fg="white", font=("Arial", 10, "bold")).pack(pady=15)
                return

    messagebox.showerror("Not Found", f"No student found with '{search_value}'")

# ------------------ GUI ------------------
root = tk.Tk()
root.title("Student Registration Form")
root.geometry("650x750")

photo_path = tk.StringVar()

form_frame = tk.Frame(root, padx=20, pady=20)
form_frame.pack(fill="both", expand=True)

# Form fields
tk.Label(form_frame, text="Full Name").grid(row=0, column=0, sticky="w")
entry_name = tk.Entry(form_frame, width=40)
entry_name.grid(row=0, column=1, pady=5)

tk.Label(form_frame, text="Father's Name").grid(row=1, column=0, sticky="w")
entry_father = tk.Entry(form_frame, width=40)
entry_father.grid(row=1, column=1, pady=5)

tk.Label(form_frame, text="Mother's Name").grid(row=2, column=0, sticky="w")
entry_mother = tk.Entry(form_frame, width=40)
entry_mother.grid(row=2, column=1, pady=5)

tk.Label(form_frame, text="DOB (DD-MM-YYYY)").grid(row=3, column=0, sticky="w")
entry_dob = tk.Entry(form_frame, width=40)
entry_dob.grid(row=3, column=1, pady=5)

tk.Label(form_frame, text="Mobile").grid(row=4, column=0, sticky="w")
entry_mobile = tk.Entry(form_frame, width=40)
entry_mobile.grid(row=4, column=1, pady=5)

tk.Label(form_frame, text="Aadhaar").grid(row=5, column=0, sticky="w")
entry_aadhaar = tk.Entry(form_frame, width=40)
entry_aadhaar.grid(row=5, column=1, pady=5)

tk.Label(form_frame, text="Address").grid(row=6, column=0, sticky="w")
entry_address = tk.Text(form_frame, height=3, width=30)
entry_address.grid(row=6, column=1, pady=5)

tk.Label(form_frame, text="City").grid(row=7, column=0, sticky="w")
combo_city = ttk.Combobox(form_frame, values=UP_CITIES, width=37)
combo_city.grid(row=7, column=1, pady=5)

tk.Label(form_frame, text="State").grid(row=8, column=0, sticky="w")
combo_state = ttk.Combobox(form_frame, values=INDIA_STATES, width=37)
combo_state.grid(row=8, column=1, pady=5)

tk.Label(form_frame, text="PIN Code").grid(row=9, column=0, sticky="w")
entry_pin = tk.Entry(form_frame, width=40)
entry_pin.grid(row=9, column=1, pady=5)

tk.Label(form_frame, text="Course").grid(row=10, column=0, sticky="w")
combo_course = ttk.Combobox(form_frame, values=COURSES, width=37)
combo_course.grid(row=10, column=1, pady=5)

tk.Button(form_frame, text="Upload Photo", command=upload_photo).grid(row=11, column=0, pady=10, sticky="w")
tk.Label(form_frame, textvariable=photo_path).grid(row=11, column=1, sticky="w")

# Submit button
tk.Button(form_frame, text="Submit", command=submit_form, bg="green", fg="white").grid(row=12, column=1, pady=20)

# Search Student Section
tk.Label(form_frame, text="Find Student (Reg No / Mobile)").grid(row=13, column=0, sticky="w")
entry_search = tk.Entry(form_frame, width=40)
entry_search.grid(row=13, column=1, pady=5)

tk.Button(form_frame, text="Find", command=find_student, bg="blue", fg="white").grid(row=14, column=1, pady=10)

root.mainloop()
