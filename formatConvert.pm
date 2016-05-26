use strict;

#-------------------------------------------
# global variables
#-------------------------------------------
sub basedir {
	"booking_log";
}

sub userInfo {
	my @userInfo = @_;
	my $i;
	for ($i=0; $i<20; $i++){
		$userInfo[$i] = "" unless $userInfo[$i];
	}
	$i=0;
	('000csl'  =>$userInfo[$i++], '001cil'  =>$userInfo[$i++], '002upi'   =>$userInfo[$i++], '003dept'   =>$userInfo[$i++],
	 '004email'=>$userInfo[$i++], '005phone'=>$userInfo[$i++], '006mobile'=>$userInfo[$i++], '007empType'=>$userInfo[$i++]);
}

sub getPersonalInfoTable {
	my ($info) = @_;
	my ($cil, $img, $dept, $email, $phone, $mobile, $upi) = get_personal_info($info);
	my $empType = "...";
	my $pInfoTab = <<__PTAB;
	<table class="table2">
		<tr><th>CIL:</th>     <td>$cil</td></tr> 
		<tr><th>工号:</th>    <td>$upi</td></tr>
		<tr><th>部门:</th>    <td>$dept</td></tr>
		<tr><th>电子邮件:</th><td>$email</td></tr>
		<tr><th>分机:</th>    <td>$phone</td></tr>
		<tr><th>移动电话:</th><td>$mobile</td></tr>
		<tr><th>员工类型:</th><td id="empType">$empType</td></tr>
<script>
	var personInfo = {'cil':'$cil', 'upi':'$upi', 'dept':'$dept', 'email':'$email', 
	                  'phone':'$phone', 'mobile':'$mobile'};

    \$(document).ready(function(){
		// load personal info

		\$.get("upi2info.cgi",
			{
			  upi: "$upi",
			  name: "User Type"
			},
			function(data,status){
				if(status == "error") {
					return false;
				}else{
					data = data.replace(/[\\r\\n]/g, '').replace(/"/g, "\\\"");
					\$("#empType").html(data);
					\$("input[name='007empType']").val(data);
				}
			}
		)
	});
</script>		
	</table>
__PTAB
	return $pInfoTab;
}


#-------------------------------------------
# global functions
#-------------------------------------------
sub plain2html {
	my ($in, $keepSimpleTags) = @_;
	$in =~ s/&/&amp;/g;
	$in =~ s/</&lt;/g;
	$in =~ s/>/&gt;/g;
	$in =~ s/"/&quot;/g;
	$in =~ s/\r?\n/<br>/g;
	
	if ($keepSimpleTags){
		$in =~ s/&lt;(\/?[bui])&gt;/<$1>/ig;
		$in =~ s/&lt;(br\s*\/?)&gt;/<$1>/ig;
		$in =~ s/&lt;(\/?h[1-5r])&gt;/<$1>/ig;
	}
	
	return $in;
}

sub html2plain {
	my $in = $_[0];
	$in =~ s/<br>/\n/g;
	$in =~ s/&quot;/"/g;
	$in =~ s/&lt;/</g;
	$in =~ s/&gt;/>/g;
	$in =~ s/&amp;/&/g;
	return $in;
}

sub trim {
	my $in = $_[0];
	$in =~ s/^\s+//;
	$in =~ s/\s+$//;
	return $in;
}

sub printHtmlHeader {
	my $title = $_[0] || "Booking System";
	my $noBanner = $_[1];

	#-----------------------------------------------------------------
	# first line for CGI. must be ended with 2 <NL>, very critical !!!
	print "Content-type: text/html; charset=utf-8\n\n";
	#print $cgi->header();
	#-----------------------------------------------------------------

	print <<__HEAD;
<html>
<head>
<meta charset="UTF-8">
	<title>$title</title>
	<link rel="stylesheet" type="text/css" href="dump.cgi/booking.css" />
	<script src="dump.cgi/jquery-1.12.3.js"></script>
	<script type="text/javascript" src="dump.cgi/booking.js"> </script>
</head>

<body>	
__HEAD

	return if $noBanner;
	
	print <<__BANNER;
	<div id="banner">
	<img style="padding:0px; margin:0px;" src="dump.cgi/logos.png" border="0" height="60px" width="725px" id="bannerImg"><br>
	<img style="padding:0px; margin:0px;" src="dump.cgi/spacer.png" border="0" height="8px" width="100%" id="spacer">
	</div>
__BANNER
}

sub printHtmlFooter {
	print "<div id=\"footer\">";
	print @_;
	print "<hr>\n";
	
	# related links
	my $helpLink = '<a href="admin.cgi">我也要创建活动报名！</a>';
	print "$helpLink | ";

	print "<a href=http://172.24.208.168/>公司内网首页</a> | ";
	print "<a href=http://172.24.208.168/Default.aspx?alias=172.24.208.168/lbucn>工会首页</a> ";
	
	print "</div>\n";
	
	print "</body>\n</html>\n\n";
}

sub printLogonEntry {
	my ($action, $user, $loginInfo) = @_;
	
	$action = "" unless $action;
	$user = "" unless $user;
	$loginInfo = "" unless $loginInfo;
	
	$user = lc($user);
	
	print "<table class=\"table2\">\n";
    if ($user) {
        print "<tr><th></th><td><br><br><br><br>\n".
		      "<font color=red>*** <b>$user</b> login failed! ***</font></td></tr>\n";
    }

    if ($loginInfo && $loginInfo ne "OK") {
        print "<tr><th colspan=2><span class=xxx><br><br>\n".
		      "<font color=red>*** Error $loginInfo , please retry! ***</font></span></th></tr>\n";
    }
	
	my $requrl = $ENV{"REQUEST_URI"} || "";
	$requrl =~ s/logout=1/logout=0/;

    print <<__END;

<form method="POST" action="validate.cgi">
<tr><th>            </th><td> <h3>Please login</h3>                      </td></tr>
<tr><th>AD4 account:</th><td> <input type=text name=user value='$user' /></td></tr>
<tr><th>   password:</th><td> <input type=password name=pass />          </td></tr>
<tr><th>            </th><td><input type="submit" value="Login">         </td></tr>
<input type=hidden name=action value="$action" />
<input type=hidden name=requrl value="$requrl" />
</form>
</table>

__END
	
}


sub get_personal_info {
	my $info = $_[0];
	my $json = new JSON;
	my ($cil, $img, $dept, $email, $phone, $mobile, $upi) = ("","","","","","","");
	my $infoObj;
	eval {
		$infoObj = $json->decode($info);
	};
	unless ($@) {
		$cil = $infoObj->{"alcatel-CIL"};
		$upi = $infoObj->{"alcatel-UPI"};
		$email = $infoObj->{"mail"};
		$dept = $infoObj->{"department"};
		$phone = $infoObj->{"telephoneNumber"};
		$mobile = $infoObj->{"mobile"};
	}
	return ($cil, $img, $dept, $email, $phone, $mobile, $upi);
}


sub printError{
	print "<h3 class=\"error\">", @_, "</h3><br>";
}

sub printDebug{
	print "<span class=\"xxx\">", @_, "</span><br>";
}

1;
