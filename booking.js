
$(document).ready(function(){
	function resizeLogo(){ 
		$("#bannerImg").animate({width:('' + Math.round(967*60/80) + 'px'), height:'60px'});
		$("#spacer").animate({height:'8px'});
	};
	$("#bannerImg").click(function(){
		resizeLogo();
	});
	$("#spacer").click(function(){
		$("#bannerImg").animate({width:('' + Math.round(967*30/80) + 'px'), height:'30px'});
		$("#spacer").animate({height:'8px'});
	});
	setTimeout(opacifyLogo,2000); 
	function opacifyLogo(){
		$("#bannerImg").css({ opacity: .4 });
		$("#spacer").css({ opacity: .4 });
	};
}); 

	
function id(id) { 
	return document.getElementById(id);
};

window.onload = function() { 
	var left = id("left");
	var right = id("right");
	var middle = id("middle"); 
	var middleWidth=9; 
	if (middle == null) {return false;}
	middle.onmousedown = function(e) { 
		var disX = (e || event).clientX; 
		middle.left = middle.offsetLeft; 
		document.onmousemove = function(e) { 
			var iT = middle.left + ((e || event).clientX - disX); 
			var e=e||window.event,tarnameb=e.target||e.srcElement; 
			maxT=document.body.clientWidth; 
			iT < 0 && (iT = 0); 
			iT > maxT && (iT = maxT); 
			middle.style.left = left.style.width = iT + "px"; 
			right.style.width = document.body.clientWidth - iT -middleWidth + "px"; 
			right.style.left = iT+middleWidth+"px"; 
			return false;
		}; 
		document.onmouseup = function() { 
			document.onmousemove = null; 
			document.onmouseup = null; 
			middle.releaseCapture && middle.releaseCapture() 
		}; 
		middle.setCapture && middle.setCapture(); 
		return false;
	}; 
};

function deleteBooking(){
    if(confirm('真的要取消报名吗？不能后悔哦！')){
        //alert('you clicked confirm');
		var deletingForm = document.getElementById('deleting');
		if (deletingForm) {
			deletingForm.submit();
		}else{
			alert("deletingForm not found!");
		}
    }else{
        //alert('you clicked cancel');
    }
    return false;
};

// check whether madatory fields have content.
function checkBooking(){
    var $trs = $("#table_login_input").children().children();
	for (var i=0; i<$trs.length; i++){
		if ($($trs[i]).css("display") == "none") continue; // ignore hidden rows
		
		var $in = $($trs[i]).find("input[type='text']");
		if ($in.length >= 1) {
			if ($.trim($($in[0]).val()) == "") {
				alert ("请填写“" + $($trs[i]).children('th').text() + "”。\n\n如无，请填‘无’。");
				$($trs[i]).fadeOut().fadeIn().focus();
				return false;
			}
		}

		$in = $($trs[i]).find("input[type='radio']");
		if ($in.length >= 1) {
			if ($($trs[i]).find("input[type='radio']:checked").length == 0) {
				alert ("请选择“" + $($trs[i]).children('th').text() + "”！");
				$($trs[i]).fadeOut().fadeIn().focus();
				return false;
			}
		}

		$in = $($trs[i]).find("input[type='select']");
		if ($in.length >= 1) {
			if ($in.val() == undefined) {
				alert ("请选择“" + $($trs[i]).children('th').text() + "”！");
				$($trs[i]).fadeOut().fadeIn().focus();
				return false;
			}
		}
	}
	$("form#booking").submit();
	return true;
};



var isshow=0;//0小窗口没有显示，1小窗口已显
function createWinD()
{			
	var msgw,msgh,bordercolor;
	msgw=200;//提示窗口的宽度
	msgh=80;//提示窗口的高度
	var sWidth,sHeight;
	if( top.location == self.location )
		doc = document;
	var docElement = doc.documentElement;
	sWidth=docElement.clientWidth;
	sHeight = docElement.clientHeight;
	if( docElement.scrollHeight > sHeight )
		sHeight = docElement.scrollHeight;
	var bgObj=document.createElement("div");
	bgObj.setAttribute('id','bgDiv');
	bgObj.style.position="absolute";
	bgObj.style.top="0";
	bgObj.style.left="0";
	bgObj.style.background="#fff";
	bgObj.style.filter="progid:DXImageTransform.Microsoft.Alpha(style=3,opacity=25,finishOpacity=75";
	bgObj.style.opacity="0.6";
	bgObj.style.width=sWidth + "px";
	bgObj.style.height=sHeight + "px";
	bgObj.style.zIndex = "10000";
	document.body.appendChild(bgObj);
		
	var msgObj=document.createElement("div");
	msgObj.setAttribute("id","msgDiv");
	msgObj.setAttribute("align","center");
	msgObj.style.position = "absolute";
    msgObj.style.left = "50%";
    msgObj.style.background="#fff";
    msgObj.style.marginLeft = "0px" ;
    //msgObj.style.top = (document.documentElement.clientHeight/2+document.documentElement.scrollTop)+"px";
    msgObj.style.top = "50%";
    msgObj.style.width = msgw + "px";
    msgObj.style.height =msgh + "px";
    msgObj.style.border = "1px";
    msgObj.style.zIndex = "10001";
    msgObj.innerHTML = "<br />请稍候...<br /><br /><a href=\"javascript:void(0);\" onclick='delWinD();return false;'>X</a>";
    document.body.appendChild(msgObj); 
}
function delWinD()
{
   document.getElementById("bgDiv").style.display="none";
   document.getElementById("msgDiv").style.display="none";
   isshow=0;
}
function showWinD()
{   
    isshow=1;
    if(!document.getElementById("msgDiv"))//小窗口不存在
        createWinD();
    else
    {
        document.getElementById("bgDiv").style.display="";
        document.getElementById("msgDiv").style.display="";
        document.getElementById("msgDiv").style.top=(document.documentElement.clientHeight/2+document.documentElement.scrollTop-252)+"px";
    }  
}





