#!/usr/bin/perl -w
use strict;
use Spreadsheet::WriteExcel;
use Encode;

my $workbook  = Spreadsheet::WriteExcel->new('/var/www/html/fnrd/filename.xls');
#my $worksheet = $workbook->add_worksheet();
my $worksheet = $workbook->add_worksheet("\x{E4BDA0}"); 
$worksheet->write(0, 0, '0,0: Hi Excel!');
$worksheet->write(0, 1, '0,1: Hi Excel! '."\x{E4BDA0}\x{E5A5BD}");
$worksheet->write(1, 0, decode('UTF-8','1,0: Hi Excel! 你好 你好'));
$worksheet->write(2, 0, decode('UTF8','2,0: Hi Excel! 你好 你好'));

$worksheet->write(1, 1, '1，1：Hi Excel!');
$worksheet->write(1, 2, '1，2：Hi Excel!');
$worksheet->write(1, 3, '1，3：Hi Excel!');
$worksheet->write(5, 5, '5，5：Hi Excel!');
$worksheet->write(6, 6, '6，6：Hi Excel!');

