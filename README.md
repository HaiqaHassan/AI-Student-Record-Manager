
# AI Student Record Manager

A beginner-friendly Flask web application for managing student academic records, calculating results, and generating personalized academic feedback and study tips using the Groq API.

## Features

- Add, view, search, update, and delete student records.
- Automatically calculate total marks, average percentage, and grade.
- Save records in `students.json`, so they remain after restarting the app.
- Use Groq AI for performance analysis and personalized study tips.
- Keep student names and IDs out of AI prompts.
- Responsive earthy beige, sage green, and brown interface.

## Technologies

Python 3, Flask, HTML, CSS, JavaScript, JSON, Groq Python SDK, and python-dotenv.

## Project structure

```text
AI_Student_Record_Manager_Web/
├── app.py
├── ai_helper.py
├── students.json
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Requirements

- Python 3 installed.
- Visual Studio Code.
- Internet connection for Groq AI features.
- A Groq API key for AI features. Student record management and result calculations work without the API key.

## Setup on macOS

Open the project folder in VS Code. Open **Terminal → New Terminal**, then run:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Configure the Groq API

1. In the project folder, make a copy of `.env.example` and name the copy `.env`.
2. Open `.env`.
3. Replace the example value with your own Groq API key:

```env
GROQ_API_KEY=your_actual_api_key
GROQ_MODEL=your_supported_model_name
```

4. `GROQ_MODEL` is optional. If it is blank, the application attempts to discover an available text-generation model from your Groq account, then uses a fallback model name.
5. Save `.env` and restart Flask after changing it.

Never upload `.env` to GitHub. The `.gitignore` file excludes it.

## Run the application

Activate the environment if it is not already active:

```bash
source venv/bin/activate
python3 app.py
```

Open this address in Chrome:

```text
http://127.0.0.1:5000
```

The app attempts to open Chrome automatically. Keep the VS Code terminal open while using the application. Press `Control + C` in the terminal to stop the server.

## How to use

1. Add a student ID, name, class/semester, comma-separated subjects, and marks in the same order.
2. Click **Add Student**. The result is calculated and saved automatically.
3. Select a table row to load a record into the form.
4. Edit the name, class, subjects, or marks and click **Update Selected**. The student ID stays unchanged.
5. Click **Delete Selected** and confirm to remove a record.
6. Search by student name or ID, or click **Show All**.
7. Select a student and choose **Analyze Performance** or **Generate Study Tips**. These features need a valid Groq API key and internet access.

## Grade scale

| Average | Grade |
|---|---|
| 85% or above | A |
| 70% to below 85% | B |
| 60% to below 70% | C |
| 50% to below 60% | D |
| Below 50% | F |

## Common issues

- **`python3: command not found`:** Install Python 3 and make sure it is available in your Terminal.
- **`No module named flask` or `No module named groq`:** Activate `venv` and run `python3 -m pip install -r requirements.txt`.
- **AI says API key is missing:** Check that `.env` is in the same folder as `app.py`, the variable is named `GROQ_API_KEY`, and Flask was restarted.
- **Model unavailable:** Set `GROQ_MODEL` to a currently supported text-generation model available to your Groq account.
- **Port 5000 is already in use:** Stop the other Flask process or close the terminal session that is using port 5000.
- **Records do not appear:** Check that `students.json` is valid JSON and that the app can write to the project folder.

## Privacy note

The AI helper sends only class/semester, subject names, marks, total, average, and grade. It does not include student names or student IDs. Avoid entering sensitive personal information in the subject or class fields.
