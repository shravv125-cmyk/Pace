# 📚 Pace  – AI Powered Study Planner

Pace AI is an intelligent study planning web application built with Django and Generative AI. It helps students organize subjects, upload study material, automatically generate learning modules, create study tasks, and track progress.

---

## 🚀 Features

- 👤 User Registration & Login
- 📖 Create and manage subjects
- 📄 Upload PDF notes and syllabus
- 🤖 AI-powered syllabus analysis using Groq LLM
- 📚 Automatic module generation
- ✅ Automatic task generation for every module
- ✔️ Task completion tracking
- 📊 Progress dashboard
- 📅 Study log
- 🔒 User-specific data isolation

---

## 🛠 Tech Stack

### Backend
- Python
- Django

### Frontend
- HTML
- CSS
- JavaScript

### Database
- SQLite

### AI
- Groq API
- Llama 3.3 70B Versatile

### PDF Processing
- PyPDF

---

## 📂 Project Structure

```
pace_project/
│
├── planner/
│   ├── migrations/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│
├── pace_project/
│   ├── settings.py
│   ├── urls.py
│
├── media/
├── static/
├── manage.py
└── requirements.txt
```

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/shravv125-cmyk/Pace.git
```

Move into the project

```bash
cd Pace
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Mac/Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root.

Example:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🗄 Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

Create admin user

```bash
python manage.py createsuperuser
```

Run server

```bash
python manage.py runserver
```

---

## 📸 Screenshots

<img width="1918" height="910" alt="image" src="https://github.com/user-attachments/assets/f767f9c3-d5dd-44b8-aa55-c36c076adac4" />
<img width="1918" height="913" alt="image" src="https://github.com/user-attachments/assets/1d1c4470-146a-4b9b-8686-e7ee3ae954a8" />
<img width="1918" height="912" alt="image" src="https://github.com/user-attachments/assets/8afebcb3-d91c-48cc-aa0a-990a5ccaa6c5" />
<img width="1918" height="912" alt="image" src="https://github.com/user-attachments/assets/6a959240-128f-4b52-a4d2-97978f14747f" />

Example

- Dashboard
- Subjects Page
- PDF Upload
- AI Generated Modules
- Study Progress

---

## ✨ How it Works

1. User creates an account.
2. User creates a subject.
3. User uploads a PDF.
4. PyPDF extracts text.
5. Groq AI analyzes the document.
6. AI generates:
   - Modules
   - Descriptions
   - Study Tasks
7. Tasks are stored in the database.
8. Users track progress by completing tasks.

---

## 🔮 Future Improvements

- Calendar integration
- AI quiz generation
- Flashcards
- Pomodoro timer
- Revision reminders
- PDF summarization
- Multi-file support
- Dark mode

---

## 👩‍💻 Author

**Shravani Kadam**


## 📄 License

This project is developed for educational purposes.
