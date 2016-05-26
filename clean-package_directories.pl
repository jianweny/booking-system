#!/usr/bin/perl -w
use strict;
use Encode;
use JSON;
use Date::Calc qw(Mktime);
use Data::Dumper;

my $json = new JSON;
my $timeNow = `date +%Y-%m-%d_%H:%M:%S`;
chop($timeNow);

my $path = '/repo/builder/buildme_request_log/';

my $allReqFiles = `cd $path; ls -1 `;
my @allReqFiles = split(/[\r\n]+/, $allReqFiles);

#print __LINE__, ": $allReqFiles\n";

foreach my $file (@allReqFiles){
#	print "-"x80, "\n";
	
#	print __LINE__, ": \$file = $file\n";

	### get file contents
	open (REQ_FILE, "$path/$file") || next;
	my $info = "";
	$info .= $_ while <REQ_FILE>;
	close REQ_FILE;

#	print __LINE__, ": \$info = $info\n";

	### decode json file.
	my $infoObj;
	eval {
		$infoObj = $json->decode($info);
	};
	if ($@) {
#		print STDERR "Error while reading $file: $@\n";
		next;
	}
	
	my $machine_address = $infoObj->{"machine_address"};
	my $filename = $infoObj->{"filename"};
#	my $package_dir = $infoObj->{"package_dir"}; # this is a tmp dir controlled by buildmgr.

=type:
	"build_type_info": {
        "package": {
            "target_directory": "/repo2/yli097/"
        }
    }, 	
=cut
	my $target_directory = $infoObj->{"build_type_info"}->{"package"}->{"target_directory"};
	my $build_id = $infoObj->{"build_id"};
	my $release = $infoObj->{"release"};
	
	
	unless ($target_directory) {
#		print "No target_directory found in $file. \n";
		next;
	}
	
#	print __LINE__, ": (\$filename, \$timeNow) = ($filename, $timeNow)\n";
	my $days = get_time_diff_sec($filename, $timeNow) / 24 / 3600;
	
	next if $days < 30;  # do not clean dir old than 1 month.
#	print __LINE__, ": \$days = $days\n";
	
	my $package_dir = "$target_directory/pack_$release.$build_id";
	if ($package_dir !~ /^\//) {
		print STDERR "Error: $filename with wrong path '$package_dir'\n";

	}else {
###		the following check is wrong. the local disks are missing.
#		unless (-e $package_dir) {
#			print "package_dir ($package_dir) not existing!\n";
#			next;
#		}
	
		print "-"x80, "\n";
		print __LINE__, ": (\$filename, \$timeNow) = ($filename, $timeNow)\n";

		my $cmd = "find $target_directory -maxdepth 1 -mtime +30 -name pack_$release.$build_id | xargs rm -rf";

		if ($package_dir =~ /^\/repo[123]\// || $package_dir =~ /^\/home\//) {	
			print "to be removed: $package_dir\n";
	#		`/bin/rm -rf $package_dir 2>/dev/null`;
	#		$cmd = "ls -ld $package_dir";
		}else{
			print "to be removed: $machine_address:$package_dir\n";
	#		`ssh $machine_address /bin/rm -rf $package_dir 2>/dev/null`;
			$cmd = "ssh $machine_address \"$cmd\"";
		}
		print "\$cmd = $cmd\n";
		my $out = `$cmd`;
		print $out, "\n";
	}
}

exit 0;

#------------------------------------------------------------------------------------

sub get_time_diff_sec {  
    #print @_;
    
	# e.g. 2015-10-19_16:46:03.518998
    my $t1 = time_str2sec ($_[0]);
    my $t2 = time_str2sec ($_[1]);
    #print "\n\n";
    
    if ($t1 < 0) {return 0;}
    if ($t2 < 0) {return 0;}
    
    return $t2 - $t1;
}

#------------------------------------------------------------------------------------

sub time_str2sec {
	# e.g. 2015-10-19_16:46:03.518998
    my $str = $_[0];
    my $s = -1;
    if ($str =~ /^(\d\d\d\d)\-(\d\d)\-(\d\d)[\._\- ](\d\d):(\d\d):(\d\d)/) {
        $s = Mktime($1, $2, $3, $4, $5, $6);
    }else{
		print STDERR "Wrong time stamp: $str\n";
	}
    $s;
}


