#!/usr/bin/perl -w
use strict;
use CGI;
use CGI::Session;
use LWP::Simple;
use HTML::TreeBuilder::XPath;
#use Data::Dumper;

print "Content-type: text/html; charset=utf-8\n\n";

my $cgi = new CGI;
my $upi = $cgi->param("upi");
my $name = $cgi->param("name");

my $pInfo = upi2info($upi);

my @person_items = ($pInfo =~ m|<div class="person_attr_name">.*?</div><div class="person_attr_value">.*?</div>|ig);
foreach my $person_item(@person_items){
	if ($person_item =~ m|<div class="person_attr_name">(.*?)</div><div class="person_attr_value">(.*?)</div>|ig) {
		my $attr_name = $1;
		my $attr_value = $2;
		if ($attr_name =~ /$name/i){
			print "$attr_value\n";
			last;
		}
	}
}

exit 0;

sub upi2info {
    my $upi = $_[0];
    my $url = "http://directory.app.alcatel-lucent.com/S?S=upi=$upi";
    my $html = get( $url );
    my $tree = new HTML::TreeBuilder::XPath;
    $tree->parse( $html );
    $tree->eof;
    #$tree->dump;
	
	my $person_col = xpath2str($tree, '/html/body/div/div[7]/div/div[2]/div/div/div/div[2]', 1); 

    return ($person_col);
}

sub xpath2str {
    my ($tree, $xpath, $asHtml) = @_;
    my $items = $tree->findnodes( $xpath );
    my $str = '';
    eval{
        my @items = $items->get_nodelist(); 
        if ($asHtml) {
            $str = $items[0]->as_HTML();
        }else{
            $str  = $items[0]->content->[0]; 
        }
    };
    return $str;
}

