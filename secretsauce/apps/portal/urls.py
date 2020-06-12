from django.urls import path, include
from secretsauce.apps.portal import views

# /users/ create user
# /token/login/ obtain user authentication token (login)
# /token/logout/ logout user, remove user authentication token

# /users/activation/ activate user (currently not in use)
# /users/resend_activation/ resend user activation email (currently not in use)
# /users/me/ retrieve or update or delete the authenricated user
# /users/set_password/ change user password
# /users/reset_password/ send email to user with password reset link (need to setup PASSWORD_RESET_CONFIRM_URL)
# /users/reset_password_confirm/ finish reset password process
# all endpoints available please view: https://djoser.readthedocs.io/en/latest/base_endpoints.html

urlpatterns = [
    path('datablocks/', views.DataBlockList.as_view()),
    path('datablocks/<int:pk>', views.DataBlockDetail.as_view()),
    path('projects/', views.ProjectList.as_view()),
    path('projects/<int:pk>', views.ProjectDetail.as_view()),
    path('constraints/', views.ConstraintList.as_view()),
    path('constraints/<int:pk>', views.ConstraintDetail.as_view()),
    path('predictionmodel/', views.PredictionModelList.as_view()),
    path('predictionmodel/<int:pk>', views.PredictionModelDetail.as_view()),
]