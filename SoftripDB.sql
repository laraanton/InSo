DROP DATABASE IF EXISTS SoftripDB;
GO

CREATE DATABASE SoftripDB;
GO

USE SoftripDB;
GO

CREATE TABLE Usuarios (
    usuario_id INT IDENTITY(1,1) CONSTRAINT PK_usuario PRIMARY KEY,
    dni_nie NVARCHAR(20) NOT NULL UNIQUE,
    nombre_completo NVARCHAR(200) NOT NULL,
    email NVARCHAR(100) NOT NULL UNIQUE,
    telefono NVARCHAR(20),
    password_hash NVARCHAR(255), 
    tipo_usuario NVARCHAR(20) NOT NULL CONSTRAINT CK_tipo_usuario 
        CHECK (tipo_usuario IN ('Administrador', 'Operador', 'Cliente')),
    fecha_registro DATETIME DEFAULT GETDATE(),
    estado NVARCHAR(15) DEFAULT 'Activo' CONSTRAINT CK_estado_usuario 
        CHECK (estado IN ('Activo', 'Inactivo', 'Suspendido')),
    cuenta_bloqueada BIT DEFAULT 0
);

ALTER TABLE Usuarios 
ADD preferencia NVARCHAR(30) DEFAULT 'General' CONSTRAINT CK_preferencia_usuario 
        CHECK (preferencia IN ('General', 'Familiar', 'Jubilado', 'Movilidad Reducida', 'Escolar'));

ALTER TABLE Usuarios 
ADD preferencia_accesibilidad NVARCHAR(30) DEFAULT 'Ninguna' CONSTRAINT CK_preferencia_accesibilidad
        CHECK (preferencia_accesibilidad IN ('Ninguna', 'Dificultad Lectura'));

CREATE TABLE Clientes_Perfiles (
    usuario_id INT CONSTRAINT PK_cliente_perfil PRIMARY KEY 
        CONSTRAINT FK_perfil_usuario FOREIGN KEY REFERENCES Usuarios(usuario_id),
    presupuesto_promedio DECIMAL(10,2)
);

CREATE TABLE Paquetes_Turisticos (
    paquete_id INT IDENTITY(1,1) CONSTRAINT PK_paquete PRIMARY KEY,
    nombre_paquete NVARCHAR(150) NOT NULL,
    descripcion_detallada NVARCHAR(MAX),
    destino NVARCHAR(100) NOT NULL,
    duracion_dias INT NOT NULL,
    precio_tpv DECIMAL(10,2) NOT NULL, 
    servicios_incluidos NVARCHAR(MAX), 
    perfil_objetivo NVARCHAR(50), 
    accesibilidad_certificada BIT DEFAULT 0, 
    creado_por_operador INT CONSTRAINT FK_paquete_operador FOREIGN KEY REFERENCES Usuarios(usuario_id),
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_ini DATE NULL,
    fecha_fin DATE NULL,
    estado_paquete NVARCHAR(20) NOT NULL DEFAULT 'Activo'
        CONSTRAINT CK_estado_paquete CHECK (estado_paquete IN ('Borrador', 'Activo', 'Inactivo'))
);

CREATE TABLE Historial_Cambios_Paquetes (
    historial_id INT IDENTITY(1,1) CONSTRAINT PK_historial PRIMARY KEY,
    paquete_id INT CONSTRAINT FK_historial_paquete FOREIGN KEY REFERENCES Paquetes_Turisticos(paquete_id),
    usuario_id INT CONSTRAINT FK_historial_usuario FOREIGN KEY REFERENCES Usuarios(usuario_id),
    fecha_cambio DATETIME DEFAULT GETDATE(),
    descripcion_cambio NVARCHAR(MAX)
);

SET DATEFORMAT ymd;
CREATE TABLE Pedidos_Viajes (
    pedido_id INT IDENTITY(1,1) CONSTRAINT PK_pedido PRIMARY KEY,
    identificador_unico AS ('ORD-' + CAST(pedido_id AS NVARCHAR(10))), 
    cliente_id INT NOT NULL CONSTRAINT FK_pedido_cliente FOREIGN KEY REFERENCES Usuarios(usuario_id),
    paquete_id INT NOT NULL CONSTRAINT FK_pedido_paquete FOREIGN KEY REFERENCES Paquetes_Turisticos(paquete_id),
    fecha_pedido DATETIME DEFAULT GETDATE(),
    fecha_inicio DATE NULL,
    fecha_fin DATE NULL,
    estado_pedido NVARCHAR(30) DEFAULT 'Pendiente' CONSTRAINT CK_estado_pedido 
        CHECK (estado_pedido IN ('Pendiente', 'Confirmado', 'Pagado', 'En curso', 'Finalizado', 'Cancelado', 'Reembolsado')),
    monto_total DECIMAL(10,2) NOT NULL,
    metodo_pago NVARCHAR(50) DEFAULT 'PayPal' 
);

CREATE TABLE Sesiones (
    sesion_id INT IDENTITY(1,1) CONSTRAINT PK_sesion PRIMARY KEY,
    usuario_id INT NOT NULL
        CONSTRAINT FK_sesion_usuario FOREIGN KEY REFERENCES Usuarios(usuario_id),
    fecha_inicio DATETIME DEFAULT GETDATE(),
    fecha_fin DATETIME NULL,
    activa BIT DEFAULT 1,
    ip_acceso NVARCHAR(45) NULL,
    intentos_fallidos INT DEFAULT 0
        CONSTRAINT CK_intentos CHECK (intentos_fallidos >= 0)
);

CREATE TABLE Historial_Estados_Pedidos (
    historial_estado_id INT IDENTITY(1,1) CONSTRAINT PK_historial_estado PRIMARY KEY,
    pedido_id INT NOT NULL
        CONSTRAINT FK_histestado_pedido FOREIGN KEY REFERENCES Pedidos_Viajes(pedido_id),
    estado_anterior NVARCHAR(30) NOT NULL,
    estado_nuevo NVARCHAR(30) NOT NULL,
    fecha_cambio DATETIME DEFAULT GETDATE(),
    motivo NVARCHAR(MAX) NULL,
    usuario_responsable INT NULL
        CONSTRAINT FK_histestado_usuario FOREIGN KEY REFERENCES Usuarios(usuario_id)
);

CREATE TABLE Feedback_Clientes (
    feedback_id INT IDENTITY(1,1) CONSTRAINT PK_feedback PRIMARY KEY,
    pedido_id INT UNIQUE CONSTRAINT FK_feedback_pedido FOREIGN KEY REFERENCES Pedidos_Viajes(pedido_id),
    val_trato_operador INT CHECK (val_trato_operador BETWEEN 1 AND 5),
    val_calidad_transporte INT CHECK (val_calidad_transporte BETWEEN 1 AND 5),
    val_satisfaccion_alojamiento INT CHECK (val_satisfaccion_alojamiento BETWEEN 1 AND 5),
    val_general INT CHECK (val_general BETWEEN 1 AND 5),
    comentarios NVARCHAR(MAX)
);
GO

CREATE TABLE Registro_Actividad (
    actividad_id    INT IDENTITY(1,1) CONSTRAINT PK_actividad PRIMARY KEY,
    usuario_id      INT NOT NULL
        CONSTRAINT FK_actividad_usuario FOREIGN KEY REFERENCES Usuarios(usuario_id),
    fecha           DATETIME DEFAULT GETDATE(),
    tipo_accion     NVARCHAR(50) NOT NULL,   -- 'Creación', 'Modificación', 'Bloqueo', 'Backup', 'Login', etc.
    detalle         NVARCHAR(500) NULL,
    ip              NVARCHAR(45) NULL
);
GO

CREATE TABLE Reclamaciones (
    reclamacion_id INT IDENTITY(1,1) CONSTRAINT PK_reclamacion PRIMARY KEY,
    identificador_reclamacion AS ('REC-' + CAST(reclamacion_id AS NVARCHAR(10))),
    pedido_id INT NOT NULL CONSTRAINT FK_reclamacion_pedido FOREIGN KEY REFERENCES Pedidos_Viajes(pedido_id),
    categoria NVARCHAR(50),
    descripcion_incidente NVARCHAR(MAX) NOT NULL,
    fecha_incidente DATE NOT NULL,
    fecha_registro DATETIME DEFAULT GETDATE(),
    estado_reclamacion NVARCHAR(20) DEFAULT 'Registrada' CONSTRAINT CK_estado_reclamacion 
        CHECK (estado_reclamacion IN ('Registrada', 'En revisión', 'En gestión', 'Resuelta', 'Rechazada', 'Cerrada'))
);

GO
CREATE TRIGGER trg_ValidateFeedbackStatus
ON Feedback_Clientes
AFTER INSERT
AS
BEGIN
    IF EXISTS (
        SELECT 1 FROM inserted i
        JOIN Pedidos_Viajes p ON i.pedido_id = p.pedido_id
        WHERE p.estado_pedido <> 'Finalizado'
    )
    BEGIN
        RAISERROR ('Solo se puede valorar un viaje una vez haya finalizado.', 16, 1);
        ROLLBACK TRANSACTION;
    END
END;

GO
INSERT INTO Usuarios (dni_nie, nombre_completo, email, telefono, tipo_usuario, estado, preferencia, preferencia_accesibilidad)
VALUES 
('11111111A', 'Lara Antón (Admin)',      'lara.admin@softrip.com',       '600111222', 'Administrador', 'Activo', 'General',          'Ninguna'),
('22222222B', 'Daniela Pino (Operador)', 'daniela.ops@softrip.com',      '600222333', 'Operador',      'Activo', 'General',          'Ninguna'),
('33333333C', 'Nuria García (Cliente)',  'nuria.garcia@email.com',       '600333444', 'Cliente',       'Activo', 'Familiar',         'Ninguna'),
('44444444D', 'Marta Royo (Cliente)',    'marta.royo@email.com',         '600444555', 'Cliente',       'Activo', 'Familiar',         'Dificultad Lectura'),
('55555555E', 'Juan Pérez (Cliente)',    'juan.perez@email.com',         '600555666', 'Cliente',       'Activo', 'Jubilado',         'Dificultad Lectura'),
('10000001A', 'Carlos Medina',           'carlos.medina@email.com',      '611001001', 'Cliente',       'Activo', 'Jubilado',         'Ninguna'),
('10000002B', 'Sofia Herrera',           'sofia.herrera@email.com',      '611002002', 'Cliente',       'Activo', 'Familiar',         'Ninguna'),
('10000003C', 'Andres Torres',           'andres.torres@email.com',      '611003003', 'Cliente',       'Activo', 'General',          'Dificultad Lectura'),
('10000004D', 'Elena Vidal',             'elena.vidal@email.com',        '611004004', 'Cliente',       'Activo', 'Escolar',          'Ninguna'),
('10000005E', 'Pablo Ruiz',              'pablo.ruiz@email.com',         '611005005', 'Cliente',       'Activo', 'General',          'Dificultad Lectura'),
('10000006F', 'Laura Campos',            'laura.campos@email.com',       '611006006', 'Cliente',       'Activo', 'Familiar',         'Dificultad Lectura'),
('10000007G', 'Miguel Serrano',          'miguel.serrano@email.com',     '611007007', 'Cliente',       'Activo', 'Jubilado',         'Ninguna'),
('10000008H', 'Ana Blanco',              'ana.blanco@email.com',         '611008008', 'Cliente',       'Activo', 'Escolar',          'Ninguna'),
('10000009I', 'Roberto Iglesias',        'roberto.iglesias@email.com',   '611009009', 'Cliente',       'Activo', 'General',          'Ninguna'),
('10000010J', 'Carmen Navarro',          'carmen.navarro@email.com',     '611010010', 'Cliente',       'Activo', 'Jubilado',         'Ninguna'),
('20000001K', 'Pedro Sainz (Op)',        'pedro.ops@softrip.com',        '622000001', 'Operador',      'Activo', 'General',          'Ninguna');
INSERT INTO Clientes_Perfiles (usuario_id, presupuesto_promedio)
VALUES 
(3,  1200.00),
(4,  2500.00),
(5,  1800.00),
(6,   900.00),
(7,  2200.00),
(8,   750.00),
(9,  1600.00),
(10,  500.00),
(11, 3000.00),
(12,  850.00),
(13, 2000.00),
(14,  650.00),
(15, 2800.00);
INSERT INTO Paquetes_Turisticos 
    (nombre_paquete, descripcion_detallada, destino, duracion_dias, precio_tpv,
     servicios_incluidos, perfil_objetivo, accesibilidad_certificada, creado_por_operador,
     fecha_ini, fecha_fin)
VALUES 
('Escapada Relax Canarias', 'Vuelo y hotel 5 estrellas en Tenerife.', 'Tenerife, España', 7,  850.00, 'Vuelo, Hotel, Traslados', 'Jubilado', 1, 2, '2026-07-01', '2026-07-08'),
('Aventura en los Pirineos', 'Rutas de senderismo y alojamiento en cabañas.', 'Huesca, España', 5,  450.00, 'Alojamiento, Guía, Seguro', 'Joven', 0, 2, '2026-07-10', '2026-07-15'),
 ('Ruta del Mediterraneo', 'Crucero por Mallorca, Ibiza y Valencia.', 'Mallorca, España', 6,  980.00, 'Crucero, Cabina, Pension completa', 'General', 1, 2, '2026-08-10', '2026-08-16'),
('Safari en Kenia', 'Aventura salvaje con guias expertos.', 'Nairobi, Kenia', 10, 3200.00, 'Vuelo, Lodge, Safari, Seguro', 'Aventurero',  0, 2, '2026-09-01', '2026-09-11'),
('Roma Clasica', 'Tour cultural por el Coliseo y el Vaticano.', 'Roma, Italia', 5,  750.00, 'Vuelo, Hotel, Visitas Guiadas', 'Jubilado', 1, 2, '2026-09-15', '2026-09-20'),
('Esqui en los Alpes', 'Semana de esqui con clases y forfait incluido.', 'Innsbruck, Austria',  7, 1400.00, 'Vuelo, Hotel, Forfait, Clases', 'Joven', 0, 2, '2026-12-20', '2026-12-27'),
('Tokyo Cultural', 'Inmersion en la cultura japonesa moderna y antigua.', 'Tokyo, Japon', 8, 2100.00, 'Vuelo, Hotel, Guia, Traslados', 'Aventurero',  0, 2, '2026-10-01', '2026-10-09');
INSERT INTO Pedidos_Viajes
    (cliente_id, paquete_id, monto_total, estado_pedido, metodo_pago, fecha_pedido, fecha_inicio, fecha_fin)
VALUES
(3,  2,  450.00, 'Finalizado', 'Tarjeta', DEFAULT, NULL, NULL),
(4,  3, 2400.00, 'Confirmado', 'PayPal', DEFAULT, NULL, NULL),
(5,  1,  850.00, 'Pagado', 'Transferencia',   DEFAULT, NULL, NULL),
( 6, 1,  850.00, 'Finalizado',  'Tarjeta', '2025-01-05', '2025-01-10', '2025-01-17'),
( 7, 3, 2400.00, 'Finalizado',  'PayPal', '2025-01-12', '2025-01-20', '2025-01-24'),
( 8, 2,  450.00, 'Finalizado',  'Transferencia', '2025-01-18', '2025-01-25', '2025-01-30'),
( 9, 4,  980.00, 'Finalizado',  'Tarjeta', '2025-01-22', '2025-01-28', '2025-02-03'),
(10, 6,  980.00, 'Finalizado',  'PayPal', '2025-02-03', '2025-02-10', '2025-02-16'),
(11, 3, 1200.00, 'Finalizado',  'Tarjeta', '2025-02-08', '2025-02-15', '2025-02-19'),
(12, 5, 3200.00, 'Finalizado',  'Transferencia', '2025-02-14', '2025-02-20', '2025-03-01'),
(13, 2,  450.00, 'Cancelado',   'PayPal', '2025-02-20', NULL,          NULL),
(14, 1,  850.00, 'Finalizado',  'Tarjeta', '2025-02-25', '2025-03-01', '2025-03-08'),
(15, 7,  750.00, 'Finalizado',  'PayPal', '2025-03-02', '2025-03-08', '2025-03-13'),
( 6, 8, 1400.00, 'Finalizado',  'Tarjeta', '2025-03-07', '2025-03-14', '2025-03-21'),
( 8, 4,  980.00, 'Reembolsado', 'PayPal', '2025-03-15', NULL,          NULL),
( 9, 1,  850.00, 'Finalizado',  'Tarjeta', '2025-03-20', '2025-03-25', '2025-04-01'),
(10, 2,  450.00, 'Finalizado',  'Tarjeta', '2025-04-02', '2025-04-08', '2025-04-13'),
(11, 6,  980.00, 'Finalizado',  'PayPal', '2025-04-08', '2025-04-14', '2025-04-20'),
(12, 3, 2400.00, 'Confirmado',  'Transferencia', '2025-04-14', '2025-05-01', '2025-05-05'),
(13, 7,  750.00, 'Finalizado',  'Tarjeta', '2025-04-19', '2025-04-25', '2025-04-30'),
(14, 5, 3200.00, 'Pagado', 'PayPal', '2025-04-23', '2025-06-01', '2025-06-11'),
(15, 8, 1400.00, 'Finalizado',  'Tarjeta', '2025-05-01', '2025-05-07', '2025-05-14'),
( 6, 2,  450.00, 'Finalizado',  'PayPal', '2025-05-06', '2025-05-12', '2025-05-17'),
( 8, 6,  980.00, 'Finalizado',  'Tarjeta', '2025-05-16', '2025-05-20', '2025-05-26'),
( 9, 3, 1200.00, 'Cancelado',   'PayPal', '2025-05-21', NULL, NULL),
(10, 1,  850.00, 'Pendiente',   'Tarjeta', '2025-05-23', NULL, NULL);

INSERT INTO Feedback_Clientes
    (pedido_id, val_trato_operador, val_calidad_transporte, val_satisfaccion_alojamiento, val_general, comentarios)
VALUES 
( 1, 5, 4, 5, 5, 'Una experiencia increíble, el guía fue muy amable.'),
( 4, 5, 5, 4, 5, 'El hotel en Tenerife era espectacular, repetiria sin dudarlo.'),
( 5, 4, 3, 4, 4, 'Disneyland genial para los ninos, el transporte mejorable.'),
( 6, 4, 4, 3, 4, 'Buen senderismo, las cabanas algo basicas pero cumple.'),
( 7, 5, 5, 5, 5, 'El crucero supero todas mis expectativas, absolutamente recomendable.'),
( 8, 3, 4, 4, 3, 'El safari estuvo bien organizado pero el lodge decepciono.'),
( 9, 5, 4, 5, 5, 'Tenerife es un destino increible, el personal muy atento.'),
(10, 4, 5, 5, 5, 'El Mediterraneo desde el barco es incomparable.'),
(12, 5, 5, 4, 5, 'Tenerife en febrero es lo mejor que puedes hacer.'),
(13, 4, 4, 4, 4, 'Roma preciosa, el tour guiado muy completo.'),
(14, 5, 5, 5, 5, 'Esquiar en los Alpes fue un sueno, repetiremos.'),
(16, 5, 5, 5, 5, 'Tenerife por segunda vez y sigue siendo perfecta.'),
(17, 4, 4, 3, 4, 'Los Pirineos en abril, una pasada.'),
(22, 4, 4, 3, 4, 'Semana de esqui muy bien organizada, forfait sin colas.'),
(23, 5, 5, 5, 5, 'Los Pirineos en mayo son espectaculares.');

SELECT pedido_id, cliente_id, estado_pedido FROM Pedidos_Viajes ORDER BY pedido_id;

INSERT INTO Reclamaciones
    (pedido_id, categoria, descripcion_incidente, fecha_incidente, estado_reclamacion)
VALUES 
( 2, 'Transporte', 'El vuelo de ida sufrió un retraso de 4 horas sin previo aviso.', '2024-03-10', 'En revisión'),
( 5, 'Transporte', 'La maleta llego con danos visibles en la cerradura.', '2025-01-21', 'Resuelta'),
(10, 'Transporte', 'El traslado al lodge llego con 3 horas de retraso.', '2025-02-22', 'Cerrada'),
(16, 'Transporte', 'Cancelacion de tren sin reembolso inmediato.', '2025-03-19', 'En revisión'),
( 6, 'Alojamiento', 'La cabana asignada no tenia agua caliente el primer dia.', '2025-01-26', 'Resuelta'),
(13, 'Alojamiento', 'La habitacion del hotel no coincidia con la reserva.', '2025-03-09', 'Cerrada'),
(18, 'Alojamiento', 'El camarote del crucero tenia problemas con el aire acondicionado.', '2025-04-15', 'Registrada'),
( 7, 'Atencion al cliente','El guia no hablaba espanol segun lo acordado.', '2025-01-27', 'Resuelta'),
(22, 'Atencion al cliente','No recibimos informacion sobre cambios en el itinerario.', '2025-05-08', 'En revisión'),
( 9, 'Actividades', 'Una de las entradas al parque no funciono en la puerta.', '2025-02-17', 'Resuelta'),
(14, 'Actividades', 'La clase de esqui fue cancelada sin alternativa ofrecida.', '2025-03-16', 'En gestión'),
( 4, 'Seguridad', 'Falta de socorrista en la zona de piscina del hotel.', '2025-01-12', 'Cerrada');

INSERT INTO Historial_Estados_Pedidos
    (pedido_id, estado_anterior, estado_nuevo, motivo, usuario_responsable)
VALUES
(11, 'Pendiente',  'Cancelado', 'Cliente solicito cancelacion por motivos personales.', 2),
(15, 'Confirmado', 'Reembolsado', 'Paquete no disponible en fecha solicitada.', 2),
(19, 'Pendiente',  'Confirmado', 'Confirmado tras verificacion de disponibilidad.', 2),
(21, 'Confirmado', 'Pagado', 'Pago recibido por transferencia bancaria.', 2),
(25, 'Pendiente',  'Cancelado', 'Cliente cancelo antes del plazo de confirmacion.', 2); 

UPDATE Usuarios 
SET preferencia = 'General' 
WHERE preferencia IS NULL;

SELECT 'USUARIOS'      AS Tabla, * FROM Usuarios;
SELECT 'PAQUETES'      AS Tabla, * FROM Paquetes_Turisticos;
SELECT 'PEDIDOS'       AS Tabla, * FROM Pedidos_Viajes;
SELECT 'FEEDBACK'      AS Tabla, * FROM Feedback_Clientes;
SELECT 'RECLAMACIONES' AS Tabla, * FROM Reclamaciones;
SELECT * FROM Clientes_Perfiles;
SELECT * FROM Usuarios;
SELECT paquete_id, nombre_paquete, fecha_ini, fecha_fin FROM Paquetes_Turisticos;
SELECT * FROM Registro_Actividad 
