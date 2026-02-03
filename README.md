# ✨Spare Change✨

This is our semester long project where we will be developing an app for the Missoula community, particularly those near the UM campus. Our app is going to target anyone looking for a small temporary job or quick way to earn some money. In terms of the job section, the goal is to have users post their job opportunity, set the expiration date and expectations, and let users quickly find a job that matches what they are looking for. 

# Members and Jobs:

*Evans:* Backend, Dev Ops

*Sam:* Developer, Testing

*Madison:* Frontend, Lead

*Jose Luis:* Backend, Dev Ops

# Problem Statement: 
  * There is no centralized place to look for quick jobs or weekend gigs that are updated daily, sorted, and for the UM community. 

# Target Users:
  * College Students
  * High School Students
  * UM Staff/Faculty
  * UM Community

# Top Features:

 * dual factor authentication for members
 * encrypted and secured payments
 * built in messaging component
 * filters for sorting jobs
 * saving posts or members
 * ratings for posters
 * user profile (bio, location, contact info, job preferences)
 * posts automaticaly delete if they go past the expiration date 

# Use Cases

## Use Case 1: Creating an account ##

Actors:
* UM students and staff
* surrounding comminity members

Description:
1. A user goes to the site and clicks sign up
2. They choose an email, username, and password from scratch or use Google to sign up
3. They agree to the terms of the site
4. A verification email is sent to the email they input
5. Once verified they sign in and go to a profile creation page
6. Users can optionaly input a bio, general location, contact info, profile picture, and job preferences
7. They hit continue and continue to the main/home page of the app
8. Once done browsing they go to their profile and sign out

Expected Outcome:
* The user has successfully signed up, created a profile, and can now add jobs, look for jobs, and sign out

## Use Case 2: Creating a weekend job ##

Actors:
* UM students
* Missoula community

Description:
1. A user logs in and is taken to the homepage
2. They navigate to their profile and go to the jobs page
3. The user clicks New Job
4. They fill in the description, general location, pay, date for job, and other details
5. The user clicks submit and the job is posted
6. They can go back to their jobs page and see the updaed list of their jobs

Expected Outcome:
* A user can successfuly create a new job, add all sufficient information, and verify that the job was posted

## Use Case 3: Searching for a job walking dogs the upcoming weekend ##

Actors:
* UM students
* UM community
* Missoula community

Description:
1. A user logs in and is taken to the home page
2. They go to flters and change the job type to dog walking
3. They then sort by earliest date
4. The user clicks on a job posting and hits save, then goes back to the main page
5. They continue looking and save a few more
6. The user then clears those filters
7. The user now filters by saved jobs
8. They choose the first job and click to see more details
9. They contact the employer and get an address through the message board
10. They click confirm and the employer gets an email asking them to deny or accept
11. The employer accepts and the user gets a confirmation email
12. The job is taken down once confirmed
13. The user logs out 

Expected Outcome:
* A user can log in, search for the desired job with filters, contact the poster through the app, and confirm the job is theirs securely. 

# User Stories #

"As a [type of user], I want to [do something] so that [benefit]."

## User Story 1 ##
As a UM student I want to browse what dog walking jobs are available this upcoming weekend so I can make some money. 

## User Story 2 ##
As a member, I want to post a quick work job with a specific expiration date so that I can find help before the date ends without having to manually delete the post later.

## User Styory 3 ##
As a UM student with specific skills, I want to filter job listings using tags like "Manual Labours," "Tech Support," or "Pet Care," so that I don't have to scroll through irrelevant posts to find the quick gigs that match my expertise and interests.

# Tests #
Test Driven Development

Usernames
Test edge cases for valid usernames

Email
Test for valid emails, # of characters etc.

Bot captcha(maybe)
Testing to ensure the users are human

Date
Ensure the date is valid (use calendar UI)

job description
Minimum/max amount of characters for description

Contact information 
via phone verification
Email
Social media

Price
tests for negative $ and jobs over $300

Location
Valid within city limits
Valid zip-code/location address

Tags


