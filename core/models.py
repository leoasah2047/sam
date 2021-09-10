from django.db import models
from django.conf import settings
from django.shortcuts import reverse
# Create your models here.

CAT_CHOICES = (
    ('song', 'song'),
    ('beat', 'beat'),
    ('book', 'book'),
    ('art', 'art'),
    ('digital_product', 'digital_product'),
)

LABEL_CHOICES = (
    ('audio', 'audio'),
    ('video', 'video'),
    ('pdf', 'pdf'),
    ('art', 'art')
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=20)
    category = models.CharField(choices=CAT_CHOICES, max_length=20)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(blank=True, null=True)
    itemfile = models.FileField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("product_page", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.CharField(
        max_length=200, default="Aromire Avenue, Ikeja")
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, null=True, blank=True)
    being_delivered = models.BooleanField(default=False)
    recieved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(
        max_length=200, default="Aromire Avenue, Ikeja")
    apartment_address = models.CharField(
        max_length=200, default="4 Aromire Avenue, Ikeja")
    phone_number = models.CharField(max_length=200, default="08156912548")
    default = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class Contact(models.Model):
    name = models.CharField(max_length=100)
    mail = models.CharField(max_length=50)
    subject = models.CharField(max_length=200)
    message = models.TextField(max_length=500)

    def __str__(self):
        return self.name


class Admin(models.Model):
    about = models.CharField(max_length=500)
    image = models.ImageField(blank=True, null=True)
    gallerya = models.ImageField(blank=True, null=True)
    galleryb = models.ImageField(blank=True, null=True)
    galleryc = models.ImageField(blank=True, null=True)
    galleryd = models.ImageField(blank=True, null=True)
    gallerye = models.ImageField(blank=True, null=True)
    galleryf = models.ImageField(blank=True, null=True)
    slug = models.SlugField()

    def __str__(self):
        return self.slug


class Payment(models.Model):
    paystack_id = models.CharField(max_length=30)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
