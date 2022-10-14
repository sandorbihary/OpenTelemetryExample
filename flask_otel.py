from urllib import response
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
#from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

import requests
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor


import time
from flask import Flask, jsonify
from flask import request




# Resource can be required for some backends, e.g. Jaeger
# If resource wouldn't be set - traces wouldn't appears in Jaeger
resource = Resource(attributes={
    "telemetry.sdk.language": "python",
    "service.name": "DemoNode3",
    "service.namespace": "DEMO"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="127.0.0.1:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)

trace.get_tracer_provider().add_span_processor(span_processor)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.route('/')
def index():
    #RequestsInstrumentor().instrument()
    return jsonify({'name': 'node5',
                    'address': '127.0.0.1:9005'})

@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    current_span = trace.get_current_span()
    current_span.set_attribute("Source IP", request.remote_addr)
    return jsonify({'ip': request.remote_addr}), 200

app.route("/call9904", methods=["GET"])
def get_my_ip():
    current_span = trace.get_current_span()
    current_span.set_attribute("Source IP", request.remote_addr)
    response = requests.get(url="http://127.0.0.1:9903")
    time.sleep(0.2)
    return jsonify({'ip': request.remote_addr}), 200


app.run(host='0.0.0.0', port=9904)
