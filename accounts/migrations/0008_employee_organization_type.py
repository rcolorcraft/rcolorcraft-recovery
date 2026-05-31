from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_employee_is_verified"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="organization_type",
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
