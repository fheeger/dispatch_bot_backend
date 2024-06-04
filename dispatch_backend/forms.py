from django import forms

from dispatch_backend.models import Message, Channel


class MessageForm(forms.ModelForm):

    channels = forms.ModelMultipleChoiceField(queryset=Channel.objects.none(), required=False)
    turn_when_received = forms.IntegerField(required=False)
    is_lost = forms.BooleanField(required=False)
    approved = forms.BooleanField(required=False)
    version = forms.IntegerField(required=False)

    class Meta:
        model = Message
        exclude = ()

    def __init__(self, *args, **kwargs):
        """ put relevant channels"""
        instance = kwargs.get('instance', None)
        super(MessageForm, self).__init__(*args, **kwargs)
        if instance:
            if "version" in self.fields:
                self.fields["version"].widget = forms.HiddenInput()
                self.fields['version'].initial = instance.version
            self.fields['channels'].choices = [(channel.id, channel.name) for channel in Channel.objects.filter(game=instance.game)]
            self.fields['channels'].initial = [c.pk for c in instance.channels.all()]
            self.fields['turn_when_received'].initial = instance.turn_when_received
            self.fields['is_lost'].initial = instance.is_lost
            self.fields['approved'].initial = instance.approved