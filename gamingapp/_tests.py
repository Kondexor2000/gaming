import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Store, Laptop, Review
from django.utils.timezone import now

@pytest.fixture
def store(db):
    user = User.objects.create_user(username='testuserstore', password='testpass')
    return Store.objects.create(title='Test Store', user=user)

@pytest.fixture
def laptop(store):
    laptop = Laptop.objects.create(
        name="Test Laptop",
        screen_size=15.6,
        price=999.99,
        processor=8,
        graphics_card=2,
        ram=16,
        storage=512,  # Adjusted to a valid value
        url="https://example.com/test-laptop",
        created_at=now(),
        updated_at=now(),
    )
    laptop.owner.add(store)  # Since it's ManyToMany, we must add the store
    return laptop

@pytest.fixture
def store(db):
    user = User.objects.create_user(username='testuserstore', password='testpass')
    laptop = Laptop.objects.create(
        name="Test Laptop",
        screen_size=15.6,
        price=999.99,
        processor=8,
        graphics_card=2,
        ram=16,
        storage=512,  # Adjusted to a valid value
        url="https://example.com/test-laptop",
        created_at=now(),
        updated_at=now(),
    )
    laptop.owner.add(store)  # Since it's ManyToMany, we must add the store
    return Review.objects.create(comment='Test Store', user=user, laptop=laptop)

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
def test_explore_categories_view(logged_in_client):
    response = logged_in_client.get(reverse('category'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_explore_stores_view(logged_in_client):
    response = logged_in_client.get(reverse('store-list'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_store_creation():
    user = User.objects.create_user(username='testuser', password='testpassword')
    store = Store.objects.create(title='Test Store', user=user)
    assert store.title == 'Test Store'
    assert store.user == user

@pytest.mark.django_db
def test_laptop_creation():
    # Create user and store
    user = User.objects.create_user(username='testuser', password='testpassword')
    store = Store.objects.create(title='Test Store', user=user)

    # Create laptop instance
    laptop = Laptop.objects.create(
        name='Test Laptop',
        screen_size=15.6,  # Fixed 'cale' typo
        price=1500.00,
        processor=4,
        graphics_card=2,
        ram=16,
        storage=512,  # Fixed 'rom' to 'storage'
        url='http://example.com/laptop'
    )
    laptop.owner.add(store)  # Correct way to add a ManyToMany relationship

    # Assertions
    assert store in laptop.owner.all()  # Correct ManyToMany assertion
    assert laptop.name == 'Test Laptop'
    assert laptop.screen_size == 15.6
    assert laptop.price == 1500.00
    assert laptop.processor == 4
    assert laptop.graphics_card == 2
    assert laptop.ram == 16
    assert laptop.storage == 512  # Fixed field name
    assert laptop.url == 'http://example.com/laptop'