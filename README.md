# BOM Compare Tool

## Overview
This project is a Django-based web application designed to facilitate the comparison of Bill of Materials (BOM) files. Users can upload a Master BOM in XLSX format, and then compare it against one or more target BOM files in various formats (XLSX, CSV, DOCX, PDF, TXT). The system provides a detailed comparison report, highlighting matching parts, parts with quantity/designator changes, added parts, and removed parts.

## Features
*   **User Authentication:** Secure sign-up, login, and logout functionality for individual users.
*   **Master BOM Upload:**
    *   Upload Master BOM files exclusively in `.xlsx` format.
    *   Robust validation ensures the presence of required header columns ("Reference designators", "Quantity", "Identified MPN", "Identified manufacturer") and at least one data row.
*   **Dynamic Master BOM Dashboard:**
    *   A personalized dashboard displaying all Master BOMs uploaded by the logged-in user.
    *   Clicking a Master BOM dynamically loads and displays its contents in a table on the same page.
*   **Multi-Format Target BOM Parsing:**
    *   Ability to upload 1 to 5 target BOM files for comparison.
    *   Supports multiple file formats: `.xlsx`, `.csv`, `.docx`, `.pdf`, `.txt`.
    *   Intelligent parsing engine identifies required columns across different formats.
*   **Comprehensive BOM Comparison Logic:**
    *   Compares Master BOM entries against each target BOM.
    *   Categorizes parts into:
        *   **Perfectly Matching:** MPN, Manufacturer, Quantity, and Reference Designators are identical.
        *   **Partially Matching:** MPN and Manufacturer match, but Quantity or Reference Designators differ.
        *   **Totally Different:** Parts present in one BOM but not the other (sum of Added and Removed parts).
*   **Detailed Comparison Results Display:**
    *   A dedicated results page presenting a clear, per-target-file comparison.
    *   Each target file's comparison includes:
        *   A summary overview (Perfectly Matching, Partially Matching, Totally Different counts).
        *   Detailed tables showing Matching Parts (highlighting differences), Added Parts, and Removed Parts.
    *   Includes robust error handling and user-friendly messages for parsing failures.

## Setup Instructions

### Prerequisites
*   Python 3.8+
*   `pip` (Python package installer)

### 1. Clone the repository (if applicable)
```bash
# If you're starting from a new project, skip this step.
# git clone git@github.com:dev22Intellial/manageBom.git
# cd manageBom
```

### 2. Create and Activate a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
Install all required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 4. Database Migrations
Apply the database migrations to set up the necessary tables:
```bash
python manage.py makemigrations bom
python manage.py migrate
```

### 5. Create a Superuser
Create an administrator account to access the Django admin interface:
```bash
python manage.py createsuperuser
```
Follow the prompts to set a username, email, and password.

### 6. Run the Development Server
Start the Django development server:
```bash
python manage.py runserver
```
The application will be accessible at `http://127.0.0.1:8000/`.

## Usage

### Accessing the Application
Open your web browser and navigate to `http://127.0.0.1:8000/`.

### Signing Up and Logging In
1.  On the home page, click "Sign Up" to create a new user account.
2.  After signing up, you will be redirected to the login page.
3.  Log in with your newly created credentials. Upon successful login, you'll be redirected to the dashboard.

### Uploading a Master BOM
1.  After logging in, click "Upload Master BOM" in the navigation bar.
2.  Provide a name for your BOM.
3.  Select an `.xlsx` file. Ensure it contains the required headers: "Reference designators", "Quantity", "Identified MPN", and "Identified manufacturer".
4.  Click "Upload". The file will be processed and listed on your dashboard.

### Comparing BOMs
1.  On the dashboard, click on one of your uploaded Master BOMs from the left list. Its contents will appear on the right.
2.  In the "Compare with Target Files" section, use the file input to select 1 to 5 target BOM files. You can select files of different types (.xlsx, .csv, .docx, .pdf, .txt).
3.  Click "Compare Files".
4.  You will be redirected to the comparison results page, showing a detailed breakdown for each target file.

## Future Enhancements
*   More advanced PDF parsing capabilities (e.g., using OCR for image-based PDFs).
*   User interface improvements for the comparison results (e.g., filtering, sorting).
*   Ability to download comparison reports.
*   Version control for BOMs.
*   Support for additional BOM file formats.