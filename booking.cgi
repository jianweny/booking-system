#!/usr/bin/perl -w

use strict;

#require "csl2info.pm";
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

my $action = $cgi->param("action") || "";
my $bookedFile = $cgi->param("bookedFile") || "";
my %userInfo = userInfo("","","","","","","","","","","","","","","");
my @userInfo = sort keys(%userInfo);

printHtmlHeader();

print "<center>";

if ($user && $login eq 'OK' && $action) {
	my $lockFile = "booking_log/$action/__lock__";
	if (-e $lockFile) {
		print "<h2>本次报名活动已经锁定，无法做任何修改!</h2>\n";
		print "</center>\n";
		printHtmlFooter ("<br /><br /><a href=login.cgi?action=$action>[back]</a>". "&nbsp;"x10 ."<a href=login.cgi?logout=1>[logout]</a>\n");
		exit 0;
	}
}

my $json = "{\n\t\"user\":\"$user\"";

foreach my $userInfo (@userInfo) {
	my $v = $cgi->param($userInfo) || "";
	$json .= ",\n\t\"$userInfo\": \"$v\"";
}


if ($user && $login eq 'OK') {
	for (my $i=100; $i<999; $i++) {
		foreach my $name("text", "radio", "select", "select-counted", "checkbox", "textarea") {
			my $param = $cgi->param("$i$name");
			if (defined $param) {
				$param = plain2html($param);
				#print "$i$name: $param\n";
				$json .= ",\n\t\"$i$name\": \"$param\"";
			}
		}
	}
	my $param = $cgi->param("note");
	if ($param) {
		$json .= ",\n\t\"note\": $param";
	}
    $json .= "\n}\n";
	print "<div style='display:none'>json: $json</div>";
	
    print "<hr>\n";

	
	my $json2 = new JSON;
	my $jsonObj;
	eval { 
#		my $jsonX = $json;
#		$jsonX =~ s/([\\])/\//g; # avoid "illegal escape char" error
		$jsonObj = $json2->decode($json);
	};
	if ($@) {
		warn "$@";
		print "<textarea cols=100 rows=20 class=xxx>$@\n\$json='$json'\n</textarea><br>"; 
	}
	if ($jsonObj && $action) {
		if (-e $bookedFile) {
			my $tobedeleted = $cgi->param("tobedeleted") || "";
			if ($tobedeleted eq 'yes') {
				my $time = `date +%Y-%m-%d_%H:%M:%S`;
				`mv $bookedFile $bookedFile.deleted.$time 2>/dev/null`;
				print "<h2>报名已经取消!</h2>\n";
			}else{
				if (open BOOKFILE, ">$bookedFile") {
					print BOOKFILE $json;
					close BOOKFILE;
					print "<h2>恭喜！报名信息修改成功!</h2>\n";
				}else{
					print "<h3>ERROR: booking failed! $@</h3>\n";
				}
			}
		}else{
			my $bCnt = $cgi->param("BookingCount") || 1000;
			my $qCnt = $cgi->param("QueueCount") || 1000;
			my $bookingType = checkBookingType($action, $bCnt, $qCnt);
		
			if ($bookingType eq "NOK") {
				print "<h2>抱歉，报名已经满额！</h2>\n";
			}else{
				`mkdir -p booking_log/$action`;
				my $time = `date +%Y-%m-%d_%H:%M:%S`;
				chop($time);
				my $file = "booking_log/$action/$user"."_"."$time.book";
				if (open BOOKFILE, ">$file") {
					print BOOKFILE $json;
					close BOOKFILE;
					print "<div style='display:none'>saved file: $file</div>\n\n";
					if ($bookingType eq "Booked") {
						print "<h2>恭喜！报名成功！Booking Successfully!</h2>\n";
					}else{
						print "<h2>由于人数限制，您的报名进入了等候队列。</h2>\n";
					}
				}else{
					print "<h3>ERROR: booking failed! $@</h3>\n";
				}
			}
		}
	}
	print "</center>\n";
    printHtmlFooter ("<br /><br /><a href=login.cgi?action=$action>[back]</a>". "&nbsp;"x10 ."<a href=login.cgi?logout=1>[logout]</a>\n");

}else{
	printHtmlHeader();
	printLogonEntry ($action, $user, $login);
	printHtmlFooter();
}

exit 0;


