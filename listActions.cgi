#!/usr/bin/perl -w
use strict;
use Encode;
require "formatConvert.pm";
require "buildInputForm.pm";
use CGI;
use CGI::Session;

my $cgi = new CGI;
my $session = new CGI::Session("driver:File", $cgi ,{Directory=>'/tmp'});
my $user = $session->param("f_name") || "";
my $login = $session->param("f_login") || "";

unless ($user && $login eq 'OK') {	
	printLogonEntry ("", $user, $login);
	exit 0;
}
my $cmd = "cd booking_log && grep -H \"^Admins:\" *.cfg | grep -iw $user | cut -d\".\" -f1 | grep -v __preview__";
my $output = `$cmd`;
my $html = "<table>";
my $class = "d1";
my $basedir = basedir();

my $action_do = lc($cgi->param("action") || "");
my $do        = $cgi->param("do")     || "";
my $cnt = 0;
my $radioIdx = 0;
foreach my $action (split(/\n/, $output)) {
	if ($action =~ /\w/) {
		if ($action eq $action_do) {  ### must be inside the loop to avoid violant deletion.
			my $cmd = "";
			if ($do eq "lock") {
				$cmd = "mkdir -p $basedir/$action_do 2>/dev/null; touch \"$basedir/$action_do/__lock__\" 2>/dev/null";
				`$cmd`;
			}elsif ($do eq "unlock") {
				$cmd = "rm -f $basedir/$action_do/__lock__ 2>/dev/null";
				`$cmd`;
			}elsif ($do eq "delete") {
				# delete all files expect images which maybe is shared by other activities.
				$cmd = "mv $basedir/$action_do     $basedir/.$action_do     2>/dev/null;".
				       "mv $basedir/$action_do.cfg $basedir/.$action_do.cfg 2>/dev/null;";
				`$cmd`;
				next;
			}
			##$html .= "[$cmd]";
		}
		
		$cmd = "cd $basedir/$action 2>/dev/null && ls *.book 2>/dev/null | cut -c1-8 | sort -u | wc -l";
		my $bookedCnt = `$cmd`;
		chop($bookedCnt);
	
		my ($rc, $cfgStr, $ActivityName) = checkAdmin($user, $action);
		my $label1 = length($action)<15 ? $action : substr($action, 0, 12) . "...";
		my $s      = decode('utf8',$ActivityName) || "";
		my $label2 = encode('utf8', (length($s)<20 ? $s : substr($s, 0, 17) . "..."));
		my $label = "$label1 ($label2)";
	
		my $checked = "";
		if ($action eq $action_do) {
			$checked = "checked=\"checked\"";
		}
	
		$class = ($class eq "d0")? "d1" : "d0";
		$html .= "<tr class=\"$class\">"; 
		$html .= "<td><input type=\"radio\" $checked name=\"pre_existing_actions\" value=\"$action\" onclick=\"pre_actions('$action')\" ".
		         "id=\"ac_$action\"><label for=\"ac_$action\" onclick=\"pre_actions('$action')\">$label</label></td>";

		$html .= "<td><input type=\"button\" value=\"查看/编辑\" onclick=\"pre_actions_2('$action'," . $radioIdx++ . ")\"></td>";
		$html .= "<td><a href=\"login.cgi?action=$action\"    target=\"_blank\">进入报名</a></td>";
		if ($bookedCnt) {
			$html .= "<td>已有".$bookedCnt."位员工报名，<a href=\"viewall.cgi?action=$action\"  target=\"_blank\">查看报名结果</a>, ";
			$html .= "<a href=\"viewall.cgi?action=$action&export=1\"  target=\"_blank\">导出到XLS文件</a></td>";
		}else{
			$html .= "<td>还没人报名</td>";
		}

		#$html .= "<td>&nbsp;&nbsp;&nbsp;&nbsp;</td>";
		if (-e "$basedir/$action/__lock__") {
			$html .= "<td><input type=\"button\" value=\"锁定\" disabled=\"true\"></td>";
			$html .= "<td><input type=\"button\" value=\"解锁\" onclick=\"unlock_action('$action')\"></td>";
		}else{
			$html .= "<td><input type=\"button\" value=\"锁定\" onclick=\"lock_action('$action')\"></td>";
			$html .= "<td><input type=\"button\" value=\"解锁\" disabled=\"true\"></td>";
		}
		
		$html .= "<td><input type=\"button\" value=\"彻底删除\" onclick=\"delete_action('$action')\"></td>";
		$html .= "</tr>";
		$cnt++;
	}
}
if ($cnt==0){
	$html .= "<tr><td>Oooops! 目前还没有您管理的活动。</td></tr>";
}
$html .= "</table>";

print "Content-type: text/html; charset=utf-8\n\n$html";
