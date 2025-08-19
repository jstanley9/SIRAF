# SIRAF modules

## Public module
This is the public interface of the SIRAF package

### Interface module
This is the public face of the package.

This modules will contain:
-- Enumerations required by the user
-- Class definition
	Methods
	@@ create
		:  Create the table
	@@ open
		: Open and existing SIRAF File
	@@ find
		: find or select records using the passed in key(s)
	@@ add 
		: add one or more records to the file. 
		  Returns and error for each record that already exists
	@@ update
		: Update one or more existing records in the File
	@@ delete
		: Delete one or more records from the file based on the keys passed in
	@@ recordcount
		: Returns the number of records in the file
	@@ close
		: Close the file
		
	

## Private modules

### Second Level modules

#### Creation module

#### File module

This is the only code that will work with the file

See `FileLayout.md` for information on the base design of the file 

#### Indexes module

#### Data module

### Third level module

#### I/O module
