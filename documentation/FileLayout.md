# SIRAF file layout

## Description

The file is handled simarly to a `heap`.

I have attempted to define this as generically as possible. The using code will be able to configure and handle the
final layout according to its needs.

The Config and Blocks are maintained by the `File module`

## Layout

1. _Config_ 
    -- Always starts at address zero
2. _Blocks_
    -- May be located anywhere 
    -- Consiste of 
        ~~ _Data blocks_
        ~~ _Available blocks_
        ~~ _Descriptor blocks_

### _Config_

Basic information that the `File module` uses to verify, and maintain the file and its contents. It is always of a fixed length.

#### Layout
1. File type validator
    -- Content: **`/~ siraf ~/`**
    -- Fixed, simply used to validata that this is realy a .siraf file
2. Version
    -- Two digit version number.
    -- Used for backward compatabiity
3. Absolute Address of the _Descriptor_ Block
    -- 32 bit unsigned integer giving the absolure address of the _Descriptor block_
    -- This is stored as an array of unsigned 8 bit integers, making it independed of any and all system _`endian`_ configuration
4. Absolute address of the first _Available block_    
    -- 32 bit unsigned integer giving the absolure address of the _Descriptor block_
    -- This is stored as an array of unsigned 8 bit integers, making it independed of any and all system _`endian`_ configuration
5. Checksum
    -- Computed wheneve there is a change
    -- Used as verification that everything is OK

### _Blocks_

#### Basic _Block_ layout
1. _Block Descriptor_
    -- Private
    -- 64 bits
    -- Maintained by the interface code
    -- Used as a fence at the beginning and ending of the block
    -- ** Contents **
        @@ Header or End block type
            ## 1 bit
            ## 1 = Header; 0 = End
        @@ Type of block
            ## 7 bits
            ## Currently defined as `Data`, `Descriptor`, and `Available`
            ## Special types for short _Blocks_ are `Avail_1_Byte`, `Avail_2_Bytes`, ... `Avail_15_bytes`
                ^^ These are _Blocks_ that are too small to hold any data
                ^^ They will have no _End Descriptor_
                ^^ They will be merged into an _`Available` block_ when the preceeding _Data Block_ is freed
    -- Size of the the data area in bytes
        @@ This is stored in an `Endian` free format
    -- Checksum
2. User _Data_
3. _Block Descriptor_
    -- Ending fence

#### _Descriptor Block_