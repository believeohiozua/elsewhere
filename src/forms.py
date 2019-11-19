from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, Profile

Gender_CHOICE = [   
        ('Male', 'Male'),
        ('Female', 'Female'),       
        ]

class MyCustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput({'placeholder':'First Name','class':'form-class'}))    
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput({'placeholder':'Last Name','class':'form-class'}))    
    gender = forms.CharField(required = True, label='Gender', widget=forms.Select(choices=Gender_CHOICE))
    birthday = forms.DateField(widget=forms.SelectDateWidget)   
    phone_number = forms.IntegerField(required = True, help_text = '',  label='Phone') 
    class Meta:
        model = User 
        fields = '__all__'
    
    def save(self, request):       
        request.user.first_name = self.cleaned_data['first_name']      
        request.user.last_name = self.cleaned_data['last_name']
        request.user.gender = self.cleaned_data['gender']       
        request.user.phone_number = self.cleaned_data['phone_number'] 
        request.user.birthday = self.cleaned_data['birthday']       
        request.user = super(MyCustomSignupForm, self).save(request)
        request.user.save()
        
        profile, created=Profile.objects.get_or_create(     
        user=request.user,       
        gender=self.cleaned_data['gender'],
        phone_number=self.cleaned_data['phone_number'],  
        birthday=self.cleaned_data['birthday']     
        )       
        profile.save()
        return request.user


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=30, label='Username', widget=forms.TextInput({'placeholder':'UserName','class': 'form-control'})) 
    first_name = forms.CharField(max_length=30, label='First name', widget=forms.TextInput({'placeholder':'first name','class': 'form-control'}))
    last_name = forms.CharField(max_length=30, label='Last name', widget=forms.TextInput({'placeholder':'last name','class': 'form-control'}))
    email = forms.EmailField( widget=forms.EmailInput({'placeholder':'E-Mail','class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email','first_name','last_name']

class ProfileForm(forms.ModelForm):
    phone_number = forms.IntegerField(required =True,  help_text = "Whatsapp",  widget=forms.NumberInput(attrs={'class': 'form-control'}))
    gender = forms.CharField(label='Gender', widget=forms.Select(choices=Gender_CHOICE))
    birthday =  forms.DateField(required = False, label='Birthday',
        widget=forms.DateInput( format='%Y-%m-%d', attrs={'class': 'form-control vDateField', 'type':'Date'}),
        input_formats=['%Y-%m-%d',]
        ) 

    class Meta:
        model = Profile
        fields = ['gender', 'birthday','profile_photo',  'phone_number',
                    ]

PAYMENT_CHOICES = (
    ('O', 'Online Payment'),
    ('B', 'Bank Payment')
)
STATE_CHOICE = (
    ('None', 'Select State'),('Abia', 'Abia'),('Abuja', 'Abuja'),('Adamawa', 'Adamawa'),('Akwa_Ibom', 'Akwa Ibom'),('Anambra', 'Anambra'),('Bauchi', 'Bauchi'),
    ('Bayelsa', 'Bayelsa'),('Benue', 'Benue'),('Borno', 'Borno'),('Cross_River', 'Cross River'),('Delta', 'Delta'),
    ('Ebonyi', 'Ebonyi'),('Enugu', 'Enugu'),('Edo', 'Edo'),('Ekiti', 'Ekiti'),('Gombe', 'Gombe'),('Imo', 'Imo'),
    ('Jigawa', 'Jigawa'),('Kaduna', 'Kaduna'),('Kano', 'Kano'),('Katsina', 'Katsina'),('Kebbi', 'Kebbi'),('Kogi', 'Kogi'),
    ('Kwara', 'Kwara'),('Lagos', 'Lagos'),('Nasarawa', 'Nasarawa'),('Niger', 'Niger'),('Ogun', 'Ogun'),('Ondo', 'Ondo'),
    ('Osun', 'Osun'),('Oyo', 'Oyo'),('Plateau', 'Plateau'),('Rivers', 'Rivers'),('Sokoto', 'Sokoto'),('Taraba', 'Taraba'),
    ('Yobe', 'Yobe'),('Zamfara', 'Zamfara'),   
)
LGA_CHOICE = (
    ('None', 'Select State'),('Abia', 'Abia'),('Abuja', 'Abuja'),('Adamawa', 'Adamawa'),('Akwa_Ibom', 'Akwa Ibom'),('Anambra', 'Anambra'),('Bauchi', 'Bauchi'),
    ('Bayelsa', 'Bayelsa'),('Benue', 'Benue'),('Borno', 'Borno'),('Cross_River', 'Cross River'),('Delta', 'Delta'),
    ('Ebonyi', 'Ebonyi'),('Enugu', 'Enugu'),('Edo', 'Edo'),('Ekiti', 'Ekiti'),('Gombe', 'Gombe'),('Imo', 'Imo'),
    ('Jigawa', 'Jigawa'),('Kaduna', 'Kaduna'),('Kano', 'Kano'),('Katsina', 'Katsina'),('Kebbi', 'Kebbi'),('Kogi', 'Kogi'),
    ('Kwara', 'Kwara'),('Lagos', 'Lagos'),('Nasarawa', 'Nasarawa'),('Niger', 'Niger'),('Ogun', 'Ogun'),('Ondo', 'Ondo'),
    ('Osun', 'Osun'),('Oyo', 'Oyo'),('Plateau', 'Plateau'),('Rivers', 'Rivers'),('Sokoto', 'Sokoto'),('Taraba', 'Taraba'),
    ('Yobe', 'Yobe'),('Zamfara', 'Zamfara'),   
)



class CheckoutForm(forms.Form):    
    shipping_street=forms.CharField(required=False, max_length=1000)#, label="Other categories", widget=forms.TextInput({'placeholder':'If Category is not listed'}))
    shipping_state=forms.CharField(required=False, widget=forms.Select(choices=STATE_CHOICE,attrs={
                                                        
                                                                }))
    shipping_lga=forms.CharField(required=False, max_length=100)
    phone_number=forms.IntegerField(required=False)
    default=forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
                           'type':"checkbox",
                           'class':"custom-control-input",
                           'id':"set_default_shipping"
                            }))
    use_default_shipping=forms.BooleanField(required=False)
    message=forms.CharField(required=False, widget=forms.Textarea(attrs={
                            'rows':4,
                            'cols':4,
                            'style':"height: 100px;"
                            }))
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    class Meta:
        model = Address
        fields = ('shipping_street', 'shipping_state','shipping_lga','default',)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


SIZES_CHOICES = (  
    ('L', 'L'),
    ('XL', 'XL'),
     ('XXL', 'XXL')
)

class FormTypeForm(forms.Form):
    #general
    size = forms.ChoiceField(
        widget=forms.RadioSelect, choices=SIZES_CHOICES)
    # skirt
    skirt_length = forms.CharField(required=False)

    # Shirt
    shirt_length = forms.CharField(required=False)
    # Gown
    gown_length = forms.CharField(required=False)
    # trouser
    trouser_length = forms.CharField(required=False)
    


    

