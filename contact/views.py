from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import ContactForm


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            content = form.cleaned_data['content']

            body = {
                'name': name,
                'email': email,
                'subject': subject,
                'content': content,
            }

            message = "\n".join(body.values())
            recipient_emails = ['admin@project.ie']

            try:
                send_mail(subject, message, email, recipient_emails)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('contact:contact_success')
    else:
        form = ContactForm()

    return render(
        request, 
        'contact_us_form.html', 
        {'form': form}
    )


def contact_success(request):
    return render(request, 'contact_success.html')
