import random
import string
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View, CreateView, TemplateView
from .models import Item, OrderItem, Order, Address, Payment, Admin, Contact
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, ContactForm
from pypaystack import Transaction
from django.http import JsonResponse, HttpResponse
import json
from .filters import ItemFilter
# Create your views here.

# def search_products(request):
# 	if request.method == 'POST':
# 		search_str = json.loads(request.body).get('searchText')

# 		results = Item.objects.filter(title__istartswith=search_str)|Item.objects.filter(category__istartswith=search_str)

# 		data = results.values()
# 		return JsonResponse(list(data), safe=False)


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {

    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


class ProductsView(ListView):
    def get(self, *args, **kwargs):
        Items = Item.objects.all()
        myfilter = ItemFilter(self.request.GET, queryset=Items)
        Items = myfilter.qs
        context = {'Item': Items, 'myfilter': myfilter}
        return render(self.request, "products.html", context)


class HomeView(TemplateView):
    template_name = "index.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


class AdminView(TemplateView):
    template_name = "about.html"


class ContactCreateView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "contact.html"
    success_url = '/contact/'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item was quantity was updated")
            return redirect('checkout')
        else:
            messages.info(request, "This item was added to your cart")
            order.items.add(order_item)
            return redirect('checkout')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
        return redirect('checkout')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart")
            return redirect('checkout')
        else:
            messages.info(request, "This item is not in your cart")
            return redirect('product_page', slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect('product_page', slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated")
            return redirect('checkout')
        else:
            messages.info(request, "This item is not in your cart")
            return redirect('product_page', slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect('product_page', slug=slug)


def final_checkout(request):
    order = Order.objects.get(user=request.user, ordered=False)
    if order.shipping_address:
        context = {
            'order': order,
        }
        return render(request, 'final_checkout.html', context)
    else:
        messages.warning(request, "You have not added an address")
        return redirect("checkout")


class PaymentView(View):
    def get(self, *args, **kwargs):
        transaction = Transaction(
            authorization_key='sk_test_4efc8832170a975a1e1eb669a89b512909d0049a')
        response = transaction.verify(kwargs['id'])
        data = JsonResponse(response, safe=False)

        if response[3]:
            try:
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                payment = Payment()
                payment.paystack_id = kwargs['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "order was successful")
                return redirect("download")
            except ObjectDoesNotExist:
                messages.success(self.request, "Your order was successful")
                return redirect("/")
        else:
            messages.danger(self.request, "Could not verify the transaction")
            return redirect("/")


@login_required
def download(request, path):
    try:
        order = Order.objects.get(user=self.request.user, ordered=True)
        order_items = order.items.all()
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        for item in order_items:
            if order_items.ordered == True and os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(
                        fh.read(), content_type="application/itemfile")
                    response['Content-Disposition'] = 'inline;filename=' + \
                        os.path.basename(file_path)
                    return response
                    print('downloading')

            raise Http404
        return render(self.request, 'download.html', context)
    except ObjectDoesNotExist:
        messages.error(self.request, "You do not have an active order")
        return redirect("/")
