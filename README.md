# Budget Manager

Budget Manager is a Django-based web application that helps users manage their expenses. Users can add, view, and delete expenses, and see a summary of their monthly expenses. The application also includes a chart that visualizes the expenses for the selected year.

## Features

- User authentication and registration
- Add, view, and delete expenses
- Monthly expense summary
- Yearly expense chart
- Responsive design

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/cPaletta/budget_manager.git
   cd budget_manager
   ```

2. Apply the migrations:
   ```sh
   python manage.py migrate
   ```

3. Create a superuser:
   ```sh
   python manage.py createsuperuser
   ```

4. Run the development server:
   ```sh
   python manage.py runserver
   ```

5. Open your browser and go to `http://127.0.0.1:8000/` to access the application.

## Running Tests

To run the tests, use the following command:
```sh
python manage.py test
```
