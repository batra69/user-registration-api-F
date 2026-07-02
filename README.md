User Registration + Listing (Flask + MySQL)

Folder structure

registration-project/
├── app.py
├── requirements.txt
├── schema.sql
├── templates/
│   ├── register.html
│   └── listing.html
└── static/
    └── uploads/        (photos get saved here automatically)

Setup steps

Install MySQL if not already installed, and make sure it's running.
Create the database and table


   mysql -u root -p < schema.sql

(or paste schema.sql into MySQL Workbench / your client and execute it)


Set your DB credentials
Open app.py and update DB_CONFIG near the top:


python   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'YOUR_MYSQL_PASSWORD',
       'database': 'registration_db'
   }


Install Python dependencies


   pip install -r requirements.txt


Run the app


   python app.py

Starts on http://127.0.0.1:5000/


Flow

http://127.0.0.1:5000/ → Registration form
On successful submit → saves to MySQL → redirects to /listing
http://127.0.0.1:5000/listing → search / filter / sort / paginated table





How the listing page works — everything goes through one API

All searching, filtering, sorting, and paging for the listing table happens through a single
endpoint: GET /api/records. The page never has its own copy of the data — it just asks the
API each time something changes, and redraws the table from the JSON response.

Query parameters accepted by /api/records:

ParamMeaningExamplenameCase-insensitive "contains" search on employee namename=magenderExact match filtergender=MalestateExact match filterstate=Delhisort_byColumn to sort by: reg_no, name, gender, statesort_by=namesort_orderasc or descsort_order=ascpagePage number (1-indexed)page=2page_sizeRecords per page (default 10, max 100)page_size=10

Response shape:

json{
  "records": [ { "reg_no": 1, "name": "...", "email": "...", "gender": "...", "state": "...", "photo": "..." } ],
  "total": 42,
  "page": 1,
  "page_size": 10,
  "total_pages": 5,
  "sort_by": "reg_no",
  "sort_order": "desc"
}

On the listing page:


Typing in the name box and pressing Search (or Enter) triggers a fresh API call with name/gender/state filters, resetting to page 1
Clicking a column header (Reg. No, Name, Gender, State) sorts by that column — click again to flip asc/desc — and calls the API again with the current filters preserved
Clicking a page number / Previous / Next calls the API again with the current filters and sort preserved, just a different page


Notes


Only Delhi (Delhi, New Delhi) and Uttar Pradesh (Noida, Lucknow) are available as State/City in the form.
Photos are stored in static/uploads/, JPEG/PNG only (validated both client-side and server-side).
If an employee has no email, their name in the table shows as plain text instead of a mailto: link.
sort_by is checked against a whitelist server-side (reg_no, name, gender, state) so arbitrary column names can't be injected into the SQL query.
