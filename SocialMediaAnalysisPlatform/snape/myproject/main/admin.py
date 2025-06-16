from django.contrib import admin
from .models import Category, UserAccount, Data , Profile, Testimonial, Businessman

# Register the models
admin.site.register(Category)
admin.site.register(Data)
admin.site.register(Profile)
admin.site.register(Testimonial)
admin.site.register(Businessman)




class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    list_filter = ('role',)

admin.site.register(UserAccount, UserAccountAdmin)



