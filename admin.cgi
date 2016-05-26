#!/usr/bin/perl -w
use strict;
require "formatConvert.pm";
require "buildInputForm.pm";

use Encode;
use JSON;
use CGI;
use CGI::Session;

my $cgi = new CGI;

my $session = new CGI::Session("driver:File", $cgi ,{Directory=>'/tmp'});
my $user = $session->param("f_name") || "";
my $login = $session->param("f_login") || "";
my $info  = $session->param("f_info") || "";
my ($cil, $img, $dept, $email, $phone, $mobile, $upi) = get_personal_info($info);

	
printHtmlHeader("");

if ($cgi->param("logout")) {
    $user = "";
    $session->delete();
}

unless ($user && $login eq 'OK') {	
	printLogonEntry ("", $user, $login);
	printHtmlFooter();
	exit 0;
}

	print <<__JS;
<script src="dump.cgi/myJquery.js"> </script>

<script>
\$(document).ready(function(){
	//\$("[name='todo']").change(function(){
		//alert(this.value);
		//todo_changes(this.value);
	//});
	\$("[name='todo']").click(function(){
		//alert(this.value);
		todo_changes(this.value);
	});

	\$("#exec_target").load(function(){
        var data = \$(window.frames['exec_target'].document.body).html();
        if(data != null){
			if (data.match(/^error:/i)) {
				alert(data);
				return false;
			}
			\$("[name='Picture']").val(data);
            \$("#upload_file").val('');
			data = "<img src=\\"dump.cgi/booking_log/" + data + "?" + Math.random() + "\\" width=\\"250px\\">";
			\$("#feedback").html(data);
			refreshCfg();
        }
    });
    \$("#upload_file").change(function(){
		\$("#upload_action_code").val(\$("[name='action_code']").val());
        if(\$("#upload_file").val() != '') {
			\$("#submit_form").submit();
			//\$("#feedback").html('please wait...');
		}
    });
	
	\$("#pre_cfg_confirm").click(function(){pre_cfg_confirm()});

	\$("#table_action_info").change(function(){refreshCfg();});
	\$("#table_inputs").change(function(){refreshCfg();});

	\$("#top-add").click(function(){showOneMoreInput(\$(this).parent().parent())});

	\$("#left").css("width", "830px");
	\$("#middle").css("left", "830px");
	\$("#right").css("left", "839px");
	\$(".tableHeader").children("td").css("font-weight","bold");
	\$("#table_inputs tr td").css("white-space","nowrap");


	\$("#preview_button").click(function(){booking_preview()});
	\$("#confirm_button").click(function(){booking_confirm()});
	\$("#save_as_button").click(function(){booking_save_as()});
	
	\$("[name='action_code']").change(function(){action_code_changes();});
	\$("[name='ActivityName']").change(function(){ActivityName_check();});
	
	\$("#Admins").change(function(){
		var admins = \$("#Admins").val().match(/(\\w+)/g);
		if (admins) {
			for (var i=0;i<admins.length;i++){
				if (admins[i].toLowerCase() == "$user".toLowerCase()) {
					return;
				}
			}
		}
		\$("#Admins").val( "$user" + "," + \$("#Admins").val());
	});
	
	//insert 3 rows by default
	var v1 = \$("[name='action_code']").val();
	var v2 = \$("[name='ActivityName']").val();
	//alert("ready1:" +v1 + "," + v2);

	if (v1 == ""){
		showOneMoreInput(); 
		showOneMoreInput(); 
		showOneMoreInput(); 
	}else{
		action_code_changes();
	}
	
	\$("#deletePicture").click(function(){
		\$("input[name='Picture']").val("");
		refreshCfg();
	});
	
});

var personInfo_user = "$user";

var jsonKeys = new Array("action_code","ActivityName","Admins","ActionGroup","StartTime",
                         "EndTime","BookingCount","QueueCount","Picture","Information");

var helpInfo = {'td_todo_2': '在此管理您已经创建的页面。包括：查看，锁定、修改、另存等。  \\n\\n如果修改了某些内容，包括重新上传了图片，请务必保存一下。', 
                'todo_1':  '活动代码是整个报名系统唯一的编码，由小写字母、数字、减号和下划线组成，其他字符自动被删除。 请选择有意义的字母数字组合，比如: ‘asb-familiday-2016’',
				'ActionGroup': "相关联的活动指一系列活动中，只允许报名一次的活动。 \\n\\n比如这个月举办了徒步活动A，甲报名了。第二个月举办徒步活动B，作为组织者，您只希望上次没有参加过的人报名，那么在建立B活动的报名入口时，把A活动的代号写在B活动的‘相关联的活动’中，那么甲就不能在B活动中报名了。无论甲在A活动中是报名成功还是候选。 \\n\\n当然，如果甲事先到A活动中撤销了上次报名，然后他就可以在B中报名了。为了防止这种情况发生，A活动结束后，管理员务必及时把A活动锁定住。切记切记！",
				'BookingCount': '允许报名的总人数，一次员工报名算1位，如果报名选择项中有‘下拉菜单数字单选项’，那么这些数字也被算入总人数中。',
				'select-counted': '第二步配置输入项时，选择‘下拉菜单数字单选项’， 那么这项数值也被计入总人数中，可以有多个。比如‘成年家属人数’，‘携带儿童人数’。',
				'select-counted2': '如果可选项是数字, 但你又不想让这些数字计入总人数, 那么请选择前一个选项:"下拉菜单", 而不是这个"数字下拉菜单"。',
				'Picture': '允许上传一幅图片，格式为JPG、PNG、或者GIF。大小限制为1MB。如果有多图，请使用工具事先拼成一幅图再上传。',
				'DefaultChoice': '文本框默认为空，单选和多选项默认均为不选中。如果某个可选项值要设成默认值，请在这个值的结尾处添加‘:1’。比如：3个选项A、B、C，但配置成‘A:1,B,C’时，‘A’就是默认选中。\\n\\n注：单选项只接受最后一个‘:1’。'
				};

function help(str){
	if (helpInfo[str]) {
		alert(helpInfo[str]);
	}else{
		alert("help info not found!");
	}
}

var dataSaved = true;
window.onbeforeunload = function(){
	if (dataSaved == false) {
		return "修改后还未保存！";
	}
}
						 
</script>
__JS


	print <<__BODY;
<div id="booking_content">
<h2>报名页面管理入口</h2>
<hr>
<table><tr>
<td id="td_todo1" nowrap><input type="radio" name="todo" class="todo" value="1" id="todo1">
                         <label for="todo1" class="toplabel">新建一个报名页面</label></td>
<td id="td_todo2" nowrap><input type="radio" name="todo" class="todo" value="2" id="todo2">
                         <label for="todo2" class="toplabel">管理已经存在的报名页面<button onclick="help('td_todo_2')">?</button></label></td>
<td></td></tr></table>
<div id="todo_1" class="xxx"><br>&nbsp;&nbsp;&nbsp;输入活动代号<button onclick="help('todo_1')">?</button>:
                             <input type="text" class="pre_cfg" id="pre_action_code"  size=30>
                             <input type="button" class="pre_cfg" value="确定" id="pre_cfg_confirm"><br>&nbsp;&nbsp;&nbsp;</div>
<div id="todo_2" class="xxx">&nbsp;&nbsp;&nbsp;<br>
                             <span id="existing_actions">请稍等...</span>
							 &nbsp;&nbsp;&nbsp;</div>

<div id="part_all" class="xxx">

<hr>
<br>


<table id="config_and_preview"><tr>
<td>
<div id="part1">
<h3>第一步：请配置活动基本信息，并随时预览</h3>
<br>
<table id="table_action_info" border=1 width="850px">
<tr><th>  活动代码(*)</th><td><input type="text" class="cfg" name="action_code"  size=30 readonly="readonly" style="background-color:#ddd">
                               <span class="remark"> (<span class="must">必填项</span>)仅限小写字母和数字</span></td></tr>
<tr><th>  活动名称(*)</th><td><input type="text" class="cfg" name="ActivityName" size=50>
                               <span class="remark">(<span class="must">必填项</span>)</span></td></tr>

<tr><th> 活动详细信息</th><td><textarea class="cfg" name="Information" cols=60 rows=4></textarea></td></tr>

<tr><th>   显示的图片<button onclick="help('Picture')">?</button></th>
                           <td><input type="hidden" class="cfg" name="Picture"       size=40 readonly="readonly">
		<form id="submit_form" method="post" action="pictureUpload.cgi" target="exec_target" enctype="multipart/form-data">
			选择图片并上传(大小1MB以内) <input type="file" name="file" id="upload_file" title="选择图片文件上传">
			<input type="text" class="xxx" name="action" id="upload_action_code" readonly="readonly" >
		</form>
		<div id="feedback"></div><input type="button" id="deletePicture"  value="取消图片">
		<iframe id="exec_target" name="exec_target" class="xxx"></iframe> 
        </td></tr>
							   
<tr><th>组织者ad4账号</th><td><input type="text" class="cfg" name="Admins"  size=25 value="$user" id="Admins">
                               自己默认，多位组织者以逗号分隔</td></tr>
<tr><th> 报名开始时间</th><td><input type="text" class="cfg" name="StartTime"> 格式：‘YYYY-mm-dd HH:MM:SS’，若为空，则无时间限制</td></tr>
<tr><th> 报名截止时间</th><td><input type="text" class="cfg" name="EndTime"  > 格式：‘YYYY-mm-dd HH:MM:SS’，若为空，则无时间限制</td></tr>
<tr><th> 报名人员总数<button onclick="help('BookingCount')">?</button></th>
                           <td><input type="text" class="cfg" name="BookingCount"  size=20>
						       员工数+<a href="javascript:void(0)" onclick="help('select-counted')">数字下拉菜单</a>指定的数字。默认值为1000</td></tr>
<tr><th> 候选人员总数</th><td><input type="text" class="cfg" name="QueueCount"    size=20> （要求同上。均为选填项。）</td></tr>

<tr><th> 相关联的活动<button onclick="help('ActionGroup')">?</button></th>
                           <td><input type="text" class="cfg" name="ActionGroup"  size=30> 可选。多个活动以逗号分隔</td></tr>

</table>
</div>

<br>
<br>
<br>
<br>


<div id="part2">
<h3>第二步：配置需要报名者提供的信息，并随时预览</h3> （注：报名者在Outlook地址簿中的基本信息，如工号、分机、邮件地址、部门等，系统默认获取，预览时看到的您自己的基本信息仅供参考。）
<br>
<table id="table_inputs" border=1 width="850px">
<tr class="tableHeader">
	<td width="60px"><input type="BUTTON" value="＋" id="top-add" class="quickset-top" title="添加一行"></td>
	<td width="130px">输入方式</td>
	<td width="130px">输入项名称</td>
	<td              >输入项内容&nbsp;<button onclick="help('DefaultChoice')">默认值?</button></td>
	<td width="200px">前置显示条件</td>
</tr>
</table>
</div>
</td>

<td id="td_part3">
<div id="part3">
<h3>报名页面预览</h3>
	<textarea id="input_preview" name="input_preview" cols="80" rows="20" readonly="readonly" style="background-color:#ddd" class="xxx"></textarea>
	<input id="preview_button" type="button" value="报名页面预览" size=20 class="xxx" />
	<div id="booking_preview" >此处预览报名页面</div>

</div>

</td></tr></table>

<br>
<hr>

<div id="part4">
<h3>第三步：确认报名链接</h3>
报名代码为: <input type="text" id="booking_code" size=20 readonly='readonly'>

<input type="button" id="confirm_button" class="submit_final" value="保存" /> 
<input type="button" id="save_as_button" class="submit_final" value="另存为..." />
<br><br>
<span id="booking_link" ></span>
<br>

<form  name='sendmail' action='mailto:' class=xxx>
<input name='cc' type='text' value='$email'> 
<input name='subject' type='text' value=''> 
<textarea name='body' ></textarea>
<input type=submit>
</form>

<br>

</div>
</div> 
</div>

__BODY

printHtmlFooter ("<br />" . "<a href=admin.cgi?logout=1>[logout]</a>\n");

exit 0;

#---------------------------------------------------------------------



	
