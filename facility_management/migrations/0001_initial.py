from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='事業者名')),
                ('corporate_number', models.CharField(blank=True, max_length=13, verbose_name='法人番号')),
                ('address', models.CharField(max_length=500, verbose_name='所在地')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='電話番号')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '事業者',
                'verbose_name_plural': '事業者',
            },
        ),
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='事業所名')),
                ('service_type', models.CharField(choices=[('home_care', '訪問介護'), ('day_service', '通所介護'), ('group_home', 'グループホーム'), ('special_nursing_home', '特別養護老人ホーム'), ('care_house', 'ケアハウス'), ('other', 'その他')], max_length=50, verbose_name='サービス種別')),
                ('facility_number', models.CharField(max_length=20, unique=True, verbose_name='事業所番号')),
                ('address', models.CharField(max_length=500, verbose_name='所在地')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='電話番号')),
                ('capacity', models.IntegerField(default=0, verbose_name='定員')),
                ('staff_count', models.IntegerField(default=0, verbose_name='職員数')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='facilities', to='facility_management.provider')),
            ],
            options={
                'verbose_name': '事業所',
                'verbose_name_plural': '事業所',
            },
        ),
    ]
