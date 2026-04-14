-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: crm_fabrica
-- ------------------------------------------------------
-- Server version	8.0.38

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auditoria_eventos`
--

DROP TABLE IF EXISTS `auditoria_eventos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auditoria_eventos` (
  `id_auditoria` bigint unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint unsigned DEFAULT NULL,
  `evento` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entidad` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entidad_id` bigint unsigned DEFAULT NULL,
  `descripcion` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_auditoria`),
  KEY `idx_auditoria_usuario` (`usuario_id`),
  KEY `idx_auditoria_entidad` (`entidad`,`entidad_id`),
  KEY `fk_auditoria_evento` (`evento`),
  CONSTRAINT `fk_auditoria_evento` FOREIGN KEY (`evento`) REFERENCES `cat_eventos` (`codigo`),
  CONSTRAINT `fk_auditoria_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auditoria_eventos`
--

LOCK TABLES `auditoria_eventos` WRITE;
/*!40000 ALTER TABLE `auditoria_eventos` DISABLE KEYS */;
INSERT INTO `auditoria_eventos` VALUES (1,NULL,'USUARIO_CREADO','usuarios',1,'Usuario creado: administrador (admin@concretum.com) - Tipo: EXTERNO',NULL,'2026-04-14 09:45:22'),(2,2,'USUARIO_CREADO','usuarios',2,'Usuario creado: ventas01 (ventas@concretum.com) - Tipo: EXTERNO',NULL,'2026-04-14 09:45:22'),(3,3,'USUARIO_CREADO','usuarios',3,'Usuario creado: compras01 (compras@concretum.com) - Tipo: EXTERNO',NULL,'2026-04-14 09:45:22'),(4,4,'USUARIO_CREADO','usuarios',4,'Usuario creado: almacen01 (almacen@concretum.com) - Tipo: EXTERNO',NULL,'2026-04-14 09:45:22'),(5,5,'USUARIO_CREADO','usuarios',5,'Usuario creado: produccion01 (produccion@concretum.com) - Tipo: EXTERNO',NULL,'2026-04-14 09:45:22'),(6,6,'USUARIO_CREADO','usuarios',6,'Usuario creado: cliente01 (cliente01@gmail.com) - Tipo: EXTERNO',NULL,'2026-04-14 09:45:22'),(7,NULL,'USUARIO_LOGIN','usuarios',1,'Inicio de sesión exitoso','Mozilla/5.0 (Windows NT 10.0; Win64; x64)','2026-02-01 08:30:00'),(8,2,'USUARIO_LOGIN','usuarios',2,'Inicio de sesión exitoso','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)','2026-02-01 09:15:00'),(9,3,'USUARIO_LOGIN','usuarios',3,'Inicio de sesión exitoso','Mozilla/5.0 (Windows NT 10.0; Win64; x64)','2026-02-03 10:00:00'),(10,NULL,'USUARIO_LOGIN_FALLIDO','usuarios',NULL,'Intento de login fallido para usuario: admin','Mozilla/5.0 (Linux; Android 10)','2026-02-02 15:30:00'),(11,NULL,'USUARIO_LOGIN_FALLIDO','usuarios',NULL,'Intento de login fallido para usuario: jperez','Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)','2026-02-03 11:45:00'),(12,NULL,'USUARIO_CREADO','usuarios',6,'Usuario creado: cliente01 (cliente01@gmail.com)','Mozilla/5.0 (Windows NT 10.0)','2026-02-01 12:00:00'),(13,NULL,'ROL_ASIGNADO','usuario_roles',1,'Rol ADMINISTRADOR asignado al usuario administrador','Mozilla/5.0 (Macintosh)','2026-01-20 09:00:00'),(14,2,'ROL_ASIGNADO','usuario_roles',2,'Rol VENTAS asignado al usuario ventas01','Mozilla/5.0 (Macintosh)','2026-01-20 09:30:00'),(15,3,'ROL_ASIGNADO','usuario_roles',3,'Rol COMPRAS asignado al usuario compras01','Mozilla/5.0 (Macintosh)','2026-01-21 10:00:00'),(16,4,'ROL_ASIGNADO','usuario_roles',4,'Rol ALMACEN asignado al usuario almacen01','Mozilla/5.0 (Macintosh)','2026-01-21 11:00:00'),(17,5,'ROL_ASIGNADO','usuario_roles',5,'Rol PRODUCCION asignado al usuario produccion01','Mozilla/5.0 (Macintosh)','2026-01-22 09:00:00'),(18,NULL,'ROL_ASIGNADO','usuario_roles',6,'Rol CLIENTE asignado al usuario cliente01','Mozilla/5.0 (Macintosh)','2026-01-22 10:15:00'),(19,6,'ACCESO_DENEGADO','usuarios',6,'Intento de acceso a módulo de administración sin permisos','Mozilla/5.0 (Windows NT 10.0)','2026-02-03 16:30:00'),(20,NULL,'USUARIO_LOGOUT','usuarios',1,'Cierre de sesión','Mozilla/5.0 (Windows NT 10.0)','2026-02-01 18:00:00'),(21,3,'USUARIO_LOGOUT','usuarios',3,'Cierre de sesión','Mozilla/5.0 (Windows NT 10.0)','2026-02-03 17:00:00'),(22,7,'USUARIO_CREADO','usuarios',7,'Usuario creado: admin (admin@concretum.com) - Tipo: EXTERNO',NULL,'2026-04-14 10:02:00'),(23,8,'USUARIO_CREADO','usuarios',8,'Usuario creado: ricardo (cliente@gmail.com) - Tipo: EXTERNO',NULL,'2026-04-14 10:03:38');
/*!40000 ALTER TABLE `auditoria_eventos` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_auditoria_before_insert` BEFORE INSERT ON `auditoria_eventos` FOR EACH ROW BEGIN
    DECLARE evento_existe INT;
    IF NEW.fecha_creacion IS NULL THEN
        SET NEW.fecha_creacion = NOW();
    END IF;
    SELECT COUNT(*) INTO evento_existe
    FROM cat_eventos WHERE codigo = NEW.evento AND es_activo = 1;
    IF evento_existe = 0 THEN
        INSERT IGNORE INTO cat_eventos (codigo, nombre, descripcion, es_activo)
        VALUES (NEW.evento, NEW.evento, CONCAT('Evento creado automáticamente el ', NOW()), 1);
    END IF;
    IF LENGTH(NEW.descripcion) > 500 THEN
        SET NEW.descripcion = CONCAT(LEFT(NEW.descripcion, 497), '...');
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `carrito_items`
--

DROP TABLE IF EXISTS `carrito_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carrito_items` (
  `id_item` bigint unsigned NOT NULL AUTO_INCREMENT,
  `carrito_id` bigint unsigned NOT NULL,
  `producto_id` bigint unsigned NOT NULL,
  `cantidad` int NOT NULL DEFAULT '1',
  `precio_unitario` decimal(12,2) NOT NULL,
  `fecha_agregado` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_item`),
  UNIQUE KEY `uq_item_producto` (`carrito_id`,`producto_id`),
  KEY `fk_item_producto` (`producto_id`),
  CONSTRAINT `fk_item_carrito` FOREIGN KEY (`carrito_id`) REFERENCES `carritos` (`id_carrito`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_item_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ck_item_cantidad` CHECK ((`cantidad` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carrito_items`
--

LOCK TABLES `carrito_items` WRITE;
/*!40000 ALTER TABLE `carrito_items` DISABLE KEYS */;
INSERT INTO `carrito_items` VALUES (2,1,1,102,15.50,'2026-04-14 17:05:37');
/*!40000 ALTER TABLE `carrito_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carritos`
--

DROP TABLE IF EXISTS `carritos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carritos` (
  `id_carrito` bigint unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint unsigned NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_carrito`),
  UNIQUE KEY `uq_carrito_usuario` (`usuario_id`),
  CONSTRAINT `fk_carrito_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carritos`
--

LOCK TABLES `carritos` WRITE;
/*!40000 ALTER TABLE `carritos` DISABLE KEYS */;
INSERT INTO `carritos` VALUES (1,8,'2026-04-14 16:03:58','2026-04-14 16:03:58');
/*!40000 ALTER TABLE `carritos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cat_eventos`
--

DROP TABLE IF EXISTS `cat_eventos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cat_eventos` (
  `codigo` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `es_activo` bigint NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cat_eventos`
--

LOCK TABLES `cat_eventos` WRITE;
/*!40000 ALTER TABLE `cat_eventos` DISABLE KEYS */;
INSERT INTO `cat_eventos` VALUES ('ACCESO_DENEGADO','Acceso Denegado','Intento de acceso sin permisos suficientes',1,'2026-04-14 09:45:22',NULL),('CONFIGURACION_MODIFICADA','Configuración Modificada','Se modificó configuración del sistema',1,'2026-04-14 09:45:22',NULL),('DATOS_EXPORTADOS','Datos Exportados','Se exportaron datos del sistema',1,'2026-04-14 09:45:22',NULL),('PERMISO_OTORGADO','Permiso Otorgado','Se otorgó un permiso a un rol',1,'2026-04-14 09:45:22',NULL),('PERMISO_REVOCADO','Permiso Revocado','Se revocó un permiso de un rol',1,'2026-04-14 09:45:22',NULL),('ROL_ASIGNADO','Rol Asignado','Se asignó un rol a un usuario',1,'2026-04-14 09:45:22',NULL),('ROL_REMOVIDO','Rol Removido','Se removió un rol de un usuario',1,'2026-04-14 09:45:22',NULL),('USUARIO_BLOQUEADO','Usuario Bloqueado','Usuario bloqueado por múltiples intentos fallidos',1,'2026-04-14 09:45:22',NULL),('USUARIO_CREADO','Usuario Creado','Se registró un nuevo usuario en el sistema',1,'2026-04-14 09:45:22',NULL),('USUARIO_DESBLOQUEADO','Usuario Desbloqueado','Usuario desbloqueado por administrador',1,'2026-04-14 09:45:22',NULL),('USUARIO_ELIMINADO','Usuario Eliminado','Se eliminó un usuario del sistema',1,'2026-04-14 09:45:22',NULL),('USUARIO_LOGIN','Inicio de Sesión','Usuario inició sesión en el sistema',1,'2026-04-14 09:45:22',NULL),('USUARIO_LOGIN_FALLIDO','Login Fallido','Intento de inicio de sesión fallido',1,'2026-04-14 09:45:22',NULL),('USUARIO_LOGOUT','Cierre de Sesión','Usuario cerró sesión',1,'2026-04-14 09:45:22',NULL),('USUARIO_MODIFICADO','Usuario Modificado','Se modificó información de un usuario',1,'2026-04-14 09:45:22',NULL);
/*!40000 ALTER TABLE `cat_eventos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias_producto`
--

DROP TABLE IF EXISTS `categorias_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_producto` (
  `id_categoria` bigint unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `es_activo` bigint NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `uq_categorias_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias_producto`
--

LOCK TABLES `categorias_producto` WRITE;
/*!40000 ALTER TABLE `categorias_producto` DISABLE KEYS */;
INSERT INTO `categorias_producto` VALUES (1,'Blocks de Concreto','Blocks prefabricados para muros estructurales y divisorios',1,'2026-04-14 09:45:22',NULL),(2,'Sistemas de Losa','Elementos prefabricados para construcción de losas',1,'2026-04-14 09:45:22',NULL),(3,'Losas Prefabricadas','Losas listas para instalación en obra',1,'2026-04-14 09:45:22',NULL),(4,'Paneles Prefabricados','Paneles de concreto para muros y fachadas',1,'2026-04-14 09:45:22',NULL),(5,'Urbanización','Elementos prefabricados para banquetas y vialidades',1,'2026-04-14 09:45:22',NULL),(6,'Infraestructura Urbana','Elementos para calles y obra pública',1,'2026-04-14 09:45:22',NULL),(7,'Registros Prefabricados','Cajas de concreto para instalaciones subterráneas',1,'2026-04-14 09:45:22',NULL),(8,'Tapas de Concreto','Tapas para registros y alcantarillado',1,'2026-04-14 09:45:22',NULL),(9,'Elementos Especiales','Prefabricados personalizados o de uso específico',1,'2026-04-14 09:45:22',NULL),(10,'Accesorios de Instalación','Componentes complementarios para montaje',1,'2026-04-14 09:45:22',NULL);
/*!40000 ALTER TABLE `categorias_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cliente_detalle`
--

DROP TABLE IF EXISTS `cliente_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente_detalle` (
  `id_detalle` bigint unsigned NOT NULL AUTO_INCREMENT,
  `cliente_id` bigint unsigned NOT NULL,
  `telefono` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `direccion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ciudad` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `codigo_postal` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notas` text COLLATE utf8mb4_unicode_ci,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_detalle`),
  UNIQUE KEY `uq_cliente_detalle_cliente` (`cliente_id`),
  CONSTRAINT `fk_cliente_detalle_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id_cliente`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente_detalle`
--

LOCK TABLES `cliente_detalle` WRITE;
/*!40000 ALTER TABLE `cliente_detalle` DISABLE KEYS */;
/*!40000 ALTER TABLE `cliente_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id_cliente` bigint unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint unsigned DEFAULT NULL,
  `razon_social` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rfc` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `es_activo` bigint NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  UNIQUE KEY `uq_clientes_rfc` (`rfc`),
  UNIQUE KEY `uq_clientes_email` (`email`),
  KEY `idx_clientes_razon` (`razon_social`),
  CONSTRAINT `fk_clientes_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES (1,8,'ricardo',NULL,'cliente@gmail.com',1,'2026-04-14 10:03:39',NULL);
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `colores`
--

DROP TABLE IF EXISTS `colores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `colores` (
  `id_color` bigint unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `clave` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `codigo_hex` varchar(7) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `es_activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_color`),
  UNIQUE KEY `clave` (`clave`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `colores`
--

LOCK TABLES `colores` WRITE;
/*!40000 ALTER TABLE `colores` DISABLE KEYS */;
INSERT INTO `colores` VALUES (1,'Gris Cemento','gris_cemento','#8A8A8A',1,'2026-04-14 09:45:22',NULL),(2,'Gris Claro','gris_claro','#B0B0B0',1,'2026-04-14 09:45:22',NULL),(3,'Gris Oscuro','gris_oscuro','#505050',1,'2026-04-14 09:45:22',NULL),(4,'Blanco','blanco','#FFFFFF',1,'2026-04-14 09:45:22',NULL),(5,'Arena','arena','#D9C7A3',1,'2026-04-14 09:45:22',NULL),(6,'Beige','beige','#F5F5DC',1,'2026-04-14 09:45:22',NULL),(7,'Café Oscuro','cafe_oscuro','#4B2E2B',1,'2026-04-14 09:45:22',NULL),(8,'Terracota','terracota','#E2725B',1,'2026-04-14 09:45:22',NULL),(9,'Rojo Ladrillo','rojo_ladrillo','#A63D2F',1,'2026-04-14 09:45:22',NULL),(10,'Negro','negro','#000000',1,'2026-04-14 09:45:22',NULL),(11,'Gris Antracita','antracita','#2E2E2E',1,'2026-04-14 09:45:22',NULL),(12,'Grafito','grafito','#3A3A3A',1,'2026-04-14 09:45:22',NULL),(13,'Verde Oliva','verde_oliva','#556B2F',1,'2026-04-14 09:45:22',NULL),(14,'Verde Musgo','verde_musgo','#4A5D23',1,'2026-04-14 09:45:22',NULL),(15,'Azul Acero','azul_acero','#4682B4',1,'2026-04-14 09:45:22',NULL),(16,'Ocre Tierra','ocre_tierra','#CC7722',1,'2026-04-14 09:45:22',NULL),(17,'Concreto Aparente','concreto_aparente','#9E9E9E',1,'2026-04-14 09:45:22',NULL),(18,'Granito Gris','granito_gris','#7D7D7D',1,'2026-04-14 09:45:22',NULL),(19,'Granito Negro','granito_negro','#1C1C1C',1,'2026-04-14 09:45:22',NULL);
/*!40000 ALTER TABLE `colores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compra_detalle`
--

DROP TABLE IF EXISTS `compra_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compra_detalle` (
  `id_detalle` bigint unsigned NOT NULL AUTO_INCREMENT,
  `compra_id` bigint unsigned NOT NULL,
  `materia_prima_id` bigint unsigned NOT NULL,
  `cantidad` decimal(14,3) NOT NULL,
  `precio_unitario` decimal(12,2) NOT NULL,
  `total_linea` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `fk_detalle_compra` (`compra_id`),
  KEY `fk_detalle_mp` (`materia_prima_id`),
  CONSTRAINT `fk_detalle_compra` FOREIGN KEY (`compra_id`) REFERENCES `compras` (`id_compra`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_detalle_mp` FOREIGN KEY (`materia_prima_id`) REFERENCES `materias_primas` (`id_materia_prima`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compra_detalle`
--

LOCK TABLES `compra_detalle` WRITE;
/*!40000 ALTER TABLE `compra_detalle` DISABLE KEYS */;
INSERT INTO `compra_detalle` VALUES (1,1,1,1000.000,12.50,12500.00),(2,2,2,50.000,450.00,22500.00),(3,3,5,50.000,85.00,4250.00),(4,4,3,20.000,380.00,7600.00),(5,5,1,3453.000,12.00,41436.00);
/*!40000 ALTER TABLE `compra_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compras`
--

DROP TABLE IF EXISTS `compras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras` (
  `id_compra` bigint unsigned NOT NULL AUTO_INCREMENT,
  `proveedor_id` bigint unsigned NOT NULL,
  `folio` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_compra` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `total` decimal(12,2) NOT NULL,
  `estado` enum('CREADA','RECIBIDA','CANCELADA') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'CREADA',
  PRIMARY KEY (`id_compra`),
  UNIQUE KEY `uq_compra_folio` (`folio`),
  KEY `fk_compra_proveedor` (`proveedor_id`),
  CONSTRAINT `fk_compra_proveedor` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id_proveedor`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras`
--

LOCK TABLES `compras` WRITE;
/*!40000 ALTER TABLE `compras` DISABLE KEYS */;
INSERT INTO `compras` VALUES (1,1,'OC-20260301-001','2026-03-01 10:30:00',12500.00,'RECIBIDA'),(2,2,'OC-20260305-002','2026-03-05 11:00:00',22500.00,'RECIBIDA'),(3,3,'OC-20260310-003','2026-03-10 09:15:00',4250.00,'RECIBIDA'),(4,2,'OC-20260401-004','2026-04-01 08:00:00',7600.00,'CREADA'),(5,1,'OC-20260414-6AFEC9','2026-04-14 23:59:59',41436.00,'CREADA');
/*!40000 ALTER TABLE `compras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `configuracion_empresa`
--

DROP TABLE IF EXISTS `configuracion_empresa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuracion_empresa` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `razon_social` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Mi Empresa',
  `rfc` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'XAXX010101000',
  `direccion` text COLLATE utf8mb4_unicode_ci,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email_facturacion` varchar(254) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `logo` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `alerta_stock_minimo` tinyint(1) NOT NULL DEFAULT '1',
  `alerta_vencimiento_credito` tinyint(1) NOT NULL DEFAULT '1',
  `alerta_merma_diaria` tinyint(1) NOT NULL DEFAULT '0',
  `moneda` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'MXN',
  `zona_horaria` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'America/Mexico_City',
  `actualizado_por` bigint unsigned DEFAULT NULL,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rfc` (`rfc`),
  KEY `fk_config_usuario` (`actualizado_por`),
  CONSTRAINT `fk_config_usuario` FOREIGN KEY (`actualizado_por`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuracion_empresa`
--

LOCK TABLES `configuracion_empresa` WRITE;
/*!40000 ALTER TABLE `configuracion_empresa` DISABLE KEYS */;
INSERT INTO `configuracion_empresa` VALUES (1,'CONCRETUM','XAXX010101000','Blvd. Universidad Tecnológica 225, San Carlos la Roncha, 37670 León de los Aldama, Gto.','4771234567','correo@empresa.com',NULL,1,1,0,'MXN','America/Mexico_City',NULL,'2026-04-14 09:45:22');
/*!40000 ALTER TABLE `configuracion_empresa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `corte_desglose`
--

DROP TABLE IF EXISTS `corte_desglose`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `corte_desglose` (
  `id_desglose` bigint unsigned NOT NULL AUTO_INCREMENT,
  `corte_id` bigint unsigned NOT NULL,
  `forma_pago` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `operaciones` int NOT NULL DEFAULT '0',
  `monto` decimal(12,2) NOT NULL DEFAULT '0.00',
  `es_credito` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_desglose`),
  KEY `idx_desglose_corte` (`corte_id`),
  CONSTRAINT `fk_desglose_corte` FOREIGN KEY (`corte_id`) REFERENCES `cortes_caja` (`id_corte`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `corte_desglose`
--

LOCK TABLES `corte_desglose` WRITE;
/*!40000 ALTER TABLE `corte_desglose` DISABLE KEYS */;
/*!40000 ALTER TABLE `corte_desglose` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cortes_caja`
--

DROP TABLE IF EXISTS `cortes_caja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cortes_caja` (
  `id_corte` bigint unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint unsigned DEFAULT NULL,
  `periodo_inicio` datetime NOT NULL,
  `periodo_fin` datetime DEFAULT NULL,
  `fondo_inicial` decimal(12,2) NOT NULL DEFAULT '0.00',
  `total_ventas` decimal(12,2) NOT NULL DEFAULT '0.00',
  `total_cobrado` decimal(12,2) NOT NULL DEFAULT '0.00',
  `ventas_credito` decimal(12,2) NOT NULL DEFAULT '0.00',
  `devoluciones` decimal(12,2) NOT NULL DEFAULT '0.00',
  `salida_proveedores` decimal(12,2) NOT NULL DEFAULT '0.00',
  `utilidad` decimal(12,2) NOT NULL DEFAULT '0.00',
  `estado` enum('ABIERTO','CERRADO') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ABIERTO',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_corte`),
  KEY `idx_corte_usuario` (`usuario_id`),
  KEY `idx_corte_fecha` (`periodo_inicio`),
  CONSTRAINT `fk_corte_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cortes_caja`
--

LOCK TABLES `cortes_caja` WRITE;
/*!40000 ALTER TABLE `cortes_caja` DISABLE KEYS */;
/*!40000 ALTER TABLE `cortes_caja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cotizaciones`
--

DROP TABLE IF EXISTS `cotizaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cotizaciones` (
  `id_cotizacion` bigint unsigned NOT NULL AUTO_INCREMENT,
  `folio` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `usuario_id` bigint unsigned NOT NULL,
  `estado` enum('BORRADOR','ENVIADA','ACEPTADA','RECHAZADA','EXPIRADA') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'BORRADOR',
  `subtotal` decimal(12,2) NOT NULL DEFAULT '0.00',
  `iva` decimal(12,2) NOT NULL DEFAULT '0.00',
  `total` decimal(12,2) NOT NULL DEFAULT '0.00',
  `notas` text COLLATE utf8mb4_unicode_ci,
  `fecha_expiracion` date DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cotizacion`),
  UNIQUE KEY `uq_cotizacion_folio` (`folio`),
  KEY `idx_cot_usuario` (`usuario_id`),
  CONSTRAINT `fk_cot_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cotizaciones`
--

LOCK TABLES `cotizaciones` WRITE;
/*!40000 ALTER TABLE `cotizaciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `cotizaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cotizaciones_detalle`
--

DROP TABLE IF EXISTS `cotizaciones_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cotizaciones_detalle` (
  `id_detalle` bigint unsigned NOT NULL AUTO_INCREMENT,
  `cotizacion_id` bigint unsigned NOT NULL,
  `producto_id` bigint unsigned NOT NULL,
  `cantidad` decimal(14,3) NOT NULL,
  `precio_unitario` decimal(12,2) NOT NULL,
  `total_linea` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `fk_cotdet_cotizacion` (`cotizacion_id`),
  KEY `fk_cotdet_producto` (`producto_id`),
  CONSTRAINT `fk_cotdet_cotizacion` FOREIGN KEY (`cotizacion_id`) REFERENCES `cotizaciones` (`id_cotizacion`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cotdet_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cotizaciones_detalle`
--

LOCK TABLES `cotizaciones_detalle` WRITE;
/*!40000 ALTER TABLE `cotizaciones_detalle` DISABLE KEYS */;
/*!40000 ALTER TABLE `cotizaciones_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estados_pedido`
--

DROP TABLE IF EXISTS `estados_pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estados_pedido` (
  `id_estado` bigint unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `orden` int NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_estado`),
  UNIQUE KEY `uq_estados_nombre` (`nombre`),
  UNIQUE KEY `uq_estados_orden` (`orden`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estados_pedido`
--

LOCK TABLES `estados_pedido` WRITE;
/*!40000 ALTER TABLE `estados_pedido` DISABLE KEYS */;
INSERT INTO `estados_pedido` VALUES (1,'Nuevo',1,'2026-04-14 09:45:22'),(2,'En Proceso',2,'2026-04-14 09:45:22'),(3,'En Producción',3,'2026-04-14 09:45:22'),(4,'Listo',4,'2026-04-14 09:45:22'),(5,'Entregado',5,'2026-04-14 09:45:22'),(6,'Cancelado',6,'2026-04-14 09:45:22');
/*!40000 ALTER TABLE `estados_pedido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `existencias`
--

DROP TABLE IF EXISTS `existencias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `existencias` (
  `id_existencias` bigint unsigned NOT NULL AUTO_INCREMENT,
  `producto_id` bigint unsigned NOT NULL,
  `stock_actual` decimal(14,3) NOT NULL DEFAULT '0.000',
  `stock_minimo` decimal(14,3) NOT NULL,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `estado_stock` enum('BAJO','PRECAUCION','ALTO') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ALTO',
  PRIMARY KEY (`id_existencias`),
  UNIQUE KEY `uq_existencias_producto` (`producto_id`),
  CONSTRAINT `fk_existencias_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ck_existencias_stock` CHECK ((`stock_actual` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `existencias`
--

LOCK TABLES `existencias` WRITE;
/*!40000 ALTER TABLE `existencias` DISABLE KEYS */;
INSERT INTO `existencias` VALUES (1,1,240.000,100.000,'2026-04-14 09:45:22','ALTO'),(2,2,17.000,100.000,'2026-04-14 10:05:36','BAJO'),(3,3,150.000,50.000,'2026-04-14 09:45:22','ALTO'),(4,4,95.500,50.000,'2026-04-14 09:45:22','PRECAUCION'),(5,5,12.000,50.000,'2026-04-14 09:45:22','BAJO'),(6,6,34.000,50.000,'2026-04-14 09:45:22','BAJO'),(7,7,60.000,20.000,'2026-04-14 09:45:22','ALTO'),(8,8,45.000,20.000,'2026-04-14 09:45:22','ALTO'),(9,9,8.000,20.000,'2026-04-14 09:45:22','BAJO'),(10,10,22.000,20.000,'2026-04-14 09:45:22','PRECAUCION');
/*!40000 ALTER TABLE `existencias` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_existencias_before_insert` BEFORE INSERT ON `existencias` FOR EACH ROW BEGIN
    IF NEW.stock_actual <= NEW.stock_minimo THEN
        SET NEW.estado_stock = 'BAJO';
    ELSEIF NEW.stock_actual <= (NEW.stock_minimo * 2) THEN
        SET NEW.estado_stock = 'PRECAUCION';
    ELSE
        SET NEW.estado_stock = 'ALTO';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_existencias_before_update` BEFORE UPDATE ON `existencias` FOR EACH ROW BEGIN
    IF NEW.stock_actual <= NEW.stock_minimo THEN
        SET NEW.estado_stock = 'BAJO';
    ELSEIF NEW.stock_actual <= (NEW.stock_minimo * 2) THEN
        SET NEW.estado_stock = 'PRECAUCION';
    ELSE
        SET NEW.estado_stock = 'ALTO';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `existencias_materia_prima`
--

DROP TABLE IF EXISTS `existencias_materia_prima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `existencias_materia_prima` (
  `id_existencia_mp` bigint unsigned NOT NULL AUTO_INCREMENT,
  `materia_prima_id` bigint unsigned NOT NULL,
  `stock_actual` decimal(14,3) NOT NULL DEFAULT '0.000',
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_existencia_mp`),
  UNIQUE KEY `uq_mp_existencia` (`materia_prima_id`),
  CONSTRAINT `fk_mp_existencia` FOREIGN KEY (`materia_prima_id`) REFERENCES `materias_primas` (`id_materia_prima`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `existencias_materia_prima`
--

LOCK TABLES `existencias_materia_prima` WRITE;
/*!40000 ALTER TABLE `existencias_materia_prima` DISABLE KEYS */;
INSERT INTO `existencias_materia_prima` VALUES (1,1,10000.000,'2026-04-14 09:45:22'),(2,2,50.000,'2026-04-14 09:45:22'),(3,3,50.000,'2026-04-14 09:45:22'),(4,4,20.000,'2026-04-14 09:45:22'),(5,5,500.000,'2026-04-14 09:45:22'),(6,6,200.000,'2026-04-14 09:45:22'),(7,7,3000.000,'2026-04-14 09:45:22');
/*!40000 ALTER TABLE `existencias_materia_prima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_compras`
--

DROP TABLE IF EXISTS `historial_compras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_compras` (
  `id_historial` bigint unsigned NOT NULL AUTO_INCREMENT,
  `compra_id` bigint unsigned NOT NULL,
  `accion` enum('CREADA','ACTUALIZADA','CANCELADA','RECIBIDA') COLLATE utf8mb4_unicode_ci NOT NULL,
  `comentario` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `modificado_por` bigint unsigned DEFAULT NULL,
  `fecha_modificacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_historial`),
  KEY `idx_hist_compra` (`compra_id`,`fecha_modificacion`),
  KEY `fk_hist_usuario` (`modificado_por`),
  CONSTRAINT `fk_hist_compra` FOREIGN KEY (`compra_id`) REFERENCES `compras` (`id_compra`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_hist_usuario` FOREIGN KEY (`modificado_por`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_compras`
--

LOCK TABLES `historial_compras` WRITE;
/*!40000 ALTER TABLE `historial_compras` DISABLE KEYS */;
INSERT INTO `historial_compras` VALUES (1,1,'CREADA','Compra registrada en el sistema',NULL,'2026-03-01 09:00:00'),(2,1,'RECIBIDA','Recepción normal',NULL,'2026-03-03 14:30:00'),(3,2,'CREADA','Compra registrada en el sistema',NULL,'2026-03-05 08:30:00'),(4,2,'RECIBIDA','Recepción normal',NULL,'2026-03-07 09:15:00'),(5,3,'CREADA','Compra registrada en el sistema',NULL,'2026-03-10 08:00:00'),(6,3,'RECIBIDA','Recepción normal',NULL,'2026-03-12 11:00:00'),(7,4,'CREADA','Compra creada',NULL,'2026-04-01 07:30:00'),(8,5,'CREADA','Compra generada automáticamente.',7,'2026-04-14 16:07:45');
/*!40000 ALTER TABLE `historial_compras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_estado_pedido`
--

DROP TABLE IF EXISTS `historial_estado_pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_estado_pedido` (
  `id_historial` bigint unsigned NOT NULL AUTO_INCREMENT,
  `pedido_id` bigint unsigned NOT NULL,
  `estado_id` bigint unsigned NOT NULL,
  `modificado_por_user_id` bigint unsigned DEFAULT NULL,
  `comentario` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_modificacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_historial`),
  KEY `idx_hist_pedido` (`pedido_id`,`fecha_modificacion`),
  KEY `idx_hist_estado` (`estado_id`),
  KEY `fk_hist_modificado_por` (`modificado_por_user_id`),
  CONSTRAINT `fk_hist_estado` FOREIGN KEY (`estado_id`) REFERENCES `estados_pedido` (`id_estado`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_hist_modificado_por` FOREIGN KEY (`modificado_por_user_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_hist_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id_pedido`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_estado_pedido`
--

LOCK TABLES `historial_estado_pedido` WRITE;
/*!40000 ALTER TABLE `historial_estado_pedido` DISABLE KEYS */;
/*!40000 ALTER TABLE `historial_estado_pedido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lotes_produccion`
--

DROP TABLE IF EXISTS `lotes_produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lotes_produccion` (
  `id_lote` bigint unsigned NOT NULL AUTO_INCREMENT,
  `produccion_id` bigint unsigned NOT NULL,
  `codigo_lote` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_fabricacion` date NOT NULL,
  PRIMARY KEY (`id_lote`),
  UNIQUE KEY `uq_lote_codigo` (`codigo_lote`),
  KEY `fk_lote_produccion` (`produccion_id`),
  CONSTRAINT `fk_lote_produccion` FOREIGN KEY (`produccion_id`) REFERENCES `producciones` (`id_produccion`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lotes_produccion`
--

LOCK TABLES `lotes_produccion` WRITE;
/*!40000 ALTER TABLE `lotes_produccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `lotes_produccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `materias_primas`
--

DROP TABLE IF EXISTS `materias_primas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materias_primas` (
  `id_materia_prima` bigint unsigned NOT NULL AUTO_INCREMENT,
  `sku` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unidad_medida` enum('KG','TON','M3','LTS') COLLATE utf8mb4_unicode_ci NOT NULL,
  `proveedor_id` bigint unsigned DEFAULT NULL,
  `stock_minimo` decimal(14,3) NOT NULL DEFAULT '0.000',
  `costo_unitario` decimal(12,2) NOT NULL DEFAULT '0.00',
  `es_activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_materia_prima`),
  UNIQUE KEY `uq_mp_sku` (`sku`),
  KEY `fk_mp_proveedor` (`proveedor_id`),
  CONSTRAINT `fk_mp_proveedor` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id_proveedor`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materias_primas`
--

LOCK TABLES `materias_primas` WRITE;
/*!40000 ALTER TABLE `materias_primas` DISABLE KEYS */;
INSERT INTO `materias_primas` VALUES (1,'MP-001','Cemento Portland','KG',1,2000.000,3.50,1,'2026-04-14 09:45:22'),(2,'MP-002','Arena','M3',4,15.000,220.00,1,'2026-04-14 09:45:22'),(3,'MP-003','Grava','M3',4,15.000,260.00,1,'2026-04-14 09:45:22'),(4,'MP-004','Agua','LTS',4,5000.000,0.03,1,'2026-04-14 09:45:22'),(5,'MP-005','Aditivo Plastificante','KG',3,100.000,48.00,1,'2026-04-14 09:45:22'),(6,'MP-006','Poliestireno Expandido','KG',3,100.000,38.00,1,'2026-04-14 09:45:22'),(7,'MP-007','Acero de Refuerzo','KG',2,500.000,19.50,1,'2026-04-14 09:45:22');
/*!40000 ALTER TABLE `materias_primas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mermas`
--

DROP TABLE IF EXISTS `mermas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mermas` (
  `id_merma` bigint unsigned NOT NULL AUTO_INCREMENT,
  `tipo_material` enum('MATERIA_PRIMA','PRODUCTO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `material_id` bigint unsigned NOT NULL,
  `cantidad` decimal(14,3) NOT NULL,
  `causa` enum('ROTURA','HUMEDAD','CADUCIDAD','PROCESO','TRANSPORTE') COLLATE utf8mb4_unicode_ci NOT NULL,
  `responsable` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `valor_monetario` decimal(12,2) NOT NULL,
  `usuario_id` bigint unsigned DEFAULT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `movimiento_id` bigint unsigned DEFAULT NULL,
  `produccion_id` bigint unsigned DEFAULT NULL,
  PRIMARY KEY (`id_merma`),
  KEY `idx_merma_fecha` (`fecha_registro`),
  KEY `fk_merma_usuario` (`usuario_id`),
  KEY `fk_merma_movimiento` (`movimiento_id`),
  KEY `fk_mermas_produccion` (`produccion_id`),
  CONSTRAINT `fk_merma_movimiento` FOREIGN KEY (`movimiento_id`) REFERENCES `movimientos_inventario` (`id_movimiento_in`) ON DELETE SET NULL,
  CONSTRAINT `fk_merma_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL,
  CONSTRAINT `fk_mermas_produccion` FOREIGN KEY (`produccion_id`) REFERENCES `producciones` (`id_produccion`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mermas`
--

LOCK TABLES `mermas` WRITE;
/*!40000 ALTER TABLE `mermas` DISABLE KEYS */;
/*!40000 ALTER TABLE `mermas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos_inventario`
--

DROP TABLE IF EXISTS `movimientos_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos_inventario` (
  `id_movimiento_in` bigint unsigned NOT NULL AUTO_INCREMENT,
  `existencia_id` bigint unsigned NOT NULL,
  `usuario_id` bigint unsigned DEFAULT NULL,
  `tipo` enum('ENTRADA','SALIDA','AJUSTE') COLLATE utf8mb4_unicode_ci NOT NULL,
  `cantidad` decimal(14,3) NOT NULL,
  `motivo` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_movimiento_in`),
  KEY `idx_mov_existencia` (`existencia_id`),
  KEY `idx_mov_usuario` (`usuario_id`),
  CONSTRAINT `fk_mov_existencia` FOREIGN KEY (`existencia_id`) REFERENCES `existencias` (`id_existencias`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_mov_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `ck_mov_cantidad` CHECK ((`cantidad` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_inventario`
--

LOCK TABLES `movimientos_inventario` WRITE;
/*!40000 ALTER TABLE `movimientos_inventario` DISABLE KEYS */;
INSERT INTO `movimientos_inventario` VALUES (1,1,NULL,'SALIDA',60.000,'Entrega a obra Fraccionamiento Las Palmas','2026-04-14 09:45:22'),(2,2,NULL,'SALIDA',82.000,'Entrega a obra Centro Comercial Norte','2026-04-14 09:45:22'),(3,4,NULL,'SALIDA',4.500,'Entrega a obra Bodega Industrial','2026-04-14 09:45:22'),(4,5,NULL,'SALIDA',8.000,'Entrega a obra Residencial Pedregal','2026-04-14 09:45:22'),(5,6,NULL,'SALIDA',16.000,'Entrega a obra Hospital Regional','2026-04-14 09:45:22'),(6,8,NULL,'SALIDA',5.000,'Ajuste por daño en almacén','2026-04-14 09:45:22'),(7,9,NULL,'SALIDA',22.000,'Entrega a obra Vialidad Periférico','2026-04-14 09:45:22'),(8,10,NULL,'AJUSTE',3.000,'Corrección por conteo físico','2026-04-14 09:45:22'),(9,2,7,'SALIDA',1.000,'Venta por pedido PED-20260414-AEA774','2026-04-14 10:05:36');
/*!40000 ALTER TABLE `movimientos_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificaciones_cliente`
--

DROP TABLE IF EXISTS `notificaciones_cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificaciones_cliente` (
  `id_notificacion` bigint unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint unsigned NOT NULL,
  `tipo` enum('INFO','PRODUCCION','STOCK','PAGO','ENTREGA') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'INFO',
  `titulo` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mensaje` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `leida` tinyint(1) NOT NULL DEFAULT '0',
  `referencia_id` bigint unsigned DEFAULT NULL,
  `referencia_tipo` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_notificacion`),
  KEY `idx_notif_usuario` (`usuario_id`),
  KEY `idx_notif_leida` (`usuario_id`,`leida`),
  CONSTRAINT `fk_notif_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificaciones_cliente`
--

LOCK TABLES `notificaciones_cliente` WRITE;
/*!40000 ALTER TABLE `notificaciones_cliente` DISABLE KEYS */;
INSERT INTO `notificaciones_cliente` VALUES (1,8,'INFO','Pedido solicitado - PED-20260414-AEA774','Tu pedido PED-20260414-AEA774 ha sido enviado para autorización. Pronto recibirás respuesta.',0,1,'pedido_cliente','2026-04-14 16:04:19');
/*!40000 ALTER TABLE `notificaciones_cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagos_proveedor`
--

DROP TABLE IF EXISTS `pagos_proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagos_proveedor` (
  `id_pago` bigint unsigned NOT NULL AUTO_INCREMENT,
  `compra_id` bigint unsigned NOT NULL,
  `fecha_vencimiento` date NOT NULL,
  `fecha_pago` date DEFAULT NULL,
  `monto` decimal(12,2) NOT NULL,
  `forma_pago` enum('EFECTIVO','TRANSFERENCIA','CHEQUE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'TRANSFERENCIA',
  `estatus` enum('PENDIENTE','PAGADO','VENCIDO') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDIENTE',
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pago`),
  KEY `idx_pago_vencimiento` (`fecha_vencimiento`),
  KEY `idx_pago_estatus` (`estatus`),
  KEY `fk_pago_compra` (`compra_id`),
  CONSTRAINT `fk_pago_compra` FOREIGN KEY (`compra_id`) REFERENCES `compras` (`id_compra`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos_proveedor`
--

LOCK TABLES `pagos_proveedor` WRITE;
/*!40000 ALTER TABLE `pagos_proveedor` DISABLE KEYS */;
/*!40000 ALTER TABLE `pagos_proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_detalle`
--

DROP TABLE IF EXISTS `pedido_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_detalle` (
  `id_detalle` bigint unsigned NOT NULL AUTO_INCREMENT,
  `pedido_id` bigint unsigned NOT NULL,
  `producto_id` bigint unsigned NOT NULL,
  `cantidad` decimal(14,3) NOT NULL,
  `precio_unitario` decimal(12,2) NOT NULL,
  `total_linea` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `idx_detalle_pedido` (`pedido_id`),
  KEY `idx_detalle_producto` (`producto_id`),
  CONSTRAINT `fk_detalle_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id_pedido`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_detalle_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ck_detalle_valores` CHECK (((`cantidad` > 0) and (`precio_unitario` >= 0) and (`total_linea` >= 0)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_detalle`
--

LOCK TABLES `pedido_detalle` WRITE;
/*!40000 ALTER TABLE `pedido_detalle` DISABLE KEYS */;
/*!40000 ALTER TABLE `pedido_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `id_pedido` bigint unsigned NOT NULL AUTO_INCREMENT,
  `folio` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cliente_id` bigint unsigned NOT NULL,
  `estado_actual_id` bigint unsigned NOT NULL,
  `fecha_pedido` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_entrega_estimada` date DEFAULT NULL,
  `observaciones` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total` decimal(12,2) NOT NULL DEFAULT '0.00',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pedido`),
  UNIQUE KEY `uq_pedidos_folio` (`folio`),
  KEY `idx_pedidos_cliente` (`cliente_id`),
  KEY `idx_pedidos_estado` (`estado_actual_id`),
  CONSTRAINT `fk_pedidos_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id_cliente`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_pedidos_estado` FOREIGN KEY (`estado_actual_id`) REFERENCES `estados_pedido` (`id_estado`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ck_pedidos_montos` CHECK ((`total` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos_cliente`
--

DROP TABLE IF EXISTS `pedidos_cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos_cliente` (
  `id_pedido_cliente` bigint unsigned NOT NULL AUTO_INCREMENT,
  `folio` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `usuario_id` bigint unsigned NOT NULL,
  `metodo_pago` enum('TARJETA','TRANSFERENCIA','OXXO') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'TARJETA',
  `estado` enum('COTIZACION','NEGOCIANDO_FECHA','AUTORIZADO','RECHAZADO','EN_PRODUCCION','PARCIALMENTE_ENTREGADO','ENTREGADO','CANCELADO') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'COTIZACION',
  `fecha_autorizacion` datetime DEFAULT NULL,
  `fecha_propuesta_entrega` date DEFAULT NULL,
  `motivo_rechazo` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subtotal` decimal(12,2) NOT NULL DEFAULT '0.00',
  `iva` decimal(12,2) NOT NULL DEFAULT '0.00',
  `total` decimal(12,2) NOT NULL DEFAULT '0.00',
  `direccion_entrega` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notas` text COLLATE utf8mb4_unicode_ci,
  `fecha_pedido` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pedido_cliente`),
  UNIQUE KEY `uq_pedido_folio` (`folio`),
  KEY `idx_pedido_usuario` (`usuario_id`),
  CONSTRAINT `fk_pedido_cli_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ck_pedido_montos` CHECK (((`subtotal` >= 0) and (`total` >= 0)))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos_cliente`
--

LOCK TABLES `pedidos_cliente` WRITE;
/*!40000 ALTER TABLE `pedidos_cliente` DISABLE KEYS */;
INSERT INTO `pedidos_cliente` VALUES (1,'PED-20260414-AEA774',8,'OXXO','ENTREGADO','2026-04-14 10:05:36',NULL,NULL,22.00,3.52,25.52,'fray bernardo','wgrfjhgfds','2026-04-14 16:04:19','2026-04-14 16:05:36');
/*!40000 ALTER TABLE `pedidos_cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos_cliente_detalle`
--

DROP TABLE IF EXISTS `pedidos_cliente_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos_cliente_detalle` (
  `id_detalle` bigint unsigned NOT NULL AUTO_INCREMENT,
  `pedido_id` bigint unsigned NOT NULL,
  `producto_id` bigint unsigned NOT NULL,
  `cantidad` int NOT NULL,
  `cantidad_entregada` int NOT NULL DEFAULT '0',
  `cantidad_pendiente` int NOT NULL DEFAULT '0',
  `precio_unitario` decimal(12,2) NOT NULL,
  `total_linea` decimal(12,2) NOT NULL,
  `stock_suficiente` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_detalle`),
  KEY `idx_det_pedido` (`pedido_id`),
  KEY `idx_det_producto` (`producto_id`),
  CONSTRAINT `fk_pedcli_det_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos_cliente` (`id_pedido_cliente`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_pedcli_det_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ck_pedcli_det` CHECK (((`cantidad` > 0) and (`precio_unitario` >= 0) and (`total_linea` >= 0) and (`cantidad_entregada` >= 0) and (`cantidad_pendiente` >= 0)))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos_cliente_detalle`
--

LOCK TABLES `pedidos_cliente_detalle` WRITE;
/*!40000 ALTER TABLE `pedidos_cliente_detalle` DISABLE KEYS */;
INSERT INTO `pedidos_cliente_detalle` VALUES (1,1,2,1,1,0,22.00,22.00,0);
/*!40000 ALTER TABLE `pedidos_cliente_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permisos`
--

DROP TABLE IF EXISTS `permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisos` (
  `id_permiso` bigint unsigned NOT NULL AUTO_INCREMENT,
  `codigo` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_permiso`),
  UNIQUE KEY `uq_permisos_codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permisos`
--

LOCK TABLES `permisos` WRITE;
/*!40000 ALTER TABLE `permisos` DISABLE KEYS */;
INSERT INTO `permisos` VALUES (1,'USUARIOS_VER','Ver listado de usuarios','2026-04-14 09:45:22',NULL),(2,'USUARIOS_CREAR','Crear nuevos usuarios','2026-04-14 09:45:22',NULL),(3,'USUARIOS_EDITAR','Editar usuarios existentes','2026-04-14 09:45:22',NULL),(4,'USUARIOS_ELIMINAR','Eliminar usuarios','2026-04-14 09:45:22',NULL),(5,'USUARIOS_ROLES_ASIGNAR','Asignar roles a usuarios','2026-04-14 09:45:22',NULL),(6,'ROLES_VER','Ver listado de roles','2026-04-14 09:45:22',NULL),(7,'ROLES_CREAR','Crear nuevos roles','2026-04-14 09:45:22',NULL),(8,'ROLES_EDITAR','Editar roles existentes','2026-04-14 09:45:22',NULL),(9,'ROLES_ELIMINAR','Eliminar roles','2026-04-14 09:45:22',NULL),(10,'CLIENTES_VER','Ver listado de clientes','2026-04-14 09:45:22',NULL),(11,'CLIENTES_CREAR','Registrar nuevos clientes','2026-04-14 09:45:22',NULL),(12,'CLIENTES_EDITAR','Editar información de clientes','2026-04-14 09:45:22',NULL),(13,'CLIENTES_ELIMINAR','Eliminar clientes','2026-04-14 09:45:22',NULL),(14,'PRODUCTOS_VER','Ver catálogo de productos','2026-04-14 09:45:22',NULL),(15,'PRODUCTOS_CREAR','Crear nuevos productos','2026-04-14 09:45:22',NULL),(16,'PRODUCTOS_EDITAR','Editar productos existentes','2026-04-14 09:45:22',NULL),(17,'PRODUCTOS_ELIMINAR','Eliminar productos','2026-04-14 09:45:22',NULL),(18,'PRODUCTOS_PRECIOS','Modificar precios de productos','2026-04-14 09:45:22',NULL),(19,'INVENTARIO_VER','Ver existencias de inventario','2026-04-14 09:45:22',NULL),(20,'INVENTARIO_AJUSTAR','Realizar ajustes de inventario','2026-04-14 09:45:22',NULL),(21,'INVENTARIO_TRANSFERIR','Transferir productos entre almacenes','2026-04-14 09:45:22',NULL),(22,'PEDIDOS_VER','Ver pedidos','2026-04-14 09:45:22',NULL),(23,'PEDIDOS_CREAR','Crear nuevos pedidos','2026-04-14 09:45:22',NULL),(24,'PEDIDOS_EDITAR','Editar pedidos','2026-04-14 09:45:22',NULL),(25,'PEDIDOS_CANCELAR','Cancelar pedidos','2026-04-14 09:45:22',NULL),(26,'PEDIDOS_APROBAR','Aprobar pedidos','2026-04-14 09:45:22',NULL),(27,'COMPRAS_VER','Ver compras','2026-04-14 09:45:22',NULL),(28,'COMPRAS_CREAR','Crear órdenes de compra','2026-04-14 09:45:22',NULL),(29,'COMPRAS_EDITAR','Editar órdenes de compra','2026-04-14 09:45:22',NULL),(30,'COMPRAS_CANCELAR','Cancelar órdenes de compra','2026-04-14 09:45:22',NULL),(31,'COMPRAS_APROBAR','Aprobar órdenes de compra','2026-04-14 09:45:22',NULL),(32,'PROVEEDORES_VER','Ver listado de proveedores','2026-04-14 09:45:22',NULL),(33,'PROVEEDORES_CREAR','Registrar nuevos proveedores','2026-04-14 09:45:22',NULL),(34,'PROVEEDORES_EDITAR','Editar información de proveedores','2026-04-14 09:45:22',NULL),(35,'PROVEEDORES_ELIMINAR','Eliminar proveedores','2026-04-14 09:45:22',NULL),(36,'PRODUCCION_VER','Ver órdenes de producción','2026-04-14 09:45:22',NULL),(37,'PRODUCCION_CREAR','Crear órdenes de producción','2026-04-14 09:45:22',NULL),(38,'PRODUCCION_EDITAR','Editar órdenes de producción','2026-04-14 09:45:22',NULL),(39,'PRODUCCION_FINALIZAR','Finalizar órdenes de producción','2026-04-14 09:45:22',NULL),(40,'PRODUCCION_CANCELAR','Cancelar órdenes de producción','2026-04-14 09:45:22',NULL),(41,'REPORTES_VENTAS','Ver reportes de ventas','2026-04-14 09:45:22',NULL),(42,'REPORTES_COMPRAS','Ver reportes de compras','2026-04-14 09:45:22',NULL),(43,'REPORTES_INVENTARIO','Ver reportes de inventario','2026-04-14 09:45:22',NULL),(44,'REPORTES_PRODUCCION','Ver reportes de producción','2026-04-14 09:45:22',NULL),(45,'REPORTES_FINANCIEROS','Ver reportes financieros','2026-04-14 09:45:22',NULL),(46,'AUDITORIA_VER','Ver registros de auditoría','2026-04-14 09:45:22',NULL),(47,'AUDITORIA_EXPORTAR','Exportar registros de auditoría','2026-04-14 09:45:22',NULL);
/*!40000 ALTER TABLE `permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produccion_consumo`
--

DROP TABLE IF EXISTS `produccion_consumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produccion_consumo` (
  `id_consumo` bigint unsigned NOT NULL AUTO_INCREMENT,
  `produccion_id` bigint unsigned NOT NULL,
  `materia_prima_id` bigint unsigned NOT NULL,
  `cantidad_usada` decimal(14,3) NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_consumo`),
  KEY `idx_consumo_produccion` (`produccion_id`),
  KEY `fk_consumo_materia` (`materia_prima_id`),
  CONSTRAINT `fk_consumo_materia` FOREIGN KEY (`materia_prima_id`) REFERENCES `materias_primas` (`id_materia_prima`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_consumo_produccion` FOREIGN KEY (`produccion_id`) REFERENCES `producciones` (`id_produccion`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ck_consumo` CHECK ((`cantidad_usada` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produccion_consumo`
--

LOCK TABLES `produccion_consumo` WRITE;
/*!40000 ALTER TABLE `produccion_consumo` DISABLE KEYS */;
/*!40000 ALTER TABLE `produccion_consumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producciones`
--

DROP TABLE IF EXISTS `producciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producciones` (
  `id_produccion` bigint unsigned NOT NULL AUTO_INCREMENT,
  `producto_id` bigint unsigned NOT NULL,
  `receta_id` bigint unsigned NOT NULL,
  `cantidad_producida` decimal(14,3) NOT NULL,
  `unidad_medida` enum('PIEZA','M2','M3','KG','TON') COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_inicio` datetime NOT NULL,
  `fecha_fin` datetime DEFAULT NULL,
  `estado` enum('PLANIFICADA','EN_PROCESO','FINALIZADA','CANCELADA') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PLANIFICADA',
  `observaciones` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `pedido_id` bigint unsigned DEFAULT NULL,
  `solicitud_id` bigint unsigned DEFAULT NULL,
  PRIMARY KEY (`id_produccion`),
  KEY `idx_prod_producto` (`producto_id`),
  KEY `idx_prod_receta` (`receta_id`),
  KEY `idx_prod_pedido` (`pedido_id`),
  KEY `idx_prod_solicitud` (`solicitud_id`),
  CONSTRAINT `fk_produccion_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos_cliente` (`id_pedido_cliente`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_produccion_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_produccion_receta` FOREIGN KEY (`receta_id`) REFERENCES `recetas` (`id_receta`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_produccion_solicitud` FOREIGN KEY (`solicitud_id`) REFERENCES `solicitudes_produccion` (`id_solicitud`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `ck_prod_cantidad` CHECK ((`cantidad_producida` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producciones`
--

LOCK TABLES `producciones` WRITE;
/*!40000 ALTER TABLE `producciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `producciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` bigint unsigned NOT NULL AUTO_INCREMENT,
  `categoria_id` bigint unsigned NOT NULL,
  `enlace_fotografia` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sku` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unidad_medida_id` bigint unsigned NOT NULL,
  `resistencia_mpa` decimal(6,2) DEFAULT NULL,
  `color_id` bigint unsigned NOT NULL,
  `precio_base` decimal(12,2) NOT NULL DEFAULT '0.00',
  `es_activo` bigint NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_producto`),
  UNIQUE KEY `uq_productos_sku` (`sku`),
  KEY `idx_productos_nombre` (`nombre`),
  KEY `idx_productos_categoria` (`categoria_id`),
  KEY `fk_producto_unidad` (`unidad_medida_id`),
  KEY `fk_producto_color` (`color_id`),
  CONSTRAINT `fk_producto_color` FOREIGN KEY (`color_id`) REFERENCES `colores` (`id_color`),
  CONSTRAINT `fk_producto_unidad` FOREIGN KEY (`unidad_medida_id`) REFERENCES `unidades_medida` (`id_unidad`),
  CONSTRAINT `fk_productos_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias_producto` (`id_categoria`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ck_productos_precio_base` CHECK ((`precio_base` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,1,'images/productos/block_hueco-sf.png','PRE-001','Block Hueco 12x20x40','Block de concreto para muros estructurales',1,12.50,1,15.50,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(2,1,'images/productos/block_solido-sf.png','PRE-002','Block Sólido 15x20x40','Block sólido de alta resistencia',1,15.00,1,22.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(3,2,'images/productos/bovedilla-sf.png','PRE-003','Bovedilla de Poliestireno','Elemento aligerante para losa',1,NULL,4,28.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(4,2,'images/productos/vigueta-sf.png','PRE-004','Vigueta Pretensada','Elemento estructural para losas',1,25.00,1,280.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(5,3,'images/productos/losa-sf.png','PRE-005','Losa Prefabricada','Losa lista para instalación',2,30.00,1,1100.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(6,4,'images/productos/panel-sf.png','PRE-006','Panel Prefabricado de Concreto','Panel para muros y fachadas',2,28.00,1,850.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(7,5,'images/productos/banqueta-sf.png','PRE-007','Banqueta Prefabricada','Sección de banqueta de concreto',1,20.00,1,85.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(8,6,'images/productos/guarnicions-sf.png','PRE-008','Guarnición Prefabricada','Elemento para delimitación de calles',1,22.00,1,78.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(9,7,'images/productos/registro-sf.png','PRE-009','Registro Prefabricado','Caja de concreto para instalaciones',1,25.00,1,320.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(10,8,'images/productos/tapa-sf.png','PRE-010','Tapa de Concreto para Registro','Tapa reforzada para registro',1,30.00,1,185.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22');
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id_proveedor` bigint unsigned NOT NULL AUTO_INCREMENT,
  `razon_social` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rfc` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contacto` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telefono_contacto` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `domicilio` text COLLATE utf8mb4_unicode_ci,
  `categoria` enum('MATERIA_PRIMA','SERVICIOS','INSUMOS') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'MATERIA_PRIMA',
  `dias_credito` int NOT NULL DEFAULT '0',
  `limite_credito` decimal(12,2) NOT NULL DEFAULT '0.00',
  `es_activo` bigint NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_proveedor`),
  UNIQUE KEY `uq_proveedor_rfc` (`rfc`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES (1,'Cementos Mexicanos S.A.','CEM123456ABC','ventas@cemex.mx','5551234567','Juan Pérez','5559876543','Av. Industrias 123, Monterrey, NL','MATERIA_PRIMA',30,500000.00,1,'2026-04-14 09:45:22',NULL),(2,'Aceros del Norte','ACE789012XYZ','compras@acerosnorte.com','5552345678','María López','5558765432','Carretera Nacional Km 15, Guadalupe, NL','MATERIA_PRIMA',45,800000.00,1,'2026-04-14 09:45:22',NULL),(3,'Aditivos Químicos S.A.','ADI456789DEF','ventas@aditivos.com','5553456789','Carlos Ruiz','5557654321','Av. Química 456, San Pedro, NL','INSUMOS',15,200000.00,1,'2026-04-14 09:45:22',NULL),(4,'Cementos del Norte SA de CV','CDN850101ABC','ventas@cementos.com','4421234567',NULL,NULL,NULL,'MATERIA_PRIMA',0,0.00,1,'2026-04-14 09:45:22',NULL);
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receta_detalle`
--

DROP TABLE IF EXISTS `receta_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receta_detalle` (
  `id_detalle` bigint unsigned NOT NULL AUTO_INCREMENT,
  `receta_id` bigint unsigned NOT NULL,
  `materia_prima_id` bigint unsigned NOT NULL,
  `cantidad` int NOT NULL,
  `unidad_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `fk_det_receta` (`receta_id`),
  KEY `fk_det_materia` (`materia_prima_id`),
  KEY `fk_det_unidad` (`unidad_id`),
  CONSTRAINT `fk_det_materia` FOREIGN KEY (`materia_prima_id`) REFERENCES `materias_primas` (`id_materia_prima`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_det_receta` FOREIGN KEY (`receta_id`) REFERENCES `recetas` (`id_receta`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_det_unidad` FOREIGN KEY (`unidad_id`) REFERENCES `unidades_medida` (`id_unidad`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ck_receta_cantidad` CHECK ((`cantidad` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receta_detalle`
--

LOCK TABLES `receta_detalle` WRITE;
/*!40000 ALTER TABLE `receta_detalle` DISABLE KEYS */;
INSERT INTO `receta_detalle` VALUES (1,1,1,250,4),(2,1,2,1,3),(3,1,3,1,3),(4,1,4,5,3),(5,2,1,300,4),(6,2,2,1,3),(7,2,3,1,3),(8,2,4,2,3),(9,3,1,180,4),(10,3,2,1,3),(11,3,3,3,3),(12,4,1,350,4),(13,4,2,1,3),(14,4,3,1,3),(15,4,7,180,4),(16,5,1,400,4),(17,5,2,2,3),(18,5,3,2,3),(19,5,7,350,4),(20,5,5,10,4),(21,6,1,320,4),(22,6,2,1,3),(23,6,3,1,3),(24,6,7,5,4),(25,7,1,200,4),(26,7,2,1,3),(27,7,3,1,3),(28,7,4,3,3),(29,8,1,250,4),(30,8,2,1,3),(31,8,3,1,3),(32,8,4,4,3),(33,9,1,300,4),(34,9,2,2,3),(35,9,3,2,3),(36,9,4,5,3),(37,9,7,50,4),(38,10,1,150,4),(39,10,2,1,3),(40,10,3,1,3),(41,10,4,2,3),(42,10,7,80,4);
/*!40000 ALTER TABLE `receta_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recetas`
--

DROP TABLE IF EXISTS `recetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas` (
  `id_receta` bigint unsigned NOT NULL AUTO_INCREMENT,
  `producto_id` bigint unsigned NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cuanto_produce` int NOT NULL,
  `tiempo_produccion` decimal(12,2) NOT NULL,
  `resistencia` decimal(10,2) NOT NULL,
  `es_activa` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_receta`),
  KEY `fk_receta_producto` (`producto_id`),
  CONSTRAINT `fk_receta_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas`
--

LOCK TABLES `recetas` WRITE;
/*!40000 ALTER TABLE `recetas` DISABLE KEYS */;
INSERT INTO `recetas` VALUES (1,1,'Block Hueco 12x20x40',120,6.00,120.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(2,2,'Block Sólido 15x20x40',100,6.50,180.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(3,3,'Bovedilla ligera',60,4.00,80.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(4,4,'Vigueta pretensada',25,48.00,350.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(5,5,'Losa prefabricada',12,24.00,250.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(6,6,'Panel prefabricado',20,18.00,200.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(7,7,'Banqueta estándar 1m',10,8.00,150.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(8,8,'Guarnición recta 1m',15,6.00,200.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(9,9,'Registro eléctrico/sanitario',5,12.00,250.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22'),(10,10,'Tapa para registro',20,4.00,250.00,1,'2026-04-14 09:45:22','2026-04-14 09:45:22');
/*!40000 ALTER TABLE `recetas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `refresh_tokens`
--

DROP TABLE IF EXISTS `refresh_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `refresh_tokens` (
  `id_rft` bigint unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint unsigned NOT NULL,
  `token` char(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_emision` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_expiracion` datetime NOT NULL,
  `fecha_revocacion` datetime DEFAULT NULL,
  `token_remplazo` char(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_rft`),
  UNIQUE KEY `uq_refresh_token` (`token`),
  KEY `idx_refresh_usuario` (`usuario_id`),
  CONSTRAINT `fk_refresh_tokens_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ck_refresh_expiracion` CHECK ((`fecha_expiracion` > `fecha_emision`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `refresh_tokens`
--

LOCK TABLES `refresh_tokens` WRITE;
/*!40000 ALTER TABLE `refresh_tokens` DISABLE KEYS */;
/*!40000 ALTER TABLE `refresh_tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol_permisos`
--

DROP TABLE IF EXISTS `rol_permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol_permisos` (
  `rol_id` bigint unsigned NOT NULL,
  `permiso_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`rol_id`,`permiso_id`),
  KEY `fk_rol_permisos_permiso` (`permiso_id`),
  CONSTRAINT `fk_rol_permisos_permiso` FOREIGN KEY (`permiso_id`) REFERENCES `permisos` (`id_permiso`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_rol_permisos_rol` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id_rol`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol_permisos`
--

LOCK TABLES `rol_permisos` WRITE;
/*!40000 ALTER TABLE `rol_permisos` DISABLE KEYS */;
INSERT INTO `rol_permisos` VALUES (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(1,10),(2,10),(1,11),(2,11),(1,12),(2,12),(1,13),(1,14),(2,14),(4,14),(5,14),(6,14),(1,15),(1,16),(1,17),(1,18),(1,19),(2,19),(3,19),(4,19),(5,19),(1,20),(4,20),(1,21),(4,21),(1,22),(2,22),(6,22),(1,23),(2,23),(6,23),(1,24),(2,24),(1,25),(1,26),(2,26),(1,27),(3,27),(1,28),(3,28),(1,29),(3,29),(1,30),(3,30),(1,31),(3,31),(1,32),(3,32),(1,33),(3,33),(1,34),(3,34),(1,35),(1,36),(5,36),(1,37),(5,37),(1,38),(5,38),(1,39),(5,39),(1,40),(5,40),(1,41),(2,41),(1,42),(3,42),(1,43),(4,43),(1,44),(5,44),(1,45),(1,46),(1,47);
/*!40000 ALTER TABLE `rol_permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id_rol` bigint unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `es_activo` bigint NOT NULL DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `uq_roles_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'ADMINISTRADOR','Control total del sistema',1,'2026-04-14 09:45:22',NULL),(2,'VENTAS','Gestión de clientes, cotizaciones y ventas',1,'2026-04-14 09:45:22',NULL),(3,'COMPRAS','Gestión de proveedores y órdenes de compra',1,'2026-04-14 09:45:22',NULL),(4,'ALMACEN','Control de inventario y materia prima',1,'2026-04-14 09:45:22',NULL),(5,'PRODUCCION','Gestión de recetas y órdenes de producción',1,'2026-04-14 09:45:22',NULL),(6,'CLIENTE','Acceso al catálogo y tienda en línea',1,'2026-04-14 09:45:22',NULL);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudes_produccion`
--

DROP TABLE IF EXISTS `solicitudes_produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudes_produccion` (
  `id_solicitud` bigint unsigned NOT NULL AUTO_INCREMENT,
  `pedido_id` bigint unsigned NOT NULL,
  `producto_id` bigint unsigned NOT NULL,
  `cantidad_faltante` decimal(14,3) NOT NULL,
  `estado` enum('PENDIENTE','ACEPTADA','RECHAZADA','EN_PROCESO','COMPLETADA') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDIENTE',
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `fecha_solicitud` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_respuesta` datetime DEFAULT NULL,
  PRIMARY KEY (`id_solicitud`),
  KEY `idx_sol_pedido` (`pedido_id`),
  KEY `idx_sol_producto` (`producto_id`),
  CONSTRAINT `fk_sol_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos_cliente` (`id_pedido_cliente`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_sol_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudes_produccion`
--

LOCK TABLES `solicitudes_produccion` WRITE;
/*!40000 ALTER TABLE `solicitudes_produccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `solicitudes_produccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unidades_medida`
--

DROP TABLE IF EXISTS `unidades_medida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unidades_medida` (
  `id_unidad` bigint unsigned NOT NULL AUTO_INCREMENT,
  `clave` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `es_activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_unidad`),
  UNIQUE KEY `clave` (`clave`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unidades_medida`
--

LOCK TABLES `unidades_medida` WRITE;
/*!40000 ALTER TABLE `unidades_medida` DISABLE KEYS */;
INSERT INTO `unidades_medida` VALUES (1,'PIEZA','Pieza',1,'2026-04-14 09:45:22',NULL),(2,'M2','Metros cuadrados',1,'2026-04-14 09:45:22',NULL),(3,'M3','Metros cúbicos',1,'2026-04-14 09:45:22',NULL),(4,'KG','Kilogramos',1,'2026-04-14 09:45:22',NULL),(5,'TON','Toneladas',1,'2026-04-14 09:45:22',NULL),(6,'LT','Litros',1,'2026-04-14 09:45:22',NULL);
/*!40000 ALTER TABLE `unidades_medida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_roles`
--

DROP TABLE IF EXISTS `usuario_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_roles` (
  `usuario_id` bigint unsigned NOT NULL,
  `rol_id` bigint unsigned NOT NULL,
  `asignado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`usuario_id`,`rol_id`),
  KEY `fk_usuario_roles_rol` (`rol_id`),
  CONSTRAINT `fk_usuario_roles_rol` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id_rol`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_usuario_roles_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_roles`
--

LOCK TABLES `usuario_roles` WRITE;
/*!40000 ALTER TABLE `usuario_roles` DISABLE KEYS */;
INSERT INTO `usuario_roles` VALUES (2,2,'2026-04-14 09:45:22'),(3,3,'2026-04-14 09:45:22'),(4,4,'2026-04-14 09:45:22'),(5,5,'2026-04-14 09:45:22'),(6,6,'2026-04-14 09:45:22'),(7,1,'2026-04-14 16:02:01'),(8,6,'2026-04-14 16:03:39');
/*!40000 ALTER TABLE `usuario_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` bigint unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fs_uniquifier` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `es_activo` bigint NOT NULL DEFAULT '1',
  `intentos_fallidos` int unsigned NOT NULL DEFAULT '0',
  `ultima_sesion` datetime DEFAULT NULL,
  `tf_primary_method` varchar(140) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tf_totp_secret` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `uq_usuarios_username` (`username`),
  UNIQUE KEY `uq_usuarios_email` (`email`),
  UNIQUE KEY `uq_usuarios_fs_uniquifier` (`fs_uniquifier`),
  KEY `idx_username_usuarios` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (2,'ventas01','ventas@concretum.com','$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW','f2a52e99-3818-11f1-bdaf-1cce51724114',1,0,NULL,NULL,NULL,'2026-04-14 09:45:22',NULL),(3,'compras01','compras@concretum.com','$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW','f2a53f50-3818-11f1-bdaf-1cce51724114',1,0,NULL,NULL,NULL,'2026-04-14 09:45:22',NULL),(4,'almacen01','almacen@concretum.com','$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW','f2a54c6b-3818-11f1-bdaf-1cce51724114',1,0,NULL,NULL,NULL,'2026-04-14 09:45:22',NULL),(5,'produccion01','produccion@concretum.com','$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW','f2a55755-3818-11f1-bdaf-1cce51724114',1,0,NULL,NULL,NULL,'2026-04-14 09:45:22',NULL),(6,'cliente01','cliente01@gmail.com','$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW','f2a57bac-3818-11f1-bdaf-1cce51724114',1,0,NULL,NULL,NULL,'2026-04-14 09:45:22',NULL),(7,'admin','admin@concretum.com','$2b$12$w8nXLcMdjH7HK0MbFRU31.Q55eYAu3V6UwDu1xGVuIcYbLWxcPFzG','25fa949a-9fc1-4e62-9eb3-da5f670562be',1,0,'2026-04-14 11:04:31',NULL,NULL,'2026-04-14 10:02:00','2026-04-14 11:04:30'),(8,'ricardo','cliente@gmail.com','$2b$12$cFrtAh2ad4ffKIXJPgU.Jul.0T6KJeAWZYxUdkE1NNtDaHRVVhSua','7280e5c4-8a00-4b98-9d96-b41f850d7486',1,0,'2026-04-14 11:05:30',NULL,NULL,'2026-04-14 10:03:38','2026-04-14 11:05:29');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_usuarios_after_insert` AFTER INSERT ON `usuarios` FOR EACH ROW BEGIN
    DECLARE tipo_usuario VARCHAR(50);
    IF NEW.email LIKE '%@empresa.com' THEN
        SET tipo_usuario = 'EMPLEADO';
    ELSE
        SET tipo_usuario = 'EXTERNO';
    END IF;
    INSERT INTO auditoria_eventos (usuario_id, evento, entidad, entidad_id, descripcion, fecha_creacion)
    VALUES (NEW.id_usuario, 'USUARIO_CREADO', 'usuarios', NEW.id_usuario,
        CONCAT('Usuario creado: ', NEW.username, ' (', NEW.email, ') - Tipo: ', tipo_usuario), NOW());
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `venta_detalle`
--

DROP TABLE IF EXISTS `venta_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venta_detalle` (
  `id_detalle` bigint unsigned NOT NULL AUTO_INCREMENT,
  `venta_id` bigint unsigned NOT NULL,
  `producto_id` bigint unsigned NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(12,2) NOT NULL,
  `total_linea` decimal(12,2) NOT NULL,
  `costo_unitario` decimal(12,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id_detalle`),
  KEY `idx_det_venta` (`venta_id`),
  KEY `idx_det_producto` (`producto_id`),
  CONSTRAINT `fk_det_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_det_venta` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id_venta`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ck_det_valores` CHECK (((`cantidad` > 0) and (`precio_unitario` >= 0) and (`total_linea` >= 0)))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta_detalle`
--

LOCK TABLES `venta_detalle` WRITE;
/*!40000 ALTER TABLE `venta_detalle` DISABLE KEYS */;
INSERT INTO `venta_detalle` VALUES (1,1,2,1,22.00,22.00,15.30);
/*!40000 ALTER TABLE `venta_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id_venta` bigint unsigned NOT NULL AUTO_INCREMENT,
  `folio` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cliente_id` bigint unsigned NOT NULL,
  `usuario_id` bigint unsigned DEFAULT NULL,
  `metodo_pago` enum('EFECTIVO','TRANSFERENCIA','CHEQUE','CREDITO','TARJETA','OXXO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` enum('PENDIENTE','COBRADO','CREDITO','CANCELADO') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDIENTE',
  `subtotal` decimal(12,2) NOT NULL DEFAULT '0.00',
  `iva` decimal(12,2) NOT NULL DEFAULT '0.00',
  `total` decimal(12,2) NOT NULL DEFAULT '0.00',
  `fecha_venta` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_venta`),
  UNIQUE KEY `uq_ventas_folio` (`folio`),
  KEY `idx_ventas_cliente` (`cliente_id`),
  KEY `idx_ventas_fecha` (`fecha_venta`),
  KEY `fk_ventas_usuario` (`usuario_id`),
  CONSTRAINT `fk_ventas_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id_cliente`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_ventas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES (1,'VTA-PED-20260414-AEA774',1,7,'OXXO','COBRADO',18.97,3.03,22.00,'2026-04-14 10:05:36','2026-04-14 10:05:36');
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-14 11:09:55
