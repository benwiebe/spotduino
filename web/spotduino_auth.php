<!--

This file is part of Spotduino.

Spotduino is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Spotduino is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Spotduino.  If not, see <http://www.gnu.org/licenses/>.

-->
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