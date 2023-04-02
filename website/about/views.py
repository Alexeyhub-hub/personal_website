from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'


class ContactsView(TemplateView):
    template_name = 'about/contacts.html'
