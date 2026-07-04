# Entorno

El fichero [pyproject.toml](./pyproject.toml) contiene la configuración del paquete de python.

Se crean un paquete con dos grupos de dependencias de desarrollo, estas dependencias no se incluyen en la metadata del paquete generado.

```toml
# https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-groups
[dependency-groups]
connect = [
    "databricks-connect==18.2.*",
    "python-dotenv",
    "ipykernel>=7.3.0",
]
pyspark = [
    "pyspark==4.1.2",
    "pandas",
    "python-dotenv",
    "ipykernel>=7.3.0",
    "pytest==8.3.4",
]
```

El entorno `pyspark` ejecuta spark de forma local en nuestro ordernador, se utiliza para lanzar los tests. El entorno `connect` se utiliza para desarrollar ejecutando el código en el cluster de databricks indicado en el fichero de configuración **~/.databrickscfg**. `connect` y `pyspark` no pueden coexistir, databricks-connect incluye pyspark, hay que indicarselo de forma explícita a `uv`.

```toml
[tool.uv]
conflicts = [
    [
        { extra = "connect" },
        { extra = "pyspark" },
    ],
]
```

Se puede modificar el interprete de `python` desde el IDLE cuando sea necesario.

![Ejecución local con `pyspark`.](./img/ejecucion-pyspark.png)

![Ejecución remota en el cluster con `databricks-connect`.](./img/ejecucion-connect.png)

Para poder ejecutar `pyspark` de forma local primero es necesario instalar el `jdk17-openjdk` en [entorno.ipynb](./entorno.ipynb). Para generar lo entornos:

```bash
$ UV_PROJECT_ENVIRONMENT=.venv-pyspark uv sync --only-group pyspark
$ UV_PROJECT_ENVIRONMENT=.venv-connect uv sync --only-group connect
```

Para ejecutar los tests:

```bash
$ UV_PROJECT_ENVIRONMENT=.venv-pyspark pytest
```

Para desarrollar con un subset del total de los datos:

```bash
$ cat <(head -1 flights-jan-apr-2018.csv) <(head -n -1 flights-jan-apr-2018.csv | shuf -n 50000) > flights-subset.csv
```