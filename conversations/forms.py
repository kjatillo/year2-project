from django import forms
from .models import ConversationMessage


class ConversationMessageForm(forms.ModelForm):
    class Meta:
        model = ConversationMessage
        fields = ('content',)

    def __init__(self, *args, **kwargs):
            super(ConversationMessageForm, self).__init__(*args, **kwargs)

            self.fields['content'].label = ''
            self.fields['content'].widget.attrs['placeholder'] = 'Enter your message..'
            self.fields['content'].widget.attrs['rows'] = 4
            self.fields['content'].widget.attrs['columns'] = 15
