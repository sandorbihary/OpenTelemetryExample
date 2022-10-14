from logging import exception
from grpc import StatusCode
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
#from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.status import Status, StatusCode

from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from opentelemetry.sdk.trace.sampling import StaticSampler
from opentelemetry.sdk.trace.sampling import Sampler
from opentelemetry.sdk.trace.sampling import Decision
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

import requests
import time
from flask import Flask, jsonify
import json
import sys
import os
import random

import mysql.connector
from opentelemetry.instrumentation.mysql import MySQLInstrumentor
MySQLInstrumentor().instrument()


#If testmode == TEST we will brake the cycle, otherwise we will run it in an infitite loop
TestMode = os.getenv('TESTMODE')
endpoint = os.getenv('OTEL_ENDPOINT')
service_name = os.getenv('ENV_TAG_OTEL')
if TestMode is None:
  TestMode = "PRODUCTION"
if service_name is None:
  service_name = "DefaultServiceFromSanyi"

resource = Resource(attributes={
"service.name": service_name,
"service.namespace": "DEMO",
"telemetry.sdk.language": "python"   
})

#Example samping using ratio
#sampler = TraceIdRatioBased(1/1)
#Example sampling based on  qAVA ANVpredefined rules.
#https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.sampling.html#opentelemetry.sdk.trace.sampling.Decision
sampler =  StaticSampler(Decision(2))
trace.set_tracer_provider(TracerProvider(resource= resource, sampler = sampler))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="endpoint", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)

trace.get_tracer_provider().add_span_processor(span_processor)

#OTEL automatic instrumentor
RequestsInstrumentor().instrument()
def telex():
    with tracer.start_as_current_span("CallTheWeb"):
        url = "http://bash.hu"
        dice = random.randint(0,9)
        if dice == 0:
            url = "https://telex.hu"
        print(url)
        try:
            response = requests.get(url)
            #print(response.status_code)
            current_span = trace.get_current_span()
            current_span.add_event("This is the Telex call")
            current_span.add_event("Calling URL: {}".format(url))
            current_span.set_attribute("URL", url)
        except Exception as e:
            print(e)
            current_span = trace.get_current_span()
            current_span.record_exception(e)
            current_span.add_event("This is the Telex call")
            current_span.add_event("Calling URL: {}".format(url))
            current_span.set_attribute("URL", url)
            current_span.set_status(Status(StatusCode.ERROR, str(e)))

def callnode1():
    with tracer.start_as_current_span("CallOtelNodes1"):
        try:
            url1 = "http://192.168.1.1:9002"
            print(url1)
            response = requests.get(url1)
            current_span = trace.get_current_span()
            current_span.add_event("This is Calling other nodes")
            current_span.set_attribute("URL1", url1)

        except Exception as e:
            print(e)
            current_span = trace.get_current_span()
            current_span.record_exception(e)
            current_span.add_event("This is Calling other nodes")
            current_span.set_status(Status(StatusCode.ERROR, str(e)))
            current_span.set_attribute("URL1", url1)
    
def callnode2():
    with tracer.start_as_current_span("CallOtelNodes9903"):
        try:

            url1 = "http://192.168.1.1:9903/get_my_ip"
            #print(url1)
            response = requests.get(url1)
            current_span = trace.get_current_span()
            current_span.add_event("This is Calling other nodes")
            current_span.set_attribute("URL1", url1)

        except Exception as e:
            #print(e)
            current_span = trace.get_current_span()
            current_span.record_exception(e)
            current_span.add_event("This is Calling node 9903")
            current_span.set_status(Status(StatusCode.ERROR, str(e)))
            current_span.set_attribute("URL1", url1)

def callnode3():
    with tracer.start_as_current_span("CallOtelNodes9904"):
        try:

            url1 = "http://192.168.1.1:9904/get_my_ip"
            #print(url1)
            response = requests.get(url1)
            current_span = trace.get_current_span()
            current_span.add_event("This is Calling node 9904")
            current_span.set_attribute("URL1", url1)

        except Exception as e:
            print(e)
            current_span = trace.get_current_span()
            current_span.record_exception(e)
            current_span.add_event("This is Calling other nodes")
            current_span.set_status(Status(StatusCode.ERROR, str(e)))
            current_span.set_attribute("URL1", url1)


def callnodeBad():
    with tracer.start_as_current_span("CallOtelNodes3"):
        try:

            url1 = "http://127.0.0.1:9009"
            #print(url1)
            response = requests.get(url1)
            current_span = trace.get_current_span()
            current_span.add_event("This is Calling other nodes")
            current_span.set_attribute("URL1", url1)

        except Exception as e:
            print(e)
            current_span = trace.get_current_span()
            current_span.record_exception(e)
            current_span.add_event("This is Calling other nodes")
            current_span.set_status(Status(StatusCode.ERROR, str(e)))
            current_span.set_attribute("URL1", url1)

def callmysql():
  time.sleep(0.1)
  try:  
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password=password,
      database=password
      )
    
    #print(mydb)
    
    mycursor = mydb.cursor()
    query = "SELECT * FROM table"
    
    mycursor.execute(query)
    rows = mycursor.fetchall()
    for row in rows:
        pass
    
  
  except mysql.connector.Error as err:
    print("Something went wrong: {}".format(err))




while True:
    telex()
    callnode1()
    callnode2()
    callnode3()
    callnodeBad()
    callmysql()


    with tracer.start_as_current_span("DivisionTestSanyi"):
        try:
            current_span = trace.get_current_span()
            current_span.add_event("We will test here the Exception handling")
            dice = random.randint(0,9)
            #print(dice)
            if dice == 8:
              X = 5 / "badtype"
            if dice == 9:
              X = 5 / novariable
            #  X = 5
            else:
              if dice == 7:
                time.sleep(1)
              X = 10 / dice
              current_span.add_event("event message 10 Divided by: {}".format(dice))
              current_span.set_attribute("DivisionParam", dice)
              current_span.set_attribute("DivisionParamSTR", str(dice))
              current_span.set_attribute("DivisionResults", X) 

        except ZeroDivisionError as e:
            current_span.add_event("event message 10 Divided by: {}".format(dice))
            current_span.set_attribute("DivisionParam", dice)
            current_span.set_attribute("DivisionParamSTR", str(dice))
            current_span.set_attribute("DivisionResults", "Error") 
            current_span.set_attribute("DivisionException",  str(e))
            
            current_span = trace.get_current_span()
            current_span.record_exception(e)
            current_span.set_status(Status(StatusCode.ERROR, str(e)))
        
        except NameError as e:
            current_span.add_event("event message 10 Divided by: {}".format(dice))
            current_span.set_attribute("DivisionParam", dice)
            current_span.set_attribute("DivisionResults", "Error") 
            current_span.set_attribute("DivisionException", str(e))

            current_span = trace.get_current_span()
            current_span.record_exception(e)
            current_span.set_status(Status(StatusCode.ERROR, str(e)))
        
        except TypeError as e:
            current_span.add_event("event message 10 Divided by: {}".format(dice))
            current_span.set_attribute("DivisionParam", dice)
            current_span.set_attribute("DivisionResults", "Error") 
            current_span.set_attribute("DivisionException", str(e))
        
            
            current_span = trace.get_current_span()
            current_span.record_exception(e)
            current_span.set_status(Status(StatusCode.ERROR, str(e)))



    if TestMode == "TEST":
        print(TestMode)
        print("Test MODE exiting.")
        sys.exit(0)
