from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from secretsauce.apps.account.models import *
from secretsauce.apps.portal.models import *


class Command(BaseCommand):
    help = "Bulks creates sample instances of model in database"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        company1 = Company.objects.create(name = "McDonalds Australia")
        company2 = Company.objects.create(name = "MyNonnas International")

        adminuser = User.objects.create_superuser("admin@rms.com", "pw123123")
        adminuser2 = User.objects.create_superuser("sutdcapstone22@gmail.com", "pw123123")

        user1 = User.objects.create_user("user1@mcdonald.com", "pw123123", company = company1)
        user2 = User.objects.create_user("user2@mcdonald.com", "pw123123", company = company1)
        user3 = User.objects.create_user("geraldine@mynonnas.com", "pw123123", company = company2)

        p1 = Project.objects.create(
            title="McDonalds Australia Project 1", 
            company = company1, 
            description = "McDonalds Australia is the largest fastfood chain in Australia",
            )
        p2 = Project.objects.create(
            title="APAC Project", 
            company = company1,
            description = "This is to for McDonalds' APAC Pricing",
            )
        p3 = Project.objects.create(
            title = "Pricing Experiment", 
            company = company1,
            description = "Experiment to test our pricing strategy. Hope it works!",
            )
        p4 = Project.objects.create(
            title="SUTD Project", 
            company=company2,
            description="We are the premier F&B option in SUTD",
            )
        p5 = Project.objects.create(
            title="Operation Pricing", 
            company=company2,
            )

        p1.owners.add(user1)
        p2.owners.add(user1, user2)
        p3.owners.add(user2)
        p4.owners.add(user3)
        p5.owners.add(user3)


        m1 = PredictionModel.objects.create(
            name="MCMC", 
            description="Markov chain Monte Carlo (MCMC) methods comprise a class of algorithms for sampling from a probability distribution."
            )
        m2 = PredictionModel.objects.create(
            name="Test Model",
            description="This is a test model!"
        )

        self.stdout.write(self.style.SUCCESS('Successfully Created Sample Database'))
