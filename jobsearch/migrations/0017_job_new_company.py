# Generated by Django 5.0.6 on 2024-07-02 14:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobsearch', '0016_company_remove_job_co_link_remove_job_company_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='new_company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobsearch.company'),
        ),
    ]