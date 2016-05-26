#!/usr/bin/perl -w
use strict;
require "formatConvert.pm";
require "buildInputForm.pm";

use Encode;
use JSON;
use CGI;
use CGI::Session;

my $cgi = new CGI;

my $session = new CGI::Session("driver:File", $cgi ,{Directory=>'/tmp'});
my $user = $session->param("f_name") || "";
my $login = $session->param("f_login") || "";

unless ($user && $login eq 'OK') {	
	printLogonEntry ("", $user, $login);
	exit 0;
}

print "Content-type: text/html; charset=utf-8\n\n";

my $action_name = $cgi->param("action_name");
if ($action_name) {
	my $basedir = basedir();
	if (-e "$basedir/$action_name.cfg") {
		# the cfg file exists, check owner
		my ($isAdmin, $retMsg) = checkAdmin($user, $action_name);
		if ($isAdmin) {
			print "OK:modify.\n$retMsg";
		}else{
			print "NOK:$retMsg";
		}
	}else{
		print "OK:create.";
	}
	exit 0;
}


print "NOK:do not know what to do.";
	
exit 0;




	
