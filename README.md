# git-oracle

El objetivo de este repositorio es mostrar cómo se puede trabajar con Git en una aplicación basada en Oracle (con lógica en PL/SQL)

# Docker
Para las pruebas locales, he tenido que crearme una cuenta en docker hub (https://hub.docker.com), para poder descargar la imagen oficial de Oracle Enterprise.

Una vez creada la cuenta, hay que: 

- Buscar la imagen oficial de Oracle Database. Entrar en el detalle y aceptar los términos del servicio (hay que registrarse)
- Hacer login desde la línea de comandos con `$ docker login`
- Ya se podría descargar el contenedor con la instrucción `docker pull store/oracle/database-enterprise:12.2.0.1`
- Con este comando se puede levantar la instancia de Oracle: `$ docker run -d -it --name <Oracle-DB> -P store/oracle/database-enterprise:12.2.0.1`, donde <Oracle-DB> será el nombre del contenedor. 
- Cuando se ejecute `docker ps` y para el contenedor el estado mostrado sea `(healthy)`, significará que Oracle ha arrancado correctamente.
- El usuario y contraseña por defecto para conectarse a la base de datos es `sys` y `Oradoc_db1`

Existe una variante "slim" del contenedor, con nombre `store/oracle/database-enterprise:12.2.0.1-slim`, que ocupa menos espacio, y no dispone de características poco usadas como  Analytics, Oracle R, Oracle Label Security, Oracle Text, Oracle Application Express and Oracle DataVault. 

Para facilitar el arranque de la base de datos he creado un fichero `docker-compose.yml` que arranca la base de datos mediante el comando:

`$ docker-compose up`

La configuración del `docker-compose.yml` linkea el puerto 1521 del contenedor al puerto local 32769. 
Este puerto es el que tiene que usarse al configurar la conexión en un cliente como DataGrip (o TOAD).

Una vez se ejecuta este comando, la imagen de Oracle muestra en pantalla todo lo que va sucediendo, incluso información sobre lo que habría que añadir a un fichero `tnsnames.ora` en caso de que quisieramos crearlo.
En todo caso, la conexión usando el SID, usuario y contraseña funciona (ver [imagen](conectar.png))

Los datos de la base de datos se guardan en el interior del contenedor, por lo que si el contenedor se borra (esto no se tiene por qué hacer) los datos se perderían.
Para un entorno de desarrollo esto no es muy importante, porque la base de datos se reconstruye usando los scripts de Flyway, pero si se quisiera mantener los datos en la máquina local, podría hacerse añadiendo `volumes` al fichero `docker-compose.yml`

```
volumes:
      - /data/OracleDBData:/ORCL
```

Donde `/data/OracleDBData` es un directorio existente en la máquina local.
 