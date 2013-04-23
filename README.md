Verilog Automatic
====================
This plugin can automatically add ports to the current editing file, generate module instances (need ctags),add instance connections ,add file header for verilog code.
I borrowed the idea from automatic.vim which is the an alike plugin for VIM, just rewrote one for sublime text2.

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

Example:

#### before:

    module test(/*autoport*/);
        input a;
        input b;
        output c;
        output d;
        inout e;

#### after:

    module test(/*autoport*/
    //inout
                e,
    //output
                c,
                d,
    //input
                a,
                b);
        input a;
        input b;
        output c;
        output d;
        inout e;



## AutoInst:(shift+f7)
*******************
Automatically generate module instances after the "/*autoinst*/" mark (need ctags).

* NOTE:Need to place the cursor on the module name, multiple-cursor supported to generate multiple instances.

Example:

#### before:
        test test_instance(/*autoinst*/);

#### after:
* place the cursor on the module name "test"

        test test_instance(/*autoinst*/
                .e(e),
                .c(c),
                .d(d),
                .a(a),
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
                .d(d),
                .a(a),
                .b(b));
#### after:

    /*autodef*/
    wire d;
    wire e;
    wire b;
    wire c;
    wire a;
    //assign d=
    //assign e=
    //assign b=
    //assign c=
    //assign a=



    test test_instance(/*autoinst*/
                .e(e),
                .c(c),
                .d(d),
                .a(a),
                .b(b));


## AddFileHeader:(shift+f9)
************************
add your personal information in the setting file(the user's setting file is better),like below or leave any of them empty:

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