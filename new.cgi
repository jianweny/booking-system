#!/usr/bin/perl -w
use strict;
require "buildInputForm.pm";
require "formatConvert.pm";

use Encode;
use JSON;
use CGI;
use CGI::Session;

my $cgi = new CGI;

my $session = new CGI::Session("driver:File", $cgi ,{Directory=>'/tmp'});
my $user = $session->param("f_name") || "";
my $login = $session->param("f_login") || "";

printHtmlHeader("");

unless ($user && $login eq 'OK') {	
	printLogonEntry ("", $user, $login);
	printHtmlFooter();
	exit 0;
}

my $cfgFile = $cgi->param("cfgfile") || "";

#========================================================
# if either of files are not given, print initial 
#========================================================
unless ($cfgFile) {
	print <<__UPLOAD;
	<pre>
			<form method="post" action="new.cgi" enctype="multipart/form-data">
			Choose a config file. must be ended with ".cfg"

			<input type="file" name="cfgfile">

			<input type="submit" value="Upload!">
			</form>
__UPLOAD

	printHtmlFooter();
	exit 0;
}

#========================================================
# now handle uploading files.
#========================================================
my $file = $cfgFile;
my $fileName = lc($file);
$fileName =~ s/^.*[\\\/]//; # get basename

if ($fileName !~ /^[\w-]+\.cfg$/i) {
	printError ("Error: config file name must be &lt;plain-chars&gt;.cfg!\n\n");
	printHtmlFooter();
	exit 0;
}

my $action = $fileName;
$action =~ s/\.cfg$//;  # get action name.

my $basedir = basedir();
	
my ($isAdmin, $errMsg);
if (-e "$basedir/$fileName") {
	# the cfg file exists, check owner
	($isAdmin, $errMsg) = checkAdmin($user, $action);

	printDebug (__LINE__ . ": ($isAdmin, $errMsg) ($user, $action)");
	
	unless ($isAdmin) {
		printError($errMsg);
		printHtmlFooter();
		exit 0;
	}
}
	
### now upload it.
unless (open (OUTFILE, ">$basedir/$fileName")) {
	printError("Failed to open \">$basedir/$fileName\"");
	printHtmlFooter();
	exit 0;
}

binmode(OUTFILE);
while(my $byteread = read ($file, my $buffer, 1024)) {
	print OUTFILE $buffer;
}
close (OUTFILE);

### sanity check.
my ($rc, $htmStr) = configSanityCheck($action);
if ($rc) {
	print <<__FIELDSET;
<fieldset>
<legend>Sanity Check Result</legend>
<h3><span class="error">$rc lines have errors, please correct them and upload again!</span></h3>
<pre>
$htmStr
</pre>
</fieldset>
__FIELDSET

	`rm -f "$basedir/$fileName"`;
	printHtmlFooter();
	exit 0;
}

### admin check, upload user must be one of users.
($isAdmin, $errMsg) = checkAdmin($user, $action, "new");
printDebug (__LINE__ . ": ($isAdmin, $errMsg) ($user, $action)\n\n");
unless ($isAdmin) {
#	print "the file seems wrong. Wrong format, or you are not admin. deleting!\n\n";
	`rm -f "$basedir/$fileName"`;
	printError($errMsg);
	printHtmlFooter();
	exit 0;
}

### now the uploaded action file is OK.
my $fullUrl = 'http://' . $ENV{'HTTP_HOST'} . $ENV{'SCRIPT_NAME'};
$fullUrl =~ s|/[^/]*$|/|;
$fullUrl .= "login.cgi?action=$action";
print "<h2>Upload config file OK!</h2>\n<br>\n<br>";
print "<h3>Booking portal is: </h3>&nbsp;&nbsp;&nbsp;";
print "<h4><a href=\"login.cgi?action=$action\">$fullUrl</a></h4>".
      "<br><h4>Please test before broadcast it!</h4>\n<br>\n<br>";

printHtmlFooter();

exit 0;


##################################
# input: config file
# return: html check result
##################################
sub configSanityCheck {
    my $action = lc($_[0]);
	my $cfgFile = "booking_log/$action.cfg";
    
    ### get file contents
	open (CFG_FILE, "$cfgFile") || return (0, "<span class=\"error\">Error: $@</span>");
	my @lines;
	push (@lines, $_) while <CFG_FILE>;
	close CFG_FILE;

	my $oldline ="";
	my $retStr = "";
	my $rc = 0;
    foreach my $newline (@lines){
	    $newline =~ s/[\r\n]+$//;
		$newline =~ s/\t/ /g;  # \t is not allowed by JSON.
		
		if ($newline =~ /\\$/) {
			$newline =~ s/\\/_NEWLINE_/; # remove \\ at tail.
			$oldline .= $newline;
			next;
		}
		$oldline .= $newline;
		my $line = $oldline;
		$oldline = "";

		$line = plain2html($line);
		
		my $validLineFalg = 0;
		if ($line =~ /^\s*#/ || $line =~ /^\s*$/) {
			$validLineFalg = 1;
		}
        elsif ($line =~ /^\s*ActivityName\s*:\s*(.*)/i || $line =~ /^\s*ActionName\s*:\s*(.*)/i ||
		    $line =~ /^\s*Admins\s*:\s*(.*)/i       || $line =~ /^\s*ActionGroup\s*:\s*(.*)/i ||
	        $line =~ /^\s*StartTime\s*:\s*(\d\d\d\d\-\d\d\-\d\d \d\d:\d\d:\d\d)/i ||
			$line =~ /^\s*EndTime\s*:\s*(\d\d\d\d\-\d\d\-\d\d \d\d:\d\d:\d\d)/i   ||
			$line =~ /^\s*BookingCount\s*:\s*(\d+)/i || $line =~ /^\s*QueueCount\s*:\s*(\d+)/i ||
			$line =~ /^\s*Information\s*:\s*(.*)/i ||
			$line =~ /^\s*Picture\s*:\s*(.*)/i ) {
			$validLineFalg = 1;
	    }
	    elsif($line =~ /^\s*Input\s*:\s*(.*)/i) {
			my $input = $1 . ",";
			#$retStr .= "\ndebug: \$input='$input'\n";
			my @inputType = qw(subtitle text radio select textarea select-counted);
			foreach my $inputType (@inputType) {
				#$retStr .= "\ndebug: \$inputType='$inputType'\n";
				if ($input =~ /^.*,\s*$inputType\s*/i) {
					$validLineFalg = 1;
					last;
				}
			}
	    }
		$line =~ s/_NEWLINE_/\\<br>/g;
		unless ($validLineFalg) {
			$line = "<span class=\"error\">$line</span>";
			$rc++;
		}
		$line .= "\n";

		$retStr .= $line;
    }
	return ($rc, $retStr);
}



	
