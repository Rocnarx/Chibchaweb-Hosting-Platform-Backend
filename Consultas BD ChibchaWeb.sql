

-- Agregar item (dominio) al carrito

	--Para agregar un dominio al carrito se debe primero Agregar
	--1 Agregar la cuenta
		--La identificacion y el correo deben ser unicos
		--el idCuenta se genera a partir de un numero aleatorio del 1-9 y el instante actual lo que 		genera que no se repita ningun ID

-- DONE!
	--INSERT INTO railway.CUENTA
	--(IDCUENTA, IDTIPOCUENTA, IDPAIS, IDPLAN, PASSWORD, IDENTIFICACION, NOMBRECUENTA, CORREO, TELEFONO, 	FECHAREGISTRO, DIRECCION)
	--VALUES(concat(FLOOR(1 + RAND() * 9),DATE_FORMAT(NOW(),'%Y%m%d%H%i%s')), 1, 170, '0', '1234', '12377457', 'Juan Perez', 'Juanr2@mail.com', 1234567, NOW(), 'carrera 55');


	--2 Agregar la tarjeta
		--Una tarjeta puede estar registrada solo una vez en el sistema pero puede estar en multiples 		cuentas

	--INSERT INTO railway.TARJETA
	--( IDTIPOTARJETA, NUMEROTARJETA, CCV, FECHAVTO)
	--VALUES( 1, 123457, 336, '2030-01-01');

	--3 Agregar el MetodoPagoCuenta

	--INSERT INTO railway.METODOPAGOCUENTA
	--(IDMETODOPAGOCUENTA, IDTARJETA, IDCUENTA, IDTIPOMETODOPAGO, ACTIVOMETODOPAGOCUENTA)
	--VALUES('1', '1', '1', 1, 1);

	--4 Agregar el carrito

	|--INSERT INTO railway.CARRITO
	--( IDESTADOCARRITO, IDCUENTA, IDMETODOPAGOCUENTA)
	--VALUES( '0', '1', 1);

	--5 Agregar el dominio

	--INSERT INTO railway.DOMINIO
	--(IDDOMINIO, NOMBREPAGINA, PRECIODOMINIO, OCUPADO)
	--VALUES('1', 'PRUEBA.COM', 200, 0);

	--6 Agregar el carrito dominio

	--INSERT INTO railway.CARRITODOMINIO
	--(IDDOMINIO, IDCARRITO, IDCARRITODOMINIO)
	--VALUES('1', 1, '1');

	--7 Actualizar el estado del carrito a en proceso 
	--UPDATE railway.CARRITO
	--SET IDESTADOCARRITO='1'
	--WHERE IDCARRITO=1;

--Eliminar item del carrito

--	DELETE FROM railway.CARRITODOMINIO
--	WHERE IDDOMINIO='1' AND IDCARRITO=1 AND IDCARRITODOMINIO='1';

-- Obtener items actuales del carrito del ususario (ID-Nombre-Precio)
	--Carrito Con idEstadoCarrito=1 obtiene el carrito que tiene dominios en proceso de la cuenta, 
	--Carrito Con idEstadoCarrito=2 obtiene los carritos facturados de la cuenta
			
	--SELECT 
	--    C.IDCUENTA AS Cuenta,
	--    K.IDCARRITO AS Carrito,
	--    D.IDDOMINIO As IDDominio,
	--    D.NOMBREPAGINA AS Dominio,
	--    D.PRECIODOMINIO As Precio
	--FROM CUENTA C
	--INNER JOIN METODOPAGOCUENTA M ON C.IDCUENTA = M.IDCUENTA
	--INNER JOIN CARRITO K ON M.IDMETODOPAGOCUENTA = K.IDMETODOPAGOCUENTA
	--INNER JOIN CARRITODOMINIO CD ON K.IDCARRITO = CD.IDCARRITO
	----INNER JOIN DOMINIO D ON D.IDDOMINIO = CD.IDDOMINIO
	--WHERE K.IDESTADOCARRITO = 2 AND C.IDCUENTA = 2;

--Realizar el pago de un carrito
		--Insertar Factura
		
	--INSERT INTO railway.FACTURA ( IDCARRITO, PAGOFACTURA, VIGFACTURA)
	--VALUES ( 1, NOW(), DATE_ADD(NOW(), INTERVAL 2 YEAR));
	--
--	SELECT * FROM CARRITO ;
	
--Actualizar Carrito (Con la id de la factura recien creada)
		
		UPDATE railway.CARRITO
--		SET IDESTADOCARRITO = '2'
--		WHERE IDCARRITO = 1;
		
	--Crear nuevo carrito para el usuario	
	
	--	INSERT INTO railway.CARRITO
	--	(IDESTADOCARRITO, IDCUENTA, IDMETODOPAGOCUENTA)
	--	VALUES('0', 1 , '1');
		
		--Establecer el estado de dominio como ocupado (Como comprado)
		--Para actualizar este dominio se tuvo que haber registrado antes de comprarlo y 		preferiblemente agregar al carrito tambien
		
		UPDATE railway.DOMINIO
		SET OCUPADO= 1
		WHERE IDDOMINIO= '1';
		
		