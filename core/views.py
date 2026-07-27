import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse, HttpResponseForbidden, Http404
from .models import Space, Note, SpaceFile
from .forms import CreateSpaceForm, OpenSpaceForm, NoteForm, SpaceFileForm

def home(request):
    return render(request, "core/home.html")

def create_space(request):
    if request.method == "POST":
        form = CreateSpaceForm(request.POST)
        if form.is_valid():
            space_id = form.cleaned_data["space_id"]
            password = form.cleaned_data["password"]

            if Space.objects.filter(space_id=space_id).exists():
                messages.error(request, f"Space ID '{space_id}' already exists. Please choose a different ID or open it.")
            else:
                Space.objects.create(
                    space_id=space_id,
                    password=make_password(password)
                )
                request.session["space_id"] = space_id
                messages.success(request, f"Space '{space_id}' created successfully!")
                return redirect("dashboard", space_id=space_id)
    else:
        form = CreateSpaceForm()

    return render(request, "core/create_space.html", {"form": form})

def open_space(request):
    if request.method == "POST":
        form = OpenSpaceForm(request.POST)
        if form.is_valid():
            space_id = form.cleaned_data["space_id"]
            password = form.cleaned_data["password"]

            try:
                space = Space.objects.get(space_id=space_id)
                if check_password(password, space.password):
                    request.session["space_id"] = space.space_id
                    messages.success(request, f"Unlocked Space '{space.space_id}'!")
                    return redirect("dashboard", space_id=space.space_id)
                else:
                    messages.error(request, "Incorrect password for this Space.")
            except Space.DoesNotExist:
                messages.error(request, f"Space '{space_id}' does not exist.")
    else:
        form = OpenSpaceForm()

    return render(request, "core/open_space.html", {"form": form})

def exit_space(request):
    if "space_id" in request.session:
        del request.session["space_id"]
    messages.info(request, "You have exited the storage space.")
    return redirect("home")

def dashboard(request, space_id):
    space_id = space_id.lower()
    if request.session.get("space_id") != space_id:
        messages.error(request, "Please enter your Space ID and password to access this space.")
        return redirect("open_space")

    space = get_object_or_404(Space, space_id=space_id)
    notes = space.notes.all()
    files = space.files.all()

    note_form = NoteForm()
    file_form = SpaceFileForm()

    return render(request, "core/dashboard.html", {
        "space": space,
        "notes": notes,
        "files": files,
        "note_form": note_form,
        "file_form": file_form,
    })

def add_note(request, space_id):
    space_id = space_id.lower()
    if request.session.get("space_id") != space_id:
        return HttpResponseForbidden("Unauthorized space access.")

    space = get_object_or_404(Space, space_id=space_id)

    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"] or "Untitled Note"
            content = form.cleaned_data["content"]
            Note.objects.create(
                space=space,
                title=title,
                content=content
            )
            messages.success(request, "Text note saved!")
        else:
            messages.error(request, "Failed to save note. Please check your content.")

    return redirect("dashboard", space_id=space_id)

def delete_note(request, space_id, note_id):
    space_id = space_id.lower()
    if request.session.get("space_id") != space_id:
        return HttpResponseForbidden("Unauthorized space access.")

    space = get_object_or_404(Space, space_id=space_id)
    note = get_object_or_404(Note, id=note_id, space=space)

    note.delete()
    messages.success(request, "Note deleted successfully.")
    return redirect("dashboard", space_id=space_id)

def determine_file_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico', '.tiff']:
        return 'image'
    elif ext in ['.txt', '.md', '.csv', '.json', '.xml', '.py', '.js', '.css', '.html', '.log', '.sh', '.c', '.cpp', '.h', '.java']:
        return 'text'
    elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.7z']:
        return 'document'
    return 'other'

def upload_file(request, space_id):
    space_id = space_id.lower()
    if request.session.get("space_id") != space_id:
        return HttpResponseForbidden("Unauthorized space access.")

    space = get_object_or_404(Space, space_id=space_id)

    if request.method == "POST":
        uploaded_files = request.FILES.getlist("file")
        if not uploaded_files:
            messages.error(request, "No files selected for upload.")
            return redirect("dashboard", space_id=space_id)

        uploaded_count = 0
        for f in uploaded_files:
            file_type = determine_file_type(f.name)
            SpaceFile.objects.create(
                space=space,
                file=f,
                filename=f.name,
                file_size=f.size,
                file_type=file_type
            )
            uploaded_count += 1

        messages.success(request, f"Successfully uploaded {uploaded_count} file(s)!")

    return redirect("dashboard", space_id=space_id)

def delete_file(request, space_id, file_id):
    space_id = space_id.lower()
    if request.session.get("space_id") != space_id:
        return HttpResponseForbidden("Unauthorized space access.")

    space = get_object_or_404(Space, space_id=space_id)
    space_file = get_object_or_404(SpaceFile, id=file_id, space=space)

    # Delete actual file from disk
    if space_file.file and os.path.isfile(space_file.file.path):
        os.remove(space_file.file.path)

    space_file.delete()
    messages.success(request, "File deleted successfully.")
    return redirect("dashboard", space_id=space_id)