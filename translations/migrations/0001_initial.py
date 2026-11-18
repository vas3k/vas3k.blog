import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('posts', '0004_alter_post_slug_alter_post_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranslationState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(max_length=2)),
                ('source_fields', models.JSONField(default=dict)),
                ('target_fields', models.JSONField(default=dict)),
                ('pending', models.BooleanField(db_index=True, default=True)),
                ('error', models.TextField(blank=True, default='')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translation_states', to='posts.post')),
                ('target', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='translation_sources', to='posts.post')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('source', 'language'), name='unique_post_translation_state')],
            },
        ),
    ]
