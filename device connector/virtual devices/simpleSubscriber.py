import paho.mqtt.client as PahoMQTT
import time
import json
from influxdb import InfluxDBClient

class MySubscriber:
	def __init__(self, clientID, topic, broker = "localhost", port = 1883, notifier = None, QoS = 2):
		self.clientID = clientID
		self.topic = topic
		self.broker = broker
		self.port = port
		self.notifier=notifier
		self.QoS = QoS

		self._paho_mqtt = PahoMQTT.Client(clientID, False)
		
		self._paho_mqtt.on_connect = self.myOnConnect
		self._paho_mqtt.on_message = self.myOnMessageReceived

	def start (self):
		print(f"{self.clientID} starting")
		self._paho_mqtt.connect(self.broker, self.port)
		self._paho_mqtt.loop_start()
		self._paho_mqtt.subscribe(self.topic, self.QoS)

	def stop (self):
		print(f"{self.clientID} stopping")
		self._paho_mqtt.unsubscribe(self.topic)
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print(f"{self.clientID} connected to {self.broker} with result code: {rc}")

	def myOnMessageReceived (self, paho_mqtt, userdata, msg):
		if self.notifier is not None:
			self.notifier.notify(msg)


if __name__ == "__main__":
	test = MySubscriber('VirtualBuilding')
	test.start()
	while (True):
		pass