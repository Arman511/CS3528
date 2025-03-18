# CS3528_alpha

## Contents

- [Project Overview](#project-overview)
- [Website](#website)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [How to Run](#how-to-run)
- [Administration Login Details - Example](#administration-login-details---example)
- [Superuser Login](#superuser-login)
- [Employer Login](#employer-login)
- [Student Login](#student-login)
- [Deadlines](#deadlines)
- [Coverage](#coverage)
- [Export/Import MongoDB](#mongodb-backup-and-restore)

## Project Overview

This project is part of the CS3028 course. Using model route framework on top of flask. We have decided to allow the placement team to upload students and opportunities. The students will rank opportunities and employers would rank students. We will then use the Gale-Shapley algorithm to compare the rankings each give. We will then using email integration send a confirmation out to the employer.

-   **Flask**: A lightweight WSGI web application framework in Python.
-   **Pymongo**: An MongoDB toolkit and Object-Relational Mapping (ORM) library for Python.
-   **Gale-Shapley Algorithm**: Also known as the stable marriage algorithm, used for matching students to opportunities.
-   **Email Integration**: To send confirmation emails to employers and students.

## Website

[Deployment Official](https://www.abdn.skillpilot.co.uk/)

[Coverage Report](https://arman511.github.io/CS3528/)

## Setup Instructions

1. Clone the repository to your local machine.
2. Create a virtual environment:
    ```
    python3 -m venv venv
    ```
3. Activate the virtual environment:
    - On macOS/Linux:
        ```
        source venv/bin/activate
        ```
    - On Windows(powershell):
        ```
        .\venv\Scripts\activate.ps1
        ```
4. Install packages
    ```
    pip3 install -r ./requirements.txt -U
    ```

## Environment Variables

To run the application, you need to create a `.env` file in the root directory of the project with the following parameters:

```
MONGO_URI= The link to the used MongoDB instance for the application
SECRET_KEY= The secret key for Flask to use to handle encryption
GUNICORN_PROCESSES=2
GUNICORN_THREADS=4
GUNICORN_BIND="0.0.0.0:8080"
IS_GITHUB_ACTION="False"
EMAIL_PASSWORD= The password for the email service used
EMAIL= The email for the email service used
SMTP= The SMTP server used for the email service
MONGO_DB_TEST="_test" The name of the test collection
MONGO_DB_PROD="_prod" The name of the prod collection
BASE_EMAIL_FOR_STUDENTS= The base email for adding students e.g. abdn.ac.uk
SUPERUSER_EMAIL= The superuser admin login email, this accounts handles the user accounts for the placement team
SUPERUSER_PASSWORD= The password for the superuser account
OFFLINE="False" - Set to true if you are using local MongoDB deployment
PORT="8080" If changed change also in the Dockerfile
GUNICORN_LOG_LEVEL="info"
GUNICORN_ACCESS_LOG="-"
GUNICORN_ERROR_LOG="-"
```

⚠️ Make sure to replace placeholder values with your actual configuration settings.

## How to Run

-   To run the project, execute the following command (make sure the `.env` is set):

    -   On macOS/Linux:
        ```
        ./run
        ```
    -   On Windows(powershell):
        ```
        .\run.ps1
        ```
If all else fails, try running the application directly with:

    - On macOS/Linux:
        ```
        python3 app.py
        ```
    - On Windows(powershell):
        ```
        python app.py
        ```

-   To run the production version, use the following command:
    ```
    gunicorn --config gunicorn_config.py app:app
    ```
    or
    ```
    ./gunicorn_run
    ```

-   To build and run the project using Docker:

    1. Build the Docker image:
        ```
        docker build --network=host -t cs3528_alpha . 
        ```

    2. Run the Docker container, exposing port 8080:
        ```
        docker run --env-file .env -p 8080:8080 cs3528_alpha
        ```

## Administration Login Details - Example

-   Email : admin@example.com
-   Password: admin

## Superuser Login

The login for the superuser is set in the `.env` file.

## Employer Login

To sign in as an employer, the employers email address should be in the database which can only be added by the placement team. once completed, the employer fill in their email address and receive an OTP (check spam folder).

## Student Login

To sign in as an student, the employers email address should be in the database which can only be added by the placement team. once completed, the student fill in their university number and receive an OTP (check spam folder).


## Deadlines

The admin team manages three key deadlines that restrict data input and user views throughout their duration:

### Stage 1
1. The placement team adds employers to the system.
2. Students fill in their profile information using the provided MS form.

### Stage 2
1. Students log in and add their university information (course, modules, skills, and any comments).
2. Employers upload the placements offered using the template file or add them manually.

### Stage 3 - After the Details Deadline
1. Students log in to see a list of eligible placements based on their degree and course modules.
2. Students rank their placement preferences.

### Stage 4 - After the Student Ranking Deadline
1. Employers rank students for each placement.

### Stage 5 - After Opportunities Ranking Deadline
1. The placement team reviews the list of students matched to placements based on preferences.
2. The team sends matchmaking results to companies and students via email.

## Coverage

To run the tests and generate a coverage report in the terminal:

```
coverage run -m pytest && coverage report
```

To run the tests and generate an HTML coverage report:

```
coverage run -m pytest && coverage html
```

## MongoDB Backup and Restore

### For Local

#### Local Dump
To create a backup of a local MongoDB database:
```
mongodump -d cs3528_prod -o ./mongo-backup
mongodump -d cs3528_test -o ./mongo-backup
```

#### Local Restore
To restore a local MongoDB database from a backup:
```
mongorestore -d cs3528_prod ./mongo-backup/cs3528_prod
mongorestore -d cs3528_test ./mongo-backup/cs3528_test
```

### For Remote
REPLACE URI WITH YOUR OWN
#### Remote Dump
To create a backup of a remote MongoDB database:
```
mongodump --uri "mongodb+srv://Admin:MYPASS@appcluster.15lf4.mongodb.net/cs3528_prod" -o ./mongo-backup
mongodump --uri "mongodb+srv://Admin:MYPASS@appcluster.15lf4.mongodb.net/cs3528_test" -o ./mongo-backup
```

#### Remote Restore
To restore a remote MongoDB database from a backup:
```
mongorestore --uri "mongodb+srv://Admin:MYPASS@appcluster.15lf4.mongodb.net/cs3528_prod" ./mongo-backup/cs3528_prod
mongorestore --uri "mongodb+srv://Admin:MYPASS@appcluster.15lf4.mongodb.net/cs3528_test" ./mongo-backup/cs3528_test
```
