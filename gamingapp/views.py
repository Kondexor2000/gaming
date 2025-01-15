from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from .models import Store, Laptop, Review, User
from .forms import LaptopForm, StoreForm, ReviewForm
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
import logging
from django.db.models import Q
from django.core.cache import cache

logger = logging.getLogger(__name__)

def check_template(template_name, request):
    try:
        get_template(template_name)
        logger.info(f"Template '{template_name}' found for user {request.user}.")
        cache.set(f"template_exists_{template_name}", True, timeout=3600)
        return True
    except TemplateDoesNotExist:
        logger.error(f"Template '{template_name}' does not exist for user {request.user}.")
        cache.set(f"template_exists_{template_name}", False, timeout=3600)
        return False

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return HttpResponse("Template not found.")
        if request.user.is_authenticated:
            messages.info(request, "You are already registered and logged in.")
            return redirect('add-post')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Registration successful. Please log in.")
        return response

class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = UserChangeForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('add-post')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profile updated successfully.")
        return response

class DeleteAccountView(LoginRequiredMixin, DeleteView):
    template_name = 'delete_account.html'
    success_url = reverse_lazy('login_existing')

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user
        raise Http404("You are not logged in.")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Account deleted successfully.")
            return response
        except Exception as e:
            logger.error(f"An error occurred during account deletion: {str(e)}")
            messages.error(self.request, f"An error occurred: {str(e)}")
            return redirect('delete_account')

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        if not check_template(self.template_name, self.request):
            return HttpResponse("Template not found.")
        
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(1209600 if remember_me else 0)  
        messages.success(self.request, "Login successful.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('add_post')

class CustomLogoutView(LoginRequiredMixin, LogoutView):
    next_page = 'login'

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)

class AddLaptopView(LoginRequiredMixin, CreateView):
    form_class = LaptopForm
    template_name = 'add_product.html'

    def form_valid(self, form):
        store_id = self.kwargs.get('store_pk')
        try:
            store = get_object_or_404(Store, pk=store_id, user=self.request.user)
            form.instance.owner = store
            response = super().form_valid(form)
            logger.info(f"User {self.request.user} created a laptop on store {store_id}.")

            return response
        except Exception as e:
            logger.error(f"Error creating laptop for store {store_id} by user {self.request.user}: {e}")
            raise

    def get_success_url(self):
        store_id = self.kwargs.get('store_pk')
        product_id = self.object.pk
        return reverse('lower-prices', kwargs={'store_pk': store_id, 'product_pk': product_id})

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return HttpResponse("Brak pliku .html")
        return super().dispatch(request, *args, **kwargs)
    
class StoreListView(ListView):
    model = Store
    template_name = 'store_list.html'  
    context_object_name = 'stores' 

    def get_queryset(self):
        return Store.objects.all()  
    
class UpdateLaptopView(LoginRequiredMixin, UpdateView):
    model = Laptop
    form_class = LaptopForm
    template_name = 'update_product.html'

    def get_object(self, queryset=None):
        store_pk = self.kwargs.get('store_pk')
        product_pk = self.kwargs.get('product_pk')
        return get_object_or_404(Laptop, pk=product_pk, owner__pk=store_pk)

    def form_valid(self, form):
        store = self.get_object().owner
        if store.user == self.request.user:
            return super().form_valid(form)
        else:
            return HttpResponse("Nie jesteś upoważniony do konfiguracji produktu")

    def get_success_url(self):
        store_id = self.kwargs.get('store_pk')
        product_id = self.object.pk
        return reverse('product-update', kwargs={'store_pk': store_id, 'product_pk': product_id})

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return HttpResponse("Brak pliku .html")
        return super().dispatch(request, *args, **kwargs)

class DeleteLaptopView(LoginRequiredMixin, DeleteView):
    model = Laptop
    template_name = 'delete_product.html'

    def get_object(self, queryset=None):
        store_pk = self.kwargs.get('store_pk')
        product_pk = self.kwargs.get('product_pk')
        return get_object_or_404(Laptop, pk=product_pk, owner__pk=store_pk)

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        if product.owner.user == self.request.user:
            return super().delete(request, *args, **kwargs)
        else:
            messages.error(request, "You are not authorized to delete this product.")
            return redirect('store-list')

    def get_success_url(self):
        store_id = self.get_object().owner.pk
        return reverse('product-list', kwargs={'store_pk': store_id})

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return HttpResponse("Template file not found.")
        return super().dispatch(request, *args, **kwargs)

class AddStoreView(LoginRequiredMixin, CreateView):
    form_class = StoreForm
    template_name = 'add_store.html'
    success_url = reverse_lazy('store-list') 

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return HttpResponse("Brak pliku .html")
        return super().dispatch(request, *args, **kwargs)

class AddReviewView(LoginRequiredMixin, CreateView):
    form_class = ReviewForm
    template_name = 'add_review.html'

    def form_valid(self, form):
        product_id = self.kwargs.get('product_pk')
        try:
            product = get_object_or_404(Laptop, pk=product_id, user=self.request.user)
            form.instance.owner = product
            response = super().form_valid(form)
            logger.info(f"User {self.request.user} created a laptop on store {product_id}.")

            return response
        except Exception as e:
            logger.error(f"Error creating laptop for store {product_id} by user {self.request.user}: {e}")
            raise

    def get_success_url(self):
        product_id = self.kwargs.get('product_pk')
        review_id = self.object.pk
        return reverse('user-review', kwargs={'product_pk': product_id, 'review_pk': review_id})

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return HttpResponse("Brak pliku .html")
        return super().dispatch(request, *args, **kwargs)
    
class UpdateReviewView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'update_review.html'

    def get_object(self, queryset=None):
        product_pk = self.kwargs.get('product_pk')
        review_pk = self.kwargs.get('review_pk')
        return get_object_or_404(Review, pk=review_pk, laptop__pk=product_pk)

    def form_valid(self, form):
        review = self.get_object().user
        if review.user == self.request.user:
            return super().form_valid(form)
        else:
            return HttpResponse("Nie jesteś upoważniony do aktualizacji recenzji")

    def get_success_url(self):
        store_id = self.kwargs.get('store_pk')
        product_id = self.object.pk
        return reverse('review-update', kwargs={'store_pk': store_id, 'product_pk': product_id})

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return HttpResponse("Brak pliku .html")
        return super().dispatch(request, *args, **kwargs)
    
class StoreDetailView(DetailView):
    model = Store
    template_name = 'store_detail.html'
    context_object_name = 'store'
    
@transaction.atomic
def display_first_record_with_lower_price(request, store_pk, product_pk):
    if request.user.is_authenticated:
        template_name = 'templates_with_first_record.html'
        if not check_template(template_name, request):
            logger.warning(f"Template '{template_name}' not found for user {request.user}.")
            return HttpResponseNotFound("Template not found.")

        try:
            product = get_object_or_404(Laptop, pk=product_pk, owner__pk=store_pk)
            first_product_with_lower_price = Laptop.objects.filter(
                price__lt=product.price, 
                cale__gte=product.cale, 
                graphics_card__gte=product.graphics_card, 
                processor__gte=product.processor, 
                ram__gte=product.ram, 
                rom__gte=product.rom
            ).first()
            
            logger.info(f"Records retrieved successfully for user {request.user}.")
            return render(request, 'templates_with_first_record.html', {'component': first_product_with_lower_price})
        except Laptop.DoesNotExist:
            first_product_with_lower_price = []
            logger.error(f"Error retrieving categories for user {request.user}")
            messages.error(request, 'Laptop o podanym identyfikatorze nie istnieje.')
            return redirect('login')
    else:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login')
    
@transaction.atomic
def display_second_and_subsequent_records_with_lower_prices(request, store_pk, product_pk):
    if request.user.is_authenticated:
        template_name = 'templates_with_record.html'
        if not check_template(template_name, request):
            logger.warning(f"Template '{template_name}' not found for user {request.user}.")
            return HttpResponseNotFound("Template not found.")

        try:
            product = get_object_or_404(Laptop, pk=product_pk, owner__pk=store_pk)
            products_with_lower_prices = Laptop.objects.filter(
                price__lt=product.price, 
                cale__gte=product.cale, 
                graphics_card__gte=product.graphics_card, 
                processor__gte=product.processor, 
                ram__gte=product.ram, 
                rom__gte=product.rom
            ).order_by('price')[1:]
            
            logger.info(f"Records retrieved successfully for user {request.user}.")
            return render(request, 'templates_with_record.html', {'components': products_with_lower_prices})
        except Laptop.DoesNotExist:
            products_with_lower_prices = []
            logger.error(f"Error retrieving categories for user {request.user}")
            messages.error(request, 'Laptop o podanym identyfikatorze nie istnieje.')
            return redirect('login')
    else:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login')
    
@transaction.atomic
def search_laptops(request, store_pk):
    template_name = 'search_laptops.html'
    if not check_template(template_name, request):
        logger.warning(f"Template '{template_name}' not found for user {request.user}.")
        return HttpResponseNotFound("Template not found.")

    try:
        products = Laptop.objects.filter(owner__pk=store_pk)
        logger.info(f"Products retrieved successfully for user {request.user}.")
    except Exception as e:
        products = []
        logger.error(f"Error retrieving categories for user {request.user}: {e}")
        return HttpResponse("An error occurred while retrieving categories.", status=500)

    return render(request, template_name, {'products': products})

@transaction.atomic
def search_stores_for_request_user(request):
    template_name = 'search_stores_users.html'
    if not check_template(template_name, request):
        logger.warning(f"Template '{template_name}' not found for user {request.user}.")
        return HttpResponseNotFound("Template not found.")
    
    try:
        products = Store.objects.filter(user=request.user)
        logger.info(f"Products retrieved successfully for user {request.user}.")
    except Exception as e:
        products = []
        logger.error(f"Error retrieving categories for user {request.user}: {e}")
        return HttpResponse("An error occurred while retrieving categories.", status=500)

    return render(request, template_name, {'products': products})


@transaction.atomic
def search_stores(request):
    template_name = 'search_stores.html'
    if not check_template(template_name, request):
        logger.warning(f"Template '{template_name}' not found for user {request.user}.")
        return HttpResponseNotFound("Template not found.")

    try:
        query = request.GET.get('q', '').strip()
        products = Store.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)) if query else Store.objects.all()
        logger.info(f"Products retrieved successfully for user {request.user}.")
    except Exception as e:
        logger.error(f"Error retrieving categories for user {request.user}: {e}")
        products = []
        return HttpResponse("An error occurred while retrieving categories.", status=500)
    
    return render(request, template_name, {'products': products, 'query': query})

def review_view(request, product_pk, user_pk):
    template_name = 'read_review.html'

    user = get_object_or_404(User, pk=user_pk)
    laptop = get_object_or_404(Laptop, pk=product_pk)
    review = Review.objects.filter(user=user, laptop=laptop)
    return render(request, template_name, {'review': review})

def review_request_user_view(request, product_pk):
    template_name = 'read_request_user_review.html'

    user = request.user
    laptop = get_object_or_404(Laptop, pk=product_pk)
    review = Review.objects.filter(user=user, laptop=laptop)
    return render(request, template_name, {'review': review})

