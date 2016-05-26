my %keyTitles = (
				"---action_code"   => ["a", "aaa"],
				"00-ActivityName"  => ["b", "bbb"],
				"08-Information"   => ["c", "ccc"]);

foreach my $keyTitle (sort keys %keyTitles){
	my $attr_name = $keyTitle;
	$attr_name =~ s/^\d\d\-//;
	$attr_name = "name=\"$attr_name\"";

	my ($item,$remark) = @($keyTitles{$keyTitle});

	if ($keyTitle =~ /^08/) {
		print "<tr><th>$item:</th><td><textarea rows=\"5\" cols=\"40\" class=\"cfg\" $attr_name></textarea>$remark</td><tr>\n";
	}else{
		print "<tr><th>$item:</th><td><input type=\"text\" class=\"cfg\" $attr_name>$remark</td><tr>\n";
	}
}
