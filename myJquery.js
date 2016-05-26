/*
Booking system
designed by Yao Jianwen on 2016.04 for ASB LBU activities.
*/
var last_todo = "";
var last_pre_action = "";

var dispSwitch = '<input class="cfg" type="hidden" value="//show_when:">\
                  <select class="cfg" name="disp_switch" >\
						<option value="0" >无条件</option>\
						<option value="1" >&nbsp;满足</option>\
				  </select>\
				  <select class="cfg" name="disp_item" >\
				  </select><br>\
				  <select class="cfg" name="disp_cond" >\
						<option value="eq" >等于</option>\
						<option value="gt" >大于</option>\
						<option value="ge" >大于等于</option>\
						<option value="lt" >小于</option>\
						<option value="le" >小于等于</option>\
						<option value="ne" >不等于</option>\
				  </select>\
				  <select class="cfg" name="disp_value" >\
				  </select>';

var input_name = new Array("",
		'<input type="text" class="cfg" size="16" name="subtitle">',
		'<input type="text" class="cfg" size="16" name="radio">',
		'<input type="text" class="cfg" size="16" name="checkbox">',
		'<input type="text" class="cfg" size="16" name="select">',
		'<input type="text" class="cfg" size="16" name="select-counted">',
		'<input type="text" class="cfg" size="16" name="text">',
		'<input type="text" class="cfg" size="16" name="textarea">');

var names4get = new Array('subtitle','radio','checkbox','select','select-counted','text','textarea');
		
var inputRow = '<tr class="inputRow">' +
               '<td ><input type="button" class="deleteRow"  value="－"  title="删除此行">'          + 
                    '<input type="button" class="up"         value="上" title="向上移动一行"><br>'  +
                    '<input type="button" class="insertRow"  value="＋"  title="添加一行">'          +
				    '<input type="button" class="down"       value="下" title="向下移动一行"></td>' +
			   '<td ><select class="cfg" name="input_selector" >\
						<option value="0">--请选择--</option>\
						<option value="1" >文字说明, 副标题</option>\
						<option value="2" >点选单选项</option>\
						<option value="3" >勾选多选项</option>\
						<option value="4" >下拉菜单</option>\
						<option value="5" >(*)数字下拉菜单</option>\
						<option value="6" >单行文本输入框</option>\
						<option value="7" >多行文本输入框</option>\
					 </select>\
				 </td>' +
				'<td class="input_name"></td>' +
				'<td class="input_item"></td>' +
				'<td class="input_disp">'+dispSwitch+'</td>' +
				"</tr>\n";

var options = new Array("",
		'（无需）',
		'单选项（逗号分隔, 如：男,女）: <br><input type="text" class="cfg" name="radio" size=25">',
		'多选项（逗号分隔, 如：苹果,橙子,菠萝）: <br><input type="text" class="cfg" name="checkbox" size="25">',
		'下拉菜单单选（逗号分隔，如：S,M,L,XL,XXL,XXXL）: <br><input type="text" class="cfg" name="select" size="25">',
		'数字下拉菜单（逗号分隔的数字, 将<u>计入总人数</u>。如：0,1,2<button onclick="help(\'select-counted2\')">?</button>）<br><input type="text" class="cfg" name="select-counted" size="25">',
		'文本框宽度: <input type="text" class="cfg" name="text" size="3" value="20">',
		'文本框行数: <input type="text" class="cfg" name="textarea" size="3" value="3">\
		 文本框列数: <input type="text" class="cfg" name="textarea_cols" size="3" value="40">');


function JSON_parse(str){
	return eval('(' + str + ')'); 
}

//---------------- conditional display -----------------------------------
function refresh_disp_cond(disp_switch_id, selection){
	var $trs = $("#table_inputs tr");

	for (var i=1; i<$trs.length; i++){ // i=1, skip header row.
		var disp_switch_i = $($trs[i]).find("select[name=disp_switch]")[0];
		if (disp_switch_id && disp_switch_id != disp_switch_i) {
			continue; // only refresh this row.
		}
		
		var disp_item_opt = "<option value=''>--请选择--</option>\n";
		for (var k=1; k<$trs.length; k++) { // scan input lines	, k=1, skip header row.
			var disp_switch_k = $($trs[k]).find("select[name=disp_switch]")[0];
			if (disp_switch_k == disp_switch_i) {
				continue; // skip my self.
			}
			if ($(disp_switch_k).val() != "0") {
				continue; // skip 
			}
			var input_name = $($trs[k]).find(".input_name").children("input.cfg").attr("name");
			var input_val  = $($trs[k]).find(".input_name").children("input.cfg").val();
			if (input_name == "radio" || input_name == "select" || input_name == "select-counted") {
				var selectAttr = "";
				if (selection && selection == input_val){
					selectAttr = "selected='selected'";
				}
				disp_item_opt += "<option value='" + input_val + "' " + selectAttr + ">"+ input_val + "</option>\n";
			}
		}
		$(disp_switch_i).parent().children("select[name=disp_item]").html(disp_item_opt);
	}
}

function refresh_disp_value(disp_item_id, selection){
	var $trs = $("#table_inputs tr");
	for (var k=1; k<$trs.length; k++) { // scan input lines	
		var input_name = $($trs[k]).find(".input_name").children("input.cfg").attr("name");
		var input_val  = $($trs[k]).find(".input_name").children("input.cfg").val();
		if (input_name == "radio" || input_name == "select" || input_name == "select-counted" ) {
			if (disp_item_id.value == input_val) {
				var input_item = $($trs[k]).find(".input_item").children("input.cfg").val();
				var opts = input_item.replace(/，/g, ",").split(/\s*,\s*/); //replace is for Chinese comma.
				var disp_value_opt = "<option value=''>-?-</option>\n";
				for (var n=0; n<opts.length; n++){
					opts[n] = opts[n].replace(/:1$/, '');  // remove default choice flag 
					if (opts[n] != ""){
						var selectAttr = "";
						if (selection && selection == opts[n]){
							selectAttr = "selected='selected'";
						}
						disp_value_opt += "<option value='" + opts[n] + "' " + selectAttr + ">" + opts[n] + "</option>\n";
					}
				}
				$(disp_item_id).parent().children("select[name=disp_value]").html(disp_value_opt);	
			}
		}
	}
}


//---------------- input changes -----------------------------------
function changeInput(id){
	var v1="";
	var v2="";
	for (var i=0; i<names4get.length; i++){
		var v = $(id).parent().parent().find(".input_name").find('input:text[name='+names4get[i]+']').val();
		if (v) {
			v1 = v;
			break;
		}
	}
	for (var i=1; i<names4get.length; i++){ //# skip subtitle
		var v = $(id).parent().parent().find(".input_item").find('input:text[name='+names4get[i]+']').val();
		if (v) {
			v2 = v;
			break;
		}
	}
	
	var idx = id.value;
	var h1 = input_name[idx].replace("<input type", "<input value='" + v1 + "' type");  // keep input content not changed to save admin's effort:)
	$(id).parent().parent().find(".input_name").html(h1);
	
	var h2 = options[idx];
	if (idx >1 && idx <6){
		h2 = h2.replace("<input type", "<input value='" + v2 + "' type");
	}
	$(id).parent().parent().find(".input_item").html(h2);
}


function name_duplicated(inputName, inputNames){
	for (var i=0; i<inputNames.length; i++) {
		if (inputName == inputNames[i]) {
			return true;
		}
	}
	return false;
}

// refresh show_when options
function updateShowWhen(){
	$trs = $("#table_inputs").children().children();
	for (var i=1; i<$trs.length; i++){
		var disp_switch = $($trs[i]).find("select[name='disp_switch']").val();
		var disp_item   = $($trs[i]).find("select[name='disp_item']").val();
		var disp_value  = $($trs[i]).find("select[name='disp_value']").val();

		if (disp_switch != "1") continue;
		
		// 1. check disp_item is valid or not.
		var valid = false;
		var disp_opts = "<option value=''>--请选择--</option>\n";
		var value_opts = "";
		for (var k=1; k<$trs.length; k++){
			if (i==k) continue; // skip myself
			
			var input_name = $($trs[k]).children(".input_name").find("input.cfg").attr("name");
			if (input_name != "select" && input_name != "select-counted" && input_name != "radio") continue;

			var input_val  = $($trs[k]).children(".input_name").find("input.cfg").val();
			input_val = $.trim(input_val);
			if (input_val == "") continue;

			var selected = "";
			if (input_val == disp_item) {
				selected = " selected=\"selected\" ";
				valid = true;
				value_opts = $($trs[k]).children(".input_item").find("input.cfg").val();
			}
			disp_opts += "<option value=\"" + input_val + "\" " + selected + " >" + input_val + "</option>\n";
		}
		// now use the new options.
		$($trs[i]).find("select[name='disp_item']").html(disp_opts); 
		
		if (valid == false) {
			// reset disp_switch
			//$($trs[i]).find("select[name='disp_switch']").val("0");
			continue;
		}
		
		// 2. disp_item is valid, check disp_values
		var values = value_opts.replace(/，/g, ",").replace(/:1\s*,/g, ",").split(/\s*,\s*/);
		valid = false;
		disp_opts = "<option value=''>-?-</option>\n";
		for (var m=0; m<values.length; m++){
			values[m] = $.trim(values[m]);
			if (values[m] == "") continue;

			var selected = "";
			if (values[m] == disp_value) {
				selected = " selected=\"selected\" ";
				valid = true;
			}
			
			disp_opts += "<option value=\"" + values[m] + "\" " + selected + " >" + values[m] + "</option>\n";
		}
		// now use the new options.
		$($trs[i]).find("select[name='disp_value']").html(disp_opts);
	}	
}

//------------------------------------------------------------------------
// refresh everything if something in tables changes.
//------------------------------------------------------------------------
function refreshCfg(){

	updateShowWhen();

	var preview = "";

	// get data from table_action_info // tbody -> tr
	var $trs = $("#table_action_info").children().children();
	for (var i=0; i<$trs.length; i++){
		var $txt = $($trs[i]).find(".cfg");
		if ($txt[0] && $($txt[0]).val()) {
			preview += $($txt[0]).attr("name") + ":" + $($txt[0]).val().replace(/\n/g,"<br>\\\n");
			preview += "\n\n"; // must double NL to avoid backslash at end:(
		}
	}

	var inputNames = new Array();
	$trs = $("#table_inputs").children().children();
	for (var i=1; i<$trs.length; i++){ // skip header
		var $txt = $($trs[i]).find(".cfg");
		if (($txt[0] && $($txt[0]).attr("name") == "input_selector"       && $($txt[0]).val() != "0") && // not '--无--'
			($txt[1] && $($txt[1]).parent().attr("class") == "input_name" && $($txt[1]).val()       )) {

			// avoid duplicated names
			var name1 = $($txt[1]).val().replace(/,/g,';').replace(/，/g,'; ');
			if (name_duplicated(name1, inputNames)) {
				alert("错误：输入项目\"" + name1 + "\"命名重复，请改正！");
				$($txt[1]).focus();
				$($txt[1]).fadeOut().fadeIn();
				return false;
			}else{
				inputNames[inputNames.length] = name1;  // extend one.
			}
			preview += "Input: " + name1 + ", " + $($txt[1]).attr("name");

			for (var k=2; k<10; k++) {
				if ($($txt[k]).val() == undefined) {
					break;
				}
				preview += ", " + $($txt[k]).val();
			}
			
			preview += "\n\n"; // must double NL to avoid backslash at end:(
		}
	}
	
	var old_cfg_data = $("textarea#input_preview").text();
	if (preview == old_cfg_data) {
		dataSaved = true;
	}else{
		if (old_cfg_data == "") {
			dataSaved = true; // init state
		}else{
			dataSaved = false;
		}
	}
	
	$("textarea#input_preview").text(preview);
	
	// for picture upload
	//alert($("[name='action_code']").val());
	$("#upload_action_code").val($("[name='action_code']").val());

	// update Picture
	var pic_path = $("[name='Picture']").val();
	if (pic_path == "") {
		$("#feedback").html("");
	}else{
		var img_url = "<img src=dump.cgi/booking_log/" + pic_path +" width=250px>";
		$("#feedback").html(img_url);
	}

	booking_preview();
	return true;
}

function showOneMoreInput(trId){
	var tr;
	var trCnt = $("#table_inputs tr").length;

	if (trId == undefined){
		$("#table_inputs").append(inputRow);
		tr = $("#table_inputs tr")[trCnt];  //#insert a new row at end.
		trCnt++;
	}else{
		$(trId).after(inputRow);
		tr = $(trId).next();
	}
	
	trCnt = $("#table_inputs tr").length;
	
	$(tr).find("select[name=input_selector]").change(function(){changeInput(this)});

	//删除一行
	$(tr).find(".deleteRow").click(function(){ 
		$(this).parent().parent().remove();
		refreshCfg();
	});

	//增加一行
	$(tr).find(".insertRow").click(function(){
		//alert("增加一行");
		showOneMoreInput($(this).parent().parent());
		refreshCfg();
	});

	//上移 
	$(tr).find(".up").click(function() { 
		var $tr = $(this).parent().parent(); 
		if ($tr.index() > 1) { // do not move header row.
			$tr.fadeOut().fadeIn(); 
			$tr.prev().before($tr); 
			refreshCfg();
		} 
	}); 

	//下移 
	$(tr).find(".down").click(function() { 
		var len = $("#table_inputs tr").length;
		var $tr = $(this).parent().parent(); 
		if ($tr.index() != len - 1) { 
			$tr.fadeOut().fadeIn(); 
			$tr.next().after($tr); 
			refreshCfg();
		} 
	}); 

	$(tr).find('select[name=disp_switch]').val("0");
	$(tr).find('select[name=disp_item]').hide();
	$(tr).find('select[name=disp_cond]').hide();
	$(tr).find('select[name=disp_value]').hide();
	$(tr).find("select[name=disp_switch]").change(function(){
		if (this.value == 0) {
			$(this).parent().find('[name=disp_item]').hide();
			$(this).parent().find('[name=disp_cond]').hide();
			$(this).parent().find('[name=disp_value]').hide();
		}else{
			$(this).parent().find('[name=disp_item]').show();
			$(this).parent().find('[name=disp_cond]').show();
			$(this).parent().find('[name=disp_value]').show();
			refresh_disp_cond(this);  // only when condition is setting, refresh lists.
		}
	});

	$(tr).find("select[name=disp_item]").change(function(){
		refresh_disp_value(this);
	});

}

function booking_preview(){
	if (action_code_check() == false || ActivityName_check() == false){
		$("#booking_preview").html("错误：必填项为空！");
		//$("#booking_portal").val("");
		return;
	}
	var portal = this.location.href;
	portal = portal.replace(/[^\/]+$/, '');
	portal = portal + "login.cgi?action=" + $("[name='action_code']").val();
	//$("#booking_portal").val(portal);
	$("#booking_code").val($("[name='action_code']").val());
	
	var txt = $("textarea#input_preview").text();

    $.post("preview.cgi",
		{
		  input_preview: txt
		},
		function(data,status){
			if(status == "error") {
				alert("数据：" + data + "\n状态：" + status);
			}else{
				$("#booking_preview").html(data);
				$("input.submit2").attr("disabled","true");
				//var pic = $("#preview_picture").html();
				//alert('pic='+pic)
			}
		}
	);
}

function booking_confirm(){
	if(!refreshCfg()) return false;
	
//	var id = $("[name='action_code']")[0];
//	action_code_check(id);
	$("#booking_link").hide();
	
	if (action_code_check() == false || ActivityName_check() == false){
		$("#booking_preview").html("错误：必填项为空！");
		//$("#booking_portal").val("");
		return false;
	}

	var url = this.location.href;
	url = url.replace(/[^\/]+$/, '') + "login.cgi?action=";

	var bcd = $("#booking_code").val();
	var txt = $("textarea#input_preview").text();

    $.post("preview.cgi",
		{
		  action: bcd,
		  input_preview: txt
		},
		function (data,status){
			if(status == "error") {
				alert("数据：" + data + "\n状态：" + status);
			}else{
				$("#booking_link").show("slow");
				if (data.match(/^NOK:/)) {
					$("#booking_link").html(data);
					alert("哎呀，出错了:)\n"+data);
				}else{
					var actName = $("input[name='ActivityName']").val();
					var subject = "《"+actName+"》活动报名通知";
					$("input[name='subject']").val(subject);

					var bookingUrl = url + bcd;
					var bookingHref = "<a target=\"_blank\" href=\"" + bookingUrl + "\">" + bookingUrl + "</a>";
					var actInfo = $("textarea[name='Information']").val();
					if (actInfo) actInfo = "\n活动信息：" + actInfo;
					var body = "你好！\n\n欢迎报名参加《" + actName+"》活动！\n\n报名网址：" +
								bookingUrl + "，\n" + actInfo +
					           "\n\nwith best regards,\n\n" + personInfo.cil + "\n";
					$("textarea[name='body']").val(body);

					$("#booking_link").html("报名网址: <a target=\"_blank\" href=\"" + bookingUrl + "\">" + 
				                        bookingUrl + "</a>, 请务必先测试一下！");
					$("#booking_link").fadeOut().fadeIn();

					if(confirm('恭喜！保存成功。现在就发邮件广播吗？')){
						//alert('you clicked confirm');
						$("form[name='sendmail']").submit();
					}

					dataSaved = true;
					//$("#existing_actions").load("listActions.cgi" + "?action=" + bcd + "&" + Math.random()); 
					reload_action_list(bcd);
				}
			}
		}
	);
	return true;
}


function booking_save_as(){
	var new_code = prompt("请输入新的活动代码（仅限英文字母，数字，-，_", $("#booking_code").val())
	if (new_code != null && new_code != "")
    {
		var newValue = new_code.replace(/[^\w\-]/g, '');
		if (newValue != "") {
			$("#booking_code").val(newValue);
			$("input[name='action_code']").val(newValue);
			booking_confirm();
		}else{
			alert("输入错误！");
		}
    }
}



// recover the data from a json string which is returned from stored base.
function recoverData(jsonStr) {
	var jsonObj;
	try{
		jsonObj = JSON_parse(jsonStr);  
	}catch(e){
		alert("JSON parse error: " + e.message);
		return;
	}

	//alert(jsonObj.Admins);
	//alert(jsonKeys);
	for (var i=0; i<jsonKeys.length; i++){
		//alert(jsonObj[jsonKeys[i]]);
		var $id = $("[name='" + jsonKeys[i] + "']");
		var v = jsonObj[jsonKeys[i]];
		if (v != undefined) {
			//if (jsonKeys[i] == "Information") {
				try {
					v = v.replace(/<br>/ig,"\n").replace(/&amp;/g,'&').replace(/&lt;/g,'<');
					v = v.replace(/&gt;/g,'>').replace(/&nbsp;/g,' ').replace(/&qout;/g,'"');
				}catch(e){}
			//}
			$id.val(v);
		}
	}
	
	// for picture upload
	//alert($("[name='action_code']").val());
	$("#upload_action_code").val($("[name='action_code']").val());
	
	var inputs = new Array;
	inputs = jsonObj['Inputs'];
	
	var showWhens = new Array;
	showWhens = jsonObj['ShowWhens'];
	
	// remove all input rows but header.
	var trs = $("#table_inputs tr");
	for (var i=1; i<$(trs).length; i++){
		$(trs[i]).remove();
	}
	
	// now add input rows.
	for (var i=0; i<inputs.length; i++){
		//alert(inputs[i]);
		var input1 = inputs[i].split(/\s*,\s*/);
		if (input1.length<2) {
			continue;
		}
		
		// insert one more row.
		showOneMoreInput();
		var tr = $("#table_inputs tr")[i+1];
		
		// fill contents
		var name = input1[0];
		var type = input1[1].toLowerCase();
		var rows_size_opts = input1[2];
		var cols = input1[3];
		
		var selector = '{"subtitle":1, "radio":2, "checkbox":3, "select":4, "select-counted":5, "text":6, "textarea":7}';
		
		try{
			jsonObj = JSON_parse(selector);  
		}catch(e){
			alert("JSON parse error: " + e.message);
			return;
		}
		
		var idx = jsonObj[type];
		if (idx == undefined) idx = 0;
		$(tr).find("select").val(idx);
		//changeInput($(tr).find(".input_name"));  // find only for class!!

		$(tr).find(".input_name").html(input_name[idx]);
		$(tr).find(".input_item").html(options[idx]);
		
		// for selectable items, do not split them with ','.
		if (idx >=2 && idx <=5) {
			for (var j=3; j<input1.length; j++){
				rows_size_opts += "," + input1[j];
			}
		}
		
		// e.g. $("[name='action_code']")
		$(tr).find(".input_name").find("[name='" + type + "']").val(name);
		$(tr).find(".input_item").find("[name='" + type + "']").val(rows_size_opts);
		if (type == "textarea") {
			$(tr).find(".input_item").find("[name='" + type + "_cols']").val(cols);
		}
	}

	// now add show_when conditions.
	for (var i=0; i<showWhens.length; i++){
		//alert(showWhens[i]);
		var tr = $("#table_inputs tr")[i+1];
		
		var re = new RegExp('^, 1, (.+), (.+), (.+)', "g"); // e.g. ", 1, 性别, ==, 男"
		if (re.exec(showWhens[i])) {
			var selectedItem  = RegExp.$1;
			var judgeCond     = RegExp.$2;
			var selectedValue = RegExp.$3;
		
			$(tr).find('select[name=disp_switch]').val("1");
			$(tr).find('select[name=disp_item]').show();
			$(tr).find('select[name=disp_cond]').show();
			$(tr).find('select[name=disp_value]').show();
			
			
			//var disp_switch_i = $($trs[i]).find("select[name=disp_switch]")[0];
			var disp_switch_id = $(tr).find("select[name=disp_switch]")[0];
			var disp_item_id   = $(tr).find("select[name=disp_item]")[0];
			refresh_disp_cond(disp_switch_id, selectedItem);
			$(tr).find('select[name=disp_cond]').val(judgeCond);
			refresh_disp_value(disp_item_id, selectedValue);
			
		}else{
			$(tr).find('select[name=disp_switch]').val("0");
			$(tr).find('select[name=disp_item]').hide();
			$(tr).find('select[name=disp_cond]').hide();
			$(tr).find('select[name=disp_value]').hide();
		}
	}
	
	// now refresh
	var id = $("[name='ActivityName']")[0];
	ActivityName_check(id);
	refreshCfg();
}

// check the action code to avoid conflicts.
function action_code_check(){
	var id = $("[name='action_code']")[0];
	//alert(id.value);
	var newValue = id.value.replace(/[^\w\-]/g, '').toLowerCase();
	if (id.value != newValue || newValue == ""){
		id.value  = newValue;
		$(id).parent().parent().find(".remark").fadeOut("fast").fadeIn("fast");
		$(id).parent().parent().find(".remark").fadeOut("fast").fadeIn("fast");
	}
	
	return newValue == ""? false:true;
}

// check ActivityName 
function ActivityName_check(){
	var id = $("[name='ActivityName']")[0];
	//alert(id.value);
	var newValue = id.value.replace(/^\s+/, '').replace(/\s+$/, '');
	id.value  = newValue;
	if (newValue == ""){
		$(id).parent().parent().find(".remark").fadeOut("fast").fadeIn("fast");
		$(id).parent().parent().find(".remark").fadeOut("fast").fadeIn("fast");
		return false;
	}
	return true;
}

function action_code_changes(){
	$("#part_all").fadeTo("fast",0.15);
	if (action_code_check() == false){
		return false;
	}

	$.get("dataCheck.cgi",
		{
		  action_name: $("[name='action_code']").val(),
		  random: Math.random()
		},
		function(data,status){
			//alert("数据：" + data + "\n状态：" + status);
			if(status == "error") {
				return false;
			}else{
				if (data.match(/^OK:/i))  {
					if (data.match(/^OK:modify/i))  {
						var jsonStr = data.replace(/^.*?\n/, ""); // remove the first line.
						//alert(jsonStr);
						recoverData(jsonStr);
						if ($("input:radio[name='todo']:checked").val() == 1) {
							alert("活动已经存在，如果不想覆盖原活动，请在最后一步选择“另存新活动”！");
						}
					}else{
						// newly created action. fine.
						initConfigPreview();
					}
					$("#part_all").fadeTo("slow",1);;
				}else{
					alert("和别人的活动代码冲突，请换个代码！");
					return false;
				}
				
			}
		}
	); // $.get()
	return true;
}


function todo_changes(c) {
	if (c==last_todo) return;
	last_todo = c;
	
	if (c == 1) {
		$("#todo_1").show("");
		$("#todo_2").hide("");
		$("#td_todo1").css("background-color","#eee");
		$("#td_todo2").css("background-color","#fff");
	}else{
		$("#todo_2").show("");
		$("#todo_1").hide("");
		$("#td_todo2").css("background-color","#eee");
		$("#td_todo1").css("background-color","#fff");
		//$("#existing_actions").load("listActions.cgi?" + Math.random());
		reload_action_list();
	}
	$("#part_all").hide();
}

function pre_cfg_confirm(){
	var v = $("#pre_action_code").val();
	var id = $("[name='action_code']")[0];
	id.value = v;
	$("#pre_action_code").val(v.replace(/[^\w\-]/g, '').toLowerCase());
	action_code_changes();
}

function pre_actions(v){
	$("#part_all").show();
	if (v==last_pre_action) return;
	last_pre_action = v;

	var id = $("[name='action_code']")[0];
	id.value = v;

	action_code_changes();
}

function pre_actions_2(v,idx){
	$('input:radio[name=pre_existing_actions]').attr('checked',false);
	$('input:radio[name=pre_existing_actions]')[idx].checked = true;
//	$('input:radio[value='+v+']').attr('checked',true);
	pre_actions(v);
}

function lock_action(action){
//	$("#existing_actions").load("listActions.cgi?action="+action+"&do=lock" + "&" + Math.random());
		reload_action_list(action, "lock");
}
function unlock_action(action){
//	$("#existing_actions").load("listActions.cgi?action="+action+"&do=unlock" + "&" + Math.random());
		reload_action_list(action, "unlock");
}

function delete_action(action){
	//alert(action);
    if(confirm('真的要彻底删除 '+action+' 的报名入口和所有报名记录？')){
        //alert('you clicked confirm');
		//$("#existing_actions").load("listActions.cgi?action="+action+"&do=delete" + "&" + Math.random());
		reload_action_list(action, "delete");
    }
};

function reload_action_list(action, doWhat){
	var url = "listActions.cgi?random=" + Math.random();
	if (action) url += "&action=" + action ;
	if (doWhat) url += "&do=" + doWhat;
	$("#existing_actions").load(url, delWinD);
	showWinD();
}

function initConfigPreview(){
	// keep necessary data
	var action_code = $("input[name='action_code']").val();

	// clean up all
	$("#table_action_info input.cfg").val("");
	$("#table_action_info textarea.cfg").val("");
	$("#table_action_info div#feedback").html("");
	
	// recover necessary data
	$("input[name='action_code']").val(action_code);
	$("input[name='Admins']").val(personInfo_user);
	
	// remove all input rows but header.
	var trs = $("#table_inputs tr");
	for (var i=1; i<$(trs).length; i++){
		$(trs[i]).remove();
	}
	
	// reset preview
	$("textarea#input_preview").text("");
	$("#booking_preview").html("");
}


