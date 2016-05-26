#!/usr/bin/perl -w
use strict;
use CGI;
use CGI::Session;
use Encode;
use JSON;

#require "csl2info.pm";
require "formatConvert.pm";
require "buildInputForm.pm";

my $cgi = new CGI;
my $logout = $cgi->param("logout");
my $action = lc($cgi->param("action") || "");

my $session = new CGI::Session("driver:File", $cgi ,{Directory=>'/tmp'});
my $user  = $session->param("f_name");
my $login = $session->param("f_login");
my $info  = $session->param("f_info") || "";
$action = $session->param("f_action") unless $action;

my $json = new JSON;

printHtmlHeader();

if ($logout) {
    $user = "";
    $session->delete();
}

if ($user && $login eq 'OK') {
	my ($cil, $img, $dept, $email, $phone, $mobile, $upi) = get_personal_info($info);
	my $empType = "wait...";
	my %userInfo = userInfo($user,$cil,$upi,$dept,$email,$phone,$mobile, $empType);
    
	my $adminLinks = "";
	my $errorInfo="";
	my $bookingStatus="";
	my ($retCfgInfo1, $retCfgInfo2, $retInputForm) = ("","");
    if ($action) {
		### 1. get config info.
#		my $cfgJsonStr = getConfigJson($action);
		my ($cfgObj, $retStr) = getConfigJsonObj($action);
#		if ($cfgJsonStr) {
#			eval { 
#				$cfgObj = $json->decode($cfgJsonStr);
#			};
#			unless ($@) {
			if ($cfgObj) {
				# get action info
				($retCfgInfo1, $retCfgInfo2) = buildCfgHtmlTable(\$cfgObj, $action);

				### 2. get sb's booking info.
				my $cmd = "ls -1 booking_log/$action/$user" . "_*.book  2>/dev/null | tail -1"; # do NOT use $user*.book, it mixed "ronghu" & "ronghuax"!!!
				my $bookedFile = `$cmd`;
				chop($bookedFile);
				my $bookedObj;
				if ($bookedFile) {
					my $bookedData = `cat $bookedFile`;
					eval { 
						$bookedObj = $json->decode($bookedData);
					};
					$bookedFile = "" if $@;
				}
				if ($bookedFile) {  # check again if the file is corrupted.
					my %newBookedData = dataMigration(\$cfgObj, \$bookedObj);
				
					### sb has booked.
					my $getIdx = getBookingIdx($action, $bookedFile);
					if ($getIdx <= $cfgObj->{"BookingCount"}) {
						$bookingStatus = "您已经成功报名！第 $getIdx 位。信息如下：";
					}else{
						$bookingStatus = "您已经报名过，但没有成功，还在排队队列中！第 ".($getIdx - $cfgObj->{"BookingCount"})." 等候位。信息如下：";
					}
					if ($cgi->param("edit")){
						$retInputForm = buildInputForm(\%userInfo, $action, \$cfgObj, \%newBookedData, "editable", $bookedFile);
					}else{
						$retInputForm = buildInputForm(\%userInfo, $action, \$cfgObj, \%newBookedData, "", $bookedFile);
					}
				}else{
					$retInputForm = buildInputForm(\%userInfo, $action, \$cfgObj, "", "", "", $bookedFile);
					
					my $rc = 0;
					($rc, $bookingStatus) = checkBookingWindow(\$cfgObj, $user);
					if ($rc < 0) {
						if ($rc == -1 && isAdmin(\$cfgObj, $user)) { 
						    # admin is allowed even not in time windows.
							$bookingStatus .= "<br><br><b>但是，作为管理员，您仍然可以提交报名数据用以测试。测试结束务必撤销哦！！！</b><br>";
						}else{
							# hrer $rc = -2 (booked in other actions), admin is still not allowed.
							$retInputForm = "<br />" x 10; ### hide the input form.
						}
					}else{
						my $getStatus = checkBookingType($action, $cfgObj->{"BookingCount"}, $cfgObj->{"QueueCount"});
						if ($getStatus eq "Booked" || $getStatus eq "Queued" ) {  ## in fact, to be booked or queued.
							if ($getStatus eq "Booked") {
								$bookingStatus = "请填写如下信息进行报名！";
							}else{
								$bookingStatus = "报名已满，如果愿意排队，请填写如下信息并提交！";
							}
							unless ($retCfgInfo1) {
								$errorInfo = "Error: config file ($action.cfg) is NOK!\n";
							}
						}else{
							$bookingStatus = "对不起，报名已满，排队队列也已满，您来晚了:(";
							$retInputForm = "<br />" x 20; ### hide the input form.
						}
					}
				}
				
				if (isAdmin(\$cfgObj, $user)) {
					$adminLinks = "<a href=\"viewall.cgi?action=$action\" target=\"_blank\">[view booking records]</a> ";
					$adminLinks .= "&nbsp;"x2;
					$adminLinks .= "<a href=\"viewall.cgi?action=$action&export=1\" >[export to XLS]</a> ";
					#$adminLinks .= "&nbsp;"x4;						
					#$adminLinks .= "[<a href=\"viewall.cgi?action=$action&lock=yes\">lock</a> / ";
					#$adminLinks .= "<a href=\"viewall.cgi?action=$action&lock=no\">unlock</a>]";
					#$adminLinks .= "&nbsp;"x8;
				}
			}else{
				$errorInfo = "配置信息错误! 请联系管理员<div style='display:none'>\$action='$action';\$retStr='$retStr'\n</div>";
			}
#		}else{
#			$errorInfo = "配置信息没有找到! 请联系管理员<div style='display:none'>$action</div>";
#		}
	}else{
		$errorInfo = "报名入口错误! 请输入正确的网址。";
	}

#	print "<div id=\"content\"><div id=\"left\">$retCfgInfo1 \n $retCfgInfo2 </div>\n";
	print "<div id=\"content\"><div id=\"left\">";
	print "<h3>系统个人信息</h3>". getPersonalInfoTable($info) . "\n";
	print "<br><br><h3>管理信息</h3>$retCfgInfo2 </div>\n";

	print "<div id=\"middle\"><img src=\"dump.cgi/vbar.png\" width=\"12px\" height=\"100%\"></div>\n";
	print "<div id=\"right\"><br>\n";
	
	print "<table class=\"table1\">\n";

#	print "<tr><td class=td1>".getPersonalInfoTable($info)."</td></tr>\n";
	print "<tr><td class=td1>" . $retCfgInfo1 . "</td></tr>\n";

	print "<tr class=td2><td class=title><h2>$bookingStatus $errorInfo</h2></td></tr>\n";
	print "<tr><td>$retInputForm</td></tr>\n";
	print "</table>\n";
	print "</div></div>\n\n";
	
    printHtmlFooter ("<br />" . $adminLinks . "&nbsp;" x 10 . "<a href=login.cgi?logout=1&action=$action>[logout]</a>\n");

}else{
	print "<div id=\"content\"><div id=\"left\">\n";
    if ($action) {
		### 1. get config info.
		my ($cfgObj, $retStr) = getConfigJsonObj($action);
#		my $cfgObj;
#		if ($cfgJsonStr) {
#			eval { 
#				$cfgObj = $json->decode($cfgJsonStr);
#			};
			if ($cfgObj) {
				print buildCfgHtmlTable(\$cfgObj, $action);
			}else{
				print "Error: $retStr";
			}
#		}
	}
	print "</div>\n\n";
	print "<div id=\"middle\"> </div>\n";
	print "<div id=\"right\">\n";
	printLogonEntry ($action, $user, $login);
	print "</div></div>\n";
    printHtmlFooter ("<br />");
}

exit 0;

#-----------------------------------------------------------------------------
sub getBookingIdx {
	my ($action, $bookedFile) = @_;
	
	my @date_bookers;
	getBookingList($action, \@date_bookers);

	$bookedFile =~ m|/(\w+)_\d\d\d\d\-\d\d-\d\d|; # get user name
	my $user = $1;
	for (my $i=0; $i<@date_bookers; $i++) {
		if ($date_bookers[$i] =~ /$user$/) {
			return $i+1;
		}
	}
	return -1;
}

#-----------------------------------------------------------------------------
sub checkBookingWindow {
	my ($jsonObj, $user) = @_;

	my @ActionGroup = @{$$jsonObj->{"ActionGroup"}};
	foreach my $actionX (@ActionGroup) {
		$actionX =~ s/[^\w\-]//g;  # avoid illegal chars.
		next unless $actionX; 
		my $bookedFile = `ls -1 booking_log/$actionX/$user*.book  2>/dev/null | tail -1`;
		chop($bookedFile);
		
		if ($bookedFile) {
			return (-2, "对不起，您已经在这一组活动中报过名了（<a href=\"login.cgi?action=$actionX\">点击查看</a>）。".
			            "如果需要在此活动中报名，请撤销那次报名，然后重新在此报名。");
		}
	}
	
	my $StartTime = $$jsonObj->{'StartTime'} || "0";
	$StartTime =~ s/ +/ /;
	my $EndTime = $$jsonObj->{'EndTime'} || "0";
	$EndTime =~ s/ +/ /;
	my $currTime = `date "+%Y-%m-%d %H:%M:%S"`;
	chop($currTime);
	
	return (-1, "抱歉！报名还未开始。请稍后刷新再试！") if ($StartTime ne "0" && $StartTime gt $currTime);
	return (-1, "抱歉！报名已经结束。下次要赶早哦！")   if ($EndTime   ne "0" && $EndTime   lt $currTime);
	
	return (0, "");
}





