# Generated by Django 4.2.4 on 2023-09-05 01:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('from_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='following_friendship_set', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='follower_friend_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('from_user_id', 'to_user_id')},
                'index_together': {('to_user_id', 'created_at'), ('from_user_id', 'created_at')},
            },
        ),
    ]
