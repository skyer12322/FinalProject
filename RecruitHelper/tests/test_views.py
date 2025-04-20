from django.test import TestCase, Client
from django.urls import reverse
from RecruitHelper.models import Vacancy
from RecruitHelper.forms import VacancyForm, VacancyFilterForm

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.vacancy = Vacancy.objects.create(
            title="Developer",
            description="Backend Developer",
            required_skills="Python, Django",
            required_experience="1",
            required_education="Bachelor"
        )

    # Тест для home view
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('vacancies', response.context)
        self.assertLessEqual(len(response.context['vacancies']), 4)

    # Тест для login view
    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    # Тест для register view
    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    # Тест для company view
    def test_company_view(self):
        response = self.client.get(reverse('company'))
        self.assertEqual(response.status_code, 200)

    # Тест для profile view
    def test_profile_view(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    # Тест для candidate view
    def test_candidate_view(self):
        response = self.client.get(reverse('candidate'))
        self.assertEqual(response.status_code, 200)

    # Тест для vacancies view
    def test_vacancies_view(self):
        response = self.client.get(reverse('vacancies'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('vacancies', response.context)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], VacancyFilterForm)

    # Тест для add_vacancy view (GET)
    def test_add_vacancy_view_get(self):
        response = self.client.get(reverse('add_vacancy'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], VacancyForm)

    # Тест для add_vacancy view (POST)
    def test_add_vacancy_view_post(self):
        data = {
            'title': 'New Vacancy',
            'description': 'New Description',
            'required_skills': 'Python, Django',
            'required_experience': '1 year',
            'required_education': 'Bachelor'
        }
        response = self.client.post(reverse('add_vacancy'), data)
        self.assertEqual(response.status_code, 302)  # Проверяем перенаправление
        self.assertEqual(Vacancy.objects.count(), 2)  # Проверяем, что вакансия создана

    # Тест для vacancy view
    def test_vacancy_view(self):
        response = self.client.get(reverse('vacancy', args=[self.vacancy.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('vacancy', response.context)
        self.assertEqual(response.context['vacancy'].title, "Developer")

    # Тест для vacancy view (404)
    def test_vacancy_view_404(self):
        response = self.client.get(reverse('vacancy', args=[999]))
        self.assertEqual(response.status_code, 404)

    # Тест для privacy view
    def test_privacy_view(self):
        response = self.client.get(reverse('privacy'))
        self.assertEqual(response.status_code, 200)

    # Тест для news view
    def test_news_view(self):
        response = self.client.get(reverse('news'))
        self.assertEqual(response.status_code, 200)

    # Тест для about_us view
    def test_about_us_view(self):
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)

    # Дополнительные тесты

    # Тестирование доступа к защищенному представлению без авторизации
    def test_protected_view_without_login(self):
        response = self.client.get(reverse('profile'))  # Предполагаем, что это защищенное представление
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    # Проверка валидации формы добавления вакансии (POST с некорректными данными)
    def test_add_vacancy_invalid_post(self):
        data = {
            'title': '',  # Пустое название
            'description': '',
            'required_skills': '',
            'required_experience': '',
            'required_education': ''
        }
        response = self.client.post(reverse('add_vacancy'), data)
        self.assertEqual(response.status_code, 200)  # Ожидаем рендеринг формы с ошибками
        self.assertFormError(response, 'form', 'title', 'Это поле обязательно.')  # Проверяем наличие ошибки
