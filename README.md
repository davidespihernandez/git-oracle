# git-oracle

El objetivo de este repositorio es mostrar cómo se puede trabajar con Git en una aplicación basada en Oracle (con lógica en PL/SQL)

Además crearemos una aplicación en Django para facilitar la creación de datos de prueba en la instancia local del desarrollador,
y permitiremos la ejecución de pruebas automáticas (también en Django) sobre el código PL existente.

Las tecnologías que usaremos para conseguir este objetivo son:

- Docker. Para arrancar Oracle en la máquina local.
- Flyway. Para mantener las _database migrations_, los scripts SQL que realizan la evolución del modelo de datos.
- Shell scripts para compilar el código PL/SQL en la instancia.
- Django Framework, usando librerías como Factory Boy para la inserción de datos.

Estructuraremos esta documentación en cuatro fases diferenciadas:

1. Instalación y configuración de Docker y Flyway.
2. Desarrollo diario: uso de Git y Flyway.
3. Generación de datos de prueba.
4. Ejecución de pruebas automáticas.

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

Flyway necesita el driver JDBC para conectarse a la base de datos. Para otros motores como Postgres o MySQL el driver está incluido en la distribución de Flyway, pero para Oracle hay que descargar el driver, ficheros `ojdbc8.jar` y `orai18n.jar`, (hay que asegurarse de que sea compatible con la versión de Oracle) y copiarlo en la carpeta `/drivers` de la instalación de Flyway. 
El driver puede descargarse de la web de [Oracle](https://www.oracle.com/technetwork/database/application-development/jdbc/downloads/index.html)
Hay instrucciones detalladas sobre el uso de Flyway con Oracle [aqui](https://flywaydb.org/documentation/database/oracle). Es importante recalcar que para versiones anteriores a Oracle 12.2 (la que usamos aquí) hay que usar una licencia de Flyway Pro.

### 1.2.2 Configuración
En la carpeta de la instalación de Flyway hay un subdirectorio llamado `conf` que contiene un fichero `flyway.conf` que puede editarse para indicar a Flyway cosas como la URL a la que acceder, usuario, contraseña, localización de los scripts SQL...
La información de configuración que necesitamos indicar es:

| Propiedad | Valor |
| --------- | ----- |
| url | jdbc:oracle:thin:@//localhost:32769/ORCLCDB.localdomain |
| user | c##local |
| password | localpass |
| locations | filesystem:../SQL/migrations |

En la carpeta `flyway` de este repositorio hay un fichero `flyway.conf` con la configuración local que he usado a modo de ejemplo. Este fichero debe pegarse en el directorio `conf` de la instalación local de Flyway, para que se use esa configuración siempre. Si no se modifica esa configuración, debe ejecutarse el comando flyway desde la carpeta `flyway` del repositorio para que lea nuestro fichero `.conf`.

Una propiedad interesante es `outOfOrder`, que nos permitirá ejecutar todas las migraciones anteriores no aplicadas, aunque hayamos aplicado migraciones posteriores en número de versión. Esto puede indicarse en cada ejecución concreta de Flyway.

La documentación sobre las posibles opciones de configuración puede encontrarse [aquí](https://flywaydb.org/documentation/configfiles)

Existe una opción de configuración llamada `initSql` para indicar instrucciones SQL que se ejecutarán antes de las migraciones, como por ejemplo un `ALTER SESSION`, si lo vemos conveniente o necesario.

### 1.2.3 Creación de la tabla de control de versiones
Flyway usa una tabla (`flyway_schema_history`) para controlar qué scripts han sido ejecutados y cuáles no.
El propio ejecutable de Flyway permite la creación de esta tabla ejecutando `flyway baseline`

```bash
$ flyway baseline
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
$ flyway migrate
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
Los comandos tienen que ejecutarse desde la carpeta `flyway` para que lean la configuración adecuadamente, o bien sobreescribir el fichero `flyway.conf` de la instalación local de Flyway con el de este repositorio (eso es lo conveniente).

#### 1.2.7.1 Limpiar la base de datos

```bash
$ flyway clean
```

Este comando **BORRA** todos los objetos de los esquemas que maneja Flyway (uno solo en nuestro caso)

Normalmente no es necesario, pero a veces viene bien recrear la base de datos de cero y aplicar todas las migraciones posteriormente.

He creado un script sh para ejecutar el borrado e inicialización de la base de datos, ejecutando `flyway clean`y `flyway baseline`. El script se llama `bd_borrar.sh`. 

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

He creado un script sh que ejecuta `flyway migrate`, que se llama `bd_migrar.sh`. 

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

Los PR no son una característica que venga con Git, se manejan de forma externa por servicios como Github o Bitbucket (que hay que contratar por separado).
Tanto Bitbucket como Github permiten integración de los PR con sistemas externos como Jira, de forma que cuando un PR se cierra (_merge_), el ticket asociado se puede cambiar de estado automáticamente.

### 2.2.2 Estrategia de creación de ramas (_Branching strategy_) 
No existe una estrategia de creación de ramas única en Git, depende habitualmente de las necesidades del proyecto en cuestión.

Si el proyecto está pensado para realizar _continuous deployment (CD)_ o _continuous integration (CI)_ (esto es siempre lo deseable), lo mejor es usar una estrategia como Github Flow.

Por otra parte, si partimos de una estructura antigua y queremos migrar a Git, quizá sea más operativo usar inicialmente algo como Gitflow.

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

#### 2.2.2.3 Ramas por sprint/release
Esta podría ser una variante simplificada de Gitflow, para compañías que trabajen con Agile, mediante _sprints_.

- Al principio del sprint se crea una rama desde master, donde se desarrollará el sprint, y que acabará siendo una release.
- Cada desarrollador crea su rama de _feature_ partiendo de la rama del sprint.
- Los PR se crean para ser mezclados contra la rama del sprint.
- La rama del sprint se despliega (preferiblemente de forma automática) en un entorno compartido, donde se pueden realizar pruebas y validaciones manuales más allá de los tests automáticos.
- Si hay algún bug/hotfix, se trata como en Gitflow, se parte de master, y se mezcla contra master y también contra la rama actual de sprint.
- Una vez el sprint está aceptado, se mezcla la rama del sprint contra master, y se despliega en producción.

### 2.2.3 Tests automáticos
Independientemente de qué estrategia de creación de ramas se use, es fundamental en el desarrollo de software la creación de tests automáticos.

Cuando el desarrollador hace los cambios en el código en su rama, junto a esos cambios puede haber asociados unos scripts de migración de base de datos (aplicables con Flyway, siempre que haya cambios en el modelo de datos), pero es **obligatorio** que haya unos tests automáticos que validen que los cambios realizados son correctos.
Puede que se trate de nuevos tests, o puede que seam modificaciones de los existentes, pero se debe validar automáticamente que los cambios son correctos.

El propio desarrollador ha de comprobar en local que todos los tests pasan antes de crear el PR.

Las herramientas de integración continua, como Jenkins o Circle CI permiten impedir que se pueda aprobar PR para los que hay tests que fallan. 

### 2.2.4 Herramientas para Git
Si se tiene la posibilidad de usar un IDE que integre Git, como las herramientas de Jetbrains (IntelliJ, Pycharm, Webstorm...), Sublime, o Visual Studio Code, esto es siempre una buena opción.

Todo lo que se puede hacer con Git se puede hacer mediante la línea de comandos. [Aquí](https://git-scm.com/book/en/v2/Getting-Started-The-Command-Line) se puede encontrar la guía oficial de comandos.

En todo caso, hay muchas herramientas específicas para trabajar visualmente con Git. Comentaremos algunas.

#### 2.2.4.1 Atlassian Sourcetree
Lo mejor de esta aplicación es que se integra con Bitbucket, permitiendo crear PR desde la misma (aunque lo que hace realmente es abrir la página web, donde se crea el PR)
Es una aplicación bastante robusta y, una vez que se controla bien los cambios de ramas, se acostumbra uno a ella muy rápidamente.

#### 2.2.4.2 Github desktop
Gráficamente es la más atractiva, en mi opinión. También es bastante sencilla de usar, e integra perfectamente con Github.

#### 2.2.4.3 Sublime merge
Hecha por los creadores de Sublime editor. Me parece la aplicación más completa, e incluye un par de características que la hacen mejor que las anteriores:
- Búsqueda avanzada
- Posibilidad de resolver _merge conflicts_ en la propia herramienta. Esto es MUY atractivo...

## 2.3 Pasos para actualizar cambios
Estos serían los pasos para actualizar los cambios que haya en `master`:

- Pull `master`
- Ejecutar `flyway migrate` o `bd_migrar.sh`
- Ejecutar `shell_scripts/compilar.sh`. Quizá haya que compilar antes, dependiendo de si los scripts de migración hacen llamadas a PL/SQL modificados. 
En ese caso, es conveniente separar los scripts de migración en 2 ficheros, uno con el DDL y DML sencillo (sólo SQL) y otro con los bloques de PL que usen paquetes.
 
# 3. Generación de datos de prueba
Una vez que mantenemos el esquema de base de datos mediante Flyway, el desarrollador tiene una base de datos "en blanco",
creada por los scripts DDL de las migraciones manejadas por Flyway (aunque Flyway ejecuta cualquier tipo de script, no sólo DDL)

Es conveniente que el desarrollador pueda generar de forma automática una serie de datos de prueba que le permitan usar la aplicación localmente para operar con ella.

Para esto, se podría escribir una serie de scripts SQL que se ejecutarían cada vez después de ejecutar las migraciones de Flyway, y que insertarían los datos necesarios.
Esta estrategia es muy complicada de mantener, y es muy fácil cometer errores en este tipo de scripts, por lo que he optado por crear una aplicación en Django y usar su ORM y algunas librerías de terceros para hacerlo.

## 3.1 Instalación de Django
[Django](https://www.djangoproject.com/) es un framework de desarrollo de aplicaciones gratuito y de código abierto basado en Python.

Django lleva muchos años en el mercado y hay muchas grandes empresas y aplicaciones que lo usan.
Todo lo que necesites hacer ya está hecho o puede hacerse fácilmente con Django.

Usaremos Python 3.6 y Django 2.2.

La documentación sobre instalación de la guía oficial puede encontrarse [aquí](https://docs.djangoproject.com/en/2.2/intro/install/).

Es conveniente hacer algún tutorial sobre Django, o leer documentación, para entender lo que estamos haciendo.

Hay un muy buen tutorial en español en [Django girls](https://tutorial.djangogirls.org/es), que incluye también la instalación.

La página oficial tiene una documentación de gran calidad. En concreto, es muy conveniente leerse el [ORM](https://docs.djangoproject.com/en/2.2/topics/db/) de Django.

La idea general es que el ORM de Django permite usar clases en Python (llamadas modelos) para acceder a la base de datos, sin tener que escribir SQL.
Django, además, tiene herramientas que facilitarán mucho esta tarea.

Hay que crear un `virtual environment` e instalar los requerimientos del proyecto en él. Hay un script `crear_venv.sh` que realiza esto (aunque se puede hacer manualmente).
Para simplificar cosas es importante que el environment se llame `oracleutils`.

Para que Django funcione adecuadamente con Oracle, hay que instalar, además los drivers de cliente de Oracle. En caso de mac OS, pueden encontrarse instrucciones [aquí](https://oracle.github.io/odpi/doc/installation.html#macos). Hay que bajar los drivers para la versión 12.2.0.1.0.

En resumen, una vez descargado el fichero zip, hay que hacer:

```
mkdir -p /opt/oracle
unzip instantclient-basic-macos.x64-12.2.0.1.0.zip
mkdir ~/lib
ln -s /opt/oracle/instantclient_12_2/libclntsh.dylib ~/lib/
```

## 3.2 Aplicaciones Django
Un `site` Django habitualmente consta de varias `aplicaciones`.
En nuesto caso hemos creado una aplicación _central_ llamada `oracleutils`, y crearemos una aplicación por módulo en la base de datos.
En el repositorio encontramos un directorio para `module1` y `module2`. Cada uno de estos directorios es una aplicación Django, y correspondería con un módulo de la aplicación monolítica.
Las `settings` están en la aplicación central, `oracleutils`, en el fichero `settings.py`. En este fichero destaca la configuración de la conexión de la base de datos, que es:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'localhost:32769/ORCLCDB.localdomain',
        'USER': 'C##LOCAL',
        'PASSWORD': 'localpass',
    },
}
```

## 3.3 Generación automática de modelos de Django

Django viene con una serie de [comandos](https://docs.djangoproject.com/en/2.2/ref/django-admin/) de administación "de serie" que permiten hacer múltiples cosas.
Entre ellos está el comando `inspectdb`. La sintaxis de este comando es:

```
django-admin inspectdb [table [table ...]]
```

El comando usa la conexión de base de datos especificada en las `settings` y escribe en la salida estándar una clase Python para cada una de las tablas que se le indiquen.
Se usa este comando cuando se quiere usar Django contra una base de datos existente (como es el caso).
El comando vuelca todas las clases, que se suelen pegar en un fichero `models.py` (en Python es habitual tener más de una clase en un fichero).

En nuestro caso hemos optado por crear un comando que genera un fichero por cada tabla, y además los almacena en un directorio `models` dentro de cada aplicación.

Este comando se llama `crear_datos_prueba`, y el código está en la aplicación `oracleutils`. En esta aplicación, en el fichero `__init.py` se observa:

```
from module1 import TABLES as MODULE1_TABLES
from module2 import TABLES as MODULE2_TABLES

ALL_TABLES = {
    'module1': MODULE1_TABLES,
    'module2': MODULE2_TABLES,
}
```

La variable `ALL_TABLES` debe contener un diccionario con una entrada por aplicación. En cada entrada están la tablas de las que consta ese módulo.
Por ejemplo, en el `__init__.py` de `module1` se observa:

```
TABLES = [
    'CUSTOMER',
    'INVOICE',
    'INVOICE_LINE',
]
```
Esa es la lista de tablas del `module1`. Cuando se ejecute el comando `crear_modelos` (bien directamente con `manage.py`,
o bien con el script `crear_modelos.sh`) se creará un fichero `.py` en el directorio `models` de la aplicación `module1` por cada tabla.

Esos modelos no son gestionados por Django, lo que significa que las Django migrations no les afectan, pero sí puede usarse el ORM para acceder a las tablas, y eso es lo que haremos.

## 3.4 Generación automática de datos de prueba usando Factory Boy
[Factory Boy)[https://factoryboy.readthedocs.io/en/latest/] es una librería Python que se integra con el ORM de Django para permitir generar datos (principalmente para tests) de forma sencilla.

Hemos creado un comando, `crear_datos_prueba`, que puede ejecutarse mediante un script `crear_datos_prueba.sh` que elimina opcionalmente toda la información de las tablas de cada aplicación y posteriormente inserta datos de prueba en las mismas.

Para ello se define una clase `TestDataBuilder` por módulo. Esta clase extiende una case base `BaseDataBuilder`. que define un método `build` y otro `clear`, que se ejecutan convenientemente por el comando.

```
class BaseDataBuilder:
    def build(self):
        raise NotImplemented

    def clear(self):
        raise NotImplemented

    class Meta:
        abstract = True
```

Cada aplicación (módulo) debe definir su `TestDataBuilder`, implementando esos métodos. El método `build` del `TestDataBuilder` de cada aplicación se llamará por el comando de generación de datos de test.

El método `build` usa un `builder`, que a su vez usa `Factories` creadas a partir de los modelos generados automáticamente con `inspectdb`, y que se encuentran en un directorio `factories` dentro de cada aplicación (módulo).

### 3.4.1 Secuencias
En Oracle es habitual usar secuencias para las claves primarias de las tablas. Las secuencias de Oracle habitualmente son números positivos. Para que no colisionen los datos de prueba generados automáticamente con lo que pueda generarse desde la aplicación en su funcionamiento normal, he decidido que los campos secuenciales generados por las factories serán enteros negativos. Para hacer esto, se define una factoría base en la aplicación central:

```
class BaseFactory(factory.django.DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return cls._meta.model.objects.count() + 1
```
El número de secuencia se calcula contando el número de filas existentes en la tabla, y sumando uno.
Posteriormente, cuando se quiere asignar un número de secuencia en una factoría de factory boy, se hace lo siguiente:

```
class PersonFactory(BaseFactory):
    class Meta:
        model = Person
        django_get_or_create = ('name', )

    person_id = factory.Sequence(lambda n: -n)
    name = factory.Faker('name', locale='es_ES')
```

El número de secuencia calculado (el número total más uno), se devuelve en negativo. Esto hace que la primera fila generada tenga un -1, la segunda un -2 y así sucesivamente.

### 3.4.2 Faker
Factory boy facilita la generación de datos aleatorios por defecto. Por ejemplo, para el nombre en la clase `PersonFactory` usamos:

```
    name = factory.Faker('name', locale='es_ES')
```

Esto nos genera (siempre que no se indique un `name` en la llamada) un nombre aleatorio, usando el la localización española (los nombres y apellidos serán más o menos nombres españoles)

### 3.4.3 Uso del Builder
Este es um ejemplo de uso del builder para la generación de datos de prueba para un módulo:

```
class TestDataBuilder(BaseDataBuilder):
    builder = Builder()

    @transaction.atomic()
    def build(self):
        log.info("Building test data for module 2")
        self.build_people()
        self.build_things()

    def build_people(self):
        log.info("Building people")
        self.person_no_things = self.builder.person(name='No things')
        self.person_car = self.builder.person(name='Car')
        self.person_house = self.builder.person(name='House')
        self.person_both = self.builder.person(name='Both')

    def build_things(self):
        log.info("Building things")
        self.builder.car(person=self.person_car, detail='Car Make')
        log.info("Building things 1")
        self.builder.house(person=self.person_house, detail='House address')
        log.info("Building things 2")
        self.builder.car(person=self.person_both, detail='Car Make')
        log.info("Building things 3")
        self.builder.house(person=self.person_both, detail='House address')

    @transaction.atomic()
    def clear(self):
        log.info("Clearing data for module 2 ")
        Car.objects.all().delete()
        House.objects.all().delete()
        Thing.objects.all().delete()
        Person.objects.all().delete()
        ThingType.objects.all().delete()


def build_test_data(clear=True):
    builder = TestDataBuilder()
    if clear:
        builder.clear()
    builder.build()
```

El método `build_test_data` es el que se ejecuta para generar los datos de cada aplicación.
En el `Builder` se definen los métodos para crear filas en todas las tablas, usando las factories de factory boy. Para cada modelo debe definirse una factory (manualmente), y el `Builder` usa esas factories para generar datos más elaborados.

### 3.4.4 Tablas maestras
Hay determinadas tablas que contendrán información más o menos fija, que será usada por otras tablas. Estas tablas se llaman habitualmente tablas de códigos o tablas maestras.

En el ejemplo, en el `module2`, tenemos una tabla de este tipo, llamada `THING_TYPE`. Es interesante que estas tablas tengan insertados los datos por defecto para nuestro entorno de pruebas. Para esto, hemos creado una clase llamada `MasterTables` donde se concentrará toda la información de las tablas maestras. Por ejemplo, en nuestra `MasterTables` definimos:

```
class MasterTables:
    THING_TYPE = {
        'CAR': {'thing_type_code': 'CAR', 'name': 'Car'},
        'HOU': {'thing_type_code': 'HOU', 'name': 'House'},
    }
```

La clase tendrá un objeto Python por cada master table. En cada `key` tendrá el código, y en el `value` tendrá otro objeto con los campos de la tabla y sus valores por defecto.

A la hora de recuperar una fila de la tabla, haremos:

```
    @functools.lru_cache(maxsize=128)
    def get_thing_type(self, thing_type_code):
        data = MasterTables.THING_TYPE[thing_type_code]
        if data:
            return ThingTypeFactory(**data)
        return None

    def thing(self, person=None, thing_type='CAR'):
        log.info(f"Building thing {thing_type}")
        thing_type_object = self.get_thing_type(thing_type)
        ...
```

`lru_cache` hace que la primera vez que se ejecuta la función se cree la fila usando la factory, y en posteriores llamadas para el mismo código se devuelve el objeto creado, sin accesos adicionales a la base de datos.

He creado un procedimiento PL/SQL que, ejecutado en un entorno de producción, genera el código Python para una tabla maestra, de forma que sea sencillo volcar la información de una tabla a la clase `MasterTables`.

```
CREATE OR REPLACE PROCEDURE export_data_to_python(p_table_name varchar2) IS
    l_sql VARCHAR2(4000);
    type t_fields is table of varchar2(255) index by binary_integer;
    pk_fields t_fields;
    all_fields t_fields;
  BEGIN
    select cc.column_name
    bulk collect into pk_fields
    from ALL_CONSTRAINTS c, ALL_CONS_COLUMNS cc
    where c.table_name=p_table_name and constraint_type='P' and cc.constraint_name=c.constraint_name
    order by cc.column_name;
    select c.column_name
    bulk collect into all_fields
    from ALL_TAB_COLUMNS c
    where c.table_name=p_table_name
    order by c.column_name;
    l_sql := 'DECLARE python varchar2(32000) := ''' || upper(p_table_name) || '={'' || chr(10); ' ||
             'k varchar2(32000); v varchar2(32000); ' ||
             'BEGIN FOR r IN (SELECT * FROM '||p_table_name|| ') LOOP ';

    l_sql := l_sql || ' k := ''''; ';
    l_sql := l_sql || ' v := ''''; ';
    -- construir la key del dict
    FOR i IN 1 .. pk_fields.COUNT loop
        l_sql := l_sql || ' k := k || r.' || pk_fields(i) || '; ';
    end loop;
    -- construir el value del dict
    FOR i IN 1 .. all_fields.COUNT loop
        l_sql := l_sql || ' v := v || ''"' || lower(all_fields(i)) || '": "'' || r.' || all_fields(i) || ' || ''", '';';
    end loop;
    --TODO
    l_sql := l_sql || 'python := python|| chr(9) || ''"'' || k || ''": { '' || v || ''}, '' || chr(10); ';

    l_sql := l_sql || '   END LOOP; '
             || 'python := python || chr(10) || '' }'';'
             || ' dbms_output.put_line(python); ' ||
             ' END; ';
    EXECUTE IMMEDIATE l_sql;
END;
```

Una vez se ejecuta el PL (en un entorno que tenga datos) así:

```
begin
    export_data_to_python('THING_TYPE');
end;
```

Obtenemos en la salida de `DBMS_OUTPUT` el código Python:

```
    THING_TYPE = {
        'CAR': {'thing_type_code': 'CAR', 'name': 'Car'},
        'HOU': {'thing_type_code': 'HOU', 'name': 'House'},
    }
```
Este código puede pegarse directamente en la clase `MasterTables`, y puede usarse en la función correspondiente para obtener los datos, usando la caché que hemos comentado.

# 4. Ejecución de pruebas automáticas

TODO
