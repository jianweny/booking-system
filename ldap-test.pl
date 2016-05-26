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
my $ldap_bind = "cn=$user;ou=users;ou=cnasb;ou=cn;dc=ad4;dc=ad;dc=alcatel;dc=com";
my $ldap_baseDN = 'dc=ad4,dc=ad,dc=alcatel,dc=com';


#ldap_searches
my @ldap_searches = ("cn=<USER>;ou=users;ou=cnasb;ou=cn;dc=ad4;dc=ad;dc=alcatel;dc=com",
					 "cn=<USER>;ou=users;ou=cnluc;ou=cn;dc=ad4;dc=ad;dc=alcatel;dc=com",
					 "cn=<USER>;ou=users;ou=cnabs;ou=cn;dc=ad4;dc=ad;dc=alcatel;dc=com",
                                         "CN=<USER>,OU=Users,OU=CNSHA,OU=CN,DC=ad4,DC=ad,DC=alcatel,DC=com");

#@ldap_searches = ("<USER>\@ad4.ad.alcatel.com");

my $errorMsg = "Login failed!";

my $ldap = Net::LDAP->new($ldap_host);
if ($ldap) {
	my $mesg = $ldap->bind($ldap_bind, password => $pass);
       # my $mesg = $ldap->bind($ldap_baseDN);
	$errorMsg = $mesg->is_error(); 
	
	print "\$errorMsg = $errorMsg\n";
	
	if ($mesg){	

		my $items = ['alcatel-CIL','alcatel-UPI','mail','telephoneNumber','mobile','title','department','company', 'distinguishedName']; # undefdata is for abnormal test.
	

	    for (my $i=2; $i<@ARGV; $i++) {
			my $csl = $ARGV[$i];
			#print "\$i=$i; \$csl=$csl\n";

			my $found = 0;
			my $oc = 'organizationalPerson';
			foreach my $ldap_search(@ldap_searches) {
                                #print __LINE__ . ": \$i=$i; \$csl=$csl\n";
				my $ldap_search2 = $ldap_search;
				$ldap_search2 =~ s/<USER>/$csl/;
				print "\$ldap_search2 = '$ldap_search2'\n";
				$mesg = $ldap->search(base => "$ldap_search2", filter => "(objectClass=$oc)", 
										attrs => $items );
				
				my @entries = $mesg->entries;
				
				if ($entries[0]) {
					$entries[0]->dump; 

					print "="x50, "\n";
					
					my $jsonStr = "{";
					my $i=0;
					foreach my $item (@$items) {
		#				print "$item:" . $entries[0]->get_value($item) . "\n";
						$jsonStr .= "," if ($i++);
						$jsonStr .= "\n    \"$item\":\"" . $entries[0]->get_value($item) . "\"";
					}
					$jsonStr .= "\n}\n";
							
					#print "\$jsonStr = $jsonStr\n";
					$found = 1;
					last;
				}
			}
			unless ($found){
				print "$csl not found!\n";
			}
		}
	}
	$ldap->unbind;  # release gracefully.		
}



