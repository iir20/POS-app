# POS (Point of Sale) System

A complete web-based Point of Sale system built with Flask, SQLite, HTML, CSS, and JavaScript.

## Overview

This is a full-featured POS application designed for small retail businesses. It includes inventory management, sales tracking, customer due management (বাকির খাতা), expense tracking, and business analytics dashboard.

## Project Architecture

### Backend (Python Flask)
- **app.py**: Main Flask application with all API endpoints
- **database.py**: SQLite database initialization and connection management
- **pos_system.db**: SQLite database (auto-created on first run)

### Frontend
- **templates/**: HTML pages for all views
  - `index.html`: Main POS interface
  - `inventory.html`: Inventory management view
  - `due_list.html`: Customer due tracking (বাকির খাতা)
  - `expenses.html`: Expense ledger (খরচের খাতা)
  - `dashboard.html`: Business overview dashboard
- **static/css/style.css**: Complete styling with responsive design

## Features Implemented

### 1. POS Interface
- Product grid with touch-friendly buttons
- Real-time shopping cart
- Product name and price display with Bengali Taka symbol (৳)
- Dual checkout system:
  - Cash Sale
  - Add to Due (বাকি)
- Stock validation before adding to cart

### 2. Database Structure
**Products Table:**
- id, name, purchase_price, sale_price, stock_quantity

**Sales Table:**
- id, items_sold (JSON), total_amount, timestamp, customer_id, status

**Customers Table:**
- id, name, phone, total_due

**Expenses Table:**
- id, category, amount, description, timestamp

### 3. API Endpoints
- `GET /api/products`: Fetch all products
- `POST /api/add_product`: Add new product to inventory
- `PUT /api/update_product/<id>`: Update existing product details
- `POST /api/add_sale`: Record sale (with transaction integrity)
- `GET /api/customers`: Fetch all customers
- `POST /api/add_customer`: Add new customer
- `POST /api/add_expense`: Record expense
- `GET /api/expenses`: Fetch all expenses
- `GET /api/dashboard_data`: Get dashboard analytics

### 4. Security & Validation
All mutation endpoints include:
- Input validation (required fields, data types, ranges)
- Transaction integrity (atomic operations with rollback)
- Error handling with meaningful messages
- Stock quantity validation
- Customer existence verification for due sales

### 5. Automatic Stock Management
- Real-time inventory updates on every sale
- Low stock alerts when quantity < 5
- Console warnings for low stock items
- Color-coded inventory status (In Stock, Low Stock, Out of Stock)

### 6. Due Tracking System (বাকির খাতা)
- Customer management with name and phone
- Automatic due balance updates on credit sales
- Customer list with outstanding balances
- Add new customers functionality

### 7. Expense Management (খরচের খাতা)
- Category-based expense tracking
- Amount and description fields
- Timestamped expense history
- Table view of all expenses

### 8. Business Dashboard (ব্যবসার ওভারভিউ)
- Total Sales Today (color-coded green)
- Total Expenses Today (color-coded red)
- Net Profit Today (color-coded purple)
- Total Due Amount (color-coded orange)
- Low Stock Alerts with Bengali text (এলার্ট মেসেজ)
- Auto-refresh every 30 seconds

### 9. Inventory Management
- Complete product listing with purchase/sale prices
- Stock quantity display with color coding
- Status indicators (✅ IN STOCK, ⚠️ LOW STOCK, OUT OF STOCK)
- **Add New Product**: Button to add products with name, prices, and stock quantity
- **Edit Product**: Edit existing product details (name, prices, stock)
- Form validation for all product fields (non-negative prices, valid quantities)
- XSS protection using secure DOM manipulation
- Auto-refresh every 10 seconds

## Recent Changes

**2025-11-03 (Product Management Update)**: Added inventory editing capabilities
- Implemented API endpoints for adding and updating products
- Added "Add New Product" button with modal form on inventory page
- Added "Edit" buttons for each product with inline editing modal
- Implemented comprehensive input validation (non-negative prices, valid quantities)
- Fixed XSS vulnerability using secure DOM manipulation (textContent, createElement)
- Verified all product management features with architect review

**2025-11-03 (Initial Release)**: Complete POS system implementation
- Built Flask backend with SQLite database
- Implemented all 5 pages with responsive design
- Added comprehensive input validation and error handling
- Fixed critical transaction integrity issues
- Added security measures to prevent inventory tampering
- Pre-loaded database with 20 sample products and 5 sample customers

## Technical Details

### Technologies Used
- **Backend**: Python 3.11, Flask 3.1.2, Flask-CORS 6.0.1
- **Database**: SQLite3
- **Frontend**: Vanilla JavaScript (Fetch API), HTML5, CSS3
- **Design**: Responsive grid layout, gradient color scheme

### Key Design Decisions
1. **Single Transaction for Sales**: All sale operations (record sale, update due, decrement stock) happen in one atomic transaction to prevent data inconsistency
2. **Server-side Validation**: All inputs validated on server to prevent client-side manipulation
3. **Bengali Language Support**: Mixed Bengali and English for user-friendly interface
4. **Touch-friendly UI**: Large buttons and responsive grid for mobile/tablet use
5. **Auto-initialization**: Database automatically creates tables and sample data on first run

## User Preferences

None specified yet.

## Running the Application

The application runs automatically via the configured workflow on port 5000. Access it through the webview preview.

**Environment Variables:**
- `SESSION_SECRET`: Flask session secret (auto-configured)

## Sample Data

The system comes pre-loaded with:
- **20 Products**: Common retail items (Rice, Lentils, Oil, Sugar, etc.)
- **5 Customers**: Sample customers with phone numbers
- All products have initial stock quantities

## Future Enhancements

Potential features for next phase:
- Payment tracking for due customers with partial payments
- Sales history with date filtering
- Product management page (add/edit/delete products)
- Receipt printing and invoice generation
- Sales reports with analytics charts
- User authentication and multi-user support
- Backup and restore functionality
