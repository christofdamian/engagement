from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from organizations.models import Organization, OrganizationMembership
import random


class Command(BaseCommand):
    help = 'Generate example org-chart data for an organization'

    def add_arguments(self, parser):
        parser.add_argument('--org-name', type=str, default='Example Corp', help='Name of the organization')
        parser.add_argument('--size', type=str, choices=['small', 'medium', 'large'], default='medium', 
                          help='Size of the organization (small: 15-25, medium: 30-50, large: 60-100)')
        parser.add_argument('--clear', action='store_true', help='Clear existing data for the organization')

    def handle(self, *args, **options):
        org_name = options['org_name']
        size = options['size']
        clear_existing = options['clear']
        
        # Size configurations
        size_configs = {
            'small': {'min_employees': 15, 'max_employees': 25},
            'medium': {'min_employees': 30, 'max_employees': 50}, 
            'large': {'min_employees': 60, 'max_employees': 100}
        }
        
        config = size_configs[size]
        num_employees = random.randint(config['min_employees'], config['max_employees'])
        
        # Job titles by level
        job_titles = {
            'ceo': ['Chief Executive Officer', 'President'],
            'c_level': ['Chief Technology Officer', 'Chief Operating Officer', 'Chief Financial Officer', 
                       'Chief Marketing Officer', 'Chief Human Resources Officer'],
            'vp': ['VP of Engineering', 'VP of Sales', 'VP of Marketing', 'VP of Operations', 
                   'VP of Finance', 'VP of Human Resources', 'VP of Product'],
            'director': ['Director of Engineering', 'Director of Sales', 'Director of Marketing', 
                        'Director of Operations', 'Director of Finance', 'Director of HR', 
                        'Director of Product', 'Director of Customer Success'],
            'manager': ['Engineering Manager', 'Sales Manager', 'Marketing Manager', 
                       'Operations Manager', 'Finance Manager', 'HR Manager', 'Product Manager',
                       'Team Lead', 'Project Manager', 'Account Manager'],
            'senior': ['Senior Software Engineer', 'Senior Sales Representative', 'Senior Marketing Specialist',
                      'Senior Operations Analyst', 'Senior Financial Analyst', 'Senior HR Specialist',
                      'Senior Product Designer', 'Senior Data Analyst', 'Senior DevOps Engineer'],
            'mid': ['Software Engineer', 'Sales Representative', 'Marketing Specialist', 
                   'Operations Analyst', 'Financial Analyst', 'HR Specialist', 'Product Designer',
                   'Data Analyst', 'DevOps Engineer', 'Business Analyst'],
            'junior': ['Junior Software Engineer', 'Junior Sales Representative', 'Junior Marketing Coordinator',
                      'Junior Operations Assistant', 'Junior Financial Analyst', 'Junior HR Coordinator',
                      'Junior Product Designer', 'Junior Data Analyst', 'Intern']
        }
        
        # Common first and last names for generating realistic names
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Emily', 'James', 'Ashley',
            'William', 'Jessica', 'Richard', 'Jennifer', 'Joseph', 'Amanda', 'Thomas', 'Melissa',
            'Christopher', 'Michelle', 'Daniel', 'Kimberly', 'Matthew', 'Amy', 'Anthony', 'Angela',
            'Mark', 'Helen', 'Donald', 'Brenda', 'Steven', 'Nicole', 'Paul', 'Katherine', 'Andrew',
            'Samantha', 'Joshua', 'Christine', 'Kenneth', 'Rachel', 'Kevin', 'Deborah', 'Brian',
            'Caroline', 'George', 'Janet', 'Edward', 'Catherine', 'Ronald', 'Maria'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez',
            'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor',
            'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez',
            'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright',
            'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker',
            'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts'
        ]
        
        self.stdout.write(f"Generating org-chart for '{org_name}' with {num_employees} employees...")
        
        with transaction.atomic():
            # Get or create organization
            org, created = Organization.objects.get_or_create(
                name=org_name,
                defaults={'questions_per_cycle': 5}
            )
            
            if clear_existing:
                # Clear existing memberships
                OrganizationMembership.objects.filter(organization=org).delete()
                self.stdout.write(f"Cleared existing data for '{org_name}'")
            
            # Always ensure user with ID=1 is added to the organization
            try:
                admin_user = User.objects.get(id=1)
                admin_membership, created = OrganizationMembership.objects.get_or_create(
                    user=admin_user,
                    organization=org,
                    defaults={
                        'role': 'owner',
                        'title': 'System Administrator',
                        'reports_to': None
                    }
                )
                if created:
                    self.stdout.write(f"Added user ID=1 ({admin_user.username}) as owner to organization")
                else:
                    self.stdout.write(f"User ID=1 ({admin_user.username}) already in organization")
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING("User with ID=1 does not exist, skipping admin user addition"))
            
            # Create users and memberships
            employees = []
            
            # Helper function to create employee
            def create_employee(title, role='member'):
                first = random.choice(first_names)
                last = random.choice(last_names)
                email = f"{first.lower()}.{last.lower()}@{org_name.lower().replace(' ', '')}.com"
                
                # Create user
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': email,
                        'first_name': first,
                        'last_name': last,
                    }
                )
                
                # Create membership
                membership, created = OrganizationMembership.objects.get_or_create(
                    user=user,
                    organization=org,
                    defaults={
                        'role': role,
                        'title': title,
                        'reports_to': None
                    }
                )
                
                return membership
            
            # Create CEO (top level)
            ceo = create_employee(random.choice(job_titles['ceo']), 'owner')
            employees.append({'membership': ceo, 'level': 0, 'can_manage': True})
            
            # Create C-level executives (1-3 depending on size)
            c_level_count = min(3, max(1, num_employees // 20))
            c_level_employees = []
            
            for _ in range(c_level_count):
                c_level = create_employee(random.choice(job_titles['c_level']), 'admin')
                c_level.reports_to = ceo
                c_level.save()
                c_level_employees.append({'membership': c_level, 'level': 1, 'can_manage': True})
                employees.append(c_level_employees[-1])
            
            # Create VPs (2-6 depending on size)
            vp_count = min(6, max(2, num_employees // 15))
            vp_employees = []
            
            for _ in range(vp_count):
                vp = create_employee(random.choice(job_titles['vp']), 'admin')
                # Assign to C-level or CEO
                if c_level_employees:
                    manager = random.choice(c_level_employees)
                else:
                    manager = {'membership': ceo}
                vp.reports_to = manager['membership']
                vp.save()
                vp_employees.append({'membership': vp, 'level': 2, 'can_manage': True})
                employees.append(vp_employees[-1])
            
            # Create Directors (3-10 depending on size)
            director_count = min(10, max(3, num_employees // 10))
            director_employees = []
            
            for _ in range(director_count):
                director = create_employee(random.choice(job_titles['director']), 'admin')
                # Assign to VP or C-level
                if vp_employees:
                    manager = random.choice(vp_employees)
                elif c_level_employees:
                    manager = random.choice(c_level_employees)
                else:
                    manager = {'membership': ceo}
                director.reports_to = manager['membership']
                director.save()
                director_employees.append({'membership': director, 'level': 3, 'can_manage': True})
                employees.append(director_employees[-1])
            
            # Create Managers (5-15 depending on size)
            manager_count = min(15, max(5, num_employees // 8))
            manager_employees = []
            
            for _ in range(manager_count):
                manager = create_employee(random.choice(job_titles['manager']), 'member')
                # Assign to Director, VP, or C-level
                if director_employees:
                    boss = random.choice(director_employees)
                elif vp_employees:
                    boss = random.choice(vp_employees)
                elif c_level_employees:
                    boss = random.choice(c_level_employees)
                else:
                    boss = {'membership': ceo}
                manager.reports_to = boss['membership']
                manager.save()
                manager_employees.append({'membership': manager, 'level': 4, 'can_manage': True})
                employees.append(manager_employees[-1])
            
            # Create remaining employees (Senior, Mid, Junior)
            remaining_count = num_employees - len(employees)
            
            # Distribute remaining employees
            senior_count = max(0, remaining_count // 3)
            mid_count = max(0, remaining_count // 2)
            junior_count = remaining_count - senior_count - mid_count
            
            all_managers = [emp for emp in employees if emp['can_manage']]
            
            # Create Senior employees
            for _ in range(senior_count):
                senior = create_employee(random.choice(job_titles['senior']), 'member')
                # Assign to any manager, ensuring max 7 reports
                available_managers = [m for m in all_managers if m['membership'].direct_reports.count() < 7]
                if available_managers:
                    manager = random.choice(available_managers)
                    senior.reports_to = manager['membership']
                    senior.save()
                employees.append({'membership': senior, 'level': 5, 'can_manage': False})
            
            # Create Mid-level employees
            for _ in range(mid_count):
                mid = create_employee(random.choice(job_titles['mid']), 'member')
                # Assign to any manager, ensuring max 7 reports
                available_managers = [m for m in all_managers if m['membership'].direct_reports.count() < 7]
                if available_managers:
                    manager = random.choice(available_managers)
                    mid.reports_to = manager['membership']
                    mid.save()
                employees.append({'membership': mid, 'level': 6, 'can_manage': False})
            
            # Create Junior employees
            for _ in range(junior_count):
                junior = create_employee(random.choice(job_titles['junior']), 'member')
                # Assign to any manager, ensuring max 7 reports
                available_managers = [m for m in all_managers if m['membership'].direct_reports.count() < 7]
                if available_managers:
                    manager = random.choice(available_managers)
                    junior.reports_to = manager['membership']
                    junior.save()
                employees.append({'membership': junior, 'level': 7, 'can_manage': False})
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created org-chart for '{org_name}' with {len(employees)} employees!"
            )
        )
        
        # Print summary
        level_counts = {}
        for emp in employees:
            level = emp['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        level_names = {
            0: 'CEO', 1: 'C-Level', 2: 'VP', 3: 'Director', 
            4: 'Manager', 5: 'Senior', 6: 'Mid-Level', 7: 'Junior'
        }
        
        self.stdout.write("\nOrg Chart Summary:")
        for level, count in sorted(level_counts.items()):
            self.stdout.write(f"  {level_names.get(level, f'Level {level}')}: {count}")
        
        # Check manager span of control
        self.stdout.write("\nManager Span of Control:")
        for emp in employees:
            if emp['can_manage']:
                direct_reports = emp['membership'].direct_reports.count()
                if direct_reports > 0:
                    self.stdout.write(f"  {emp['membership'].user.get_full_name()}: {direct_reports} reports")