from django.urls import path, include
from rest_framework import routers
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

router = routers.SimpleRouter()
router.register(r'datablocks', views.VizDataBlock, basename='datablocks')
router.register(r'datablocks', views.DataBlockPrice, basename='datablocks')
router.register(r'trainedmodels', views.TrainedModelInfo, basename='trainedmodels')

urlpatterns = [
    path('datablocks/', views.DataBlockList.as_view(), name='data-block-list'),
    path('datablocks/<uuid:pk>', views.DataBlockDetail.as_view(), name='data-block-detail'),

    path('projects/', views.ProjectList.as_view(), name='project-list'),
    path('projects/<uuid:pk>', views.ProjectDetail.as_view(), name='project-detail'),
    path('projects/<uuid:pk>/items/', views.ProjectItems.as_view(), name='item-directory-list'),

    path('constraintsets/', views.ConstraintBlockListCreate.as_view()),
    path('constraintsets/<uuid:pk>', views.ConstraintBlockDetail.as_view()),
    path('constraintsets/<uuid:pk>/parameters/', views.ConstraintBlockItems.as_view()),
    path('constraints/', views.ConstraintListAndCreate.as_view()),
    path('constraints/<uuid:pk>', views.ConstraintDetail.as_view()),
    path('constraintcategories/', views.ConstraintCategoryList.as_view()),
    path('constraintcategories/<uuid:pk>', views.ConstraintCategoryDetail.as_view()),

    path('predictionmodels/', views.PredictionModelList.as_view(), name='prediction-model-list'),
    path('predictionmodels/<uuid:pk>', views.PredictionModelDetail.as_view(), name='prediction-model-detail'),
    path('modeltags/', views.ModelTagList.as_view(), name='model-tag-list'),
    path('modeltags/<int:pk>', views.ModelTagDetail.as_view(), name='model-tag-detail'),

    path('trainedmodels/', views.TrainModel.as_view()), 
    path('trainedmodels/<uuid:pk>', views.TrainedModelDetail.as_view()),

    path('optimizers/', views.OptimizerListCreate.as_view()),
    path('optimizers/<uuid:pk>', views.OptimizerDetail.as_view()),
] + router.urls