from django.shortcuts import render

def home(req):
    context = {

    }
    return render(req, 'index.html', context)


def vacancies_list(req):
    context = {

    }
    return render(req, 'vacancies_list.html', context)
