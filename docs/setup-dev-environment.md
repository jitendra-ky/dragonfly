# Setting Up Development Environment

Follow these steps to set up the development environment for the Dragonfly project.

## Prerequisites

Ensure you have the following installed on your system:

- Python 3.10 or higher
- Node.js (version 18.x)
- npm (Node Package Manager)
- Docker (optional, for running tests in a containerized environment)

## Clone the Repository

Clone the Dragonfly repository from GitHub: (your forked one)

```bash
git clone https://github.com/your-username/dragonfly.git
cd dragonfly
```

## Set Up Python Environment

Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

Install the required Python packages:

```bash
pip install -r requirements/development.txt
```

## Set Up Node.js Environment

Install the required Node.js packages:

```bash
npm install
```

## Set Up Environment Variables

Create a `.env` file in the project root and add the necessary environment variables:

```bash
cp .env.example .env
# Edit the .env file to include your environment-specific variables
```

## Apply Database Migrations

Run the following command to apply database migrations:

```bash
python manage.py migrate
```

## Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The application should now be running at `http://localhost:8000`.
