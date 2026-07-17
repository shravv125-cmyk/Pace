import json
import datetime
from groq import Groq
from pypdf import PdfReader
from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.db.models import Sum, Count, Q, F
from django.contrib.auth import authenticate,login
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Subject,SubjectDocument,Module,Task ,StudyLog,Document

import os
from dotenv import load_dotenv

load_dotenv()
api = os.getenv("groq_api")

# Create your views here.
def index(request):
    return redirect("/landing")

def landing(request):
    return render(request,'landing.html')


def userLogin(request):
    if request.method == "POST":

        email_input = request.POST.get('email')
        password_input = request.POST.get('password')

        if not email_input or not password_input:
            return render(request, "login.html", {"error": "Email and Password are required."})

        user = authenticate(request, username=email_input,password=password_input)  # Django authenticates using usernamepassword=password_input

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        return render(request, "login.html", {
            "error": "Invalid email or password."
        })

    return render(request, "login.html")



def register(request):
    if request.method == "POST":
        username_input = request.POST.get('username')
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')

        # Email must be unique
        if User.objects.filter(email=email_input).exists():
            return render(request, 'register.html', {'error': 'Email already exists'})

        user = User.objects.create_user(
            username=email_input,      # unique value
            email=email_input,
            password=password_input,
            first_name=username_input
        )

        login(request, user)

        print("SUCCESS: User created and logged in")

        return redirect('dashboard')  # use URL name, not '/dashboard'

    return render(request, 'register.html')

@login_required
def dashboard(request):
    """ Renders the main dashboard summary matching image_2edd4f.png in light mode """
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    # 1. Determine Greeting based on current time
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # 2. Extract primary course for prominent syllabus banner display
    # (Taking the first active course, or a fallback if empty)
    active_subject = Subject.objects.filter(user=request.user).first()
    
    subject_info = {
        'name': "No Active Courses Added Yet",
        'modules_count': 0,
        'estimated_hours': 0,
        'parsed_file': "Upload a syllabus to begin tracking"
    }
    
    if active_subject:
        modules_query = Module.objects.filter(subject=active_subject).order_by('order')
        total_tasks = Task.objects.filter(module__subject=active_subject).count()
        
        # Simple estimation logic: 4.5 hours per module or based on tasks weight
        subject_info = {
            'name': active_subject.name,
            'modules_count': modules_query.count(),
            'estimated_hours': int(total_tasks * 1.5) if total_tasks > 0 else (modules_query.count() * 5),
            'parsed_file': f"{active_subject.name.replace(' ', '_')}_Syllabus_2026.pdf"
        }

    # 3. Aggregate Metric Cards Stats
    total_modules_all = Module.objects.filter(subject__user=request.user).count()
    completed_modules_all = Module.objects.filter(
        subject__user=request.user
    ).annotate(
        total_t=Count('tasks'),
        done_t=Count('tasks', filter=Q(tasks__is_completed=True))
    ).filter(total_t__gt=0, total_t=F('done_t')).count() if total_modules_all > 0 else 0

    # Total logged study hours
    total_minutes = StudyLog.objects.filter(user=request.user).aggregate(total=Sum('duration_minutes'))['total'] or 0
    hours_studied = round(total_minutes / 60, 1)
    
    # Needs review count (Struggled tasks context placeholder)
    flagged_count = Task.objects.filter(module__subject__user=request.user, is_completed=False).count() // 4

    # 4. Generate the Weekly Grid Array Strip
    week_days = []
    day_names = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    for i in range(7):
        loop_date = start_of_week + timedelta(days=i)
        daily_logs = StudyLog.objects.filter(user=request.user, session_date=loop_date).select_related('module__subject')
        
        first_log = daily_logs.first()
        if first_log is not None:
            status = 'done'
            label = first_log.module.subject.name
        else:
            status = 'scheduled' if loop_date >= today else 'none'
            label = "Pending" if loop_date >= today else "Rest"
            
        week_days.append({
            'day_name': day_names[i],
            'day_number': loop_date.day,
            'status': status,
            'label': label,
            'is_today': loop_date == today
        })

    # 5. Overall Progress percentage computation
    all_tasks_count = Task.objects.filter(module__subject__user=request.user).count()
    all_completed_tasks = Task.objects.filter(module__subject__user=request.user, is_completed=True).count()
    overall_progress_pct = int((all_completed_tasks / all_tasks_count) * 100) if all_tasks_count > 0 else 0

    context = {
        'greeting': greeting,
        'first_name': request.user.first_name,  
        'subject_info': subject_info,
        'week_days': week_days,
        'completed_modules': completed_modules_all,
        'total_modules': total_modules_all,
        'hours_studied': hours_studied,
        'flagged_count': flagged_count if flagged_count > 0 else 1,
        'overall_progress_pct': overall_progress_pct
    }
    return render(request, 'dashboard.html', context)

@login_required
def subjects(request):
    if request.method == "POST":
        # ✨ Read 'subject_name' to match your HTML template input parameter!
        subject_name = request.POST.get('subject_name')
        
        if subject_name:
            # Create the course and explicitly tie it to the current user
            last_subject = Subject.objects.filter(user=request.user).order_by("-user_slug_id").first()
            
            if last_subject:
                next_slug = last_subject.user_slug_id + 1
            else:
                next_slug = 1
                
            Subject.objects.create(
                user=request.user,
                name=subject_name,
                user_slug_id=next_slug,
            )

            return redirect('subjects')  # Reload page cleanly to prevent form resubmissions

    # Fetch only this user's courses to list on the grid layout
    user_subjects = Subject.objects.filter(user=request.user).order_by('user_slug_id')

    for s in user_subjects:
        print(
            f"id={s.user}, name={s.name}, user_slug_id={s.user_slug_id}"         #prints information about each subject.
        )

    return render(request, "subjects.html", {"subjects": user_subjects})


@login_required
def subject_detail(request, user_slug_id):
    print("URL user_slug_id =", user_slug_id)
    print("Logged in user =", request.user)
    subject = get_object_or_404(Subject, user=request.user,user_slug_id=user_slug_id)

    print("Subject PK =", subject.pk)
    print("Subject user_slug_id =", subject.user_slug_id)
    
    if request.method == "POST":
        title = request.POST.get('title')
        raw_doc_type = request.POST.get('doc_type')
        uploaded_file = request.FILES.get('uploaded_file')
        
        if title and raw_doc_type and uploaded_file:
            # Clean string input values to guarantee they match database filters
            doc_type = raw_doc_type.strip().lower()
            if "note" in doc_type:
                doc_type = "notes"
            elif "syllabus" in doc_type:
                doc_type = "syllabus"

            doc = SubjectDocument.objects.create(
                subject=subject,
                title=title,
                doc_type=doc_type,
                file=uploaded_file
            )
            
            try:
                # 1. Extract plain text content from the uploaded PDF stream
                reader = PdfReader(doc.file.path)
                extracted_text = ""
                for page in reader.pages:
                    text_content = page.extract_text()
                    if text_content:
                        extracted_text += text_content + "\n"
                
                print(f"\n--- DEBUG: Extracted {len(extracted_text)} characters from PDF ---")
                
                # 2. Fire up the Groq Pipeline if text exists
                if extracted_text.strip():
                    client = Groq(api_key=api)
                    
                    prompt_instructions = f"""
                    You are an expert academic curriculum planner.

                    Analyze the following syllabus/notes carefully.

                    Document:
                    ---------------------
                    {extracted_text[:9000]}
                    ---------------------

                    Break the syllabus into logical learning modules.

                    For each module provide:
                    - module_title
                    - description
                    - 3 to 5 study tasks

                    Return ONLY valid JSON.

                    {{
                        "modules":[
                            {{
                                "module_title":"Introduction",
                                "description":"Basic concepts",
                                "tasks":[
                                    "Study topic 1",
                                    "Study topic 2",
                                    "Practice questions"
                                ]
                            }}
                        ]
                    }}
                    """

                    # 3. Request completion using an ACTIVE Groq model
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": prompt_instructions,
                            }
                        ],
                        model="llama-3.3-70b-versatile", 
                        temperature=0.2,
                        response_format={"type": "json_object"} 
                    )
                    
                    response_text = chat_completion.choices[0].message.content
                    print("="*60)
                    print(response_text)
                    print("="*60)
                    
                    if response_text:
                        print("\n=== RAW GROQ RESPONSE ===")
                        print(response_text)
                        print("===========================\n")
                        
                        raw_json_data = json.loads(response_text)
                        parsed_modules = []
                        
                        # ✨ ROBUST ARRAY EXTRACTION LOGIC
                        if isinstance(raw_json_data, list):
                            parsed_modules = raw_json_data
                        elif isinstance(raw_json_data, dict):
                            # Handle scenarios where Llama wraps the list inside an object key
                            if "modules" in raw_json_data and isinstance(raw_json_data["modules"], list):
                                parsed_modules = raw_json_data["modules"]
                            else:
                                # Fallback: Grab the first list element found anywhere inside the keys
                                for val in raw_json_data.values():
                                    if isinstance(val, list):
                                        parsed_modules = val
                                        break
                        
                        print(f"👉 Normalized Modules Found Count: {len(parsed_modules)}")
                        
                        # 4. Save parsed layout parameters to Database
                        for idx, mod_data in enumerate(parsed_modules, start=1):

                            module_obj = Module.objects.create(
                                subject=subject,
                                title=mod_data.get(
                                    "module_title",
                                    mod_data.get("title", f"Module {idx}")
                                ),
                                description=mod_data.get("description", ""),
                                order=idx
                            )

                            print(f"\nCreated Module: {module_obj.title}")

                            # Handle multiple possible AI response formats
                            tasks = (
                                mod_data.get("tasks")
                                or mod_data.get("milestones")
                                or mod_data.get("checklist")
                                or mod_data.get("activities")
                                or []
                            )

                            # Convert string to list if AI returns a single string
                            if isinstance(tasks, str):
                                tasks = [tasks]

                            print(f"Tasks found: {len(tasks)}")

                            for task_title in tasks:
                                task_title = str(task_title).strip()
                                if not task_title:
                                    continue
                                Task.objects.create(
                                    user=request.user,
                                    module=module_obj,
                                    title=task_title,
                                    is_completed=False
                                )

                                print(f"  -> Created Task: {task_title}")
                        
                else:
                    print("⚠️ PDF Text extraction resulted in an empty string. The file might be an image/scanned copy.")
                        
            except Exception as e:
                import traceback

                print("\n" + "="*80)
                print("AI PIPELINE ERROR")
                traceback.print_exc()
                print("="*80 + "\n")
                
            return redirect('subject_detail', user_slug_id=subject.user_slug_id)

    # Gather data context collections to feed frontend layers
    syllabi = subject.documents.filter(doc_type='syllabus') # type: ignore
    notes = subject.documents.filter(doc_type='notes') # type: ignore
    modules = subject.modules.all().order_by('order') # type: ignore

    context = {
        'subject': subject,
        'syllabi': syllabi,
        'notes': notes,
        'modules': modules,
    }
    return render(request, 'subject_detail.html', context)

# @login_required
# @require_POST
# def subject_upload_pdf_view(request, pk):  # or user_slug_id depending on your path parameters
#     subject = get_object_or_404(Subject, pk=pk, user=request.user)
    
#     if request.method == "POST":
#         uploaded_files = request.FILES.getlist('pdf_files')
#         if uploaded_files:
#             for file in uploaded_files:
#                 clean_title = file.name.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ')
#                 Document.objects.create(
#                     subject=subject,
#                     title=clean_title,
#                     pdf_file=file
#                 )
#             messages.success(request, f"Successfully uploaded {len(uploaded_files)} source files.")
#         else:
#             messages.error(request, "No valid files detected.")
            
#     # 🌟 CHANGE THIS LINE HERE:
#     # Match the keyword argument to exactly what your URL routing pattern dictates!
#     return redirect('subject_detail', pk=subject.pk)


@login_required
@require_POST
def toggle_task_completion(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    data = json.loads(request.body)

    task.is_completed = data.get("is_completed", False)

    task.save()

    return JsonResponse({
        "status": "success",
        "is_completed": task.is_completed
    })


@login_required
def study_log_view(request, pk=None):
    """ Generates a study log stream derived entirely from subject context """
    
    # 1. Fetch the active course context
    if pk:
        subject = get_object_or_404(Subject, pk=pk, user=request.user)
    else:
        subject = Subject.objects.filter(user=request.user).first()
        if not subject:
            return render(request, 'study_log.html', {'no_course': True})

    # 2. Get modules and their task completions
    modules = Module.objects.filter(subject=subject).prefetch_related('tasks').order_by('order')
    
    generated_logs = []
    mock_days_ago = 0  # To cleanly distribute items like "Today", "Yesterday" visually
    
    for idx, mod in enumerate(modules):
        tasks = mod.tasks.all() # type: ignore
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(is_completed=True).count()
        
        # Calculate progress matching subject_detail logic
        mod_progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        mod_hours = total_tasks * 1.5 if total_tasks > 0 else 4.0
        
        # Determine human-friendly relative timeline tags
        if mock_days_ago == 0:
            time_tag = "Today"
        elif mock_days_ago == 1:
            time_tag = "Yesterday"
        else:
            time_tag = f"{mock_days_ago} days ago"

        # Row 1: If the module has progress or is completed, show a completion entry
        if completed_tasks > 0:
            generated_logs.append({
                'time_tag': time_tag,
                'title': f"Completed {completed_tasks} targets on {mod.title}" if mod_progress < 100 else f"Completed {mod.title}",
                'meta': f"{completed_tasks * 1.5}h logged · {subject.name}",
                'is_review': False
            })
            mock_days_ago += 1  # Shift next item back in time visually
            
        # Row 2: Add a "Review / Struggled" card mock for any incomplete task to simulate plan adjustments
        uncompleted_tasks = tasks.filter(is_completed=False)
        if uncompleted_tasks.exists() and idx == 0:  # Highlight on the current active module
            generated_logs.append({
                'time_tag': "Today",
                'title': f"Logged 1.5h on {uncompleted_tasks.first().title}",
                'meta': f"Marked as struggled — plan adjusted",
                'is_review': True
            })

    context = {
        'subject': subject,
        'logs': generated_logs
    }
    return render(request, 'study_log.html', context)

def userLogout(request):
    return redirect('/landing')



