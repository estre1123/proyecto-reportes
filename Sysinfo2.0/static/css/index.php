<!DOCTYPE html>
<html lang="es">
<head>
	<title>Sistema CTN</title>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
	<link rel="stylesheet" href="./css/main.css">
	</head>
<body class="cover" style="background-image: url(./assets/img/loginFont.jpg);">
	<form action="login.php" method="POST" autocomplete="off" class="full-box logInForm" >
		<p class="text-center text-muted"><i class="zmdi zmdi-account-circle zmdi-hc-5x"></i></p>
		<p class="text-center text-muted text-uppercase">Inicia sesión con tu cuenta</p>
		<div class="form-group label-floating">
		  <label class="control-label" for="UserUsuario">Usuario</label>
		  <input class="form-control" id="UserUsuario" type="text"  name="username" style="color:white"  required>
		  <p class="help-block">Escribe tu usuario</p>
		</div>
		<div class="form-group label-floating">
		  <label class="control-label" for="UserPass" >Contraseña</label>
		  <input style="color:white" class="form-control" id="UserPass" type="password" name="userpass"required >
		  <p class="help-block">Escribe tú contraseña</p>
		</div>
		<div class="form-group text-center">
			<input type="submit" value="Iniciar sesión" class="btn btn-raised btn-danger" name="enviar">
		</div>
	</form>
	
	<!--====== Scripts -->
	<script src="./js/jquery-3.1.1.min.js"></script>
	<script src="./js/bootstrap.min.js"></script>
	<script src="./js/material.min.js"></script>
	<script src="./js/ripples.min.js"></script>
	<script src="./js/sweetalert2.min.js"></script>
	<script src="./js/jquery.mCustomScrollbar.concat.min.js"></script>
	<script src="./js/main.js"></script>
	<script>
		$.material.init();
	</script>
</body>
</html>