from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from .models import Category, ResultScale, Tag

User = get_user_model()

# Методы-фабрики

def create_test(category, result_scale, *tags,
    anonymous_loader, name, description, controlling,
    time_restricting, rating, publishing_days_offset, ready_for_passing):
    """
    Создает и возвращает тест с переданными аргументами, добавляемый с текущей датой.
    Дата публикации устанавливается со смещением `publishing_days_offset`
    относительно текущей даты. Отрицательное значение для публикации
    теста в прошлом, положительное для тестов, публикуемых в будущем.
    """
    author = User.objects.create(username='SomeUser', first_name="Vasya",
    last_name="Pupkin", email="pupkin@yandex.ru", is_active=True)
    publishing_time = timezone.now() + datetime.timedelta(days=publishing_days_offset)
    new_test = Test.objects.create(author=author,
            category=category,
            result_scale=result_scale,
            anonymous_loader=anonymous_loader, name=name,
            description=description, controlling=controlling,
            time_restricting=time_restricting, rating=rating,
            created_date=timezone.now(), published_date=publishing_time,
            ready_for_passing=ready_for_passing)
    # Назначает теги определенному тесту
    for tag in tags:
        if not Tag.objects.filter(name__iexact=tag):
            new_tag_object = Tag.objects.create(name=tag)
            test.tags.add(new_tag_object)
    return test

def create_category(name, confirmed):
    """
    Создает и возвращает категорию, подтвержденную либо неподтвержденную
    """
    return Category.objects.create(name=name, confirmed=confirmed)

def create_standart_scale():
    """
    Создает и возвращает стандартную оценочную шкалу.
    """
    return ResultScale.objects.create(name="Стандартная 5-балльная шкала",
    scale_divisions_amount=5, divisions_layout="20,20,20,20")

def create_tag(name):
    """
    Создает и возвращает тег.
    """
    return Tag.objects.create(name=name)

def create_some_tags():
    """
    Создает кортеж тегов.
    """
    tag1 = create_tag('образовательные')
    tag2 = create_tag('для студентов')
    tag3 = create_tag('для школьников')
    tag4 = create_tag('большие')
    return (tag1, tag2, tag3, tag4)

def create_some_categories():
    """
    Создает кортеж категорий.
    Третья и четвертая категории — неподтвержденные.
    """
    confirmed_category1 = create_category('SomeConfCat', True)
    confirmed_category2 = create_category('SomeConfCat2', True)
    unconfirmed_category1 = create_category('SomeUnconfCat', False)
    unconfirmed_category2 = create_category('SomeUnconfCat2', False)
    return (confirmed_category1, confirmed_category2, unconfirmed_category1, unconfirmed_category2)



class TestsListsViewTests(TestCase):
    def test_tests_lists_view_with_no_tests(self):
        """
        Если никаких тестов не существует, то
        должно быть показано сообщение "Нет таких тестов"
        """
        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Нет таких тестов")
        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'], [])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])
        self.assertQuerysetEqual(response.context['showing_tags_and_count_of_published_tests'], [])
        self.assertQuerysetEqual(response.context['showing_categories_and_count_of_published_tests'], [])
        self.assertQuerysetEqual(response.context['count_of_published_tests_with_unconf_cat'], 0)
        self.assertQuerysetEqual(response.context['count_of_tests_without_category'], 0)
        self.assertQuerysetEqual(response.context['count_of_tests_without_tags'], 0)

    def test_tests_lists_view_with_a_past_test(self):
        """
        Тест с датой публикации, которая уже миновала, меньше текущей,
        должен отображаться на главной странице — tests_lists, а контекст представления
        должен содержать соответствующие данные.
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()
        create_test(category=some_categories[0],
                    result_scale=create_standart_scale(),
                    # Назначаем для теста первые два тега.
                    tags=some_tags[:2], anonymous_loader=False,
                    name='Тест с минувшей датой публикации',
                    description='Тест по основам теории вероятности',
                    controlling=True, time_restricting=True, rating=0,
                    publishing_days_offset=-30, ready_for_passing=False)
        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тест с минувшей датой публикации')
        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'], ['<Test: Тест с минувшей датой публикации>'])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'], ['<Test: Тест с минувшей датой публикации>'])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])
        
        # Количество тестов в категориях и тегах должно быть 1 для использованной категории
        # и использованных тегов
        self.assertQuerysetEqual(response.context['showing_tags_and_count_of_published_tests'],
        [[some_tags[0], 1], [some_tags[1], 1], [some_tags[2], 0], [some_tags[3], 0]])
        
        # Неподтвержденные категории отображаться либо входить в контекст не должны вовсе.        
        self.assertQuerysetEqual(response.context['showing_categories_and_count_of_published_tests'],
        [[some_categories[0], 1], [some_categories[1], 0])
        
        self.assertQuerysetEqual(response.context['count_of_published_tests_with_unconf_cat'], 0)
        self.assertQuerysetEqual(response.context['count_of_tests_without_category'], 0)
        self.assertQuerysetEqual(response.context['count_of_tests_without_tags'], 0)

    def test_tests_lists_view_with_a_future_test(self):
        """
        Тест с будущей датой публикации, которая еще не наступила,
        не должен отображаться на главной странице — tests_lists.
        В контексте представления не должно быть такого теста.
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()
        create_test(category=some_categories[0],
                    result_scale=create_standart_scale(),
                    # Назначаем для теста первые два тега.
                    tags=some_tags[:2], anonymous_loader=False,
                    name='Тест с будущей датой публикации',
                    description='Тест по основам теории вероятности',
                    controlling=True, time_restricting=True, rating=0,
                    publishing_days_offset=30, ready_for_passing=False)
        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Нет таких тестов')
        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'], [])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])
        
        # Количество тестов в категориях и тегах должно быть 0, поскольку
        # неопубликованные тесты считаться не должны.
        self.assertQuerysetEqual(response.context['showing_tags_and_count_of_published_tests'],
        [[some_tags[0], 0], [some_tags[1], 0], [some_tags[2], 0], [some_tags[3], 0]])
        
        # Неподтвержденные категории отображаться либо входить в контекст не должны вовсе.        
        self.assertQuerysetEqual(response.context['showing_categories_and_count_of_published_tests'],
        [[some_categories[0], 0], [some_categories[1], 0])

        self.assertQuerysetEqual(response.context['count_of_published_tests_with_unconf_cat'], 0)
        self.assertQuerysetEqual(response.context['count_of_tests_without_category'], 0)
        self.assertQuerysetEqual(response.context['count_of_tests_without_tags'], 0)

    def test_tests_lists_view_with_future_test_and_past_test(self):
        """
        Если есть как тест с минувшей датей публикации, так и тест с будущей,
        то отображаться и быть в контексте должен быть только тест с минувшей.
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()

        create_test(category=some_categories[0],
                    result_scale=create_standart_scale(),
                    # Назначаем для теста первые два тега.
                    tags=some_tags[:2], anonymous_loader=False,
                    name='Тест с минувшей датой публикации',
                    description='Тест дискретной математике',
                    controlling=True, time_restricting=True, rating=0,
                    publishing_days_offset=-30, ready_for_passing=False)

        create_test(category=some_categories[0],
                    result_scale=create_standart_scale(),
                    # Назначаем для теста 3 и 4 теги.                    
                    tags=some_tags[2:], anonymous_loader=False,
                    name='Тест с будущей датой публикации',
                    description='Тест по основам теории вероятности',
                    controlling=True, time_restricting=True, rating=0,
                    publishing_days_offset=30, ready_for_passing=False)

        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тест с минувшей датой публикации')
        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'], ['<Test: Тест с минувшей датой публикации>'])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'], ['<Test: Тест с минувшей датой публикации>'])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])
        
        # Количество тестов в категориях и тегах должно быть 1, поскольку
        # неопубликованные тесты считаться не должны.
        self.assertQuerysetEqual(response.context['showing_tags_and_count_of_published_tests'],
        [[some_tags[0], 1], [some_tags[1], 1], [some_tags[2], 0], [some_tags[3], 0]])
        
        # Неподтвержденные категории отображаться либо входить в контекст не должны вовсе.
        # Несмотря на то, что для 2 тестов назначена одна и та же категория, считаться для этой
        # категории должен только опубликованный тест
        self.assertQuerysetEqual(response.context['showing_categories_and_count_of_published_tests'],
        [[some_categories[0], 1], [some_categories[1], 0])

        self.assertQuerysetEqual(response.context['count_of_published_tests_with_unconf_cat'], 0)
        self.assertQuerysetEqual(response.context['count_of_tests_without_category'], 0)
        self.assertQuerysetEqual(response.context['count_of_tests_without_tags'], 0)

    def test_tests_lists_view_with_two_past_tests(self):
        """
        Могут отображаться несколько тестов с минувшей датей публикации, т.е. опубликованных тестов.
        В том числе, если у них нет тегов, нет категории, либо категория не подтверждена.
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()

        # Тест с тегами (первый и второй тег),
        # подтвержденной категорией и с минувшей датой публикации.
        # В кортеже создаваемых категорий первая и вторая по счету категории — подтвержденные.
        t1 = create_test(category=some_categories[0],
                    result_scale=create_standart_scale(),
                    # Назначаем для теста первые два тега.
                    tags=some_tags[:2], anonymous_loader=False,
                    name='Тест с минувшей датой публикации, с 2 тегами, с подтвержденной категорией',
                    description='Тест дискретной математике',
                    controlling=True, time_restricting=True, rating=0,
                    publishing_days_offset=-30, ready_for_passing=False)

        # Тест с тегами (третий и четвертый тег),
        # неподтвержденной категорией и с минувшей датой публикации.
        # В кортеже создаваемых категорий третья и четвертая по счету категории — неподтвержденные.
        t2 = create_test(category=some_categories[2],
                    result_scale=create_standart_scale(),
                    # Назначаем для теста 3 и 4 теги.                    
                    tags=some_tags[2:], anonymous_loader=False,
                    name='Тест с минувшей датой публикации, с 2 тегами, с неподтвержденной категорией',
                    description='Тест по основам теории вероятности',
                    controlling=True, time_restricting=True, rating=0,
                    publishing_days_offset=-3, ready_for_passing=False)

        # Тест без тегов, подтвержденной категорией и с минувшей датой публикации.
        t3 = create_test(category=some_categories[0],
                    result_scale=create_standart_scale(),
                    # Без тегов.                    
                    tags=(), anonymous_loader=False,
                    name='Тест с минувшей датой публикации, без тегов, с подтвержденной категорией',
                    description='Тест по основам теории вероятности',
                    controlling=True, time_restricting=True, rating=0,
                    publishing_days_offset=-3, ready_for_passing=False)

        # Тест без тегов, неподтвержденной категорией и с минувшей датой публикации.
        t4 = create_test(category=some_categories[2],
                    result_scale=create_standart_scale(),
                    # Без тегов.                    
                    tags=(), anonymous_loader=False,
                    name='Тест с минувшей датой публикации, без тегов, с неподтвержденной категорией',
                    description='Тест по основам теории вероятности',
                    controlling=True, time_restricting=True, rating=0,
                    publishing_days_offset=-3, ready_for_passing=False)

        # Тест без тегов, без категории и с минувшей датой публикации.
        t5 = create_test(category=None,
                    result_scale=create_standart_scale(),
                    # Без тегов.                    
                    tags=(), anonymous_loader=False,
                    name='Тест с минувшей датой публикации, без тегов, без категории',
                    description='Тест по основам теории вероятности',
                    controlling=True, time_restricting=True, rating=0,
                    publishing_days_offset=-3, ready_for_passing=False)

        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тест с минувшей датой публикации, с 2 тегами, с подтвержденной категорией')
        self.assertContains(response, 'Тест с минувшей датой публикации, с 2 тегами, с неподтвержденной категорией')
        self.assertContains(response, 'Тест с минувшей датой публикации, без тегов, с подтвержденной категорией')
        self.assertContains(response, 'Тест с минувшей датой публикации, без тегов, с неподтвержденной категорией')
        self.assertContains(response, 'Тест с минувшей датой публикации, без тегов, без категории')
        
        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'], [t1, t2, t3, t4, t5])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'], [t1, t2, t3, t4, t5])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])
        
        # Первые 2 тега назначены первому тесту, 2 два — второму
        self.assertQuerysetEqual(response.context['showing_tags_and_count_of_published_tests'],
        [[some_tags[0], 1], [some_tags[1], 1], [some_tags[2], 1], [some_tags[3], 1]])
        
        # Неподтвержденные категории отображаться либо входить в контекст не должны вовсе.
        self.assertQuerysetEqual(response.context['showing_categories_and_count_of_published_tests'],
        [[some_categories[0], 2], [some_categories[1], 0]])

        self.assertQuerysetEqual(response.context['count_of_published_tests_with_unconf_cat'], 2)
        self.assertQuerysetEqual(response.context['count_of_tests_without_category'], 1)
        self.assertQuerysetEqual(response.context['count_of_tests_without_tags'], 3)

class TestDetailViewTests(TestCase):
    def test_detail_view_with_a_future_test(self):
        """
        The detail view of a test with a pub_date in the future should
        return a 404 not found.
        """
        future_test = create_test(name='Будущий тест.',
                                          days=5)
        response = self.client.get(reverse('octapp:detail',
                                   args=(future_test.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_test(self):
        """
        The detail view of a test with a pub_date in the past should
        display the test's text.
        """
        past_test = create_test(name='Старый тест.',
                                        days=-5)
        response = self.client.get(reverse('octapp:detail',
                                   args=(past_test.id,)))
        self.assertContains(response, past_test.name,
                            status_code=200)
