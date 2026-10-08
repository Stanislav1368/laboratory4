import json
import os
import uuid
import xml.etree.ElementTree as ET

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AthleteForm
from .models import Athlete

# Создаём папки для файлов с данными, если их ещё нет
settings.JSON_DIR.mkdir(parents=True, exist_ok=True)
settings.XML_DIR.mkdir(parents=True, exist_ok=True)


# ---------- Работа с файлами ----------

def save_to_json(data):
    """Сохраняет словарь в JSON-файл с uuid-именем. Возвращает имя файла."""
    filename = f"athlete_{uuid.uuid4().hex[:10]}.json"
    path = settings.JSON_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump([data], f, ensure_ascii=False, indent=2)
    return filename


def save_to_xml(data):
    """Сохраняет словарь в XML-файл с uuid-именем. Возвращает имя файла."""
    filename = f"athlete_{uuid.uuid4().hex[:10]}.xml"
    root = ET.Element('athletes')
    athlete = ET.SubElement(root, 'athlete')
    for key, value in data.items():
        tag = ET.SubElement(athlete, key)
        tag.text = str(value)
    tree = ET.ElementTree(root)
    tree.write(settings.XML_DIR / filename, encoding='utf-8', xml_declaration=True)
    return filename


def read_json_files():
    """Читает все JSON-файлы из папки и возвращает список словарей."""
    items = []
    for filename in os.listdir(settings.JSON_DIR):
        if not filename.endswith('.json'):
            continue
        try:
            with open(settings.JSON_DIR / filename, encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = [data]
            for record in data:
                record['file'] = filename
                items.append(record)
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
    return items


def read_xml_files():
    """Читает все XML-файлы из папки и возвращает список словарей."""
    items = []
    for filename in os.listdir(settings.XML_DIR):
        if not filename.endswith('.xml'):
            continue
        try:
            tree = ET.parse(settings.XML_DIR / filename)
            root = tree.getroot()
            for athlete in root.findall('athlete'):
                record = {child.tag: child.text for child in athlete}
                record['file'] = filename
                items.append(record)
        except (ET.ParseError, OSError):
            continue
    return items


# ---------- Страницы ----------

def index(request):
    """Главная страница."""
    return render(request, 'athletes/index.html')


def add_athlete(request):
    """Добавление спортсмена: в БД, JSON или XML."""
    if request.method == 'POST':
        form = AthleteForm(request.POST)
        save_to = request.POST.get('save_to', 'db')
        if form.is_valid():
            data = form.cleaned_data
            if save_to == 'json':
                filename = save_to_json(data)
                messages.success(request, f'Спортсмен сохранён в JSON-файл {filename}')
            elif save_to == 'xml':
                filename = save_to_xml(data)
                messages.success(request, f'Спортсмен сохранён в XML-файл {filename}')
            else:
                exists = Athlete.objects.filter(
                    name=data['name'],
                    sport=data['sport'],
                    age=data['age'],
                    country=data['country'],
                ).exists()
                if exists:
                    messages.warning(request, 'Такая запись уже есть в базе данных')
                else:
                    Athlete.objects.create(**data)
                    messages.success(request, 'Спортсмен добавлен в базу данных')
            return redirect('add_athlete')
    else:
        form = AthleteForm()
    return render(request, 'athletes/add.html', {'form': form})


def upload_file(request):
    """Загрузка файла .json или .xml пользователем."""
    if request.method == 'POST':
        uploaded = request.FILES.get('file')
        if not uploaded:
            messages.error(request, 'Файл не выбран')
        else:
            ext = os.path.splitext(uploaded.name)[1].lower()
            if ext not in ('.json', '.xml'):
                messages.error(request, 'Разрешены только файлы .json и .xml')
            else:
                try:
                    content = uploaded.read().decode('utf-8')
                except UnicodeDecodeError:
                    messages.error(request, 'Ошибка: файл не в кодировке UTF-8. Удалён.')
                    return redirect('upload_file')
                try:
                    if ext == '.json':
                        json.loads(content)
                    else:
                        ET.fromstring(content)
                except (json.JSONDecodeError, ET.ParseError):
                    messages.error(request, 'Ошибка: файл повреждён или имеет неверную структуру. Удалён.')
                    return redirect('upload_file')
                # Имя от пользователя не используем — генерируем своё
                safe_name = uuid.uuid4().hex + ext
                folder = settings.JSON_DIR if ext == '.json' else settings.XML_DIR
                with open(folder / safe_name, 'w', encoding='utf-8') as f:
                    f.write(content)
                messages.success(request, f'Файл загружен как {safe_name}')
        return redirect('upload_file')
    return render(request, 'athletes/upload.html')


def list_data(request):
    """Просмотр данных из файлов или из базы."""
    source = request.GET.get('source', 'files')
    if source == 'db':
        athletes = Athlete.objects.all().order_by('-id')
        return render(request, 'athletes/list_db.html', {'athletes': athletes})
    json_items = read_json_files()
    xml_items = read_xml_files()
    return render(request, 'athletes/list_files.html', {
        'json_items': json_items,
        'xml_items': xml_items,
    })


def edit_athlete(request, pk):
    """Редактирование записи из базы данных."""
    athlete = get_object_or_404(Athlete, pk=pk)
    if request.method == 'POST':
        form = AthleteForm(request.POST, instance=athlete)
        if form.is_valid():
            form.save()
            messages.success(request, 'Запись обновлена')
            return redirect('/list/?source=db')
    else:
        form = AthleteForm(instance=athlete)
    return render(request, 'athletes/edit.html', {'form': form, 'athlete': athlete})


@require_POST
def delete_athlete(request, pk):
    """Удаление записи через AJAX."""
    athlete = get_object_or_404(Athlete, pk=pk)
    athlete.delete()
    return JsonResponse({'ok': True})


def search_ajax(request):
    """AJAX-поиск по текстовым полям."""
    q = request.GET.get('q', '').strip()
    if q:
        athletes = Athlete.objects.filter(
            Q(name__icontains=q)
            | Q(sport__icontains=q)
            | Q(country__icontains=q)
            | Q(achievements__icontains=q)
        )
    else:
        athletes = Athlete.objects.all()
    athletes = athletes.order_by('-id')
    items = [
        {
            'id': a.id,
            'name': a.name,
            'sport': a.sport,
            'age': a.age,
            'country': a.country,
            'achievements': a.achievements,
        }
        for a in athletes
    ]
    return JsonResponse({'items': items})
