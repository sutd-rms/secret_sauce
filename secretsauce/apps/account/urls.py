from django.urls import path, include
from secretsauce.apps.account import views

# /users/ create user or retrieve current user details (for non-admin) or user list (for admin)
# /token/login/ obtain user authentication token (login)
# /token/logout/ logout user, remove user authentication token

# /users/activation/ activate user (currently not in use)
# /users/resend_activation/ resend user activation email (currently not in use)
# /users/<uuid:pk>/ retrieve or update or delete the authenticated user (only acccessible by admin user)
# /users/set_password/ change user password
# /users/reset_password/ send email to user with password reset link (need to setup PASSWORD_RESET_CONFIRM_URL)
# /users/reset_password_confirm/ finish reset password process
# all endpoints available please view: https://djoser.readthedocs.io/en/latest/base_endpoints.html

urlpatterns =[
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('editprofile/', views.EditProfile.as_view(), name='edit_profile'),
    path('company/', views.CompanyList.as_view()),
    path('company/<uuid:pk>', views.CompanyDetail.as_view()),
    path('inviteuser/', views.InviteUser.as_view(), name='user_creation')
]
