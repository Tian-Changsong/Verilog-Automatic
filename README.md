Verilog Automatic
====================
This plugin can automatically add ports to the current editing file,  generate module instances (need ctags),add instance connections ,add file header for verilog code. Both verilog-1995 and verilog-2001 style are supported.
I borrowed the idea from automatic.vim which is a similar plugin for VIM, I just rewrote one for sublime text2&3.

# Features
***********
* AutoPort
* AutoInst
* AutoDef
* AddFileHeader


# Description


## AutoPort:(shift+f6)
*******************
Automatically add ports to the current editing file after the "/*autoport*/" mark.

* NOTE:
    ** NOT SUPPORTED STYLE:
        input clk,output single_out,   //multiple input/output/inout keywords in the same line
        input clk,rst,
        chip_en;                       //multiple signals separated by comma written in different lines
    ** Do not use this function when there are multiple modules in the same file.

Example:

#### Before

    (verilog-1995 style):

    module test(/*autoport*/);
        input [1:0]a;
        input b;
        output [2:0]c,d;
        inout e;

    (verilog-2001 style):

    module test(/*autoport*/);
        input wire[1:0]a;
        input wire b;
        output reg [2:0]c,d;
        inout wire e;

#### After:

    module test(/*autoport*/
    //inout
                e,
    //output
                c,
                d,
    //input
                a,
                b);


## AutoInst:(shift+f7)
*******************
Automatically generate module instances after the "/*autoinst*/" mark (need ctags).

* NOTE:Need to place the cursor on the module name, multiple-cursor supported to generate multiple instances.

Example:

#### Before:
        test test_instance(/*autoinst*/);

#### After:
* Place the cursor on the module name "test"

        test test_instance(/*autoinst*/
                .e(e),
                .c(c),
                .d(d[2:0]),
                .a(a[1:0]),
                .b(b));



## AutoDef:(shift+f8)
******************
Automatically add instance connections after the /*autodef*/ mark.

Example:
#### before:

    /*autodef*/



        test test_instance(/*autoinst*/
                .e(e),
                .c(c),
                .d(d[2:0]),
                .a(a[1:0]),
                .b(b));
#### after:

    /*autodef*/
    wire e;
    wire [2:0]d;
    wire c;
    wire b;
    wire [1:0]a;
    //assign e=
    //assign d=
    //assign c=
    //assign b=
    //assign a=



    test test_instance(/*autoinst*/
                .e(e),
                .c(c),
                .d(d[2:0]),
                .a(a[1:0]),
                .b(b));


## AddFileHeader:(shift+f9)
************************
Add your personal information in the setting file(the user's setting file is better),like below or leave any of them empty:

        {
            "Author":"Mike",
            "Company":"Microsoft",
            "Email":"whatever@yahoo.com"
        }
thus generates the file header like this:

       //==================================================================================================
        //  Filename      : test.v
        //  Created On    : 2013-04-01 21:37:31
        //  Last Modified : 
        //  Revision      : 
        //  Author        : Mike
        //  Company       : Microsoft
        //  Email         : whatever@yahoo.com
        //
        //  Description   : 
        //
        //
        //==================================================================================================

## Change log

#### 05/08/2013 
Add verilog-2001 style port declaration support.
Add comments support, single line commneted-out code will be ignored.