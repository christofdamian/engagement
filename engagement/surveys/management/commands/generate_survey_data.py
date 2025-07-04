from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
import random
from datetime import datetime, timedelta
from organizations.models import Organization, OrganizationMembership
from surveys.models import Survey, Question, SurveyResponse, Answer


class Command(BaseCommand):
    help = 'Generate random users and survey responses for an organization'

    def add_arguments(self, parser):
        parser.add_argument(
            'organization_id',
            type=int,
            help='ID of the organization to generate data for'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=15,
            help='Number of users to create (default: 15)'
        )
        parser.add_argument(
            '--weeks',
            type=int,
            default=12,
            help='Number of weeks to spread responses over (default: 12 weeks = 3 months)'
        )
        parser.add_argument(
            '--responses-per-week',
            type=int,
            default=3,
            help='Average number of responses per week (default: 3)'
        )

    def handle(self, *args, **options):
        organization_id = options['organization_id']
        num_users = options['users']
        num_weeks = options['weeks']
        responses_per_week = options['responses_per_week']

        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Organization with ID {organization_id} does not exist')
            )
            return

        # Check if organization has a survey
        try:
            survey = organization.survey
        except Survey.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Organization "{organization.name}" does not have a survey')
            )
            return

        # Get all questions for the survey
        questions = list(Question.objects.filter(theme__survey=survey))
        if not questions:
            self.stdout.write(
                self.style.ERROR(f'Survey for "{organization.name}" has no questions')
            )
            return

        self.stdout.write(f'Generating data for organization: {organization.name}')
        self.stdout.write(f'Survey: {survey.title}')
        self.stdout.write(f'Available questions: {len(questions)}')
        self.stdout.write(f'Questions per cycle: {organization.questions_per_cycle}')

        with transaction.atomic():
            # Generate users
            users = self.create_users(num_users, organization)
            
            # Generate survey responses spread over time
            self.create_survey_responses(
                users, organization, questions, num_weeks, responses_per_week
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated {num_users} users and survey responses '
                f'for "{organization.name}"'
            )
        )

    def create_users(self, num_users, organization):
        """Create random users and add them to the organization"""
        users = []
        
        # Sample first and last names for variety
        first_names = [
            'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry',
            'Ivy', 'Jack', 'Kate', 'Liam', 'Maya', 'Noah', 'Olivia', 'Peter',
            'Quinn', 'Rachel', 'Sam', 'Tara', 'Uma', 'Victor', 'Wendy', 'Xavier',
            'Yara', 'Zoe', 'Alex', 'Blake', 'Casey', 'Drew'
        ]
        
        last_names = [
            'Anderson', 'Brown', 'Clark', 'Davis', 'Evans', 'Garcia', 'Harris',
            'Johnson', 'Jones', 'Lee', 'Martinez', 'Miller', 'Moore', 'Rodriguez',
            'Smith', 'Taylor', 'Thomas', 'White', 'Williams', 'Wilson'
        ]

        for i in range(num_users):
            # Generate unique email
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f'{first_name.lower()}.{last_name.lower()}{i}@{organization.name.lower().replace(" ", "")}.com'
            
            # Ensure email is unique
            while User.objects.filter(email=email).exists():
                email = f'{first_name.lower()}.{last_name.lower()}{i}{random.randint(10, 99)}@{organization.name.lower().replace(" ", "")}.com'
            
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='testpassword123'
            )
            
            # Add user to organization as member
            OrganizationMembership.objects.create(
                user=user,
                organization=organization,
                role='member'
            )
            
            users.append(user)
            
            if (i + 1) % 5 == 0:
                self.stdout.write(f'Created {i + 1} users...')

        self.stdout.write(f'Created {len(users)} users total')
        return users

    def create_survey_responses(self, users, organization, questions, num_weeks, responses_per_week):
        """Create survey responses spread over the specified time period"""
        
        # Calculate date range (last N weeks)
        end_date = timezone.now()
        start_date = end_date - timedelta(weeks=num_weeks)
        
        total_responses = num_weeks * responses_per_week
        
        self.stdout.write(
            f'Creating approximately {total_responses} responses over {num_weeks} weeks '
            f'({start_date.date()} to {end_date.date()})'
        )

        responses_created = 0
        
        for week in range(num_weeks):
            # Calculate week boundaries
            week_start = start_date + timedelta(weeks=week)
            week_end = week_start + timedelta(weeks=1)
            
            # Randomize number of responses for this week (around the average)
            week_responses = max(1, responses_per_week + random.randint(-1, 2))
            
            for _ in range(week_responses):
                # Random date within the week (weekdays more likely)
                random_day = random.randint(0, 6)
                if random_day < 5:  # Weekday (Monday-Friday more likely)
                    response_date = week_start + timedelta(
                        days=random_day,
                        hours=random.randint(8, 18),  # Business hours
                        minutes=random.randint(0, 59)
                    )
                else:  # Weekend (less likely)
                    response_date = week_start + timedelta(
                        days=random_day,
                        hours=random.randint(10, 22),
                        minutes=random.randint(0, 59)
                    )
                
                # Ensure date doesn't exceed current time
                if response_date > timezone.now():
                    response_date = timezone.now() - timedelta(minutes=random.randint(5, 60))
                
                # Pick a random user
                user = random.choice(users)
                
                # Create survey response
                response = SurveyResponse.objects.create(
                    user=user,
                    organization=organization,
                    created_at=response_date,
                    completed_at=response_date
                )
                
                # Select random questions based on organization's questions_per_cycle
                selected_questions = random.sample(
                    questions, 
                    min(organization.questions_per_cycle, len(questions))
                )
                
                # Create answers for selected questions
                for question in selected_questions:
                    # Generate realistic ratings (slight bias toward higher ratings)
                    rating = self.generate_realistic_rating()
                    
                    Answer.objects.create(
                        response=response,
                        question=question,
                        rating=rating
                    )
                
                responses_created += 1
                
                if responses_created % 10 == 0:
                    self.stdout.write(f'Created {responses_created} responses...')

        self.stdout.write(f'Created {responses_created} total responses')

    def generate_realistic_rating(self):
        """Generate realistic ratings with some bias toward positive scores"""
        # 70% chance of positive rating (6-10)
        # 20% chance of neutral rating (4-5)
        # 10% chance of negative rating (1-3)
        
        rand = random.random()
        if rand < 0.7:  # Positive
            return random.randint(6, 10)
        elif rand < 0.9:  # Neutral
            return random.randint(4, 5)
        else:  # Negative
            return random.randint(1, 3)