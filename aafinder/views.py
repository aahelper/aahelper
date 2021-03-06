import datetime
from django.views import generic
from django.shortcuts import redirect
# from django.http import Http404
# from django.utils.translation import gettext as _

from .models import Meeting, MeetingArea, MeetingType, Location, MeetingCode
from .forms import MeetingSearchForm
from .utils import now
from django.shortcuts import render

def manifest(request):
    resp = render(request, 'site.webmanifest')
    resp.content_type='application/json'
    print(dir(resp))
    return resp

class InitialFormMixin:
    form_class = MeetingSearchForm
    initial = {}
    prefix = None

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        initial_data = {
            # 'date': get_now_date(),
            # 'start_time': get_now_time(),
            'area': 'all',
            'time': now,
            'day': self.get_current_day_meeting_type_slug,
            'hours_from_start': 3,
        }
        return initial_data

    def get_prefix(self):
        """Return the prefix to use for forms."""
        return self.prefix

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_class

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_current_day_word(self):
        return now().strftime("%A")

    def get_current_day_meeting_type_slug(self):
        return MeetingType.objects.only("slug").get(
            type=self.get_current_day_word()).slug

    def set_filter_values(self, form):
        if form.is_valid():
            start_time = form.cleaned_data['time']
            today = datetime.datetime.combine(now().today(), start_time)
            end_time = today + datetime.timedelta(
                hours=form.cleaned_data['hours_from_start'])
            day_word = MeetingType.objects.get(
                slug=form.cleaned_data['day']).type
            area = form.cleaned_data['area']
        else:
            start_time = now()
            today = now().today()
            end_time = datetime.datetime.combine(today, start_time.time())
            end_time = end_time + datetime.timedelta(hours=3)
            day_word = MeetingType.objects.get(
                type=self.get_current_day_word())
            area = "All"

        if area.lower() == 'all':
            area = MeetingArea(area=area)
        else:
            area = MeetingArea.objects.get(slug=area)

        if end_time.day > today.day or end_time.month > today.month:
            end_time = end_time.replace(hour=23, minute=59)

        self.start_time = start_time
        self.end_time = end_time
        self.day_word = day_word
        self.area = area

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self, 'day_word'):
            self.form = self.get_form()
            self.set_filter_values(self.form)
        context['today'] = self.day_word
        context['now'] = self.start_time
        context['hours_from'] = self.end_time
        context['area'] = self.area

        context['form'] = self.form
        return context

class IndexView(InitialFormMixin, generic.ListView):
    template_name = 'aasandiego/index.html'
    context_object_name = 'latest_meeting_list'

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_queryset(self):
        """Return the last five published questions."""
        self.form = self.get_form()
        self.set_filter_values(self.form)
        qs = Meeting.objects.filter(
            types__type=self.day_word,
            time__gte=self.start_time,
            time__lte=self.end_time,
            ).select_related('area').order_by('time')

        if self.area.id:
            qs = qs.filter(area=self.area)

        return qs


class DetailView(InitialFormMixin, generic.DetailView):
    model = Meeting
    template_name = 'aasandiego/detail.html'


class AreaDetailView(InitialFormMixin, generic.DetailView):
    model = MeetingArea
    template_name = 'aasandiego/area_detail.html'


class LocationDetailView(InitialFormMixin, generic.DetailView):
    model = Location
    template_name = 'aasandiego/location_detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        self.form = self.get_form()
        self.set_filter_values(self.form)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meetings'] = context['object'].meeting_set.all().select_related('area').order_by('time', )
        return context

class CodeDetailView(InitialFormMixin, generic.DetailView):
    model = MeetingCode
    template_name = 'aasandiego/meeting_code_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meetings'] = context['object'].meeting_set.all().select_related('area').order_by('time', )
        return context

# class MeetingSearch(IndexView):
#     # model = Meeting
#     # template_name = 'aasandiego/detail.html'

#     # def get_form_kwargs(self):
#     #     """Return the keyword arguments for instantiating the form."""
#     #     kwargs = {
#     #         'initial': self.get_initial(),
#     #         'prefix': self.get_prefix(),
#     #     }

#     #     # if self.request.method in ('POST', 'PUT'):
#     #     kwargs.update({'data': self.kwargs})
#     #     # kwargs.update({
#     #     #     'data': self.request.POST,
#     #     #     'files': self.request.FILES,
#     #     # })
#     #     return kwargs

#     def get(self, request, *args, **kwargs):
#         form = self.get_form()
#         if form.is_valid():
#             return redirect(
#                 "aafinder:meeting_redirect",
#                 day=form.cleaned_data['day'],
#                 area=form.cleaned_data['area'],
#                 time=form.cleaned_data['time'].strftime("%H:%M"),
#                 hours_from_start=form.cleaned_data['hours_from_start']
#             )

#         return super().get(request, *args, **kwargs)


# class MeetingView(IndexView):
#     # model = Meeting
#     # template_name = 'aasandiego/detail.html'

#     def get_form_kwargs(self):
#         """Return the keyword arguments for instantiating the form."""
#         kwargs = {
#             'initial': self.get_initial(),
#             'prefix': self.get_prefix(),
#         }

#         # if self.request.method in ('POST', 'PUT'):
#         kwargs.update({'data': self.kwargs})
#         # kwargs.update({
#         #     'data': self.request.POST,
#         #     'files': self.request.FILES,
#         # })
#         return kwargs
