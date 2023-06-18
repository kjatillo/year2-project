from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from services.models import Service
from .forms import ConversationMessageForm
from .models import Conversation


@login_required
def new_conversation(request, service_pk):
    service = get_object_or_404(Service, pk=service_pk)

    if service.provider == request.user:
        return redirect('home')
    
    conversations = Conversation.objects.filter(service=service).filter(members__in=[request.user.id])

    if conversations:
        return redirect('conversation:conversation_detail', pk=conversations.first().id)
    
    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            conversation = Conversation.objects.create(service=service)
            conversation.members.add(request.user)
            conversation.members.add(service.provider)
            conversation.save()

            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            return redirect('conversation:conversation_detail', pk=conversation.id)
    else:
        form = ConversationMessageForm()

    return render(
        request,
        'conversation/new_conversation.html',
        {'form': form, 'service': service}
    )


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(members__in=[request.user.id])

    return render(
        request, 
        'conversation/inbox.html', 
        {'conversations': conversations}
    )


@login_required
def detail(request, pk):
    conversation = Conversation.objects.filter(members__in=[request.user.id]).get(pk=pk)

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            conversation.save()

            return redirect('conversation:conversation_detail', pk=pk)
    else:
        form = ConversationMessageForm()

    return render(
        request, 
        'conversation/conversation_detail.html', 
        {'conversation': conversation, 'form': form}
    )


class ConversationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Conversation
    template_name = 'conversation/conversation_delete.html'
    success_url = reverse_lazy('conversation:inbox')

    def test_func(self):
        conversation = self.get_object()
        return self.request.user in conversation.members.all()
