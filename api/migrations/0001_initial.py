# Generated by Django 4.2 on 2023-08-28 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StaffPick",
            fields=[
                (
                    "Staff_Member",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("Media_ID", models.CharField(max_length=100)),
                (
                    "Media_Type",
                    models.CharField(
                        choices=[("tv", "tv"), ("movie", "movie")], max_length=20
                    ),
                ),
            ],
        ),
    ]