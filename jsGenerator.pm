use strict;
use Encode;
use JSON;
sub jsGen4ShowWhen{
    my $showWhens = $_[0];
    my $js = "";
    my $showWhenStmts = "";
    my %op = ('eq' => '==',
              'gt' => '>',
              'ge' => '>=',
              'lt' => '<',
              'le' => '<=',
              'ne' => '!=');

    for (my $i=0; $i<@$showWhens; $i++){
        if ($$showWhens[$i] =~ /^, 1, (.+), (.+), (.+)/) {
            my $selectedItem  = $1 . ':';
            my $judgeCond     = $2;
            my $selectedValue = $3;
            
            $showWhenStmts .= <<__JS2 if $op{$judgeCond};
        if (th == '$selectedItem'){
            var currTr = \$("#table_login_input").find("tr")[$i];
			
			if(currTr == tr[0]) {
				alert("myself");
			}
			
            if (currSelVal $op{$judgeCond} '$selectedValue') {
                \$(currTr).show();
                \$(currTr).css("background-color","#eee");
            }else{ 
                \$(currTr).hide();
                
                // clean up if invisible
                \$(currTr).find("select").val("");
                \$(currTr).find("input:text").val("");
                \$(currTr).find("input:radio").attr("checked", false);
                \$(currTr).find("input:checkbox").attr("checked", false);
            }
        }
__JS2

        }
    }

    $js .= <<__JS1;
<script>

    
\$(document).ready(function(){
    \$("#table_login_input").find("select").change(function(){onChange(this)});
    \$("#table_login_input").find("input:radio").change(function(){onChange(this)});
    function onChange(id){
        var tr = \$(id).parent().parent();  // select -> td -> tr
        var th = \$(tr).children("th").html();
        //var disp = \$(tr).attr("display");
        var currSelVal = id.value;
        if (currSelVal == undefined ) return;
        //alert(th + " " + currSelVal);

$showWhenStmts
    }

    // init
    var selects = \$("#table_login_input").find("select");
    for (var i=0; i<selects.length; i++){
        onChange(selects[i]);
    }

    var radios = \$("#table_login_input").find("input:radio[checked=checked]");
    for (var i=0; i<radios.length; i++){
        onChange(radios[i]);
    }    
    
});
</script>
__JS1


    return $js;
}

1;
