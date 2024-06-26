from django import forms
from .models import Driver, Ride
from users.models import User


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your first name',
        'type': 'text',
        'name': 'username',
        'id': 'username',
        'class': 'form-control'
    }
    ))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter password',
        'type': 'password',
        'name': 'password1',
        'id': 'password1',
        'class': 'form-control'
    }
    ), required=True)
    # password2 = forms.CharField(widget=forms.PasswordInput(attrs={
    #     'placeholder': 'Confirm password',
    #     'type': 'password',
    #     'name': 'password2',
    #     'id': 'password2',
    #     'class': 'form-control'
    # }
    # ), required=True)
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter email address',
        'type': 'email',
        'name': 'email',
        'id': 'email',
        'class': 'form-control'
    }
    ))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1',
                  # 'password2'
                  ]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        # password1 = cleaned_data.get("password1")
        # password2 = cleaned_data.get("password2")

        # Check if email is already in use
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("The email address is already in use.")

        # if password1 and password2 and password1 != password2:
        #     raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class DriverProfileForm(forms.ModelForm):
    license_number = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter license number',
        'type': 'text',
        'name': 'license_number',
        'id': 'license_number',
        'class': 'form-control'
    }
    )
                                     )
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter phone number',
        'type': 'text',
        'name': 'phone_number',
        'id': 'phone_number',
        'class': 'form-control'
    }
    )
                                   )
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())
    car_model = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter car model',
        'type': 'text',
        'name': 'car_model',
        'id': 'car_model',
        'class': 'form-control'
    }
    )
                                )
    color = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter color',
        'type': 'text',
        'name': 'color',
        'id': 'color',
        'class': 'form-control'
    }
    )
                            )

    class Meta:
        model = Driver
        fields = ['license_number', 'phone_number', 'latitude',
                  'longitude', 'car_model', 'color', "driver_picture"]


class RideBookingForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Ride
        fields = ['start_location', 'end_location', "latitude", "longitude"]
