# git-oracle

El objetivo de este repositorio es mostrar cómo se puede trabajar con Git en una aplicación basada en Oracle (con lógica en PL/SQL)

Las tecnologías que usaremos para conseguir este objetivo son:

- Docker. Para arrancar Oracle en la máquina local.
- Flyway. Para mantener las _database migrations_, los scripts SQL que realizan la evolución del modelo de datos.
- Shell scripts para compilar el código PL/SQL en la instancia.

Hay dos fases diferenciadas: configuración y desarrollo diario.

# Configuración

Tenemos que instalar y configurar tanto Docker como Flyway en la máquina del desarrollador.

## Docker
Para desarrollar software es necesario que cada desarrollador tenga su propia base de datos Oracle funcionando en su máquina.
Para esto, hay que instalar [Docker](https://www.docker.com/products/docker-desktop), que permite arrancar sistemas operativos virtuales, llamados contenedores, con software de todo tipo funcionando, como si de una máquina virtual se tratase. 

En nuestro caso, necesitamos una instancia de Oracle funcionando en la máquina local.

Para conseguir esto he tenido que crearme una cuenta en docker hub (https://hub.docker.com), para poder descargar la imagen oficial de Oracle Enterprise.

Una vez creada la cuenta, hay que: 

- Buscar la imagen oficial de Oracle Database. Entrar en el detalle y aceptar los términos del servicio (hay que registrarse)
- Hacer login desde la línea de comandos con `$ docker login`
- Ya se podría descargar el contenedor con la instrucción `docker pull store/oracle/database-enterprise:12.2.0.1`
- Con este comando se puede levantar la instancia de Oracle: `$ docker run -d -it --name <Oracle-DB> -P store/oracle/database-enterprise:12.2.0.1`, donde <Oracle-DB> será el nombre del contenedor. 
- Cuando se ejecute `docker ps` y para el contenedor el estado mostrado sea `(healthy)`, significará que Oracle ha arrancado correctamente.
- El usuario y contraseña por defecto para conectarse a la base de datos es `sys` y `Oradoc_db1`. El SID es `ORCLCDB`.

Existe una variante "slim" del contenedor, con nombre `store/oracle/database-enterprise:12.2.0.1-slim`, que ocupa menos espacio, y no dispone de características poco usadas como  Analytics, Oracle R, Oracle Label Security, Oracle Text, Oracle Application Express and Oracle DataVault. 

Para facilitar el arranque de la base de datos he creado un fichero `docker-compose.yml` que arranca la base de datos mediante el comando:

`$ docker-compose up`

Una vez el contenedor ha sido descargado (después del `pull`), se puede ejecutar directamente `docker-compose up` para arrancar oracle sin tener que hacer login de nuevo.

La configuración del `docker-compose.yml` une el puerto 1521 del contenedor al puerto local 32769. 
Este puerto es el que tiene que usarse al configurar la conexión en un cliente SQL como DataGrip (o TOAD).

Una vez se ejecuta este comando, la imagen de Oracle muestra en pantalla todo lo que va sucediendo, incluso información sobre lo que habría que añadir a un fichero `tnsnames.ora` en caso de que quisieramos crearlo.
En todo caso, la conexión usando el SID, usuario y contraseña funciona (ver [imagen](conectar.png))

Los datos de la base de datos se guardan en el interior del contenedor, por lo que si el contenedor se borra (esto no se tiene por qué hacer) los datos se perderían.
Para un entorno de desarrollo esto no es muy importante, porque la base de datos se reconstruye usando los scripts de Flyway, pero si se quisiera mantener los datos en la máquina local, podría hacerse añadiendo `volumes` al fichero `docker-compose.yml`

```
volumes:
      - /data/OracleDBData:/ORCL
```

Donde `/data/OracleDBData` es un directorio existente en la máquina local. Esto haría que los datos se guardaran fuera del contenedor, pudiendo recuperarlos en caso de borrado del mismo.

## Crear esquema de base de datos

La instancia de Oracle viene sin ningún esquema creado, además de los estándar. Para ello, necesitamos crear un esquema donde se crearán nuestras tablas y paquetes PL/SQL.

Esto se debe hacer una única vez, después de la creación del contenedor. Podría hacerse manualmente, pero he creado un shell script que se conecta al contenedor y ejecuta el script SQL en `/SQL/migrations/init.sql`.
Este script crea un esquema/usuario llamado `c##local`, con password `localpass`. Estas serán las credenciales que usaremos posteriormente en Flyway.

El script se ejecuta desde el shell (en Mac y Linux):

```bash
$ ./shell_scripts/init.sh
```

Antes tendrá que marcarse el fichero como ejecutable, con `chmod +x`.
Para usuarios de Windows, la versión `.bat` debe ser sencilla de hacer...

# Desarrollo diario

## Estrategia de creación de ramas (_Branching strategy_) 

## Compilación del código

He creado un shell script que compila todos los paquetes (cabeceras primero, bodies después) en el container. El script se ejecuta:

```bash
./shell_scripts/compilar.sh
```

El script une todas las cabeceras en un fichero, cambia el usuario de la sesión y los ejecuta en `sqlplus`. También hace lo mismo con los bodies de los PL.
En caso de tener triggers o clases, o cualquier otro código PL que compilar, puede añadirse en este mismo script.

En todo caso, hay clientes SQL como TOAD que permiten la compilación masiva de los ficheros PL/SQL. 