#!/usr/bin/perl -w
use strict;
require "buildInputForm.pm";
require "formatConvert.pm";

use Encode;
use JSON;
use CGI;
use CGI::Session;

print "Content-type: text/html; charset=utf-8\n\n";

my $cgi = new CGI;

my $file = $cgi->param("file") || "";
my $action = $cgi->param("action") || "__preview__";
my $basedir = basedir();
my $savedFile = "";

if ($file =~ /\.(png)$/i || $file =~ /\.(jpg)$/i || $file =~ /\.(gif)$/i) {
	my $suffix = $1;
	my $ts = `date +"%s"`;
	chop($ts);
	$savedFile = "$action" . "_$ts." . lc($suffix);
}else{
	print "Error: file format not allowed!";
	exit 0;
}

### make sure the folder is readdy, and clean up prevoius pictures if any.
`mkdir -p $basedir/$action 2>/dev/null`;
#`rm -f $basedir/$action/$action.jpg`;
#`rm -f $basedir/$action/$action.png`;
#`rm -f $basedir/$action/$action.gif`;

### now upload it to a tmp file.
unless (open (OUTFILE, ">$basedir/$action/$savedFile.tmp")) {
	print "Error: Failed to create \">$basedir/$action/$savedFile.tmp\".";
	exit 0;
}

my $byteTotal = 0;
my $byteRead = 0;
binmode(OUTFILE);
while($byteRead = read ($file, my $buffer, 1024)) {
	print OUTFILE $buffer;
	$byteTotal += $byteRead;
}
close (OUTFILE);

if ($byteTotal > 0 && $byteTotal <= 1024*1024){
	`mv -f $basedir/$action/$savedFile.tmp $basedir/$action/$savedFile`;
	print "$action/$savedFile";
}else{
	`rm -f $basedir/$action/$savedFile.tmp`;
	if ($byteTotal == 0) {
		print "Error: upload failed!";
	}else{ 
		print "Error: picture size exceeds 1MB, not allowed!";
	}
}

exit 0;



	
