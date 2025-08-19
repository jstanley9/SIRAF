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

## Blocks    