#!/usr/bin/perl -w
use strict;

use CGI ':standard';  
use CGI::Carp qw(fatalsToBrowser);   


my $cgi = new CGI;
my $action = $cgi->param("action");

my $files_location;   
my $ID;   
my @fileholder;  

$files_location = "booking_log";  

$ID = $action . '.cfg';

if ($ID eq '') {   
	print "Content-type: text/htmlnn";   
	print "You must specify a file to download."; 
	exit 0;
}

open(DLFILE, "<$files_location/$ID") || Error('open', 'file');   

@fileholder = <DLFILE>;   

close (DLFILE) || Error ('close', 'file');   

print "Content-Type:application/x-download\n";
print "Content-Disposition:attachment;filename=$ID\n\n";

print @fileholder;

exit 0;



	
