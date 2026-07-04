import pyspark.sql.functions as F
import pyspark.sql.types as T

from ..etl import Featurizer


class FlujoDiario:
    """
    ETL diaria
    """

    def __init__(self, spark, properties: dict):
        self.properties = properties
        self.spark = spark
        self.type_map = {
            "string": T.StringType(),
            "integer": T.IntegerType(),
            "int": T.IntegerType(),
            "long": T.LongType(),
            "double": T.DoubleType(),
            "float": T.FloatType(),
            "boolean": T.BooleanType(),
            "date": T.DateType(),
            "timestamp": T.TimestampType(),
        }

    def run(self):
        # podríamos recuperar la SparkSession activa desde cualquier DF o bien con SparkSession.builder.getOrCreate()
        # porque se comporta de manera similar a un Singleton (objeto del que solo existe una instancia en nuestro
        # programa), aunque no es exactamente un Singleton ya que en casos particulares, es posible crear varias
        # sesiones al mismo tiempo:
        # https://medium.com/analytics-vidhya/spark-session-and-the-singleton-misconception-1aa0eb06535a

        # storage_account_name = self.properties["STORAGE_ACCOUNT_NAME"]
        schema = T.StructType(
            [
                T.StructField(field["name"], self.type_map[field["type"]], True)
                for field in self.properties["input_file_schema"]
            ]
        )

        # si necesitas leer, lo ideal es usar una
        # propiedad del fichero de configuración, que podemos llamar por ejemplo STORAGE_ACCOUNT_NAME
        flights_df = (
            self.spark.read
            # Si estás usando Databricks Free Edition, necesitarás indicar la clave de acceso a tu cuenta de almacenamiento
            # de Azure cada vez que quieras leer , ya que Free Edition no permite editar las propiedades
            # del cluster para configurar ahí la clave para todas las lecturas.
            # .option("fs.azure.account.key.tu_storage_account_aquí.dfs.core.windows.net",
            #        "tu_api_key_aquí")
            .option("header", "true")
            .schema(schema)
            .csv(self.properties["raw_input_file"])
        )

        flights_df.printSchema()

        if raw_ingestion_date := self.properties.get("raw_ingestion_date"):
            flights_df = flights_df.filter(F.col("FlightDate") == raw_ingestion_date)

        print(
            f"Guardando los datos sin procesar en la tabla «{self.properties['bronze_table']}»"
        )
        print("=" * 50)
        flights_df.write.mode("overwrite").format("delta").saveAsTable(
            self.properties["bronze_table"]
        )

        # Llamada a Featurizer para preprocesar el DataFrame
        flights_preprocess = Featurizer.preprocesa(flights_df)

        print(
            f"Guardando los datos procesados en la tabla «{self.properties['silver_table']}»"
        )
        print("=" * 50)
        flights_preprocess.write.mode("overwrite").format("delta").saveAsTable(
            self.properties["silver_table"]
        )
