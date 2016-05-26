#!/usr/bin/perl -w
require "buildInputForm.pm";

print "<html>\n<head>\n<meta charset=\"utf-8\">\n</head>\n";


print "<body>\n";

&buildInputForm("familyday2016.cfg");

print "</body></html>\n\n";
