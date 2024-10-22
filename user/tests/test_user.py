import pytest
from rest_framework.reverse import reverse
import pytest
# from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_register_success(client):
    data={
    "first_name":"Om",
    "last_name":"Bhamare",
    "email":"ombhamare2001@gmail.com",
    "password":"Vinit@2002"
}
    url=reverse('register')
    response=client.post(url,data=data,content_type='application/json')
    print(response.data)
    assert response.status_code==201

@pytest.mark.django_db
def test_register_userExist(client):
    data={
    "first_name":"Om",
    "last_name":"Bhamare",
    "email":"ombhamare2001@gmail.com",
    "password":"Vinit@2002"
}
    url=reverse('register')
    response=client.post(url,data=data,content_type='application/json')
    response=client.post(url,data=data,content_type='application/json')
    print(response.data)
    assert response.status_code==400

@pytest.mark.django_db
def test_register_missing_fields(client):
    data = {
        "first_name": "Om",
        "email": "ombhamare2001@gmail.com",
    }
    url = reverse('register')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 400 
@pytest.mark.django_db
def test_register_invalid_email(client):
    data = {
        "first_name": "Om",
        "last_name": "Bhamare",
        "email": "invalid-email-format",
        "password": "Vinit@2002"
    }
    url = reverse('register')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 400

@pytest.mark.django_db
def test_register_weak_password(client):
    data = {
        "first_name": "Om",
        "last_name": "Bhamare",
        "email": "ombhamare2001@gmail.com",
        "password": "12345" 
    }
    url = reverse('register')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 400

@pytest.mark.django_db
def test_register_existing_email(client, django_user_model):
    django_user_model.objects.create_user(
        first_name="Existing",
        last_name="User",
        email="ombhamare2001@gmail.com",
        password="Existing@2002"
    )

    data = {
        "first_name": "Om",
        "last_name": "Bhamare",
        "email": "ombhamare2001@gmail.com",
        "password": "Vinit@2002"
    }
    url = reverse('register')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 400

@pytest.mark.django_db
def test_register_extra_fields(client):
    data = {
        "first_name": "Om",
        "last_name": "Bhamare",
        "email": "ombhamare2001@gmail.com",
        "password": "Vinit@2002",
        "extra_field": "extra_value"
    }
    url = reverse('register')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 201 

@pytest.mark.django_db
def test_register_empty_payload(client):
    data = {} 
    url = reverse('register')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 400

@pytest.mark.django_db
def test_verify_user(client):
    User = get_user_model() 
    user = User.objects.create_user(
        first_name="Vinit",
        last_name="Bhamare",
        email="ombhamare2001@gmail.com",
        password="Vinit@2002"
    )

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    url = reverse('verify', kwargs={'token': access_token})
    
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {access_token}', content_type='application/json')
    print(response.data)
    
    assert response.status_code == 200 

    user.refresh_from_db() 
    assert user.is_verified is True

@pytest.mark.django_db
def test_login_success(client, django_user_model):
    django_user_model.objects.create_user(
        first_name="Vinit",
        last_name="Bhmare",
        email="ombhamare2001@gmail.com",
        password="Vinit@2002",
        is_verified=True
    )

    data = {
        "email": "ombhamare2001@gmail.com",
        "password": "Vinit@2002"
    }
    url = reverse('login')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 200

@pytest.mark.django_db
def test_login_invalid_credentials(client, django_user_model):
    django_user_model.objects.create_user(
        first_name="Vinit",
        last_name="Bhamare",
        email="ombhamare2001@gmail.com",
        password="Vinit@2002",
        is_verified=True
    )

    data = {
        "email": "ombhamare2001@gmail.com",
        "password": "wrongpassword"
    }
    url = reverse('login')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 401

@pytest.mark.django_db
def test_login_unverified_user(client, django_user_model):
    django_user_model.objects.create_user(
        first_name="Vinit",
        last_name="Bhamare",
        email="ombhamare2001@gmail.com",
        password="Vinit@2002",
        is_verified=False
    )

    data = {
        "email": "ombhamare2001@gmail.com",
        "password": "Vinit@2002"
    }
    url = reverse('login')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 403

@pytest.mark.django_db
def test_login_missing_fields(client, django_user_model):
    django_user_model.objects.create_user(
        first_name="Vinit",
        last_name="Bhamare",
        email="ombhamare2001@gmail.com",
        password="Vinit@2002",
        is_verified=True
    )

    data = {
        "email": "ombhamare2001@gmail.com"
        # Password
    }
    url = reverse('login')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 400

def test_login_non_existent_user(client, django_user_model):
    data = {
        "email": "vinitbhamare2002@gmail.com",
        "password": "vinit@2002"
    }
    url = reverse('login')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 401

@pytest.mark.django_db
@pytest.mark.vinit
def test_login_invalid_email_format(client, django_user_model):
    django_user_model.objects.create_user(
        first_name="Vinit",
        last_name="Bhamare",
        email="ombhamare2001@gmail.com",
        password="Vinit@2002",
        is_verified=True
    )

    data = {
        "email": "Vinit-email@-com",
        "password": "Vinit@2002"
    }
    url = reverse('login')
    response = client.post(url, data=data, content_type='application/json')
    print(response.data)
    assert response.status_code == 400