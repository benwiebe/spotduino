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