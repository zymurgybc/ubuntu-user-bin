#!/usr/bin/perl

use LWP::UserAgent;
use LWP::Simple;
#use Data::Dumper;

my $UA = new LWP::UserAgent;
$UA->agent("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0"); # pretend we are very capable browser
my $REQ = new HTTP::Request 'GET' => 'https://www.whatismyip.com/';
$REQ->header('Accept' => 'text/html');

my $ua_response = $UA->request($REQ);
if ($ua_response->is_success) {
    #print Dumper($ua_response);

    #print($ua_response->content(), "\r\n\r\n");
    my $IP = $ua_response->content() =~m/(\d+\.\d+\.\d+\.\d+)/;
    # 2023-07-20 ... this isn't working as LWP::UserAgent isn't handling the Javascript and 
    # the page just contains "Loading..." at the target site before the JS runs.
    print("WhatsMyIP.com => ",$IP, "\r\n");
} else {
    die $ua_response->status_line;
}
