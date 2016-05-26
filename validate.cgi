#!/usr/bin/perl
use strict;
use CGI;
use CGI::Session;
use Net::LDAP;

my $cgi= new CGI;
my $session = new CGI::Session("driver:File", $cgi , {Directory=>'/tmp'});
my $cookie = $cgi->cookie(CGISESSID => $session->id );

### get parameters
my $user = $cgi->param("user");
my $pass = $cgi->param("pass");
my $action = $cgi->param("action");
my $requrl = $cgi->param("requrl");

### use the user+pass to bind AD server
my $ldap_host = "ad4.ad.alcatel.com";
my $ldap_baseDN = 'dc=ad4,dc=ad,dc=alcatel,dc=com';

$user =~ s/^ad4[\\\/]//;
$user =~ s/\W//g;
$user = lc($user);

my $errorMsg = "Login failed!";
my $infoJsonStr = "";


my $ldap;
my $mesg;

$ldap = Net::LDAP->new($ldap_host);
unless ($ldap) { # retry in 2 sec if failed.
	$errorMsg = "new ldap failed: $@";
	print STDERR __LINE__ . ":($user)" . $errorMsg;
	sleep 2;
	$ldap = Net::LDAP->new($ldap_host);
}
if ($ldap) {
	$mesg = $ldap->bind("ad4\\$user", password => $pass);
	if ($mesg){
		$errorMsg = $mesg->is_error(); 
		print STDERR __LINE__ . ":($user)" . $errorMsg . "\n" if $errorMsg;

		my $filter = "(sAMAccountName=$user)";
		$infoJsonStr = getInfoStr(\$ldap, $ldap_baseDN, $filter) unless $errorMsg;

		$ldap->unbind;  # release gracefully.		

	}else{
		$errorMsg = $@;
	}
	unless($errorMsg) {
		print STDERR __LINE__ . ":($user)" . $errorMsg . "\n";
	}
}else{
	$errorMsg = "new ldap failed: $@";
	print STDERR __LINE__ . ":($user)" . $errorMsg;
} 

my $loginInfo = $errorMsg ? "NOK: $errorMsg" : "OK";

print $cgi->header(-cookie=>$cookie);

$session->param('f_name', $user);
$session->param('f_login', $loginInfo);
$session->param('f_action', $action);
$session->param('f_info', $infoJsonStr);

print "<script language=\"javascript\">";
print " location.href=\"$requrl\"";
print "</script>";

exit 0;

##############################################

sub getInfoStr {
	my ($ldap, $ldap_bind, $filter) = @_;

	my $items = ['alcatel-CIL','alcatel-UPI','mail','telephoneNumber','mobile','title','department','company', 'distinguishedName'];
	
	my $mesg = $$ldap->search(base => $ldap_bind, filter => $filter, attrs => $items );
						 
	my @entries = $mesg->entries;
	
	if ($entries[0]) {
		my $jsonStr = "{\n\"dummy\":\"dummy\"";
		foreach my $item (@$items) {
			$jsonStr .= ",\n\"$item\":\"" . $entries[0]->get_value($item) . "\"";
		}
		$jsonStr .= "\n}\n";
		return $jsonStr;
	}
	return "";
}


