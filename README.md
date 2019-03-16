# git-oracle

El objetivo de este repositorio es mostrar cómo se puede trabajar con Git en una aplicación basada en Oracle (con lógica en PL/SQL)

Las tecnologías que usaremos para conseguir este objetivo son:

- Docker. Para arrancar Oracle en la máquina local.
- Flyway. Para mantener las _database migrations_, los scripts SQL que realizan la evolución del modelo de datos.
- Shell scripts para compilar el código PL/SQL en la instancia.

Hay dos fases diferenciadas: configuración y desarrollo diario.

# 1. Configuración

Tenemos que instalar y configurar tanto Docker como Flyway en la máquina del desarrollador.

## 1.1 Docker

### 1.1.1 Instalación
Para desarrollar software es necesario que cada desarrollador tenga su propia base de datos Oracle funcionando en su máquina.
Para esto, hay que instalar [Docker](https://www.docker.com/products/docker-desktop), que permite arrancar sistemas operativos virtuales, llamados contenedores, con software de todo tipo funcionando, como si de una máquina virtual se tratase. 

En nuestro caso, necesitamos una instancia de Oracle funcionando en la máquina local.

Para conseguir esto he tenido que crearme una cuenta en docker hub (https://hub.docker.com), para poder descargar la imagen oficial de Oracle Enterprise.

Una vez creada la cuenta, hay que: 

- Buscar la imagen oficial de Oracle Database. Entrar en el detalle y aceptar los términos del servicio (hay que registrarse)
- Hacer login desde la línea de comandos con `$ docker login`
- Ya se podría descargar el contenedor con la instrucción `docker pull store/oracle/database-enterprise:12.2.0.1`

Existe una variante "slim" del contenedor, con nombre `store/oracle/database-enterprise:12.2.0.1-slim`, que ocupa menos espacio, y no dispone de características poco usadas como Analytics, Oracle R, Oracle Label Security, Oracle Text, Oracle Application Express y Oracle DataVault. 

### 1.1.2 Arrancar la base de datos y conectarse a ella
Para facilitar el arranque de la base de datos he creado un fichero `docker-compose.yml` que arranca la base de datos mediante el comando:

`$ docker-compose up -d`

Una vez el contenedor ha sido descargado (después del `pull`), se puede ejecutar directamente `docker-compose up` para arrancar oracle sin tener que hacer login de nuevo.

La opción `-d` significa que se ejecute en background, si se omite esta opción Docker muestra en pantalla todo lo que va sucediendo, incluso información sobre lo que habría que añadir a un fichero `tnsnames.ora` en caso de que quisieramos crearlo.

Para saber si la instancia de Oracle está lista, se puede ejecutar `docker ps` y cuando para el contenedor `oracle-local` el estado mostrado sea `(healthy)`, significará que Oracle ha arrancado correctamente.

La configuración del `docker-compose.yml` une el puerto 1521 del contenedor al puerto local 32769. 
Este puerto es el que tiene que usarse al configurar la conexión en un cliente SQL como DataGrip (o TOAD).
En todo caso, la conexión usando el SID, usuario y contraseña funciona (ver [imagen](conectar.png)).

Los datos de la base de datos se guardan en el interior del contenedor, por lo que si el contenedor se borra (esto no se tiene por qué hacer) los datos se perderían.
Para un entorno de desarrollo esto no es muy importante, porque la base de datos se reconstruye usando los scripts de Flyway, pero si se quisiera mantener los datos en la máquina local, podría hacerse añadiendo `volumes` al fichero `docker-compose.yml`

```
volumes:
      - /data/OracleDBData:/ORCL
```

Donde `/data/OracleDBData` es un directorio existente en la máquina local. Esto haría que los datos se guardaran fuera del contenedor, pudiendo recuperarlos en caso de borrado del mismo.

El usuario y contraseña por defecto para conectarse a la base de datos es `sys` y `Oradoc_db1`. El SID es `ORCLCDB`.

### 1.1.3 Crear esquema de base de datos

La instancia de Oracle viene sin ningún esquema creado, además de los estándar. Para ello, necesitamos crear un esquema donde se crearán nuestras tablas y paquetes PL/SQL.

Esto se debe hacer una única vez, después de la creación del contenedor. Podría hacerse manualmente, pero he creado un shell script que se conecta al contenedor y ejecuta el script SQL en `/SQL/migrations/init.sql`.
Este script crea un esquema/usuario llamado `c##local`, con password `localpass`. Estas serán las credenciales que usaremos posteriormente en Flyway.

El script se ejecuta desde el shell (en Mac y Linux):

```bash
$ ./shell_scripts/init.sh
```

Para usuarios de Windows, la versión `.bat` debe ser sencilla de hacer...

### 1.1.4 Comandos útiles en Docker

#### 1.1.4.1 Acceder a la línea de comandos Linux del contenedor

```bash
$ docker exec -it oracle-local bash
```

#### 1.1.4.2 Ver qué contenedores hay ejecutándose

```bash
$ docker ps
```

#### 1.1.4.3 Listar las imágenes que tenemos descargadas
Los conceptos de imagen y contenedor son análogos a los conceptos de clase y objeto.
La imagen es la clase (por ejemplo, la imagen de Oracle), y el contenedor es una instancia de esa imagen ejecutándose. 
Podemos, por lo tanto, tener varios contenedores que ejecuten la misma imagen (con nombres distintos) 

```bash
$ docker images
```

#### 1.1.4.4 Parar un contenedor que se está ejecutando

```bash
$ docker kill oracle-local
```

Si se ejecutó `docker-compose up` sin la opción `-d`, se puede parar pulsando la combinación de teclas `ctrl+c`. 

## 1.2 Flyway

[Flyway](https://flywaydb.org/) es una herramienta para el control de versiones en el modelo de datos. 
Simplificando, no es más que un gestor de scripts SQL que establece una serie de normas de nombrado de ficheros y permite la ejecución de scripts SQL para actualizar una base de datos.

Al trabajar con Flyway, los scripts de cambios en modelo de datos (DDL y DML) se guardan en el repositorio Git como ficheros de texto SQL con una nomenclatura definida.
Flyway crea una tabla en la base de datos (`flyway_schema_history`) para almacenar qué scripts están ejecutados, y también guarda un hash de cada script. 
Cuando un desarrollador actualiza o descarga una rama de Git, los scripts asociados a esos cambios están ahí, y Flyway sabe qué scripts están ejecutados y cuáles no, permitiendo actualizar la versión de la base de datos de forma que sea compatible con los cambios en el código.

### 1.2.1 Instalación
Para instalar Flyway se tiene que descargar de [aquí](https://flywaydb.org/documentation/commandline/#download-and-installation) la versión de escritorio (command-line) de Flyway para tu sistema operativo.

Una vez descomprimido el fichero descargado, es conveniente mover el directorio completo a la carpeta de aplicaciones o a algún sitio más "estable" que la carpeta de descargas. Es conveniente también añadir esta carpeta al PATH para permitir el acceso rápido al ejecutable de Flyway.

Flyway necesita el driver JDBC para conectarse a la base de datos. Para otros motores como Postgres o MySQL el driver está incluido in la distribución de Flyway, pero para Oracle hay que descargar el driver (hay que asegurarse de que sea compatible con la versión de Oracle) y copiarlo en la carpeta `/drivers` de la instalación de Flyway. 
El driver puede descargarse de la web de [Oracle](https://www.oracle.com/technetwork/database/application-development/jdbc/downloads/index.html)
Hay instrucciones detalladas sobre el uso de Flyway con Oracle [aqui](https://flywaydb.org/documentation/database/oracle). Es importante recalcar que para versiones anteriores a Oracle 12.2 (la que usamos aquí) hay que usar una licencia de Flyway Pro.
Hay que descargar los ficheros `ojdbc8.jar` y `orai18n.jar` de la web de Oracle y moverlos al directorio `drivers` de la instalación

### 1.2.2 Configuración
En la carpeta de la instaiación de Flyway hay un subdirectorio llamado `conf` que contiene un fichero `flyway.conf` que puede editarse para indicar a Flyway cosas como la URL a la que acceder, usuario, contraseña, localización de los scripts SQL...
La información de configuración que necesitamos indicar es:

| Propiedad | Valor |
| --------- | ----- |
| url | jdbc:oracle:thin:@//localhost:32769/ORCLCDB.localdomain |
| user | c##local |
| password | localpass |
| locations | filesystem:/ruta/completa/a/carpeta/SQL/migrations |

En la carpeta `flyway` de este repositorio hay un fichero `flyway.conf` con la configuración local que he usado a modo de ejemplo.  
Una propiedad interesante es `outOfOrder`, que nos permitirá ejecutar todas las migraciones anteriores no aplicadas, aunque hayamos aplicado migraciones posteriores en número de versión. Esto puede indicarse en cada ejecución concreta de Flyway.

La documentación sobre las posibles opciones de configuración puede encontrarse [aquí](https://flywaydb.org/documentation/configfiles)

Existe una opción de configuración llamada `initSql` para indicar instrucciones SQL que se ejecutarán antes de las migraciones, como por ejemplo un `ALTER SESSION`, si lo vemos conveniente o necesario.

### 1.2.3 Creación de la tabla de control de versiones
Flyway usa una tabla (`flyway_schema_history`) para controlar qué scripts han sido ejecutados y cuáles no.
El propio ejecutable de Flyway permite la creación de esta tabla ejecutando `flyway baseline`

```bash
Davids-MacBook-Pro:shell_scripts davidespihernandez$ flyway baseline
Flyway Community Edition 5.2.4 by Boxfuse
Database: jdbc:oracle:thin:@//localhost:32769/ORCLCDB.localdomain (Oracle 12.2)
Creating Schema History table: "C##LOCAL"."flyway_schema_history"
Successfully baselined schema with version: 1
```

Esto hay que hacerlo antes de poder ejecutar migraciones. 

### 1.2.4 Nomenclatura de los scripts
Flyway sigue una nomenclatura concreta para los scripts SQL. Por ejemplo:

`V2__Crear_tabla.sql`

En este caso,
- **V**: es el prefijo que indica que es un script a ejecutar, un script de nueva versión. Se puede crear scripts repetibles, que se ejecutan siempre, y comienzan por R, o scripts de deshacer que empiezan por U (sólo para versión pro de Flyway)
- **2**: Es el número de versión.
- **__**: El doble subrayado señala la separación con el campo de descripción.
- **Crear_tabla.sql**: Descripción y extensión del fichero.

En mi opinión, un buen ejemplo de nombrado de script debería usar como número de versión una fecha con hora minutos y segundos. Por ejemplo:

`V201903112006__Creacion_tabla.sql`

La fecha hasta minutos (o segundos si se quiere) hace que el número de versión sea prácticamente único.

### 1.2.5 Actualización del modelo de datos usando Flyway
Una vez Flyway está configurado, para actualizar la base de datos con los scripts de migración se ejecuta `flyway migrate`. 
Por ejemplo, en este repositorio hay un script de prueba, que crea una tabla en la base de datos, `V201903112012__Crear_tabla_ejemplo.sql`.
Si ejecutamos `flyway migrate`, la salida es:

```bash
Davids-MacBook-Pro:shell_scripts davidespihernandez$ flyway migrate
Flyway Community Edition 5.2.4 by Boxfuse
Database: jdbc:oracle:thin:@//localhost:32769/ORCLCDB.localdomain (Oracle 12.2)
Successfully validated 2 migrations (execution time 00:00.050s)
Current version of schema "C##LOCAL": 1
Migrating schema "C##LOCAL" to version 201903112012 - Crear tabla ejemplo
Successfully applied 1 migration to schema "C##LOCAL" (execution time 00:00.049s)
``` 

Flyway ejecuta el script y crea la tabla. Además, inserta una fila en la tabla de versiones, con un hash para validar que el contenido del fichero no se cambie en el futuro (los scripts han de ser inmutables)

### 1.2.6 Normas para el SQL y PL/SQL en los scripts
- Cualquier DDL exportado por Oracle debe poder ser ejecutado por Flyway sin modificaciones.
- Las instrucciones SQL deben terminar en `;`
- Los bloques de PL/SQL deben comenzar por `DECLARE` o `BEGIN` y terminar en `END; /` (la barra es importante)
- Se permite también el uso de _placeholders_, que pueden definirse en el fichero de configuración y usarse en el SQL (ver documentación de FLyway para más información)

### 1.2.7 Comandos más habituales

#### 1.2.7.1 Limpiar la base de datos

```bash
$ flyway clean
```

Este comando **BORRA** todos los objetos de los esquemas que maneja Flyway (uno solo en nuestro caso)

Normalmente no es necesario, pero a veces viene bien recrear la base de datos de cero y aplicar todas las migraciones posteriormente. 

#### 1.2.7.2 Estado de las migraciones

```bash
$ flyway info
```

Imprime en pantalla la situación de todas las migraciones (ejecutadas o no)

La salida es algo similar a esto:

```
+-----------+--------------+-----------------------+----------+---------------------+----------+
| Category  | Version      | Description           | Type     | Installed On        | State    |
+-----------+--------------+-----------------------+----------+---------------------+----------+
|           | 1            | << Flyway Baseline >> | BASELINE | 2019-03-13 19:23:11 | Baseline |
| Versioned | 201903112012 | Crear tabla ejemplo   | SQL      | 2019-03-13 19:36:59 | Success  |
+-----------+--------------+-----------------------+----------+---------------------+----------+
```

#### 1.2.7.3 Aplicar migraciones

```bash
$ flyway migrate
```

Aplica todas las migraciones no aplicadas. Es lo habitual cuando se cambia de rama.
En ocasiones, cuando hay ramas que tardan mucho tiempo en volver a mezclarse contra master, nos encontraremos con scripts de migración no ejecutados con número de versión anterior a la última versión que ya tenemos aplicada.
En ese caso Flyway, por defecto, da un error, que se puede evitar ejecutando `flyway migrate -outOfOrder=true`. 

# 2. Uso diario

## 2.1 Compilación del código

He creado un shell script que compila todos los paquetes (cabeceras primero, bodies después) en el container. El script se ejecuta:

```bash
./shell_scripts/compilar.sh
```

El script compila cada cabecera y body por separado en `sqlplus`. 
En caso de tener triggers o clases, o cualquier otro código PL que compilar, puede añadirse en este mismo script.
Al final se ejecuta un par de veces el paquete `UTL_RECOMP` para recompilar los paquetes con errores.

En todo caso, hay clientes SQL como TOAD que permiten la compilación masiva de los ficheros PL/SQL, por lo que esto puede hacerse manualmente, pero un script siempre simplifica las cosas. 

## 2.2 Uso de Git
Git es el estándar de facto para el control de versiones de código fuente.
Es un software muy versátil, que permite usarse de diferentes formas para diferentes proyectos, en base a las necesidades de cada uno.

### 2.2.1 Pull requests
Sea cual sea la estrategia de creación de ramas, sí que hay una única forma correcta de que los cambios sean aprobados: los **pull requests** (PR a partir de ahora).
Trabajar con PR tiene múltiples beneficios:

- Los cambios son revisados antes de ser incorporados a la `master` branch (o a cualquier otra rama)
- Herramientas como Github o Bitbucket permiten realizar comentarios y discusiones sobre el código, lo que al final acaba resultando en mejoras del mismo.
- Aunque un desarrollador no esté como revisor de un PR, siempre puede acceder al mismo, ver el código y hacer los comentarios que quiera. Añadir a un desarrollador como revisor de un PR puede significar simplemente que se quiere que esté al tanto de los cambios, no la revisión concreta de los mismos.
- Las herramientas de integración continua como Jenkins permiten comprobar que para los cambios de ese PR todos los tests automáticos funcionan, y pueden deshabilitar la aprobación del PR en caso contrario.

### 2.2.2 Estrategia de creación de ramas (_Branching strategy_) 
No existe una estrategia de creación de ramas única en Git, depende habitualmente de las necesidades del proyecto en cuestión.

Si el proyecto está pensado para realizar _continuous deployment (CD)_ o _continuous integration (CI)_ (esto es siempre lo deseable), lo mejor es usar una estrategia como [Github Flow](#2.2.1.1 Github flow).

Por otra parte, si partimos de una estructura antigua y queremos migrar a Git, quizá sea más operativo usar inicialmente algo como [Gitflow](#2.2.1.2 Gitflow).

En todo caso, siempre puede crearse una estategia _ad hoc_ para cada proyecto.
A continuación comentamos las principales estrategias para el uso de Git.

#### 2.2.2.1 Github flow
En esta estrategia, existe una rama `master` con el código fuente que está actualmente en producción.

Esta estrategia se basa en una máxima: **todo lo que está en la rama `master` se puede desplegar en producción.**

Cuando se quiere desarrollar algo (da igual lo que sea, un error o una nueva _feature_), el desarrollador:

* Crea una nueva rama, a partir de `master`.
* Realiza los cambios en la rama.
* Añade sus nuevos tests automáticos, y comprueba que los existentes sigan funcionando.
* Crea un pull request
* Se revisa el código usando el pull request, y se realizan las modificaciones oportunas
* En mi opinión, antes de aprobar el pull requests, debería mezclarse `master` de nuevo contra el pull request, y ejecutar los tests de nuevo. Esto no está en el procedimiento de github flow.
* Una vez está todo correcto, se aprueba y mezcla (_merge_) el pull request.

Este proceso está muy bien explicado [aquí](https://guides.github.com/introduction/flow/) 

#### 2.2.2.2 Gitflow
No hay que confundir esto con Github flow, esta estrategia es algo totalmente distinto. 

En esta estrategia se crean muchas más ramas, y el proceso de desarrollo es mucho más rígido, siguiendo unos pasos muy definidos.

[Este](https://nvie.com/posts/a-successful-git-branching-model/) artículo define cómo se trabajaría con Gitflow. Es un post de 2010, pero sigue igual de válido hoy en día... 

En resumen, este método define ramas para:

* master (producción)
* develop (desarrollo)
* feature (ramas para cada ticket o trabajo)
* release (ramas para cada despliegue en producción)
* hotfix (ramas para solucionar problemas en producción)

Además, se define muy claramente cómo se crean y contra qué se mezclan las ramas. 
Por ejemplo, una rama de Hotfix se crea desde `master`, y cuando se mezcla (_merge_) se hace contra `master` y contra `develop`.
El proceso está tan definido que herramientas como Atlassian Sourcetree lo incorporan para que no haya que hacerlo manualmente.

Esta estrategia puede ser una buena opción para empresas que no usen integración continua, y se basen en releases.

Hay que notar que la máxima **todo lo que está en la rama `master` se puede desplegar en producción.** sigue valiendo aquí, por lo que se podría crear scripts para CI a partir de master, o bien usar software como Jenkins para la integración continua.

Hay una buena comparativa entre Gitflow y Github flow [aquí](https://lucamezzalira.com/2014/03/10/git-flow-vs-github-flow/).

### 2.2.3 Tests automáticos
Independientemente de qué estrategia de creación de ramas se use, es fundamental en el desarrollo de software la creación de tests automáticos.

Cuando el desarrollador hace los cambios en el código en su rama, junto a esos cambios puede haber asociados unos scripts de migración de base de datos (aplicables con Flyway, siempre que haya cambios en el modelo de datos), pero es **oblbigatorio*** que haya unos tests automáticos que validen que los cambios realizados son correctos.
Puede que se trate de nuevos tests, o puede que seam modificaciones de los existentes, pero se debe validar automáticamente que los cambios son correctos.

El propio desarrollador ha de comprobar en local que todos los tests pasan antes de crear el PR.

Las herramientas de integración continua, como Jenkins o Circle CI permiten impedir que se pueda aprobar PR para los que hay tests que fallan. 

### 2.2.4 Herramientas para Git

#### 2.2.4.1 Línea de comandos

#### 2.2.4.2 Atlassian Sourcetree

#### 2.2.4.3 Github desktop

#### 2.2.4.4 Sublime merge
