import json
from pathlib import Path

from databricks.connect import DatabricksSession

BASE_DIR = Path(__file__).parent

config = json.loads((BASE_DIR / "config/config.json").read_text())

print("config", config)

spark = DatabricksSession.builder.profile(
    config["DATABRICKS_CONFIG_PROFILE"]
).getOrCreate()

df = (
    spark.read.option("header", "true")
    .option("inferSchema", "true")
    .csv(config["raw_input_file"])
)

print("flights jan apr 2018")
print("====================")
df.show(5)
