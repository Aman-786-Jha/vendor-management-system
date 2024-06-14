Vendor Management System


Objective:
The aim of this project is to build a Vendor Management System using Django and Django REST Framework. The system will manage vendor profiles, monitor purchase orders, and evaluate vendor performance metrics.

Key Features:
User Authentication: Users can sign up as either buyers or vendors and securely log in to the system.
Vendor Management: Vendors can set up and maintain their profiles, including contact information and address details.
Purchase Order Tracking: Buyers can generate purchase orders, which vendors can then acknowledge, process, and fulfill.
Performance Metrics Evaluation: The system computes various performance metrics for vendors, such as on-time delivery rate, quality rating average, average response time, and fulfillment rate.
Historical Performance Monitoring: Performance metrics are recorded over time to observe trends in vendor performance.


Project Details
User Model:
A custom user model has been developed to accommodate both buyers and vendors, distinguishing between the two user types.

API Endpoints:
Multiple endpoints have been implemented to manage user authentication(Vendor and Buyer), vendor profiles, purchase order tracking, and performance metrics computation.

Swagger Documentation:
Swagger has been utilized to create interactive API documentation, aiding developers in comprehending and testing the various endpoints.

Filters and Pagination:
Filters and pagination have been implemented for list pages to enhance usability and performance, allowing users to filter data based on specific criteria and efficiently navigate through large datasets.

This project is designed to streamline vendor management processes, enhance transparency and accountability, and support data-driven decision-making by providing valuable insights into vendor performance.


Setting up the project :- 

1. Simply git clone the repo by writing command:- git clone in any folder or dir

2. Make virtual environment in the directory by writing command in terminal:- python -m venv myenv(If you are on windows)

3. Activate the virtual environment by writing command:- myenv\Scripts\activate

4. Install the all necessary libraries used in the project to run the project by writing command:- pip install -r requirements.txt (make sure in which directory requirements.txt is run there only), requirements.txt will be in the manage.py directory. 

5. After installing libraries in the virtual environment, run the following commands to migrate the table schemas into the database:- python manage.py makemigrations and python manage.py migrate, Run these 2 commands one by one and make sure to run this command in the directory where the manage.py file is.

6. After installing libraries in the virtual environment, simply in the root directory(where the manage.py file is there) run the project by simply running the command:-

python manage.py runserver

7. Now to test and explore all the apis, go to the url http://127.0.0.1:8000/swagger/ running on your system, This will give you the swagger document interface where all the endpoints will be listed out. 

8. All the endpoints are there to test that simply click on arrow button in the right corner then click on try it out then where the Bearer is required provide the access token.

9. Acess token will get after the login.

10. In the Authorization field, Input like that Bearer will be already written, write the access token giving one space after Bearer.

11. Now after successfully setting up and running the project start using vendor platform by creating vendor, buyers and purchase orders and see the vendors history performance.

12. APIs Testing

To run and check all the apis first create buyer or vendor first by the endpoints:- 

/buyers-create/ and /vendors-create/

after creating corresponding type user,login with that user credential on the endpoint /login/
13. After succesful login access token will generate, use that access token for other endpoints implementaion wherever authentication is required.

14. To enter the token wherever authentication required use the generated token in the Authorization field writing "Bearer <token>" then execute with giving all required parameters in the request_body of the endpoint.

15. All Endpoints List :- 
Buyers Endpoints:

CRUD POST:- /buyers-create/
CRUD POST:- /login/
CRUD GET:- /buyers/{buyer_code}
CRUD GET:- /buyers/
CRUD DELETE:- /buyers/{buyer_code}
CRUD PUT:- /buyers/{buyer_code}/update/


Vendor Endpoints:
CRUD POST:- /vendors-create/
CRUD GET:- /vendors/
CRUD GET:- /vendors/{vendor_code}
CRUD DELETE:- /vendors/{vendor_code}/delete/
CRUD PUT:- /vendors/{vendor_code}/update/

Purchase order: 
CRUD POST:- /purchase-orders-create/
CRUD GET:- /purchase-orders/
CRUD GET:- /purchase-orders/{po_number}/
CRUD DELETE:- /purchase-orders/{po_number}/delete
CRUD PUT:- /purchase-orders/{po_number}/update


Performance endpoints:
CRUD GET:- /api/vendors/{vendor_id}/performance/

Purchase order status endpoints:
CRUD POST:- /purchase_orders_status/{po_id}/acknowledge
CRUD POST:- /purchase_orders_status/{po_id}/cancel
CRUD POST:- /purchase_orders_status/{po_id}/complete
CRUD POST:- /purchase_orders_status/{po_id}/issue


16. Real-time Updates:
Django signals are employed in signals.py to update metrics instantly whenever related purchase order data is modified.

17. Request and Response Formats:
Request Format: Requests utilize HTTP methods (GET, POST, PUT, DELETE) directed at specific endpoints. Depending on the endpoint, requests may include parameters in the URL, query parameters, request body, or headers.
Response Format: Responses are in JSON format, comprising a response_message field that describes the outcome and a response_data field with pertinent data. The response status code indicates whether the request was successful or not.
Authentication:
JWT Token: JSON Web Tokens (JWT) are used for authentication. Users must include a valid JWT token in the Authorization header to access API endpoints. Most endpoints are inaccessible without proper authentication.
Filters and Pagination:
Filters: Some list endpoints allow filtering based on specific criteria, such as vendor name. Users can add filter parameters to the query string to refine the results.
Pagination: List endpoints are paginated to enhance performance and manage large datasets. Users can specify the page number and page size in the query string to navigate through the results.
Error Handling:
Error handling is managed extensively using try and except blocks throughout the project.

This project aims to streamline vendor management processes, boost transparency and accountability, and support data-driven decision-making by offering valuable insights into vendor performance.

18. It was having fun making these apis, Thank You



























