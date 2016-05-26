use strict;
use LWP::Simple;
use HTML::TreeBuilder::XPath;
use Data::Dumper;

sub csl2info {
    my $csl = $_[0];
    my $url = "http://directory.app.alcatel-lucent.com/S?S=uid=$csl";
    my $html = get( $url );
    my $tree = new HTML::TreeBuilder::XPath;
    $tree->parse( $html );
    $tree->eof;
    #$tree->dump;
    my $cil = xpath2str ($tree, '/html/body/div/div[7]/div/h2');
    my $img = xpath2str ($tree, '/html/body/div/div[7]/div/div[2]/div/div/div/div[2]/div[1]/div/div/img', 1);
	my $email = xpath2str($tree, '/html/body/div/div[7]/div/div[2]/div/div/div/div[2]/div[2]/div[2]/a');
    unless($email =~ /\w\@\w/) {
       $email = xpath2str($tree, '/html/body/div/div[7]/div/div[2]/div/div/div/div[2]/div[3]/div[2]/a');
    }
    my $phone = xpath2str($tree, '/html/body/div/div[7]/div/div[2]/div/div/div/div[1]/div[2]/div[2]/span');
    my $mobile = xpath2str($tree, '/html/body/div/div[7]/div/div[2]/div/div/div/div[1]/div[3]/div[2]/span');
	
    my $upi_str = xpath2str($tree, '/html/body/div/div[7]/div/div[2]/div/div/div/div[2]/div[5]/div[1]');
    my $upi = xpath2str($tree, '/html/body/div/div[7]/div/div[2]/div/div/div/div[2]/div[5]/div[2]');
    if ($upi_str !~ /UPI/i) {
        $upi = xpath2str($tree, '/html/body/div/div[7]/div/div[2]/div/div/div/div[2]/div[6]/div[2]');
    }
	
    return ($cil, $img, $email, $phone, $mobile, $upi);
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

1;

