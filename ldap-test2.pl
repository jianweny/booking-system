#!/usr/bin/perl
use strict;

use Net::LDAP;
use Encode;
use JSON;

if (scalar(@ARGV) < 2) {
	print "Usage: $0 <csl> <passwd> [<csl1> <csl2> ...]\n";
	exit 0;
}

### get parameters
my $user = $ARGV[0];
my $pass = $ARGV[1];

### use the user+pass to bind AD server
my $ldap_host = "ad4.ad.alcatel.com";
my $ldap_baseDN = 'dc=ad4,dc=ad,dc=alcatel,dc=com';

my $errorMsg = "Login failed!";

my $ldap = Net::LDAP->new($ldap_host);
if ($ldap) {
	my $mesg = $ldap->bind("ad4\\$user", password => $pass);

	$errorMsg = $mesg->is_error(); 
	
	print __LINE__ . ": \$errorMsg = $errorMsg\n";
	
	if ($mesg){	
        my $items = ['alcatel-CIL','alcatel-UPI','mail','telephoneNumber','mobile','title','department','company', 'distinguishedName']; # undefdata is for abnormal test.
	

	    for (my $i=2; $i<@ARGV; $i++) {
			my $csl = $ARGV[$i];
			my $dn = "cn=$csl;ou=users;ou=cnasb;ou=cn;dc=ad4;dc=ad;dc=alcatel;dc=com"; # default
			
			# first search his dn
			my $filter = "(sAMAccountName=$csl)";
			$mesg = $ldap->search(base => $ldap_baseDN, filter => $filter, attrs => $items);

			print __LINE__ . ": \$errorMsg = $errorMsg; \$mesg = $mesg\n";

			my @entries0 = $mesg->entries;
			print __LINE__ . ": \@entries0 = @entries0\n";
			
            if ($entries0[0]) {
                $entries0[0]->dump;

                print "=-"x25, "\n";
				$dn = $entries0[0]->get_value("distinguishedName");

				foreach my $item0 (@$items) {
					print "$item0:" . $entries0[0]->get_value($item0) . "\n";
				}

				
            }

			print __LINE__ . ": \$dn = $dn\n";
        }
	}
	$ldap->unbind;  # release gracefully.		
}



