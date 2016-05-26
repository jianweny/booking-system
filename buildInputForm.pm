use strict;
use Encode;
use JSON;
require "jsGenerator.pm";


##################################
# input: config file
# return: json string
##################################
sub getConfigJson {
    my $action = lc($_[0]);
	my $cfgFile = "booking_log/$action.cfg";
      
    ### define basic variables and set default values.
    my $ActivityName = "";
    my @Admins = ();
	my @ActionGroup = ();
    my ($StartTime, $EndTime) = ("", "");
    my ($BookingCount, $QueueCount) = (1000,1000);
    my $Information = "";
    my $Picture = "";
    my @Inputs = ();
    my @ShowWhens = ();
   
    ### get file contents
	open (CFG_FILE, "$cfgFile") || return "";
	my @lines;
	push (@lines, $_) while <CFG_FILE>;
	close CFG_FILE;

	my $oldline ="";
    foreach my $newline (@lines){
	    $newline =~ s/[\r\n]+$//;
		$newline =~ s/\t/ /g;  # \t is not allowed by JSON.
		
		if ($newline =~ /\\$/) {
			$newline =~ s/\\//; # remove \\ at tail.
			$oldline .= $newline;
			next;
		}
		$oldline .= $newline;
		my $line = $oldline;
		$oldline = "";

		#to avoid convert HTML tags, but still keep <br> <b> <u> <i>.
		$line =~ s/\357\274\214/, /g;  # 接受中文逗号
		$line =~ s/([\\])/\//g;  # replace back-slash to normal slash to avoid JSON errors.
		$line =~ s/(["])/''/g;  # replace back-slash to normal slash to avoid JSON errors.
		$line = plain2html($line, "keepSimpleTags");
		
		# for show_when
		my $show_when="";
		if ($line =~ /^(.*)\/\/show_when:(.*)$/i){
			$line = $1;
			$show_when = $2;
		}
		
        if   ($line =~ /^\s*ActivityName\s*:\s*(.*)/i || $line =~ /^\s*ActionName\s*:\s*(.*)/i) {
	        $ActivityName = $1;
	    }
	    elsif($line =~ /^\s*Admins\s*:\s*(.*)/i) {
	        @Admins = split(/[\s,;\/]+/, $1);
	    }
	    elsif($line =~ /^\s*ActionGroup\s*:\s*(.*)/i) {
			my $s = $1;
			$s =~ s/[^\w\-\s,;\/]//g;
	        @ActionGroup = split(/[\s,;\/]+/, $s) if $s;
	    }
	    elsif($line =~ /^\s*StartTime\s*:\s*(.*)/i) { #2016-03-22 12:34:56
	        $StartTime = $1;
	    }
	    elsif($line =~ /^\s*EndTime\s*:\s*(.*)/i) {
	        $EndTime = $1;
	    }
	    elsif($line =~ /^\s*BookingCount\s*:\s*(\d+)/i) { #99
	        $BookingCount = $1;
	    }
	    elsif($line =~ /^\s*QueueCount\s*:\s*(\d+)/i) {
	        $QueueCount = $1;
	    }
	    elsif($line =~ /^\s*Information\s*:\s*(.*)/i) { #text
	        $Information = $1;
	    }
	    elsif($line =~ /^\s*Picture\s*:\s*(.*)/i) { #text
	        $Picture = $1;
	    }
	    elsif($line =~ /^\s*Input\s*:\s*(.*)/i) {
			push (@Inputs, $1);
			push (@ShowWhens, $show_when);
	    }
    }

	### generate Json file.
	my $json = "{\n";
    $json .="\t\"ActivityName\": \"$ActivityName\",\n";

	$json .= "\t\"Admins\":[";
	my $flag = 0;
	foreach my $admin(@Admins) {
		$json .= "," if ($flag++);
	    $json .= "\"$admin\"";
	}
	$json .= "],\n";

	$json .= "\t\"ActionGroup\":[";
	$flag = 0;
	foreach my $act(@ActionGroup) {
		$json .= "," if ($flag++);
	    $json .= "\"$act\"";
	}
	$json .= "],\n";
	
	$json .="\t\"StartTime\": \"$StartTime\",\n";
	$json .="\t\"EndTime\": \"$EndTime\",\n";
	$json .="\t\"BookingCount\": \"$BookingCount\",\n";
	$json .="\t\"QueueCount\": \"$QueueCount\",\n";
	$json .="\t\"Information\": \"$Information\",\n";
	$json .="\t\"Picture\": \"$Picture\",\n";

	$json .= "\t\"Inputs\":[";  # Inputs begins
	$flag = 0;
	foreach my $input(@Inputs) {
		$json .= ",\n        " if ($flag++);
        $json .= "\"$input\"";
	}
	$json .= "],\n";		# Inputs ends

	$json .= "\t\"ShowWhens\":[";   # ShowWhens begins
	$flag = 0;
	foreach my $show(@ShowWhens) {
		$json .= ",\n        " if ($flag++);
        $json .= "\"$show\"";
	}
	$json .= "]\n";  # ShowWhens ends
	
	
	$json .= "}\n";

	#print $json, "\n";
	
	return $json;
}

####################################################
# input: action
# return: (config json obj, errorInfo)
#---------------------------------------------------
sub getConfigJsonObj {
	my ($action) = @_;

	my $cfgJsonStr = getConfigJson($action);
	return (undef, "Opening the config file for '$action' failed!") unless $cfgJsonStr;
	
	my $cfgObj;
	eval { 
		my $json = new JSON;
		$cfgObj = $json->decode($cfgJsonStr);
	};
	return (undef, "Wrong format!\nError code:$@\n") if $@;
	return ($cfgObj, "");
}
	
###################################################
# input:
#        $userInfo: ref of user info array
#        $jsonObj: json obj of config file
#        $bookedData: hash obj of booked record
#        $editable: is editable or not
# return: ($retCfgInfo1, $retCfgInfo2, $retInputForm)
###################################################
sub buildInputForm {
	my ($userInfo, $action, $jsonObj, $bookedData, $editable, $bookedFile) = @_;
	
	my $retInputForm = "";
	
	my $readonly = 0;
	$readonly = 1 if $bookedData;  # if sb has booked, readonly.
	$readonly = 0 if $editable;    # but if editable, same as newly bookable.
	
	my %fakeList = ();
	$bookedData = \%fakeList unless $bookedData; # avoid potential errors.
	
    my $BookingCount = $$jsonObj->{'BookingCount'} || "1000";
	my $QueueCount = $$jsonObj->{'QueueCount'} || "1000";
    my @Inputs = @{$$jsonObj->{'Inputs'}};	

	
	### insert a form for deletion.
	$retInputForm .= "<form name='deleting' id='deleting' method=post action='booking.cgi'>\n";
	$retInputForm .= "<input type=hidden name=action value=\"$action\" />\n";
	$retInputForm .= "<input type=hidden name='tobedeleted'  value='yes' />\n";
	$retInputForm .= "<input type=hidden name='bookedFile'   value='$bookedFile' />\n";
	$retInputForm .= "</form>\n";
    
	### build the form for booking.
	my $formAction = "booking.cgi";
	$formAction = "login.cgi" if ($readonly);
	$retInputForm .= "<form name='booking' id='booking' method=post action=$formAction>\n";

	$retInputForm .= "<input type=hidden name='BookingCount' value=\'$BookingCount\' />\n";
	$retInputForm .= "<input type=hidden name='QueueCount'   value=\'$QueueCount\' />\n";
	$retInputForm .= "<input type=hidden name='bookedFile'   value=\'$bookedFile\' />\n";
			
	foreach my $userInfoKey (sort keys %$userInfo) { 
		$retInputForm .= "<input type=hidden name='$userInfoKey' value=\'".$$userInfo{$userInfoKey}."\' />\n";
	}

    #$retInputForm .= "<tr><th colspan=2></th></tr>\n";

	my $attr = "";
	$attr = " readonly disabled " if $readonly;
	
	### define the index for input fields
	my %paramName2realName;
	my $globalIdx = 100;
	$retInputForm .= "<table class=\"table3\" id=\"table_login_input\">\n";
	foreach my $t (@Inputs) { #Type, Name, param1, param2, param3,…
	    my ($name, $type, @params) = split(/\s*,\s*/, $t);
		if ($name && $type) {
			if (lc($type) eq "subtitle") {
				$retInputForm .= "<tr><th><br /><u>$name:</u></th><td>";
			}else{
				$retInputForm .= "<tr><th>$name:</th><td>";
			}
			if (lc($type) eq "text") {
			    my ($size, $content) = ("", "");
				$size = "size=\"$params[0]\"" if $params[0];
				$content = "value=\"$params[1]\"" if $params[1];
				
				my $inputName = $globalIdx++ . "text";
				$content = "value=\"" . $$bookedData{$inputName} . "\"" if $$bookedData{$inputName};

				$retInputForm .= "<input type=\"text\" name=\"$inputName\" $size $content $attr />";
				$paramName2realName{$inputName} = $name;
			}
			elsif (lc($type) eq "textarea") {
			    my ($rows, $cols, $content) = ("", "", "");
				$rows = "rows=\"$params[0]\"" if $params[0];
				$cols = "cols=\"$params[1]\"" if $params[1];
				$content = $params[2] if $params[2];
				
				my $inputName = $globalIdx++ . "textarea";
				$content = $$bookedData{$inputName} if $$bookedData{$inputName};

				$retInputForm .= "<textarea name=\"$inputName\" $rows $cols $attr>".html2plain($content)."</textarea>";
				$paramName2realName{$inputName} = $name;
			}
			elsif (lc($type) eq "radio") {
				my $inputName = $globalIdx++ . "radio";
				my $localIdx = 0;
			    foreach my $param (@params){
					next if trim($param) eq "";
				    my $checked = "";
				    if ($param =~ /(.+)\s*:\s*(.*)/){
					    $param = $1;
						my $defaultValue = $2;
						unless ($$bookedData{$inputName}) {
							$checked = 'checked="checked"' if $defaultValue;
						}
					}
					if ($$bookedData{$inputName}) {
						$checked = 'checked="checked"' if ($$bookedData{$inputName} eq $param);
					}
					$retInputForm .= "<input type=\"radio\" name=\"$inputName\" $checked value=\"$param\" $attr ".
					                 "id=\"R-$globalIdx-$localIdx\"/><label for=\"R-$globalIdx-$localIdx\">$param</label>   ";
					$localIdx++;
					$paramName2realName{$inputName} = $name;
				}
			}
			elsif (lc($type) eq "checkbox") {
				my $localIdx = 0;
			    foreach my $param (@params){
					next if trim($param) eq "";;
					my $inputName = $globalIdx++ . "checkbox";  # checkbox is diff from radio!!!
				    my $checked = "";
				    if ($param =~ /(.+)\s*:\s*(.*)/){
					    $param = $1;
						my $defaultValue = $2;
						unless ($$bookedData{$inputName}) {
							$checked = 'checked="checked"' if $defaultValue;
						}
					}
					if ($$bookedData{$inputName}) {
					    $checked = 'checked="checked"' if ($$bookedData{$inputName} eq $param);
					}
					$retInputForm .= "<input type=\"checkbox\" name=\"$inputName\" $checked value=\"$param\" $attr ".
					                 "id=\"R-$globalIdx-$localIdx\"/><label for=\"R-$globalIdx-$localIdx\">$param</label>   ";
					$localIdx++;
					$paramName2realName{$inputName} = $name;
				}
			}
			elsif (lc($type) eq "select" || lc($type) eq "select-counted") {
				my $inputName = $globalIdx++ . lc($type);
				$retInputForm .= "<select name=\"$inputName\">\n";
				$paramName2realName{$inputName} = $name;
			    foreach my $param (@params){
					next if trim($param) eq "";
				    my $selected = "";
				    if ($param =~ /(.+)\s*:\s*(1)\s*$/){  ## make it as default if tailed with ":1"
					    $param = $1;
						my $defaultValue = $2;
						unless ($$bookedData{$inputName}) {
							$selected = 'selected="selected"' if $defaultValue;
						}
					}
					if ($$bookedData{$inputName}) {
						$selected = 'selected="selected"' if ($$bookedData{$inputName} eq $param);
					}
					$retInputForm .= "    <option value=\"$param\" $selected $attr >$param</option>\n";
				}
				$retInputForm .= "</select>";
				$retInputForm .= "&nbsp;(计入总人数)" if lc($type) eq "select-counted";
			}

			$retInputForm .= "</td></tr>\n";
		}
	}
	my $lockStatus = (-e "booking_log/$action/__lock__")? "disabled=\"true\"" : "";
	my $comment    = (-e "booking_log/$action/__lock__")? "&nbsp;&nbsp;(报名已经锁定)" : "";
	if ($readonly) {
	    $retInputForm .= "<input type=hidden name=edit value=1 />\n";
		$retInputForm .= "<tr><th colspan=2 class=submit1><input type=\"submit\" value=\"修改\" class=\"submit2\" $lockStatus />".
		                 "&nbsp;"x10 .
		                 "<input type=\"button\" class=\"submit2\" onclick=\"javascript:deleteBooking()\" value=\"撤销\" $lockStatus/>".
						 "<span id=\"comment\">$comment</span></th></tr>\n";
	}else{
	    my $buttonValue = $bookedFile ? "确认修改" : "报名";
		
		$retInputForm .= "<tr><th colspan=2 class=submit1><input type=\"button\" value=\"$buttonValue\" class=\"submit2\" $attr $lockStatus ".
						 "onclick=\"javascript:checkBooking()\"/>".
		                 "<span id=\"comment\">$comment</span></th></tr>\n";
	}
    $retInputForm .= "</table>\n";

	$retInputForm .= "<textarea name=note cols=80 rows=40 readonly class=xxx>{\n";
	
	my $cnt=0;
	foreach my $userInfoKey (sort keys %$userInfo) {
		$retInputForm .= ",\n" if $cnt++;
		$retInputForm .= "  \"$userInfoKey\":\"$userInfoKey\"";
	}
	foreach my $k (sort keys(%paramName2realName)) {
		$retInputForm .= ",\n  \"$k\":\"$paramName2realName{$k}\"";
	}
	$retInputForm .= "\n}\n</textarea>\n";

	$retInputForm .= "<input type=hidden name=action value=\"$action\" />\n";
	
	$retInputForm .= "</form>\n";
	
	### add javascript for show_when feature.
	my @ShowWhens = @{$$jsonObj->{'ShowWhens'}};	
	$retInputForm .= jsGen4ShowWhen(\@ShowWhens);
	
	return $retInputForm;
}


sub getBookedInfo {
	my ($file, $cfgObj) = @_;
	
    my $jsonData = "";
	open (BOOKEDFILE, "$file") || return (0,0,0);
	$jsonData .= $_ while (<BOOKEDFILE>);
	close BOOKEDFILE;
	
	my $json = new JSON;
	my $jsonObj;
	eval { 
		$jsonObj = $json->decode($jsonData);
	};
	
	warn $@ if $@;
	return (0,0,0) if ($@);

	my %newDb = dataMigration($cfgObj, \$jsonObj);
		
	my $noteRow = "";
	my $totalCnt = 1; #at least 1, including himself.
	my %noteHash = getCfgNote($cfgObj);
	foreach my $key(sort keys %noteHash) { 
		# convert "000csl-000csl" to "000-csl"
		my $key2 = substr($key,0,3);
		my $value = $noteHash{$key};
		if ($value =~ /^0\d\d(.*)/) {
			$value = uc($1);
		}
		$noteRow .= "</th><th>" . $key2 . '-' . $value;
	}
	
	my $dataRow = "";
	foreach my $key(sort keys %noteHash) {
	
		$dataRow .= "</td><td>";
		
		my $data = $newDb{$key};
		if (defined $data){   # "0" or "" is also valid.
			# count numbers 
			if ($key =~ /\d{3}select\-counted/) {
				$totalCnt += $data if ($data =~ /^[+\-]?[\d\.]+$/);
			}

			# for excel digit handling
			if ($data =~ /^\s*[\+\-]?([\d\.][\d\. ]+[\d\.])\s*$/) {
				if (length($1)>5) {
					$data = "'$data";
				}
			}
			$dataRow .= $data;
		}
		###$dataRow .= $jsonObj->{$key} if $jsonObj->{$key};
	}
	$dataRow =~ s/,$//;
	
	return ($noteRow, $dataRow, $totalCnt);
}

sub checkBookingType{
	my ($action, $BookingCount, $QueueCount) = @_;
	
	my @date_bookers;
	my $bookedCnt = getBookingList($action, \@date_bookers);
			
	my $type = "NOK";
	if ($bookedCnt < $BookingCount) {
		$type = "Booked";
	}elsif ($bookedCnt < ($BookingCount + $QueueCount)) {
		$type = "Queued";
	}
	return $type;
}

sub getBookingList {
	my ($action, $date_bookers) = @_;
	
	### list booking records.
	# 1. one booker one line, the newest file only.
	my $path = "booking_log/$action/";
	my $bookedFiles = `ls -1 $path*.book 2>/dev/null`;
	my %dates;
	foreach my $file(split(/[\r\n]+/, $bookedFiles)){
		$file =~ s/^$path//;
		if ($file =~ /^(\w{2,8})_(\d\d\d\d\-\d\d\-\d\d_\d\d:\d\d:\d\d)/) { # should be {2,8}. shortest name like "qc"
			my $booker = $1;
			my $date = $2;
			if ($dates{$booker}) { # only record the newest booking.
				#print __LINE__, "\n";
				$dates{$booker} = $date if ($dates{$booker} lt $date);
			}else{
				$dates{$booker} = $date;
			}
		}
	}
	# 2. put date _ booker into an array
	foreach my $bk (keys %dates) {
		push (@$date_bookers, $dates{$bk}.' '.$bk);  #  "2016-04-06_13:28:29 meilingp"
	}
	# 3. sort
	@$date_bookers = sort @$date_bookers;
	
	# 4. count total people numbers by open each valid one by one.
	my $totalPeople = 0;
	my $json = new JSON;
	my $jsonObj;
	my ($cfgObj, $errorInfo) = getConfigJsonObj($action);
	foreach my $date_booker (@$date_bookers) {
		$totalPeople++;
		my @a = split(' ', $date_booker);
		my $file = $a[1] . '_' . $a[0] . '.book'; # "13:28:29 meilingp_2016-04-06.book"
		if (open (BOOKEDFILE,  $path . $file)) {
			my $jsonStr = "";
			$jsonStr .= $_ while (<BOOKEDFILE>);
			close (BOOKEDFILE);

			eval { 
				$jsonObj = $json->decode($jsonStr);
			};
			next if $@;

			if ($cfgObj) {
				my %newDb = dataMigration(\$cfgObj, \$jsonObj); # data migration to use latest cfg obj.
				
				foreach my $key(sort keys %newDb) {
					if ($key =~ /^\d\d\dselect\-counted$/) {  # add other people number.
						$totalPeople += $newDb{$key} if ($newDb{$key} && ($newDb{$key} =~ /^[+\-]?[\d\.]+$/)); 
					}
				}
			}
		}else{
			print STDERR "Error: $@";
		}
	}
	return $totalPeople;
}

###########################################
# return config info table 1 & table 2
# table1: general introduction of the action
# table2: administrative info
# ----------------------------------------
sub buildCfgHtmlTable {
	my ($jsonObj, $action) = @_;
	
	### define basic variables and set default values.
    my $ActivityName = $$jsonObj->{'ActivityName'} || "";
    my @Admins = @{$$jsonObj->{'Admins'}};
    my @ActionGroup = @{$$jsonObj->{'ActionGroup'}};
    my $StartTime = $$jsonObj->{'StartTime'} || "0";
	my $EndTime = $$jsonObj->{'EndTime'} || "0";
    my $BookingCount = $$jsonObj->{'BookingCount'} || "1000000";
	my $QueueCount = $$jsonObj->{'QueueCount'} || "0";
    my $Information = $$jsonObj->{'Information'};
    my $Picture = $$jsonObj->{'Picture'} || "";
    my @Inputs = @{$$jsonObj->{'Inputs'}};	

	my $adminStr = "";
	foreach my $a (@Admins) {
		$adminStr .= "$a, ";
	}
	$adminStr =~ s/, $//;

	my $ActionGroup = "";
	foreach my $a (@ActionGroup) {
		$ActionGroup .= "<a href=\"login.cgi?action=$a\">$a</a>, ";
	}
	$ActionGroup =~ s/, $//;


	if ($StartTime) {
		if ($StartTime !~ /^\d\d\d\d\-\d\d\-\d\d +\d\d:\d\d:\d\d/) {
			$StartTime .= "格式错误，必须类似2016-02-22 10:30:00";
		}
	}
	if ($EndTime) {
		if ($EndTime !~ /^\d\d\d\d\-\d\d\-\d\d +\d\d:\d\d:\d\d/) {
			$EndTime .= "格式错误，必须类似2016-02-22 10:30:00";
		}
	}
	if ($StartTime gt $EndTime) {
		$StartTime .= "<br>致命错误：起始时间晚于结束时间！";
	}
	
	## calculate people numbers
	my @bookers;
	my $totalPeople = getBookingList($action, \@bookers);
	my $staffCount = scalar(@bookers);
	
	## find a latest picture.
	#my $Picture = `ls -1art booking_log/$action/$action.[pjg][npi][gf] 2>/dev/null | tail -1`;
	#chop($Picture);
	
	# check the picture. If the picture is save-as-ed from other action, make a hard link here and return own path.
	if ($Picture) {
		if (-e "booking_log/$Picture"){
			if ($Picture !~ /^$action/ && $action ne '__preview__') { # not match? now own
				my $ownPic = $Picture;
				$ownPic =~ s/^(.*\/)/$action\//;
				mkdir("booking_log/$action");
				my $cmd = "ln booking_log/$Picture booking_log/$ownPic";
				`$cmd`;
				if (-e "booking_log/$ownPic") {
					$Picture = $ownPic;
				}
			}
		}
		$Picture = "<img src=\"dump.cgi/booking_log/$Picture\" id=\"action_picture\" >" if $Picture;
	}
	
    ### generate HTML texts
	my $retCfgInfo1 = "<table class=\"table5\">\n";
    $retCfgInfo1 .= "<tr><td colspan=2 align=\"center\"><h1>$ActivityName</h1></td></tr>";
	$retCfgInfo1 .= "<tr><td colspan=2 class=\"ActionInfo\">$Information</td></tr>\n";
	$retCfgInfo1 .= "<tr><td colspan=2 align=\"center\" id=\"preview_picture\">$Picture</td></tr>\n" if $Picture; 
	$retCfgInfo1 .= "</table>\n";
	
	my $retCfgInfo2 .= "<table class=\"table2\">\n";
	$retCfgInfo2 .= "<tr><th>管理员账号:</th><td>$adminStr</td></tr>\n";
	$retCfgInfo2 .= "<tr><th>报名开始时间:</th><td>$StartTime</td></tr>\n" if $StartTime;
	$retCfgInfo2 .= "<tr><th>报名截止时间:</th><td>$EndTime</td></tr>\n" if $EndTime;
	$retCfgInfo2 .= "<tr><th>允许报名人数</remark>:</th><td>$BookingCount</td></tr>\n";
	$retCfgInfo2 .= "<tr><th>允许候选人数:</th><td>$QueueCount</td></tr>\n";
	$retCfgInfo2 .= "<tr><th>已报名员工数:</th><td>$staffCount</td></tr>\n";
	$retCfgInfo2 .= "<tr><th>已报名总人数:</th><td>$totalPeople</td></tr>\n";
	$retCfgInfo2 .= "<tr><th>关联报名项目:</th><td>$ActionGroup</td></tr>\n" if $ActionGroup;
	$retCfgInfo2 .= "</table>\n";

	return ($retCfgInfo1, $retCfgInfo2);
}
	

	
sub isAdmin {
	my ($cfgObj, $user) = @_;
	my @admins = @{$$cfgObj->{"Admins"}};
	foreach my $admin (@admins) {
		if (lc($user) eq lc($admin)) {
			return 1;
		}
	}
	return 0;
}


####################################################
# return config json string for parse on client
#---------------------------------------------------
sub checkAdmin {
	my ($user, $action, $isNew) = @_;

	my $json = new JSON;
	my $cfgObj;

	my $cfgJsonStr = getConfigJson($action);
	eval { 
			$cfgObj = $json->decode($cfgJsonStr);
	};
	return (0, "Wrong format!\nError code:$@\n") if $@;

	if (scalar(@{$cfgObj->{"Admins"}}) == 0 && 
		scalar(@{$cfgObj->{"Inputs"}}) == 0 && 
			$cfgObj->{"ActivityName"} eq "") {
			return (0, "The uploaded file is not a valid config file!");
	}
	
	#printDebug (__LINE__ . ": \$cfgJsonStr = $cfgJsonStr<br>");
	
	my $isAdmin = isAdmin(\$cfgObj, $user);
	unless ($isAdmin) {
			if ($isNew) {
					return (0, "Failed! you must be one of the Admins!\n");
			}else{
					return (0, "Sorry, the booking activity \"$action\" already uploaded by others. Please use another name.\n");
			}
	}
	
	return (1, $cfgJsonStr, $cfgObj->{"ActivityName"});
}


############################################################
#
# new cfg:                  old data:
#   101text: item_new,        101text: value_1
#   102text: item_1,          102text: value_2
#   103radio: item_2
#                              note: { 101text: item_1,
#                                      102radio: item_2 }
#
# ==> dataMigrating("item_1") = value_1
# ==> dataMigrating("item_2") = value_2
#
#------------------------------------------------------------

sub dataMigration {
	my ($cfgObj, $bookedObj) = @_;

	my %newDb;

	my %userInfo = userInfo();
	foreach my $userInfo (sort keys(%userInfo)){
		foreach my $userKey (keys %{$$bookedObj}) {
			my ($k0, $k1) = ($userInfo, $userKey);
			$k0 =~ s/^0\d\d(\S+)$/0xx$1/;
			$k1 =~ s/^0\d\d(\S+)$/0xx$1/;
			if (lc($k0) eq lc($k1)) {
				$newDb{$userInfo} = $$bookedObj->{$userKey};
			}
		}
	}

	my $globalIdx = 100;
    my @Inputs = @{$$cfgObj->{'Inputs'}};	
    foreach my $t (@Inputs) { #Type, Name, param1, param2, param3,…
	    my ($name, $type, @params) = split(/\s*,\s*/, $t);
		if ($name && $type) {
			$type = lc($type);
			if ($type eq "text" || 
			    $type eq "radio" ||
				$type eq "select" ||
				$type eq "select-counted" ) 
			{
				my $inputName = $globalIdx++ . $type;

				foreach my $k (keys %{$$bookedObj->{"note"}}) {
					if ($$bookedObj->{"note"}->{$k} eq $name) {
						$newDb{$inputName} = $$bookedObj->{$k};
					}
				}
			}elsif ($type eq "checkbox"){
				my @oldValues;
				my $i=0;
				foreach  my $k (sort keys %{$$bookedObj->{"note"}}) {
					if ($$bookedObj->{"note"}->{$k} eq $name) {
						if ($$bookedObj->{$k}){
							$oldValues[$i] = $$bookedObj->{$k};
							#print STDERR "\$oldValues[$i] = '$oldValues[$i]'\n";
						}
						$i++;
					}
				}
				#print STDERR "\@oldValues = '@oldValues'\n";
				my $localIdx = 0;
			    foreach my $param (@params){
					next if trim($param) eq "";
					my $inputName = $globalIdx++ . $type; 
					if ($oldValues[$localIdx]) {
						$newDb{$inputName} = $oldValues[$localIdx];
						#print STDERR "\$localIdx = $localIdx; \$inputName = $inputName; v=".  $oldValues[$localIdx] . "\n";
					}
					$localIdx++;
				}
			}
		}
	}
	return %newDb;
}
#############################################################
# return new note hash
#------------------------------------------------------------
sub getCfgNote {
	my ($cfgObj) = @_;
	my %cfgNote;
	
	my %userInfo = userInfo();
	my @userInfo = sort keys(%userInfo);
	foreach my $userInfo (@userInfo){
		$cfgNote{$userInfo} = $userInfo;
	}

	my $globalIdx = 100;
    my @Inputs = @{$$cfgObj->{'Inputs'}};	
    foreach my $t (@Inputs) { #Type, Name, param1, param2, param3,…
	    my ($name, $type, @params) = split(/\s*,\s*/, $t);
		if ($name && $type) {
			$type = lc($type);
			if ($type eq "text" || 
			    $type eq "radio" ||
				$type eq "select" ||
				$type eq "select-counted" ) 
			{
				my $inputName = $globalIdx++ . $type;
				$cfgNote{$inputName} = $name;
			}
			elsif ($type eq "checkbox"){
			    foreach my $param (@params){
					next if trim($param) eq "";
					my $inputName = $globalIdx++ . $type; 
					$cfgNote{$inputName} = $name;
				}
			}
		}
	}
	return %cfgNote;
}

1;