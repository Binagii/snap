from django import forms
from .models import UserAccount, Category , DataItem , Profile  
from pytz import common_timezones

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
               
class UserAccountForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ['username', 'email', 'password','role']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
       }
        
        
class BusinessmanForm(UserAccountForm):
    class Meta:
        model = UserAccount
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
       }
        
        
class ContentCreatorForm(UserAccountForm):
    
    class Meta:
        model = UserAccount
        fields = ['username', 'email', 'password']   
        widgets = {
            'password ': forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
        }     
       
class DataAnalystForm(UserAccountForm):
    
    class Meta:
        model = UserAccount
        fields = ['username', 'email', 'password']   
        widgets = {
            'password ': forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
        }  
        
class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile 
        fields = ['first_name', 'last_name', 'company' , 'timezone']            
        widgets = {
            'timezone': forms.Select(choices=[(tz, tz) for tz in common_timezones], attrs={'class': 'form-control'}),
        }
        
class CreatorForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'company', 'timezone']
        widgets = {
            'timezone' : forms.Select(choices=[(tz, tz) for tz in common_timezones], attrs={'class': 'form-control'}),
        }        
    

class DataAnalystForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'company', 'timezone']
        widgets = {
            'timezone' : forms.Select(choices=[(tz, tz) for tz in common_timezones], attrs={'class': 'form-control'}),
        }
        
    


class VisibilitySettingsForm(forms.ModelForm):
    class Meta:
        model = DataItem
        fields = ['visibility']
        widgets = {
            'visibility' : forms.RadioSelect
        }
                    
 
       
   

     
        
        
