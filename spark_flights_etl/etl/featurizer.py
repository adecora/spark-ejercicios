import pyspark.sql.functions as F
from pyspark.sql import DataFrame


class Featurizer:
    @staticmethod
    def preprocesa(df: DataFrame) -> DataFrame:
        # elimina este error y añade aquí tu código
        return (
            df.fillna(
                0,
                subset=[
                    "CarrierDelay",
                    "WeatherDelay",
                    "NASDelay",
                    "SecurityDelay",
                    "LateAircraftDelay",
                ],
            )
            .withColumn("Diverted", F.col("Diverted") == 1)
            .fillna(0, subset=["DepTime"])
            .withColumn(
                "DepTime",
                F.when(F.col("DepTime") == 2400, 0).otherwise(F.col("DepTime")),
            )
            .withColumn(
                "FlightTs",
                F.to_timestamp(
                    F.concat_ws(
                        " ", F.col("FlightDate"), F.lpad(F.col("DepTime"), 4, "0")
                    ),
                    "yyyy-MM-dd HHmm",
                ),
            )
        )
