#!/usr/bin/perl -w
use strict;
use CGI;

my $cgi = new CGI;

my $file = "." . $ENV{"PATH_INFO"};

if ($file !~ /\w/) {
	print "Content-type: text/html; charset=utf-8\n\n";
	exit 0;
}


=content-type
    text/html ： HTML格式
    text/plain ：纯文本格式      
    text/xml ：  XML格式
    image/gif ：gif图片格式    
    image/jpeg ：jpg图片格式 
    image/png：png图片格式

	以application开头的媒体格式类型：

    application/xhtml+xml ：XHTML格式
    application/xml     ： XML数据格式
    application/atom+xml  ：Atom XML聚合格式    
    application/json    ： JSON数据格式
    application/pdf       ：pdf格式  
    application/msword  ： Word文档格式
    application/octet-stream ： 二进制流数据（如常见的文件下载）
    application/x-www-form-urlencoded ： <form encType=””>中默认的encType，form表单数据被编码为key/value格式发送到服务器（表单默认的提交数据的格式）
=cut

my %contentType = ('html' => 'text/html', 
                   'htm'  => 'text/html',
				   'xml'  => 'text/xml',
                   'css'  => 'text/css',
				   'js'   => 'text/javascript',
				   'gif'  => 'image/gif',
				   'jpeg' => 'image/jpeg',
				   'jpg'  => 'image/jpeg',
				   'png'  => 'image/png');

my $contentType = "image/jpeg";  # default value
foreach my $suffix(keys %contentType) {
	if ($file =~ /\.$suffix$/i) {
		$contentType = $contentType{$suffix};
		last;
	}
}
print "Content-type: $contentType; charset=utf-8\n\n";

unless (open (OPENFILE, "$file")) {
	print "Failed to open \"$file\".";
	exit 0;
}

if ($contentType =~ /^text/) {
	print $_ while (<OPENFILE>);
	close (OPENFILE);
}else{
	binmode(OPENFILE);
	my $buffer = "";
	while(read(OPENFILE, $buffer, 1024)) {
        print "$buffer";
    }
    close(OPENFILE);
}

exit 0;


