from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0018_rename_status_artist_is_active_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PremiumService",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("image_url", models.CharField(max_length=500)),
                ("book_slug", models.CharField(max_length=120)),
                ("explore_slug", models.CharField(max_length=120)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "premium_service",
                "ordering": ["sort_order", "id"],
            },
        ),
    ]
