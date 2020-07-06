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
    path('datablocks/', views.DataBlockList.as_view(), name='data-block-list'),
    path('datablocks/<uuid:pk>', views.DataBlockDetail.as_view(), name='data-block-detail'),
    path('projects/', views.ProjectList.as_view(), name='project-list'),
    path('projects/<uuid:pk>', views.ProjectDetail.as_view(), name='project-detail'),
    path('constraintblocks/', views.ConstraintBlockList.as_view(), name='constraint-block-list'),
    path('constraintblocks/<uuid:pk>', views.ConstraintBlockDetail.as_view(), name='constraint-block-detail'),
    path('constraint/', views.ConstraintList.as_view(), name='constraint-list'),
    path('constraint/<uuid:pk>', views.ConstraintDetail.as_view(), name='constraint-detail'),
    path('constraintparameter/', views.ConstraintParameterList.as_view(), name='constraint-parameter-list'),
    path('constraintparameter/<uuid:pk>', views.ConstraintParameterList.as_view(), name='constraint-parameter-list'),
    path('constraintrelationship/', views.ConstraintRelationshipCreate.as_view(), name='constraint-relationship-create'),
    path('constraintrelationship/<uuid:pk>', views.ConstraintRelationshipDetail.as_view(), name='constraint-relationship-detail'),
    path('predictionmodel/', views.PredictionModelList.as_view(), name='prediction-model-list'),
    path('predictionmodel/<uuid:pk>', views.PredictionModelDetail.as_view(), name='prediction-model-detail'),
    path('modeltag/', views.ModelTagList.as_view(), name='model-tag-list'),
    path('modeltag/<int:pk>', views.ModelTagDetail.as_view(), name='model-tag-detail'),
    path('itemlist/', views.ItemListList.as_view(), name='itemlist-list')
]