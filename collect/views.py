from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import Category, Place, Collect, Photo, Comment, Tag, Nice, Offer
from user.models import User
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin as LR, UserPassesTestMixin as UP
from django.db.models import Count, Q, F
import string, random
from django import forms
from .forms import PostForm, ImageForm#, CategoryForm, PlaceForm
import csv
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
import re

from history.models import LastVisit, History, SearchHistory

PAGINATION_COUNT = 10

# post [LR]
@login_required
def add_post(request):
    slug = ''.join(random.choice(string.ascii_letters + string.digits + '-_') for _ in range(8))
    form = PostForm(request.user, request.POST)
    tags = Tag.Text
    FileFormset = forms.inlineformset_factory(Collect, Photo, fields='__all__', extra=4, can_delete=False)
    context = {'form': form}
    next_ = request.POST.get('next', '/')
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        selected = request.POST.getlist('post_tag')
        formset = FileFormset(request.POST, request.FILES, instance=post)
        if formset.is_valid():
            post.user = request.user
            post.id = slug
            tag_ = Tag.objects.filter(text__in=selected)
            #tag_ = selected
            post.save()
            post.tag.set(tag_)
            #post.tag.set(text=selected)
            formset.save()
            #return redirect('home')
            return redirect(next_)

        else:
            context['formset'] = formset(instance=post)

    else:
        context['formset'] = FileFormset()
        context['button'] = _("Create")
        context['tytle'] = _("Create a new collection")
        context['tags'] = tags
        context['init_tags'] = []
    return render(request, 'collect/post.html', context)

@login_required
def update(request, pk):
    collect = get_object_or_404(Collect, pk=pk)
    len_im = Photo.objects.filter(collect=collect).count()
    form = PostForm(request.user, request.POST or None, instance=collect)
    FileFormset = forms.inlineformset_factory(Collect, Photo, fields='__all__', extra=4 - len_im, can_delete=True)
    tags = Tag.Text
    #init_tags = collect.tag.all()
    init_tags = []
    for tag in collect.tag.all():
        init_tags.append(tag.text)
    next_ = request.POST.get('next', '/')
    if collect.user == request.user:
        if request.method == "POST" and form.is_valid():
            post = form.save(commit=False)
            selected = request.POST.getlist('post_tag')
            formset = FileFormset(request.POST or None, files=request.FILES or None, instance=post)
            if formset.is_valid():
                post.user = request.user
                post.id = pk
                tag_ = Tag.objects.filter(text__in=selected)
                post.save()
                post.tag.set(tag_)
                formset.save()
                return redirect(next_)
            else:
                context['formset'] = formset(instance=collect)
    
        else:
            context = {
                'form': form,
                'formset': FileFormset(instance=collect),
                'button': _("Update"),
                'tytle': _("Update collection"),
                'tags': tags,
                'init_tags': init_tags,
            }
        return render(request, 'collect/post.html', context)
    else:
        raise Http404

#home [LR]
class Home(generic.ListView):
    model = Collect
    template_name = 'collect/the_home.html'
    context_object_name = 'collects'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Collect.objects.filter(user=user).order_by('-posted').annotate(niced=Count('nice', filter=Q(nice__user=user)))
        else:
            return Collect.objects.filter(public=True).order_by('-posted')[:50]

    def get_context_data(self, **kwargs):
        user = self.request.user
        tags = Tag.objects.all()
        context = super().get_context_data(**kwargs)
        if user.is_authenticated:
            context['theme'] = _("Your collection")
        else:
            context['theme'] = _("Newest 50")
        context['tags'] = tags
        return context

class ExampleList(generic.ListView):
    model = Collect
    template_name = 'collect/example.html'
    context_object_name = 'collects'
    
    def get_queryset(self):
        return Collect.objects.filter(public=True).order_by('-posted')[:100]

    def get_context_data(self, **kwargs):
        tags = Tag.objects.all()
        context = super().get_context_data(**kwargs)
        context['theme'] = _('Newest 100')
        return context

#user's collect list
class CollectList(generic.ListView):
    model = Collect
    template_name = 'collect/user_home.html'
    context_object_name = 'collects'

    def get_queryset(self):
        guest_user = self.request.user
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if guest_user.is_authenticated:
            return Collect.objects.filter(user=user, public=True).order_by('-posted').annotate(niced=Count('nice', filter=Q(nice__user=guest_user)))
        else:
            return Collect.objects.filter(user=user, public=True).order_by('-posted').annotate(coms=Count('comment'))

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        tags = Tag.objects.all()
        context = super().get_context_data(**kwargs)
        context['theme'] = _("Collection")
        context['tags'] = tags
        context['target'] = user
        return context

#wish of myself [LR]
class WishList(LR, generic.ListView):
    model = Collect
    template_name = 'collect/home.html'
    #paginated_by = PAGINATION_COUNT
    context_object_name = 'collects'

    def get_queryset(self):
        user = self.request.user
        return Collect.objects.filter(user=user, state="THIRSTY").order_by('-posted').annotate(niced=Count('nice', filter=Q(nice__user=user))).annotate(coms=Count('comment'))

    def get_context_data(self, **kwargs):
        tags = Tag.objects.all()
        context = super().get_context_data(**kwargs)
        context['theme'] = _("Your wish list")
        context['tags'] = tags
        return context

#wish of user [LR]
class UserWish(LR, generic.ListView):
    model = Collect
    template_name = 'collect/user_home.html'
    #paginated_by = PAGINATION_COUNT
    context_object_name = 'collects'

    def get_queryset(self):
        guest_user = self.request.user
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if guest_user.is_authenticated:
            return Collect.objects.filter(user=user, public=True).filter(state="THIRSTY").order_by('-posted')\
                .annotate(niced=Count('nice', filter=Q(nice__user=guest_user))).annotate(coms=Count('comment'))
        else:
            return Collect.objects.filter(user=user, public=True).filter(state="THIRSTY").order_by('-posted').annotate(coms=Count('comment'))

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        collects = Collect.objects.filter(user=user, public=True).filter(state="THIRSTY").order_by('-posted')
        tags = Tag.objects.all()
        context = super().get_context_data(**kwargs)
        context['theme'] = _("Wish List")
        context['tags'] = tags
        context['target'] = user
        return context

#detail
def detail(request, pk):
    collect = get_object_or_404(Collect, id=pk)
    user = request.user
    images = Photo.objects.filter(collect=collect).order_by("id")
    len_im = Photo.objects.filter(collect=collect).count()
    comments = Comment.objects.filter(collect=collect).order_by("pk")
    target = collect.user
    offers = Offer.objects.filter(target_col=collect).order_by('-posted')
    context = {}
    if images:
        main_image = Photo.objects.filter(collect=collect).order_by("id").first()
    if images:
        context['images'] = images
        context['main_image'] = main_image
        context['len_im'] = len_im
    context['offers'] = offers
    context['collect'] = collect
    context['comments'] = comments
    context['target'] = target
    if user.is_authenticated:
        pub_offers = Offer.objects.filter(target_col=collect).filter(Q(rec_col__public=True) | Q(rec_col__user=user)).order_by('-posted')
        niced = Nice.objects.filter(user=user, collect=collect).count()
        user_coll = Collect.objects.filter(user=user).order_by("-posted")
        context['user_coll'] = user_coll
        context['niced'] = niced
        context['pub_offers'] = pub_offers
        if user == collect.user:
            if LastVisit.objects.filter(user=user, collect=collect):
                visit = LastVisit.objects.filter(user=user, collect=collect)
                visit.update(time=timezone.now())
                return render(request, 'collect/detail.html', context)
            else:
                LastVisit.objects.create(user=user, collect=collect, time=timezone.now())
                return render(request, 'collect/detail.html', context)
        else:
            if History.objects.filter(user=user, collect=collect):
                history = History.objects.filter(user=user, collect=collect)
                history.update(time=timezone.now())
                return render(request, 'collect/detail.html', context)
            else:
                History.objects.create(user=user, collect=collect, time=timezone.now())
                return render(request, 'collect/detail.html', context)
    return render(request, 'collect/detail.html', context)

# category list
class CategoryList(LR, generic.ListView):
    model = Collect
    template_name = 'collect/category.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        categories = Category.objects.filter(user=user).annotate(num=Count('collect')).order_by('-num')
        no_cats = Collect.objects.filter(user=user).filter(category__isnull=True).order_by('-posted').annotate(niced=Count('nice', filter=Q(nice__user=user)))
        context = super().get_context_data(**kwargs)
        if categories:
            for category in categories:
                collects = Collect.objects.filter(category=category).order_by('-posted').annotate(niced=Count('nice', filter=Q(nice__user=user)))
                count = Collect.objects.filter(category=category).order_by('-posted')
            context['count'] = count
            context['collects'] = collects
        context['theme'] = _("Categories")
        context['categories'] = categories
        context['no_cats'] = no_cats
        return context

class UserCategory(generic.ListView):
    model = Collect
    template_name = 'collect/user_category.html'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        categories = Category.objects.filter(user=user).annotate(num=Count('collect')).order_by('-num')
        no_cats = Collect.objects.filter(user=user, public=True).filter(category__isnull=True).order_by('-posted')
        if categories:
            for category in categories:
                collects = Collect.objects.filter(category=category, public=True).order_by('-posted')
                counts = Collect.objects.filter(category=category, public=True).count()
        context = super().get_context_data(**kwargs)
        context['theme'] = user.username + _("'s categories")
        context['categories'] = categories
        context['no_cats'] = no_cats
        if categories:
            context['collects'] = collects
            context['counts'] = counts
        return context

#place 毎
class PlaceList(LR, generic.ListView):
    model = Place
    template_name = 'collect/place.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        places = Place.objects.filter(user=user).annotate(num=Count('collect')).order_by('-num')
        no_places = Collect.objects.filter(user=user).filter(place__isnull=True).order_by('-posted').annotate(niced=Count('nice', filter=Q(nice__user=user)))
        context = super().get_context_data(**kwargs)
        if places:
            for place in places:
                collects = Collect.objects.filter(place=place).order_by('-posted').annotate(niced=Count('nice', filter=Q(nice__user=user)))
                count = Collect.objects.filter(place=place).order_by('-posted')
            context['count'] = count
            context['collects'] = collects
        context['theme'] = _("Places")
        context['places'] = places
        context['no_places'] = no_places
        return context

#tag
class TagList(LR, generic.ListView):
    model = Tag
    template_name = 'collect/tag.html'

    def get_context_data(self, **kwargs):
        user = self.request.suer
        tags = Tag.objects.all()
        context['tags'] = tags
        return context

@login_required
def download_page(request):
    return render(request, 'collect/download.html')

@login_required
def download(request):
    response = HttpResponse(content_type='text/csv')
    context = {
        'file_name': request.POST.get('file_name')
    }
    if context['file_name'] == "":
        filename = 'data.csv'
    else:
        filename = context['file_name'] + '.csv'
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    all_fields = {
        "Name": 'name', "Product name": 'product_name', "Maker": 'maker',
        "Num": 'num', "Saved state": 'saved', "Place": 'place', "Category": 'category', "Tag": 'tag',
        "Acquisition day": 'acq_day', "Acquisition place": 'acq_place', "Price": 'price',
        "State": 'state', "Public": 'public', "Explain": 'explain'
    }
    checked = request.POST.getlist("select_for_csv")
    fields = []
    for key, value in all_fields.items():
        if value in checked:
            fields.append(key)
    writer = csv.writer(response)
    writer.writerow(fields)    #先頭
    for collect in Collect.objects.filter(user=request.user):
        #writer.writerow([collect.name, collect.product_name])
        list_ = []
        if "name" in checked:
            list_.append(collect.name)
        if "product_name" in checked:
            list_.append(collect.product_name)
        if "maker" in checked:
            list_.append(collect.maker)
        if "num" in checked:
            list_.append(collect.num)
        if "saved" in checked:
            list_.append(collect.saved)
        if "place" in checked:
            list_.append(collect.place)
        if "category" in checked:
            list_.append(collect.category)
        if "tag" in checked:
            strin = ""
            for tag in collect.tag.all():
                strin += str(Tag.Text(str(tag)).label) + "|"
            st = re.sub(",", '', strin)
            list_.append(st)
        if "acq_day" in checked:
            list_.append(collect.acq_day)
        if "acq_place" in checked:
            list_.append(collect.acq_place)
        if "price" in checked:
            list_.append(collect.price)
        if "state" in checked:
            list_.append(collect.state)
        if "public" in checked:
            list_.append(collect.public)
        if "explain" in checked:
            list_.append(collect.explain)
        writer.writerow(list_)
    return response

#search
def search(request):
    user = request.user
    context = {}
    context = {
        "search": request.GET.get("search"),
        "selection": request.GET.get("selection"),
    }
    condition = Q()

    selection = context['selection']
    search = context['search']

    condition_name = Q(name__icontains=search)
    condition_product = Q(product_name__icontains=search)
    condition_maker = Q(maker__icontains=search)

    context['theme'] = _('Search result - "{}"'.format(search))

    if user.is_authenticated:
        if search != "":
            if selection == "all":
                collects = Collect.objects.filter(condition_name | 
                condition_product | condition_maker).filter(public=True).annotate(niced=Count('nice', filter=Q(nice__user=user))).order_by('-posted')
            elif selection == "name":
                collects = Collect.objects.filter(condition_name, public=True).annotate(niced=Count('nice', filter=Q(nice__user=user))).order_by("-posted")
            elif selection == "product":
                collects = Collect.objects.filter(condition_product, public=True).annotate(niced=Count('nice', filter=Q(nice__user=user))).order_by("-posted")
            elif selection == "maker":
                collects = Collect.objects.filter(condition_maker, public=True).annotate(niced=Count('nice', filter=Q(nice__user=user))).order_by("-posted")
        else:
            collects = Collect.objects.filter(public=True).annotate(niced=Count('nice', filter=Q(nice__user=user))).order_by("-posted")
    else:
        if search != "":
            if selection == "all":
                collects = Collect.objects.filter(condition_name | 
                condition_product | condition_maker).filter(public=True).order_by('-posted')
            elif selection == "name":
                collects = Collect.objects.filter(condition_name, public=True).order_by("-posted")
            elif selection == "product":
                collects = Collect.objects.filter(condition_product, public=True).order_by("-posted")
            elif selection == "maker":
                collects = Collect.objects.filter(condition_maker, public=True).order_by("-posted")
        else:
            collects = Collect.objects.filter(public=True).order_by("-posted")
    paginator = Paginator(collects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    context['csrf_token'] = request.GET.get('csrfmiddlewaretoken')
    if user.is_authenticated:
        if search != "":
            if SearchHistory.objects.filter(user=user, text=search):
                hist = SearchHistory.objects.filter(user=user, text=search)
                hist.update(time=timezone.now())
            else:
                SearchHistory.objects.create(user=user, text=search, time=timezone.now())
    else:
        pass
    return render(request, 'collect/search.html', context)


class NiceList(LR, generic.ListView):
    model = Nice
    template_name = 'collect/nice.html'
    context_object_name = 'collects'

    def get_queryset(self):
        user = self.request.user
        return Collect.objects.annotate(niced=Count('nice', filter=Q(nice__user=user))).exclude(niced=0).annotate(nice_time=F('nice__posted')).order_by('-nice_time')
    
    def get_context_data(self, **kwargs):
        tags = Tag.objects.all()
        context = super().get_context_data(**kwargs)
        context['theme'] = _("Nice list")
        context['tags'] = tags
        return context

class NiceUser(LR, generic.ListView):
    model = User
    template_name = 'collect/nice_users.html'
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        collect = get_object_or_404(Collect, id=self.kwargs.get('collect_pk'))
        nices = Nice.objects.filter(collect=collect).order_by('-posted')
        #nicers = User.objects.annotate(niced=Count('nice', filter=Q(nice__collect=collect))).exclude(niced=0).annotate(nice_time=F('nice__posted')).order_by('-nice_time')
        niced = Nice.objects.filter(collect=collect).filter(user=user)
        context = {
            'collect': collect,
            #'nicers' = nicers,
            'nices': nices,
            'theme': _("Nice users"),
            'niced': niced,
        }
        return context