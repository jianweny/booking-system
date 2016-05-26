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
my $info  = $session->param("f_info") || "";

unless ($user && $login eq 'OK') {	
	printLogonEntry ("", $user, $login);
	exit 0;
}

print "Content-type: text/html; charset=utf-8\n\n";

my $pInfoTable = getPersonalInfoTable($info);

my $buffer = $cgi->param("input_preview") || "";


my $action = $cgi->param("action") || '__preview__';  # if no action, it's preview.

my $basedir = basedir();
my $fileName = "$basedir/$action.cfg";

if ($action ne "__preview__") {
	if (-e "$basedir/$action/__lock__") {
		$action = "__preview__"; # if locked, preview only!
	}elsif (-e $fileName) {
		my ($isAdmin, $retMsg) = checkAdmin($user, $action);
		if ($isAdmin) {
		}else{
			print "NOK:$retMsg";
			exit 0;
		}
	}else{
		# a newly created action. fine.
	}
}

		
### now upload it.
unless (open (OUTFILE, ">$fileName")) {
	print "NOK: save config file failed.\n";
	printError("Failed to open \">$fileName\"");
	exit 0;
}
print OUTFILE $buffer;

close (OUTFILE);

my %userInfo = ();

my $json = new JSON;
my $cfgJsonStr = getConfigJson($action);
my $cfgObj;
my	($retCfgInfo1, $retCfgInfo2, $retInputForm) = ("","");

if ($cfgJsonStr) {
	eval { 
		$cfgObj = $json->decode($cfgJsonStr);
	};
	unless ($@) {
		($retCfgInfo1, $retCfgInfo2) = buildCfgHtmlTable(\$cfgObj, $action);
		$retInputForm = buildInputForm(\%userInfo, $action, \$cfgObj, "", "", "", "");
	}
}

#print "<a href=\"login.cgi?action=$action\">click</a>";
print <<__PREVIEW;
<table border=0 class="preview_table">
	<tr>
		<td>
			<fieldset>
				<legend>活动信息</legend>
				$retCfgInfo1
				<hr>
				$retCfgInfo2
			</fieldset>
		</td>
	</tr>
	<tr>
		<td>
			<fieldset>
				<legend>来自系统的报名者个人信息，无需报名者提交</legend>
				$pInfoTable
			</fieldset>
		</td>
	</tr>
	<tr>
		<td>
			<fieldset>
				<legend>需要报名者提交的信息</legend>
				$retInputForm
			</fieldset>
		</td>
	</tr>
</table>
__PREVIEW

exit 0;



	
