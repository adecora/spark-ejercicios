import json
import os
from pprint import pprint

from . import FlujoDiario


class Launcher:
    def __init__(self, config_path: str):
        """
        Inicializa un lanzador y lo deja preparado para ejecutar cualquier tipo de procesamiento
        :param config_path: ruta al fichero JSON de configuración para este trabajo. Debe estar en DBFS si ejecutamos
                            desde un notebook de Databricks, o en una ruta de nuestro portátil si usamos dbconnect
        """
        with open(config_path, "r") as f:
            self.properties = json.load(f)
            pprint(self.properties)

            # fijamos la variable de entorno necesaria para que lea la config adecuada del fichero .databrickscfg
            os.environ["DATABRICKS_CONFIG_PROFILE"] = self.properties[
                "DATABRICKS_CONFIG_PROFILE"
            ]

        if self.properties["EXECUTION_ENVIRONMENT"] == "databricks":
            from databricks.connect import DatabricksSession

            self.spark = DatabricksSession.builder.profile(
                self.properties["DATABRICKS_CONFIG_PROFILE"]
            ).getOrCreate()
            self.spark.addTag(
                self.properties.get("SPARK_APP_NAME", "Spark Flights ETL")
            )

        else:
            from pyspark.sql import SparkSession

            self.spark = SparkSession.builder.appName(
                self.properties.get("SPARK_APP_NAME", "Spark Flights ETL")
            ).getOrCreate()

    def flujo_diario(self):
        flujo_diario = FlujoDiario(self.spark, self.properties)
        flujo_diario.run()


if __name__ == "__main__":
    from pathlib import Path

    BASE_DIR = Path(__file__).parent.parent
    print("BASE_DIR", BASE_DIR)
    launcher = Launcher(BASE_DIR / "config/config.json")
    launcher.flujo_diario()
