import os

import pyspark
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split

os.environ["PYSPARK_PYTHON"] = "python3"
os.environ["SPARK_LOCAL_HOSTNAME"] = "localhost"


def send_data(tags: dict) -> None:
    url = 'http://localhost:5001/updateData'
    response = requests.post(url, json=tags)


def process_row(row: pyspark.sql.types.Row) -> None:
    tags = row.asDict()
    print(tags)  # {'hashtag': '#Colorado', 'count': 1}
    send_data(tags)


def new():
   
    spark = SparkSession.builder.appName("SparkTwitterAnalysis").getOrCreate()

    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    lines = spark.readStream.format("socket").option("host", "127.0.0.1").option("port", 9009).load()
    words = lines.select(explode(split(lines.value, " ")).alias("hashtag"))
    wordCounts = words.groupBy("hashtag").count()
    query = wordCounts.writeStream.foreach(process_row).outputMode('Update').start()

    query.awaitTermination()


if __name__ == '__main__':
    try:
        new()
    except BrokenPipeError:
        exit("Pipe Broken, Exiting...")
    except KeyboardInterrupt:
        exit("Keyboard Interrupt, Exiting..")
    except Exception as e:
        # traceback.print_exc()
        exit("Error in Spark App")
