#!/usr/bin/perl -w
use strict;
require "buildInputForm.pm";
require "formatConvert.pm";

use Encode;
use JSON;
use CGI;
use CGI::Session;
use Spreadsheet::WriteExcel;


my $cgi = new CGI;

my $session = new CGI::Session("driver:File", $cgi ,{Directory=>'/tmp'});
my $user = $session->param("f_name") || "";
my $login = $session->param("f_login") || "";
my $action = lc($cgi->param("action") || "");

my $export = $cgi->param("export") || "";

my $DEBUG = $cgi->param("debug") || "";

my $json = new JSON;
my $cfgObj;

## global variables for XLS
my ($workbook, $worksheet);
my ($xlsRow, $xlsCol) = (0,0);
my ($format_h, $format_d0, $format_d1);
my @colWidth = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0); # should be enough:)

if ($user && $action && $login eq 'OK') {	
	### get config info.
	my $cfgJsonStr = getConfigJson($action);
	eval { 
		$cfgObj = $json->decode($cfgJsonStr);
	};
	if ($@) {
		printHtmlHeader();
		print "<h3>action 指定的活动错误，请检查网址或者联系活动组织者。</h3>";
		printHtmlFooter();
		exit 0;
	}
	
	unless (isAdmin(\$cfgObj, $user)) {
		printHtmlHeader();
		print "<h3>Sorry, only for admins.</h3>";
		printHtmlFooter();
		exit 0;
	}

	### by default, list booking data.
	if ($export) {
		print "Content-Type:application/x-download\n";
		print "Content-Disposition:attachment;filename=$action.xls\n\n";
		binmode(STDOUT);
		
		$workbook  = Spreadsheet::WriteExcel->new(\*STDOUT);
		$worksheet = $workbook->add_worksheet("booking result");

		my $bgcolor_h  = $workbook->set_custom_color(40, '#FFFFCC');
		my $bgcolor_d0 = $workbook->set_custom_color(41, '#FFFFFF');
		my $bgcolor_d1 = $workbook->set_custom_color(42, '#EEEEEE');
 
		$format_h  = $workbook->add_format(bg_color => 40, border => 1, text_wrap => 1, bold => 1);
		$format_d0 = $workbook->add_format(bg_color => 41, border => 1, text_wrap => 1);
		$format_d1 = $workbook->add_format(bg_color => 42, border => 1, text_wrap => 1);

	}else{
		printHtmlHeader("Booking results","");
		print "<table border=1 class=\"table10\">\n";
	}
		
	my @date_bookers;
	getBookingList($action, \@date_bookers);
	
	# 4. list one by one
	my $noteRowOld = "";
	my $totalPeople = 0;
	for (my $i=0; $i<@date_bookers; $i++) {
		my ($date, $booker) = split (" ", $date_bookers[$i]);
		my $path = "booking_log/$action/";
		my $file = $path . $booker . '_' . $date . '.book';
		my ($noteRow, $dataRow, $totalCnt) = getBookedInfo ($file, \$cfgObj);
		next unless ($noteRow && $dataRow);
		$totalPeople += $totalCnt;
		
		if ($noteRow ne $noteRowOld){
			printCGI("<tr class=h><th>Index</th><th>Type" . $noteRow . "</th></tr>\n");
			$noteRowOld = $noteRow;
		}
		my $type = "<span class=\"NOK\">NOK</span>";
		if ($totalPeople < $cfgObj->{"BookingCount"}) {
			$type = "<span class=\"Booked\">Booked</span>";
		}elsif ($totalPeople < ($cfgObj->{"BookingCount"} + $cfgObj->{"QueueCount"})) {
			$type = "<span class=\"Queued\">Queued</span>";
		}
		if ($export) {
			$type =~ s/<.*?>//g;
		}
		
		my $class = (int($i/2)*2 == $i) ? "d0" : "d1";
		my $debugInfo = $DEBUG ? "(total:$totalPeople; file:$file)" : "";
		printCGI ("<tr class=$class><td>". ($i+1) ."$debugInfo</td><td>$type$dataRow</td></tr>\n");
	}
	if ($export) {
		printCGI ("还没人报名。\n") unless $noteRowOld;
		
		for (my $i=0; $i<@colWidth; $i++) {
			if ($colWidth[$i]) {
				$worksheet->set_column($i, $i, $colWidth[$i]);
				#$worksheet->write($xlsRow, $xlsCol+$i, $colWidth[$i]);
			}
		}
		
		$workbook->close();
	}else{
		print "<tr><td><br><h3>还没人报名。</h3><td><tr>\n" unless $noteRowOld;
		print "</table>\n";
		print "</body></html>\n";

		my $adminLinks = "<a href=\"viewall.cgi?action=$action&export=1\" >[export to XLS]</a> " . "&nbsp;"x4;

		printHtmlFooter("\n<br>$adminLinks<a href=login.cgi?logout=1&action=$action>[logout]</a><br>\n");
	}
	
	exit 0;
}

printHtmlHeader();

if ($user && $login eq 'OK') {
	print "<h3>没有指定的活动，请检查网址或者联系活动组织者。</h3>";
}else{
	printLogonEntry ($action, $user, $login);
}
printHtmlFooter();

exit 0;

#------------------------------------------------------------------------------------
sub printCGI {
	my $str = $_[0];
	unless ($export) {
		print $str;
	}else{
		# to XLS
		my $format;
		if ($str =~ /^<tr class=h>/i) { #head row
			$format = $format_h;
		}elsif( $str =~ /^<tr class=d0>/i) {
			$format = $format_d0;
		}else{
			$format = $format_d1;
		}
		
		my @cells = ($str =~ /<t[hd]>(.*?)<\/t[hd]>/ig);
		for (my $i=0; $i<@cells; $i++){
			$colWidth[$i] = length($cells[$i]) if $colWidth[$i] < length($cells[$i]);
			$colWidth[$i] = 40 if $colWidth[$i] > 40;
			$colWidth[$i] = $colWidth[$i] * 1.2; # a minor improvement for small-width cells.
			$colWidth[$i] = $colWidth[$i] / 1.2 if $colWidth[$i] > 20;
			
			$cells[$i] = html2plain($cells[$i]);
			#$worksheet->write(row, col, string, [format]);
			$worksheet->write($xlsRow, $xlsCol+$i, decode('UTF8', $cells[$i]), $format);
		}
		$xlsRow++;
	}
}

