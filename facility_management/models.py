from django.db import models

class Provider(models.Model):
    name = models.CharField("事業者名", max_length=200)
    corporate_number = models.CharField("法人番号", max_length=13, blank=True)
    address = models.CharField("所在地", max_length=500)
    phone = models.CharField("電話番号", max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "事業者"
        verbose_name_plural = "事業者"

class Facility(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('home_care', '訪問介護'),
        ('day_service', '通所介護'),
        ('group_home', 'グループホーム'),
        ('special_nursing_home', '特別養護老人ホーム'),
        ('care_house', 'ケアハウス'),
        ('other', 'その他'),
    ]
    
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='facilities')
    name = models.CharField("事業所名", max_length=200)
    service_type = models.CharField("サービス種別", max_length=50, choices=SERVICE_TYPE_CHOICES)
    facility_number = models.CharField("事業所番号", max_length=20, unique=True)
    address = models.CharField("所在地", max_length=500)
    phone = models.CharField("電話番号", max_length=20, blank=True)
    capacity = models.IntegerField("定員", default=0)
    staff_count = models.IntegerField("職員数", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"
    
    class Meta:
        verbose_name = "事業所"
        verbose_name_plural = "事業所"
