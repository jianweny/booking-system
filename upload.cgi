#!/usr/bin/perl -w

use strict;
use CGI;

my $cgi= new CGI;

my $maxuploadcount = 2;

my $basedir = "booking_log";
my $allowall = "no";
my @theext = (".jgp", ".png", ".gif", ".cfg");

print "Content-type: text/html\n\n";
my $message = "<pre>hello\n";
print  STDERR "pwd=". `pwd` . "\n\n";

for (my $upfilecount=1; $upfilecount<=$maxuploadcount; $upfilecount++) {
	my $file = $cgi->param("file$upfilecount") || "";
	print "file$upfilecount = $file\n";
	if ($file ne ""){
		my $fileName = $file;
		$fileName =~ s/^.*[\\\/]//; # get basename
		my $newmain = $fileName;
		my $filenIsGood = "no";
		if ($allowall ne "yes"){
			my $extname = lc(substr($newmain, length($newmain)-4,4)); #get suffix
			for (my $i=0; $i<@theext; $i++){
				if ($extname eq $theext[$i]) {
					$filenIsGood = "yes";
	print "$file is good.\n";
					last;
				}
			}
		}
		if ($filenIsGood eq "yes") {
			open (OUTFILE, ">$basedir/$fileName");
			binmode(OUTFILE);
			while(my $byteread = read ($file, my $buffer, 1024)) {
				print OUTFILE $buffer;
			}
			close (OUTFILE);
			$message .= $file . "upload successful!\n";
		}else{
			$message .= $file . " file suffix error, uploading failed!\n";
		}
	}
}
print $message;

