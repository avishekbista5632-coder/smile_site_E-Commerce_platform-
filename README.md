# Smile Cleaning Products — E-Commerce Web Application

A full-stack e-commerce platform built using **Django** for the backend and **HTML, CSS, JavaScript** for the frontend. The platform allows users to browse products, sign up, login, add items to a cart, checkout, and receive email notifications for account verification and order confirmation.

## Features

- **User Authentication**
  - Signup with email verification
  - Login and logout
  - Forgot and reset password via email
- **Product Management**
  - View product listings
  - Detailed product pages
- **Cart & Checkout**
  - Add products to a cart
  - Select quantity and payment method
  - Place orders with order summary
- **Email Notifications**
  - Email verification upon signup
  - Order confirmation for users and admin
- **Responsive Design**
  - Fully responsive layouts for desktop and mobile

## Tech Stack

- Backend: **Django**, **Python**
- Frontend: **HTML5**, **CSS3**, **JavaScript**
- Database: **SQLite** (default) or any Django-supported database
- Email: Django’s **EmailMessage / EmailMultiAlternatives**
- Optional: **Bootstrap / Tailwind CSS** for styling

## Project Structure
 
## Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/smile-cleaning-products.git
cd smile-cleaning-products
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Open your browser at http://127.0.0.1:8000/

Usage

Signup: /signin/ — New users register with email verification.

Login: /login/ — Existing users can log in.

Browse Products: /products/ — View product listings.

Checkout: /checkout/ — Place orders (login required).

Thank You Page: /thankyou/?order_id=<id> — Confirmation after successful order.