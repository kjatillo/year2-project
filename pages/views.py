from django.views.generic import TemplateView 


class HomePageView(TemplateView):
    template_name = 'index.html'
    

class TeamView(TemplateView):
    template_name = 'team.html'
