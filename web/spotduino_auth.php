<?php
	$client_id = "YOUR_CLIENT_ID";
	$client_secret = "YOUR_CLIENT_SECRET";
	$redirect_uri = "YOUR_REDIRECT_URI";
	//see https://developer.spotify.com/web-api/using-scopes/
	$scopes = "user-library-read user-library-modify playlist-read-private";
	//see https://developer.spotify.com/web-api/authorization-guide/
	$query_url = "https://accounts.spotify.com/authorize?client_id={$client_id}&response_type=code&redirect_uri={$redirect_uri}&scope={$scopes}&show_dialog=false";
?>

<html>
	<head>
		<h1>Spotduino Authorization Portal</h1>
	</head>
	<body>
		<a href="<?php echo($query_url);?>">Click Here to Start Authorization</a>
	</body>
</html>