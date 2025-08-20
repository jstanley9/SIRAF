# RAVRF file layout

## Description

This is a random access file. It is designed to handle variable size data records with the ability to update existing records where the size of the record changes with the update. 

This package does not specify or know how to locate the individual records. When adding or updating records an associated address is returned. It can be used to retrieve that record at a later time. Note, that an updated record may have a different different address when the update is complete; when that happens the previous block will have been deleted.

I have attempted to define this as generically as possible. The using code will be able to configure and handle the
final layout according to its needs.

The Config and Blocks are maintained by the `File module`

## Layout

1. _Config_ 
    - Always starts at address zero
2. _Blocks_
    - May be located anywhere 
    - Consiste of 
        - _Data blocks_
        - _Available blocks_
        - Meta blocks_

### _Config_

Basic information that the `File module` uses to verify, and maintain the file and its contents. It is always of a fixed length.

#### Layout
1. File type validator
    - Content: **`/~ ravrf ~/`**
    - Fixed, simply used to validata that this is realy a .ravrf file
2. Version
    - Two digit version number.
    - Used for backward compatabiity
3. Absolute Address of the _Meta Block_
    - 32 bit unsigned integer giving the absolure address of the _Meta Block_
    - This is stored as an array of unsigned 8 bit integers, making it independed of any and all system _`endian`_ configuration
4. Absolute address of the first _Available block_    
    - 32 bit unsigned integer giving the absolure address of the _Meta Block_
    - This is stored as an array of unsigned 8 bit integers, making it independed of any and all system _`endian`_ configuration
5. Checksum
    - Computed wheneve there is a change
    - Used as verification that everything is OK

### _Blocks_

#### Basic _Block_ layout
1. _Block Description_
    - Private
    - 64 bits
    - Maintained by the interface code
    - Used as a fence at the beginning and ending of the block
    - ** Contents **
        - Header or End block type
            - 1 bit
            - 1 = Header; 0 = End
        - Type of block
            - 7 bits
            - Currently defined as `Data`, `Meta`, and `Available`
            - Special types for short _Blocks_ are `Avail_1_Byte`, `Avail_2_Bytes`, ... `Avail_15_bytes`
                - These are _Blocks_ that are too small to hold any data
                - They will have no _End Descriptor_
                - They will be merged into an _`Available` block_ when the preceeding _Data Block_ is freed
    - Size of the the data area in bytes
        - This is stored in an `Endian` free format
    - Checksum
2. User _Data_
3. _Block Descriptor_
    - Ending fence

#### _Meta Block_

There is a single `Meta` block allowed. It is user definable. The purpose is to allow the user to provide configuration definitions on the the file content and how to access the data.

This package will keep track of where this block is. It provides functions to store, update, and delete the _Meta_ data. 

#### _Data Block_

There are as many data records as needed. The user is responsible for figuring out how to find these records.

Users can Read, Add, Update, Delete these records from the file. There is also an ability to retrieve all the data records in an unordered sequence.

#### _Available Block_

Users never see these. These blocks are exclusively maintained by this package