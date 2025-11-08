from django.contrib.auth.models import User
from finances.models import Category, Transaction
from finances.services import get_user_summary

def test_user_summary(db):
    user = User.objects.create_user(username='test', password='1234')
    cat_inc = Category.objects.create(user=user, name='Sueldo', type='income')
    cat_exp = Category.objects.create(user=user, name='Comida', type='expense')
    Transaction.objects.create(user=user, category=cat_inc, amount=2000)
    Transaction.objects.create(user=user, category=cat_exp, amount=500)
    summary = get_user_summary(user)
    assert summary['balance'] == 1500
