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
<html>
	<?php

		if(isset($_GET['error'])){
			$reason = $_GET['error'];
			die("Authorization Failed! Reason: {$reason}");
		}else{
			$authcode = $_GET['code'];
			echo("Your auth code is:<br /> {$authcode}");
		}
		
	?>
</html>