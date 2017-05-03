from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Test, Category, ResultScale, Tag

User = get_user_model()

# Методы-фабрики

def create_category(name, confirmed):
    """
    Создает и возвращает категорию, подтвержденную либо неподтвержденную
    """
    return Category.objects.create(name=name, confirmed=confirmed)

def create_or_return_standart_scale():
    """
    Создает и возвращает стандартную оценочную шкалу.
    """
    if ResultScale.objects.filter(name='Стандартная 5-балльная шкала').count() >= 1:
        return ResultScale.objects.get(name='Стандартная 5-балльная шкала')
    else:
        return ResultScale.objects.create(name='Стандартная 5-балльная шкала',
                                          scale_divisions_amount=5, divisions_layout='20,20,20,20')


def create_tag(name):
    """
    Создает и возвращает тег.
    """
    return Tag.objects.create(name=name)

def create_some_tags():
    """
    Создает список тегов.
    """
    tag1 = create_tag('большие')
    tag2 = create_tag('для студентов')
    tag3 = create_tag('образовательные')
    tag4 = create_tag('для школьников')
    return [tag1, tag2, tag3, tag4]

def create_some_categories():
    """
    Создает список категорий.
    Третья и четвертая категории — неподтвержденные.
    """
    confirmed_category1 = create_category('SomeConfCat', True)
    confirmed_category2 = create_category('SomeConfCat2', True)
    unconfirmed_category1 = create_category('SomeUnconfCat', False)
    unconfirmed_category2 = create_category('SomeUnconfCat2', False)
    return [confirmed_category1, confirmed_category2, unconfirmed_category1, unconfirmed_category2]

def create_test(category=None, result_scale=None, tags=[],
    anonymous_loader=False, name='Некий тест', description='Без описания', controlling=True,
    time_restricting=True, rating=0, publishing_days_offset=-30,ready_for_passing=False):
    """
    Создает и возвращает тест с переданными аргументами, добавляемый с текущей датой.
    Дата публикации устанавливается со смещением `publishing_days_offset`
    относительно текущей даты. Отрицательное значение для публикации
    теста в прошлом, положительное для тестов, публикуемых в будущем.
    """
    if not User.objects.filter(username='SomeUser'):
        author = User.objects.create(username='SomeUser', first_name="Vasya",
                last_name="Pupkin", email="pupkin@yandex.ru", is_active=True)
    else:
        author = get_object_or_404(User, username='SomeUser')
    publishing_time = timezone.now() + datetime.timedelta(days=publishing_days_offset)
    if result_scale == None:
        result_scale = create_or_return_standart_scale()
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
        new_test.tags.add(tag)
        # new_test.save()
    return new_test


class TestsListsViewTests(TestCase):
    """
    Класс с тестами для представления tests_lists
    """
    def test_tests_lists_view_with_no_tests(self):
        """
        Если никаких тестов не существует, то
        должно быть показано сообщение 'Нет таких тестов'
        """
        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'Нет таких тестов')
        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'], [])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])
        self.assertQuerysetEqual(response.context['showing_tags_and_count_of_published_tests'], [])
        self.assertQuerysetEqual(response.context['showing_categories_and_count_of_published_tests'], [])
        self.assertEqual(response.context['count_of_published_tests_with_unconf_cat'], 0)
        self.assertEqual(response.context['count_of_tests_without_category'], 0)
        self.assertEqual(response.context['count_of_tests_without_tags'], 0)

        # Статистика в подвале, считаются как опубликованные, так и неопубликованные тесты
        self.assertEqual(response.context['all_tests_count'], 0)
        self.assertContains(response, u'Тестов: 0')

        # Должны считаться все категории, в том числе неподтвержденные
        self.assertEqual(response.context['all_categories_count'], 0)
        self.assertContains(response, u'Категорий: 0')

        self.assertEqual(response.context['all_tags_count'], 0)
        self.assertContains(response, u'Тегов: 0')


    def test_tests_lists_view_with_a_past_test(self):
        """
        Тест с датой публикации, которая уже миновала, меньше текущей,
        должен отображаться на главной странице — tests_lists, а контекст представления
        должен содержать соответствующие данные.
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()
        create_test(category=some_categories[0],
                    tags=some_tags[:2], name='Опубликованный тест',
                    publishing_days_offset=-30)
        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)

        # Для просмотра содержимого ответа
        # f = open('octapp/test_tests_lists_view_with_a_past_test_content.html', 'w', encoding='utf-8')
        # f.write(response.content.decode('utf-8'))
        # f.close()

        self.assertContains(response, u'Опубликованный тест')

        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'], ['<Test: Опубликованный тест>'])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'], ['<Test: Опубликованный тест>'])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])
        
        # Количество тестов в категориях и тегах
        # должно быть 1 для использованной категории и использованных тегов.
        # ВАЖНО! Набор тегов, по которому выполняется итерация для получения пар
        # [тег, количество опубликованных тестов с данным тегом] отсортирован в представлении по убыванию id,
        # поэтому учитываем это при сравнении.
        self.assertEqual(response.context['showing_tags_and_count_of_published_tests'],
            [[some_tags[3], 0], [some_tags[2], 0], [some_tags[1], 1], [some_tags[0], 1]])
        
        # Неподтвержденные категории отображаться либо входить в контекст не должны вовсе.        
        self.assertEqual(response.context['showing_categories_and_count_of_published_tests'],
            [[some_categories[1], 0], [some_categories[0], 1]])
        
        self.assertEqual(response.context['count_of_published_tests_with_unconf_cat'], 0)
        self.assertEqual(response.context['count_of_tests_without_category'], 0)
        self.assertEqual(response.context['count_of_tests_without_tags'], 0)

        # Статистика в подвале, считаются как опубликованные, так и неопубликованные тесты
        self.assertEqual(response.context['all_tests_count'], 1)
        self.assertContains(response, u'Тестов: 1')

        # Должны считаться все категории, в том числе неподтвержденные
        self.assertEqual(response.context['all_categories_count'], 4)
        self.assertContains(response, u'Категорий: 4')

        self.assertEqual(response.context['all_tags_count'], 4)
        self.assertContains(response, u'Тегов: 4')

    def test_tests_lists_view_with_a_future_test(self):
        """
        Тест с будущей датой публикации, которая еще не наступила,
        не должен отображаться на главной странице — tests_lists.
        В контексте представления не должно быть такого теста.
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()

        create_test(category=some_categories[0],
                    tags=some_tags[:2], name='Тест с будущей датой публикации',
                    publishing_days_offset=30)
        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'Нет таких тестов')
        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'], [])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])

        # Количество тестов в категориях и тегах должно быть 0, поскольку
        # неопубликованные тесты считаться не должны.
        self.assertEqual(response.context['showing_tags_and_count_of_published_tests'],
            [[some_tags[3], 0], [some_tags[2], 0], [some_tags[1], 0], [some_tags[0], 0]])

        # Неподтвержденные категории отображаться либо входить в контекст не должны вовсе.
        self.assertEqual(response.context['showing_categories_and_count_of_published_tests'],
            [[some_categories[1], 0], [some_categories[0], 0]])

        self.assertEqual(response.context['count_of_published_tests_with_unconf_cat'], 0)
        self.assertEqual(response.context['count_of_tests_without_category'], 0)
        self.assertEqual(response.context['count_of_tests_without_tags'], 0)

        # Статистика в подвале, считаются как опубликованные, так и неопубликованные тесты
        self.assertEqual(response.context['all_tests_count'], 1)
        self.assertContains(response, u'Тестов: 1')

        # Должны считаться все категории, в том числе неподтвержденные
        self.assertEqual(response.context['all_categories_count'], 4)
        self.assertContains(response, u'Категорий: 4')

        self.assertEqual(response.context['all_tags_count'], 4)
        self.assertContains(response, u'Тегов: 4')

    def test_tests_lists_view_with_an_unconfirmed_category_test(self):
        """
        Тест с неподтвержденной категорией и с минувшей
        датой публикации должен отображаться на главной странице.
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()
        published_test_with_uncf_cat =  create_test(category=some_categories[2],
                    tags=some_tags[:2], name='Тест с неподтвержденной категорией',
                    publishing_days_offset=-30)
        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'Тест с неподтвержденной категорией')
        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'],
                                 ['<Test: ' + published_test_with_uncf_cat.name + '>'])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'],
                                 ['<Test: ' + published_test_with_uncf_cat.name + '>'])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])

        self.assertEqual(response.context['showing_tags_and_count_of_published_tests'],
                         [[some_tags[3], 0], [some_tags[2], 0], [some_tags[1], 1], [some_tags[0], 1]])

        # Неподтвержденные категории отображаться либо входить в контекст не должны вовсе.
        self.assertEqual(response.context['showing_categories_and_count_of_published_tests'],
                         [[some_categories[1], 0], [some_categories[0], 0]])

        self.assertEqual(response.context['count_of_published_tests_with_unconf_cat'], 1)
        self.assertEqual(response.context['count_of_tests_without_category'], 0)
        self.assertEqual(response.context['count_of_tests_without_tags'], 0)

        # Статистика в подвале, считаются как опубликованные, так и неопубликованные тесты
        self.assertEqual(response.context['all_tests_count'], 1)
        self.assertContains(response, u'Тестов: 1')

        # Должны считаться все категории, в том числе неподтвержденные
        self.assertEqual(response.context['all_categories_count'], 4)
        self.assertContains(response, u'Категорий: 4')

        self.assertEqual(response.context['all_tags_count'], 4)
        self.assertContains(response, u'Тегов: 4')

    def test_tests_lists_view_with_future_test_and_past_test(self):
        """
        Если есть как тест с минувшей датей публикации, так и тест с будущей,
        то отображаться и быть в контексте должен быть только тест с минувшей.
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()
        create_test(category=some_categories[0],
                    tags=some_tags[:2], name='Тест с минувшей датой публикации',
                    publishing_days_offset=-30)
        create_test(category=some_categories[0],
                    tags=some_tags[2:], name='Тест с будущей датой публикации',
                    publishing_days_offset=30)
        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'Тест с минувшей датой публикации')
        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'], ['<Test: Тест с минувшей датой публикации>'])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'], ['<Test: Тест с минувшей датой публикации>'])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])

        # При расчете количества тестов с определенным тегом считаться должны только опубликованные тесты
        self.assertEqual(response.context['showing_tags_and_count_of_published_tests'],
            [[some_tags[3], 0], [some_tags[2], 0], [some_tags[1], 1], [some_tags[0], 1]])

        # Неподтвержденные категории отображаться либо входить в контекст не должны вовсе.
        # Несмотря на то, что для 2 тестов назначена одна и та же категория, считаться для этой
        # категории должен только опубликованный тест
        self.assertEqual(response.context['showing_categories_and_count_of_published_tests'],
            [[some_categories[1], 0], [some_categories[0], 1]])

        self.assertEqual(response.context['count_of_published_tests_with_unconf_cat'], 0)
        self.assertEqual(response.context['count_of_tests_without_category'], 0)
        self.assertEqual(response.context['count_of_tests_without_tags'], 0)

        # Статистика в подвале, считаются как опубликованные, так и неопубликованные тесты
        self.assertEqual(response.context['all_tests_count'], 2)
        # Должны считаться все категории, в том числе неподтвержденные
        self.assertEqual(response.context['all_categories_count'], 4)
        self.assertEqual(response.context['all_tags_count'], 4)

    def test_tests_lists_view_with_five_past_tests_and_one_future(self):
        """
        Могут отображаться несколько тестов с минувшей датей публикации, т.е. опубликованных тестов.
        В том числе, если у них нет тегов, нет категории, либо категория не подтверждена.
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()

        # Тест с тегами (первый и второй тег),
        # с подтвержденной категорией и с минувшей датой публикации.
        # В списке создаваемых категорий первая и вторая по счету категории — подтвержденные,
        # а третья и четвертая — неподтвержденные.
        t1tagsPublsConf =  create_test(category=some_categories[0],
                    tags=some_tags[:2], name='Опубликованный тест, 2 тега, подтв. кат.',
                    publishing_days_offset=-10)

        # Тест с тегами (третий и четвертый тег),
        # с неподтвержденной категорией и с минувшей датой публикации.
        t2tagsPublsUnc =  create_test(category=some_categories[2],
                    tags=some_tags[2:], name='Опубликованный тест, 2 тега, неподтв. кат.',
                    publishing_days_offset=-9)

        # Тест без тегов, с подтвержденной категорией и с минувшей датой публикации.
        t3noTagsPublsConf =  create_test(category=some_categories[0],
                    tags=[], name='Опубликованный тест, без тегов, подтв. кат.',
                    publishing_days_offset=-8)

        # Тест без тегов, с неподтвержденной категорией и с минувшей датой публикации.
        t4noTagsPublsUnconf =  create_test(category=some_categories[2],
                    tags=[], name='Опубликованный тест, без тегов, неподтв. кат.',
                    publishing_days_offset=-7)

        # Тест без тегов, без категории и с минувшей датой публикации.
        t5noTagsPublsNoCat =  create_test(category=None,
                    tags=[], name='Опубликованный тест, без тегов, без кат.',
                    publishing_days_offset=-6)

        # Тест с будущей датой публикации
        t6 =  create_test(category=None,
                    tags=some_tags[2:], name='Тест с будущей датой публикации',
                    publishing_days_offset=30)

        response = self.client.get(reverse('tests_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'Опубликованный тест, 2 тега, подтв. кат.')
        self.assertContains(response, u'Опубликованный тест, 2 тега, неподтв. кат.')
        self.assertContains(response, u'Опубликованный тест, без тегов, подтв. кат.')
        self.assertContains(response, u'Опубликованный тест, без тегов, неподтв. кат.')
        self.assertContains(response, u'Опубликованный тест, без тегов, без кат.')

        # Для подробного вывода различий в выводе консоли при запуске тестов
        self.maxDiff = None

        # Тесты на главной странице должны сортироваться
        # по возрастанию рейтинга и убыванию даты публикации
        # для списка рейтинговых тестов и списка новых тестов соответственно,
        # а также по имени как второму критерию сортировки.
        # number в переводе — ряд (в данном случае)
        self.assertQuerysetEqual(response.context['left_number_of_new_tests_list'],
                         ['<Test: ' + t5noTagsPublsNoCat.name + '>',
                          '<Test: ' + t4noTagsPublsUnconf.name + '>',
                          '<Test: ' + t3noTagsPublsConf.name + '>',
                          '<Test: ' + t2tagsPublsUnc.name + '>',
                          '<Test: ' + t1tagsPublsConf.name + '>'])
        self.assertQuerysetEqual(response.context['right_number_of_new_tests_list'], [])
        self.assertQuerysetEqual(response.context['left_number_of_rating_tests'],
                         ['<Test: ' + t2tagsPublsUnc.name + '>',
                          '<Test: ' + t1tagsPublsConf.name + '>',
                          '<Test: ' + t5noTagsPublsNoCat.name + '>',
                          '<Test: ' + t4noTagsPublsUnconf.name + '>',
                          '<Test: ' + t3noTagsPublsConf.name + '>'])
        self.assertQuerysetEqual(response.context['right_number_of_rating_tests'], [])

        # Первые 2 тега назначены первому тесту, 2 два — второму
        self.assertEqual(response.context['showing_tags_and_count_of_published_tests'],
            [[some_tags[3], 1], [some_tags[2], 1], [some_tags[1], 1], [some_tags[0], 1]])

        # Неподтвержденные категории отображаться либо входить в контекст не должны вовсе.
        self.assertEqual(response.context['showing_categories_and_count_of_published_tests'],
            [[some_categories[1], 0], [some_categories[0], 2]])

        self.assertEqual(response.context['count_of_published_tests_with_unconf_cat'], 2)
        self.assertEqual(response.context['count_of_tests_without_category'], 1)
        self.assertEqual(response.context['count_of_tests_without_tags'], 3)

        # Статистика в подвале, считаются как опубликованные, так и неопубликованные тесты
        self.assertEqual(response.context['all_tests_count'], 6)
        self.assertContains(response, u'Тестов: 6')

        # Должны считаться все категории, в том числе неподтвержденные
        self.assertEqual(response.context['all_categories_count'], 4)
        self.assertContains(response, u'Категорий: 4')

        self.assertEqual(response.context['all_tags_count'], 4)
        self.assertContains(response, u'Тегов: 4')

class TestDetailViewTests(TestCase):
    """
    Класс с тестами для представления test_detail
    """
    def test_detail_view_with_a_future_test(self):
        """
        Подробное представление, страничка теста с будущей либо
        отсутствующей датой публикации должно выдавать перенаправление
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()

        # Тест с публикацией в будущем
        future_test =  create_test(category=some_categories[0],
                    tags=some_tags[2:], name='Тест с будущей датой публикации',
                    publishing_days_offset=30)

        response = self.client.get(reverse('test_detail', args=(future_test.id,)))

        # Проверка статистики в подвале здесь не требуется,
        # поскольку у response нет content

        # Должно выполняться перенаправление на главную страницу
        self.assertRedirects(response, reverse('tests_lists'))

    def test_detail_view_with_a_past_test(self):
        """
        Подробное представление, страничка теста с минувшей датой
        публикации и с кодом 200
        """
        some_categories = create_some_categories()
        some_tags = create_some_tags()

        # Опубликованный тест
        past_test =  create_test(category=some_categories[0],
                    tags=some_tags[:2], name='Опубликованный тест',
                    publishing_days_offset=-30)

        response = self.client.get(reverse('test_detail', args=(past_test.id,)))

        # Статистика в подвале, считаются как опубликованные, так и неопубликованные тесты
        self.assertEqual(response.context['all_tests_count'], 1)
        self.assertContains(response, u'Тестов: 1')

        # Должны считаться все категории, в том числе неподтвержденные
        self.assertEqual(response.context['all_categories_count'], 4)
        self.assertContains(response, u'Категорий: 4')

        self.assertEqual(response.context['all_tags_count'], 4)
        self.assertContains(response, u'Тегов: 4')

        # На страничке с тестом его наименование приводится в верхний регистр
        self.assertContains(response, str(past_test.name).upper(), status_code=200)

class QuestionsOfTestsViewTests(TestCase):
    """
    Класс с тестами для представления test_questions
    """
    def test_test_questions_view_with_no_questions(self):
        """
        Если для данного теста пользователем
        еще не добавлено никаких вопросов к тесту,
        то и в контексте их быть не должно.
        """
        past_test_with_no_questions = create_test(category=None,
                    tags=[], name='Некий опубликованный тест',
                    publishing_days_offset=-30)

        response = self.client.get(reverse('questions_of_test', args=(past_test_with_no_questions.id,)))
        self.assertEqual(response.status_code, 200)
        # Должно выводиться название теста, чтобы пользователь был в курсе,
        # к какому тесту он добавляет вопросы (или редактирует, просматривает их
        self.assertContains(response, u'Некий опубликованный тест')
        self.assertContains(response, u'Вы еще не добавили никаких вопросов для данного теста.')
        # В контекст должен передаваться тест с id, полученным из URL
        self.assertEqual(response.context['test'], past_test_with_no_questions)
        # В данном случае переменная контекста для хранения вопросов теста должна быть пустой
        self.assertQuerysetEqual(response.context['questions_of_test'], [])

        self.assertEqual(response.context['all_tests_count'], 1)
        self.assertContains(response, u'Тестов: 1')
        self.assertEqual(response.context['all_categories_count'], 0)
        self.assertContains(response, u'Категорий: 0')
        self.assertEqual(response.context['all_tags_count'], 0)
        self.assertContains(response, u'Тегов: 0')
