from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import FeedingForm
import uuid
import boto3
import os
from .models import Cat, Toy, Photo
from django.conf  import settings 

S3_BASE_URL = settings.S3_BASE_URL
BUCKET = settings.BUCKET
ACCESS_ID = settings.ACCESS_ID
ACCESS_KEY = settings.ACCESS_KEY
# BUCKET, ACCESS_ID, ACCESS_KEY

# S3_BASE_URL = os.environ['S3_BASE_URL']
# S3_BASE_URL = 'https://s3.amazonaws.com/'
# BUCKET = os.environ['S3_BUCKET']
# BUCKET = 'test-cat-collect-for-fruitcakes'
# Create your views here.

def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

@login_required
def cats_index(request):
  cats = Cat.objects.filter(user=request.user)
  # You could also retrieve the logged in user's cats like this
  # cats = request.user.cat_set.all()
  return render(request, 'cats/index.html', { 'cats': cats })

@login_required
def cats_detail(request, cat_id):
  cat = Cat.objects.get(id=cat_id)
  feeding_form = FeedingForm()

  toys = Toy.objects.filter(user=request.user)
  toys_cat_doesnt_have = toys.exclude(id__in = cat.toys.all().values_list('id'))  

  return render(request, 'cats/detail.html', {
    # include the cat and feeding_form in the context
    'cat': cat, 'feeding_form': feeding_form,
    'toys': toys_cat_doesnt_have
  })

@login_required
def add_feeding(request, cat_id):
  # create the ModelForm using the data in request.POST
  form = FeedingForm(request.POST)
  # validate the form
  if form.is_valid():
    # don't save the form to the db until it
    # has the cat_id assigned
    new_feeding = form.save(commit=False)
    new_feeding.cat_id = cat_id
    new_feeding.save()
  return redirect('detail', cat_id=cat_id)

@login_required
def assoc_toy(request, cat_id, toy_id):
  Cat.objects.get(id=cat_id).toys.add(toy_id)
  return redirect('detail', cat_id=cat_id)

@login_required
def unassoc_toy(request, cat_id, toy_id):
  Cat.objects.get(id=cat_id).toys.remove(toy_id)
  return redirect('detail', cat_id=cat_id)

@login_required
def add_photo(request, cat_id):
    # photo-file will be the "name" attribute on the <input type="file">
    # attempt to collect the photo file data
    photo_file = request.FILES.get('photo-file', None)
    # use conditional logic to determine if file is present
    if photo_file:
      # if present, we will create a reference to the boto3 client
        # ACCESS_ID = os.environ['AWS_ACCESS_KEY']
        # ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_ID, aws_secret_access_key= ACCESS_KEY )
        # create a unique id for each photo file
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
          # if successful
            s3.upload_fileobj(photo_file, BUCKET, key)
            # build the full url string
            # take the exchanged url and save it to the database
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # create a photo instance with a photo model and provide cat_id as a foreign key value
            photo = Photo(url=url, cat_id=cat_id)
            # save the phto intance to the database
            photo.save()
        except Exception as error:
          #  print an error message
            print('Error uploading photo: ', error)
            return redirect('detail', cat_id=cat_id)      
    return redirect('detail', cat_id=cat_id) 
    # redirect the user to the cat detail page

def signup(request):
  error_message = ''
  if request.method == "POST":
    # This is how to create a 'user' form object that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  
  return render(request, 'registration/signup.html', context)   

class CatCreate(LoginRequiredMixin, CreateView):
  model = Cat
  fields = ['name', 'breed', 'description', 'age']
  success_url = '/cats/'

  # This inherited method is called when a
  # valid cat form is being submitted
  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user  # form.instance is the cat
    # Let the CreateView do its job as usual
    return super().form_valid(form)

class CatUpdate(LoginRequiredMixin, UpdateView):
  model = Cat
  # Let's disallow the renaming of a cat by excluding the name field!
  fields = [ 'breed', 'description', 'age']

class CatDelete(LoginRequiredMixin, DeleteView):
  model = Cat
  success_url = '/cats/'

class ToyList(LoginRequiredMixin, ListView):
  model = Toy
  template_name = 'toys/index.html'
  
  def get_queryset(self):
    return Toy.objects.filter(user = self.request.user)

class ToyDetail(LoginRequiredMixin, DetailView):
  model = Toy
  template_name = 'toys/detail.html'

class ToyCreate(LoginRequiredMixin, CreateView):
  model = Toy
  fields = ['name', 'color']

  # This inherited method is called when a
  # valid toy form is being submitted
  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user  # form.instance is the toy
    # Let the CreateView do its job as usual
    return super().form_valid(form)


class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ['name', 'color']


class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'
