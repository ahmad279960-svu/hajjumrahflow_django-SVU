# HajjUmrahFlow - Integrated Management System

## Overview

[cite_start]HajjUmrahFlow is a comprehensive, web-based system designed to automate and streamline the management of Hajj and Umrah trips for travel agencies[cite: 2]. [cite_start]This project aims to replace manual, fragmented tools with a centralized, efficient, and reliable software solution, ultimately allowing agencies to focus on providing exceptional service to pilgrims[cite: 3, 12].

Built with a robust, scalable architecture, the system provides role-based access for managers, agents, and accountants, each with a tailored dashboard and functionalities covering the entire operational lifecycle from customer relationship management (CRM) to financial reporting.

## Tech Stack

| Component | Technology | Version | Rationale |
| :--- | :--- | :--- | :--- |
| Language | **Python** | 3.11+ | [cite_start]Modern, readable, and boasts a massive ecosystem for web development[cite: 192]. |
| Backend Framework | **Django** | 5.0+ | [cite_start]A high-level framework that enables rapid development of secure and maintainable web applications[cite: 194]. |
| API Framework | **Django REST Framework** | 3.14+ | [cite_start]The gold standard for building powerful and flexible RESTful APIs in Django[cite: 196]. |
| Database | **PostgreSQL** | 16+ | [cite_start]An object-relational database system known for its reliability, feature robustness, and performance[cite: 198]. |
| Frontend | **Bootstrap 5 & HTMX** | 5.3+ | [cite_start]A combination for creating responsive, professional UIs with dynamic interactions without the complexity of a full JS framework[cite: 200, 201]. |
| Automation | **n8n.io** | Latest | [cite_start]An open-source workflow automation tool used to connect HajjUmrahFlow with external services like email and WhatsApp[cite: 204]. |

## Project Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd hajjumrahflow_django
    ```

2.  **Environment Variables:**
    -   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    -   Populate the `.env` file with your specific credentials for the database, Django `SECRET_KEY`, etc. This file is intentionally not tracked by Git.

3.  **Setup Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Database Setup:**
    -   Ensure you have PostgreSQL installed and running.
    -   Create a database and user according to your `.env` settings.

6.  **Run Migrations:**
    ```bash
    python manage.py migrate
    ```

7.  **Create a Superuser:**
    ```bash
    python manage.py createsuperuser
    ```

8.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000`.

## Key Features

-   **Role-Based Dashboards:** Customized views for Managers, Agents, and Accountants.
-   **Full Customer Lifecycle Management (CRM).**
-   **Trip & Package Administration.**
-   **Booking & Payment Tracking.**
-   **Automated Reporting (Passenger Manifests, Financial Summaries).**
-   **Webhook Integration with n8n for Process Automation.**