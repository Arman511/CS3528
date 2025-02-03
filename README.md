# CS3028_alpha

## Contents

1. [Project Overview](#project-overview)
2. [Setup Instructions](#setup-instructions)
3. [How to Run](#how-to-run)

## Project Overview

This project is part of the CS3028 course. Using model route framework ontop of flask. We have decied to allow the placement team to upload students and opportunities. The students will rank opportuniites and employers would rank students. We will then use the Gale-Shapley algorithm to compare the rankings each give. We will then using email integration send a confirmation out to the employer.

-   **Flask**: A lightweight WSGI web application framework in Python.
-   **Pymongo**: An MongoDB toolkit and Object-Relational Mapping (ORM) library for Python.
-   **Gale-Shapley Algorithm**: Also known as the stable marriage algorithm, used for matching students to opportunities.
-   **Email Integration**: To send confirmation emails to employers and students.

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

## How to Run

-   To run the project, execute the following command:

    -   On macOS/Linux:
        ```
        ./run
        ```
    -   On Windows(powershell):
        ```
        .\run.ps1
        ```

-   To run the production version, use the following command:
    ```
    gunicorn --config gunicorn_config.py app:app
    ```

https://dev.to/andrewbaisden/how-to-deploy-a-python-flask-app-to-vercel-2o5k


## Admininstration Login Details

- Email : admin@example.com
- Password: admin

## Student Login Details

- Student 1: 
    Username : 12345678
    Password : 54d37f9c96a711ef93523388226f7343

- Student 2: 
    Username : 52207669
    Password : 649fe83e96a711ef93523388226f7343

- Student 3: 
    Username : 45327347
    Password : 6b31741a96a711ef93523388226f7343

## Employer Login

- To sign in as an employer, the employers email address should be in the database which can only be added by the admin team. once completed, the employer fill in their email address and receive an OTP (check spam folder).

## Deadlines

- There are 3 deadlines which are managed by the admin team which throughout their duration restrict the data that can be inputted and user views available
    1. The students fill in their profile information
    2. Employers upload the placements offered
    3. The students and employers rank one another
## Coverage

```
coverage run -m pytest && coverage report
```

## Website

https://cs-3528-alpha.vercel.app/
