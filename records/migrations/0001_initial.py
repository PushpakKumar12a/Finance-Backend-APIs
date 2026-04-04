import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amt', models.DecimalField(decimal_places=2, help_text='Transaction amount.', max_digits=12)),
                ('type', models.CharField(choices=[('income', 'Income'), ('expense', 'Expense')], help_text='Income or expense.', max_length=7)),
                ('cat', models.CharField(help_text='Category label.', max_length=100)),
                ('date', models.DateField(help_text='Date of the transaction.')),
                ('desc', models.TextField(blank=True, default='', help_text='Optional notes or description.')),
                ('del_flag', models.BooleanField(default=False, help_text='Soft delete flag.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(help_text='The user who created this record.', on_delete=django.db.models.deletion.CASCADE, related_name='records', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date', '-created_at'],
                'indexes': [models.Index(fields=['type'], name='records_rec_type_ec8484_idx'), models.Index(fields=['cat'], name='records_rec_cat_8e57d6_idx'), models.Index(fields=['date'], name='records_rec_date_c3aabe_idx'), models.Index(fields=['del_flag'], name='records_rec_del_fla_5c2da1_idx')],
            },
        ),
    ]
