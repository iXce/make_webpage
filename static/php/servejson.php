<?php

if (!isset($_GET['json'])) {
    header("HTTP/1.0 404 Not Found");
    die();
}

$json = basename($_GET['json']);
$jsonpath = "../../json/" . $json;
$jsonpathgz = $jsonpath . '.gz';
if (!is_file($jsonpath)) {
    header("HTTP/1.0 404 Not Found");
    die();
}

$supportsGzip = strpos($_SERVER['HTTP_ACCEPT_ENCODING'], 'gzip') !== false;

header('Content-Type: application/json');
if ($supportsGzip && is_file($jsonpathgz)) {
    header('Content-Encoding: gzip');
    header('Vary: Accept-Encoding');
    header('Content-Length: ' . filesize($jsonpathgz));
    readfile($jsonpathgz);
} else {
    header('Content-Length: ' . filesize($jsonpathgz));
    readfile($jsonpath);
}

?>
