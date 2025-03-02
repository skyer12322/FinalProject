from django.shortcuts import render, redirect, get_object_or_404
from .models import Vacancy
from django import forms

def home(req):
    context = { }
    return render(req, 'index.html', context)

def HR(req):
    context = { }
    return render(req, 'HRpage.html', context)


def profile(req):
    context = { }
    return render(req, 'profile.html',context)

def candidatepage(req):
    context = { }
    return render(req, 'candidatepage.html',context)

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'required_skills', 'required_experience', 'required_education']
        widgets = {
            'required_skills': forms.Textarea(attrs={'placeholder': 'Skills (comma-separated)'}),
        }


def vacancies_list(request):
    vacancies = Vacancy.objects.all()  # Получаем все вакансии
    return render(request, 'vacancies_list.html', {'vacancies': vacancies})


def add_vacancy(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vacancies_list')
    else:
        form = VacancyForm()

    return render(request, 'add_vacancy.html', {'form': form})

def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy})