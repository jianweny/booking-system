#!/usr/bin/perl
use strict;

use Net::LDAP;
use Encode;
use JSON;


### get parameters
my $user = 'jianweny';
my $pass = 'w37/ware';

### use the user+pass to bind AD server
my $ldap_host = "ad4.ad.alcatel.com";
my $ldap_bind = "cn=$user;ou=users;ou=cnasb;ou=cn;dc=ad4;dc=ad;dc=alcatel;dc=com";

my $errorMsg = "Login failed!";

my $ldap = Net::LDAP->new($ldap_host);
if ($ldap) {
	my $mesg = $ldap->bind($ldap_bind, password => $pass);
	$errorMsg = $mesg->is_error(); 
	
	print "\$errorMsg = $errorMsg\n";
	
	if ($mesg){	

		my $items = ['alcatel-CIL','alcatel-UPI','mail','telephoneNumber','mobile','title','department','company', 'undefdata'];
		
		$mesg = $ldap->search(base => "$ldap_bind", filter => "(objectClass=organizationalPerson)", 
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
				$jsonStr .= "\n'$item':'" . $entries[0]->get_value($item) . "'";
			}
			$jsonStr .= "\n}\n";
					
			print "\$jsonStr = $jsonStr\n";

		}
	}
	$ldap->unbind;  # release gracefully.		
}


=basic info
                alcatel-CIL: Jianwen YAO
                alcatel-UPI: CV0003083
                       mail: Jianwen.Yao@alcatel-sbell.com.cn
            telephoneNumber: +86 21 38436156 (2712 6156)
                     mobile: 8618616387201
					  title: Fixed Protocol DEV Manager
				 department: FNBBABU
                    company: Alcatel-Lucent Shanghai Bell
					
					
# OO-interface
 
$json = JSON->new->allow_nonref;
 
$json_text   = $json->encode( $perl_scalar );
$perl_scalar = $json->decode( $json_text );

=cut
	
				
