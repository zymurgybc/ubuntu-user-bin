#!/usr/bin/perl

use LWP::Simple;

my($HTML) = get("http://www.whatismyip.com/"); 
print($HTML, "\r\n\r\n");
my($IP) = $HTML =~m/(\d+\.\d+\.\d+\.\d+)/;
print($IP, "\r\n");
