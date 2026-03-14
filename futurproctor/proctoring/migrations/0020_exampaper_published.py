# Generated manually to fix missing published field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proctoring', '0019_alter_cheatingaudio_timestamp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='exampaper',
            name='published',
            field=models.BooleanField(default=False, help_text='Is exam published and visible to students'),
        ),
    ]
