# Generate Survey Data Script

This script creates random users and survey responses for testing purposes.

## Usage

```bash
# Basic usage - generates data for organization ID 1
python manage.py generate_survey_data 1

# Custom parameters
python manage.py generate_survey_data 1 --users 20 --weeks 16 --responses-per-week 4

# Help
python manage.py generate_survey_data --help
```

## Parameters

- `organization_id` (required): ID of the organization to generate data for
- `--users`: Number of users to create (default: 15)
- `--weeks`: Number of weeks to spread responses over (default: 12 = 3 months)
- `--responses-per-week`: Average responses per week (default: 3)

## What it does

1. **Creates realistic users** with names like alice.anderson1@company.com
2. **Adds users to organization** as members
3. **Generates survey responses** spread over time:
   - Responses distributed randomly across weeks
   - Weekdays more likely than weekends
   - Business hours more likely
   - Realistic rating distribution (70% positive, 20% neutral, 10% negative)
4. **Respects organization settings** - uses `questions_per_cycle` for response length

## Example Output

```
Generating data for organization: Acme Corp
Survey: Employee Engagement Survey
Available questions: 25
Questions per cycle: 5
Created 5 users...
Created 10 users...
Created 15 users total
Creating approximately 36 responses over 12 weeks (2024-01-04 to 2024-04-04)
Created 10 responses...
Created 20 responses...
Created 36 total responses
Successfully generated 15 users and survey responses for "Acme Corp"
```

## Prerequisites

- Organization must exist
- Organization must have a survey
- Survey must have questions

## Note

This script is for testing/demo purposes only. All generated users have password: `testpassword123`