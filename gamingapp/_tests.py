import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Store, Laptop

@pytest.fixture
def store(db):
    user = User.objects.create_user(username='testuserstore', password='testpass')
    return Store.objects.create(title='Test Store', user=user)

@pytest.fixture
def laptop(store):
    return Laptop.objects.create(
        owner=store,
        name='Test Laptop',
        cale=15.6,
        price=999.99,
        processor=8,
        graphics_card=4,
        ram=16,
        rom=512,
        url='https://example.com/test-laptop'
    )

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpassword')


@pytest.fixture
def logged_in_client(client, user):
    client.login(username='testuser', password='testpassword')
    return client

@pytest.mark.django_db
def test_signup_view(client):
    response = client.get(reverse('signup'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_edit_profile_view(logged_in_client):
    response = logged_in_client.get(reverse('edit_profile'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_delete_account_view(logged_in_client):
    response = logged_in_client.get(reverse('delete_account'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_login_view(client):
    response = client.get(reverse('login'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_logout_view(logged_in_client):
    response = logged_in_client.get(reverse('logout'))
    assert response.status_code == 302

@pytest.mark.django_db
def test_explore_products_view(logged_in_client, store):
    response = logged_in_client.get(reverse('product-list', args=[store.pk]))
    assert response.status_code == 200
    
@pytest.mark.django_db
def test_explore_categories_view(logged_in_client):
    response = logged_in_client.get(reverse('category'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_explore_stores_view(logged_in_client):
    response = logged_in_client.get(reverse('store-list'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_explore_store_view(logged_in_client, store):
    response = logged_in_client.get(reverse('store-detail', args=[store.pk]))
    assert response.status_code == 200

@pytest.mark.django_db
def test_store_creation():
    user = User.objects.create_user(username='testuser', password='testpassword')
    store = Store.objects.create(title='Test Store', user=user)
    assert store.title == 'Test Store'
    assert store.user == user

@pytest.mark.django_db
def test_laptop_creation():
    user = User.objects.create_user(username='testuser', password='testpassword')
    store = Store.objects.create(title='Test Store', user=user)
    laptop = Laptop.objects.create(
        owner=store,
        name='Test Laptop',
        cale=15.6,
        price=1500.00,
        processor=4,
        graphics_card=2,
        ram=16,
        rom=512,
        url='http://example.com/laptop'
    )
    assert laptop.owner == store
    assert laptop.name == 'Test Laptop'
    assert laptop.cale == 15.6
    assert laptop.price == 1500.00
    assert laptop.processor == 4
    assert laptop.graphics_card == 2
    assert laptop.ram == 16
    assert laptop.rom == 512
    assert laptop.url == 'http://example.com/laptop'