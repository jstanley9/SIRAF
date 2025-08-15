# SIRAF Package
## Single Indexed Random Access File Package
## First Boot.dev Personal Project

### Definition 
- Python package to create, and access an old school ISAM file.
- Initially will support the creation, open, find, add, update, delete, recordcount, and close.
- Creation
    - `<file name>: <field>, <field>, ..., <key>`
    - `<field>:  <type> <id>`
    - `<key>` key (<id>, <id>, ...)`
    - `<file name>` will be used as the file name. Define sans extension
	- `<id>` name of the field; cannot be `key`
    - **Types**
	    @ `bool`
	    @ `int`
	    @ `float`
	    @ `complex`
	    @ `str`
	    @ `date`
	    @ `time`
	    @ `timestamp`
	- Leaves file open
- All calls return a dictionary
	- `records`: A list of the affected records
	- `result`: an enumeration of the call result; Success, Fail, others TBD
	- `message`: Usually the reason for the failure
- **`open`**
    - Pass in path
	- By default file is opened for read and write
- **`find`**
    - Pass in list/couple of key values.
	    @ The list must list the values in the order that the keys were defined
		    - Each entry can be just the key value or
			- A couple that gives the key value and comparison (`==, !=, >, >=, <, <=`: TBD)
	    @ An empty, or missing list entry is allowed
	- Optionally pass in a list of the field names to return
	- Returns a list of the file records that match the key values; empty if no records found
	- *Result*: Success, Fail
- **`add`**
	- Pass in the record to be added
	- For now the record is to be a dictionary with the key being the field name
	- Missing field names will result in a None value for that field
	- All key values must be set and not None
	- An error will occur if the key already exists in the file
	- *Result*: Success, Fail,  
- **`update`**
	- Pass in the record to be updated
	    @ Keys are required for success
	- *Result*: Success, Fail
- **`delete`**
	- Pass in keys
	- *Result: Success, Fail
- **`recordcount`**
	- returns the number of records in the file
- **`close`**
	- *Result*: Success, Fail	
