# Backend Intern Assignment - Codemonk

A REST API built with Django REST Framework. This project fulfills all the requirements of the Codemonk Backend Intern assignment, featuring custom user authentication, asynchronous text processing, and a highly efficient word-frequency search algorithm.

---

## Features Implemented

### 1. User Module
*   **Custom User Model**: Uses Email as the unique identifier (no username required), alongside ID (UUID), Name, Date of Birth, Created Date, and Modified Date.
*   **Registration**: Users can securely register an account with automatic password hashing.
*   **Authentication**: Uses modern JWT (JSON Web Tokens) for secure, stateless login and token refreshing.

### 2. Paragraph Module
*   **Paragraph Ingestion**: Users can submit multiple paragraphs of text at once. The system automatically splits the text by double newlines (`\n\n`) and saves them.
*   **Asynchronous Tokenisation**: To ensure the API remains lightning fast, paragraph word counting is offloaded to a background task queue (Celery). Words are converted to lowercase and split by whitespace.
*   **Word Frequency Tracking**: The system calculates and stores exactly how many times each word is used across all paragraphs for a user.

### 3. Word Search API
*   **Optimized Searching**: Users can query a word (e.g., `?word=fox`) and instantly receive the top 10 paragraphs where that word appears the most.
*   **N+1 Query Prevention**: The search logic uses advanced database techniques (Correlated Subqueries) to rank paragraphs in a single, efficient database call.

---

## Tech Stack

This project was built using industry-standard tools for scalable web applications:

1.  **Web Framework:** Django 4.2 + Django REST Framework (DRF)
2.  **Containerisation:** Docker + Docker Compose (for easy "Clone & Run" setup)
3.  **Relational Database:** PostgreSQL 15
4.  **Task Queue & Workers:** Celery
5.  **Message Broker / Cache:** Redis 7
6.  **Task Scheduler:** Celery Beat (for database cleanup tasks)
7.  **Authentication:** `djangorestframework-simplejwt`
8.  **API Documentation:** `drf-spectacular` (Swagger UI)
9.  **Production Server:** Gunicorn

---

## Project Setup Instructions

This project has been completely containerised using Docker. You do **not** need to install Python, Django, PostgreSQL, or Redis on your computer. Docker will handle everything for you!

### Prerequisites
Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running on your computer.

### Step 1: Clone the repository
Open your terminal or command prompt and run:
```bash
git clone https://github.com/ansoncodes/codemonk-backend-assignment.git
cd codemonk-backend-assignment
```

### Step 2: Start the application
The project comes with a pre-configured `.env` file so you don't have to worry about setting up database passwords. Just run:
```bash
docker-compose up --build
```
*Note: This will download PostgreSQL, Redis, and Python, and then start the API, the database, and the background workers. It might take a minute or two the very first time.*

### Step 3: Run Database Migrations
Once the server is running (you'll see logs scrolling in your terminal), open a **new** terminal window, navigate to the same project folder, and run:
```bash
docker-compose exec web python manage.py migrate
```
*This creates the necessary tables in the PostgreSQL database.*

### Step 4: Create an Admin User (Optional)
If you want to access the Django Admin panel, create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

---

## API Documentation

The easiest way to test this API is using the built-in interactive documentation (Swagger UI). 

While the server is running (from Step 2), open your web browser and go to:
**[http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)**

### How to test the app using Swagger:

1.  **Register:** Scroll down to `POST /api/users/register/`, click "Try it out", fill in the JSON with your email and a password, and click Execute.
2.  **Login:** Go to `POST /api/users/login/`, enter the same email and password, and click Execute. Copy the long `access` token string from the response.
3.  **Authorize:** Scroll to the very top of the page, click the green **Authorize** button. Type the word `Bearer` followed by a space, and paste your access token (e.g., `Bearer eyJhbGci...`). Click Authorize.
4.  **Submit Paragraphs:** Go to `POST /api/paragraphs/`, click "Try it out", and paste some text with multiple paragraphs (separated by double Enters). Click Execute.
5.  **Search:** Go to `GET /api/paragraphs/search/`, click "Try it out", type a word that exists in your paragraphs into the `word` box, and click Execute. You will see your paragraphs ranked!

---
